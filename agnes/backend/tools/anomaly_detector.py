import pandas as pd
import numpy as np
from typing import List


class AnomalyDetector:
    """
    Detects anomalies in sales, returns, and channel data
    using Z-score and IQR methods.
    """

    def detect_all(self, sales_data: pd.DataFrame, products: pd.DataFrame,
                   inventory: pd.DataFrame, channels: pd.DataFrame) -> List[dict]:
        """Run all anomaly detection checks and return alerts."""
        alerts = []
        alerts.extend(self.detect_sales_anomalies(sales_data, products))
        alerts.extend(self.detect_return_anomalies(sales_data, products))
        alerts.extend(self.detect_slow_movers(sales_data, products, inventory))
        alerts.extend(self.detect_channel_mismatches(channels, products))
        return alerts

    def detect_sales_anomalies(self, sales_data: pd.DataFrame,
                                products: pd.DataFrame) -> List[dict]:
        """Detect unusual sales spikes or drops per SKU."""
        alerts = []
        for sku in sales_data["sku_id"].unique():
            sku_data = sales_data[sales_data["sku_id"] == sku].copy()
            daily = sku_data.groupby("date")["quantity_sold"].sum().sort_index()

            if len(daily) < 14:
                continue

            mean = daily.tail(30).mean()
            std = daily.tail(30).std()
            if std == 0:
                continue

            # Check last 7 days for anomalies
            recent = daily.tail(7)
            for date, value in recent.items():
                z_score = (value - mean) / std

                if z_score > 2.5:
                    name = self._get_name(products, sku)
                    alerts.append({
                        "sku_id": sku,
                        "product_name": name,
                        "alert_type": "sales_spike",
                        "severity": "high" if z_score > 3 else "medium",
                        "description": f"Sales spike detected for {name}: {int(value)} units on {date.strftime('%Y-%m-%d')} vs avg {mean:.0f}",
                        "metric_value": float(value),
                        "expected_value": round(mean, 1),
                        "deviation_pct": round((value - mean) / mean * 100, 1),
                        "recommendation": f"Investigate cause of spike. Check if promotion is running. Consider increasing safety stock.",
                    })
                elif z_score < -2.0:
                    name = self._get_name(products, sku)
                    alerts.append({
                        "sku_id": sku,
                        "product_name": name,
                        "alert_type": "sales_drop",
                        "severity": "medium",
                        "description": f"Unusual sales drop for {name}: {int(value)} units on {date.strftime('%Y-%m-%d')} vs avg {mean:.0f}",
                        "metric_value": float(value),
                        "expected_value": round(mean, 1),
                        "deviation_pct": round((value - mean) / mean * 100, 1),
                        "recommendation": f"Check for stockout, listing issues, or competitor activity.",
                    })
        return alerts

    def detect_return_anomalies(self, sales_data: pd.DataFrame,
                                 products: pd.DataFrame) -> List[dict]:
        """Detect unusual return rate spikes."""
        alerts = []
        for sku in sales_data["sku_id"].unique():
            sku_data = sales_data[sales_data["sku_id"] == sku].copy()
            daily = sku_data.groupby("date").agg(
                sold=("quantity_sold", "sum"),
                returned=("returns", "sum"),
            )
            daily["return_rate"] = daily["returned"] / daily["sold"].replace(0, 1)

            if len(daily) < 14:
                continue

            avg_rate = daily["return_rate"].tail(30).mean()
            recent_rate = daily["return_rate"].tail(7).mean()

            if avg_rate > 0 and recent_rate > avg_rate * 2.5 and recent_rate > 0.08:
                name = self._get_name(products, sku)
                alerts.append({
                    "sku_id": sku,
                    "product_name": name,
                    "alert_type": "return_spike",
                    "severity": "critical" if recent_rate > 0.15 else "high",
                    "description": f"Return rate for {name} jumped to {recent_rate:.1%} (avg: {avg_rate:.1%}). This is {recent_rate/avg_rate:.1f}x the normal rate.",
                    "metric_value": round(recent_rate * 100, 1),
                    "expected_value": round(avg_rate * 100, 1),
                    "deviation_pct": round((recent_rate - avg_rate) / avg_rate * 100, 1),
                    "recommendation": f"Check product quality, shipping damage, or listing accuracy for {name}. Consider pausing ads until resolved.",
                })
        return alerts

    def detect_slow_movers(self, sales_data: pd.DataFrame,
                           products: pd.DataFrame,
                           inventory: pd.DataFrame) -> List[dict]:
        """Flag products with high stock but low recent sales."""
        alerts = []
        recent_sales = (
            sales_data[sales_data["date"] >= sales_data["date"].max() - pd.Timedelta(days=14)]
            .groupby("sku_id")["quantity_sold"].sum()
        )

        for _, inv_row in inventory.iterrows():
            sku = inv_row["sku_id"]
            stock = inv_row["quantity_on_hand"]
            recent = recent_sales.get(sku, 0)
            daily_avg = recent / 14 if recent > 0 else 0

            if stock > 0 and daily_avg > 0:
                days_of_stock = stock / daily_avg
                if days_of_stock > 90:
                    name = self._get_name(products, sku)
                    alerts.append({
                        "sku_id": sku,
                        "product_name": name,
                        "alert_type": "slow_moving",
                        "severity": "medium",
                        "description": f"{name} has {int(days_of_stock)} days of stock remaining at current sales rate ({daily_avg:.1f}/day). Consider running a promotion.",
                        "metric_value": round(days_of_stock, 1),
                        "expected_value": 45.0,
                        "deviation_pct": round((days_of_stock - 45) / 45 * 100, 1),
                        "recommendation": f"Run a promotion or discount to move excess inventory. Consider reallocating warehouse space.",
                    })
        return alerts

    def detect_channel_mismatches(self, channels: pd.DataFrame,
                                   products: pd.DataFrame) -> List[dict]:
        """Detect when one channel significantly outperforms/underperforms others."""
        alerts = []
        if channels.empty:
            return alerts

        for sku in channels["sku_id"].unique():
            sku_data = channels[channels["sku_id"] == sku]
            channel_totals = sku_data.groupby("channel")["quantity_sold"].sum()

            if len(channel_totals) < 2:
                continue

            mean_sales = channel_totals.mean()
            for channel, sales in channel_totals.items():
                if mean_sales > 0 and sales > mean_sales * 2.5:
                    name = self._get_name(products, sku)
                    alerts.append({
                        "sku_id": sku,
                        "product_name": name,
                        "alert_type": "channel_mismatch",
                        "severity": "low",
                        "description": f"{name} sells {sales/mean_sales:.1f}x more on {channel} vs other channels. Consider reallocating marketing budget.",
                        "metric_value": float(sales),
                        "expected_value": round(mean_sales, 1),
                        "deviation_pct": round((sales - mean_sales) / mean_sales * 100, 1),
                        "recommendation": f"Investigate why {channel} outperforms. Replicate success on other channels or double down.",
                    })
        return alerts

    def detect_for_sku(self, sku_id: str, sales_data: pd.DataFrame,
                       products: pd.DataFrame, inventory: pd.DataFrame,
                       channels: pd.DataFrame) -> List[dict]:
        """Run all checks but filter results to a specific SKU."""
        all_alerts = self.detect_all(sales_data, products, inventory, channels)
        return [a for a in all_alerts if a["sku_id"] == sku_id]

    def _get_name(self, products: pd.DataFrame, sku: str) -> str:
        match = products[products["sku_id"] == sku]
        return match["product_name"].values[0] if len(match) > 0 else sku
