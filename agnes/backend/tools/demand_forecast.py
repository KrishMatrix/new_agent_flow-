import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Optional


class DemandForecaster:
    """
    Demand forecasting using exponential smoothing and moving averages.
    Provides predictions with confidence intervals.
    """

    def forecast(
        self,
        sales_data: pd.DataFrame,
        horizon_days: int = 14,
        sku_id: str = "",
        product_name: str = "",
    ) -> dict:
        """
        Generate demand forecast for a SKU.

        Args:
            sales_data: DataFrame with columns [date, quantity_sold]
            horizon_days: Number of days to forecast
            sku_id: SKU identifier
            product_name: Human-readable product name

        Returns:
            Dict with forecast points, trend, and summary stats.
        """
        if len(sales_data) < 7:
            return self._insufficient_data_response(sku_id, product_name, horizon_days)

        sales_data = sales_data.sort_values("date").copy()
        ts = sales_data.set_index("date")["quantity_sold"].astype(float)

        # Fill missing dates
        full_idx = pd.date_range(ts.index.min(), ts.index.max(), freq="D")
        ts = ts.reindex(full_idx).fillna(method="ffill").fillna(0)

        # Exponential smoothing
        alpha = 0.3
        smoothed = ts.ewm(alpha=alpha, adjust=False).mean()

        # Trend detection via linear regression on last 30 days
        recent = ts.tail(30)
        x = np.arange(len(recent))
        if len(recent) > 1:
            slope = np.polyfit(x, recent.values, 1)[0]
        else:
            slope = 0

        # Moving average baselines
        ma7 = ts.tail(7).mean()
        ma30 = ts.tail(30).mean()

        # Determine trend
        if slope > 0.5:
            trend = "up"
        elif slope < -0.5:
            trend = "down"
        else:
            trend = "stable"

        # Generate forecast
        last_date = ts.index.max()
        last_value = smoothed.iloc[-1]
        std_dev = ts.tail(14).std()

        forecast_points = []
        for i in range(1, horizon_days + 1):
            date = last_date + timedelta(days=i)
            # Base prediction with trend continuation
            predicted = last_value + slope * i
            predicted = max(0, predicted)

            # Day-of-week seasonality
            dow = date.weekday()
            if dow >= 5:  # Weekend
                predicted *= 1.15

            lower = max(0, predicted - 1.96 * std_dev)
            upper = predicted + 1.96 * std_dev

            forecast_points.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_sales": round(predicted, 1),
                "lower_bound": round(lower, 1),
                "upper_bound": round(upper, 1),
            })

        # Seasonal note
        seasonal_note = None
        if ma7 > ma30 * 1.3:
            seasonal_note = "Sales are trending significantly above the 30-day average — possible seasonal surge or promotion effect."
        elif ma7 < ma30 * 0.7:
            seasonal_note = "Sales have dipped well below the 30-day average — potential demand cooling off."

        total_predicted = sum(p["predicted_sales"] for p in forecast_points)

        return {
            "sku_id": sku_id,
            "product_name": product_name,
            "horizon_days": horizon_days,
            "forecast": forecast_points,
            "trend": trend,
            "seasonal_note": seasonal_note,
            "total_predicted": round(total_predicted, 1),
            "ma7": round(ma7, 1),
            "ma30": round(ma30, 1),
        }

    def _insufficient_data_response(self, sku_id, product_name, horizon_days):
        return {
            "sku_id": sku_id,
            "product_name": product_name,
            "horizon_days": horizon_days,
            "forecast": [],
            "trend": "unknown",
            "seasonal_note": "Insufficient data for reliable forecasting.",
            "total_predicted": 0,
            "ma7": 0,
            "ma30": 0,
        }
