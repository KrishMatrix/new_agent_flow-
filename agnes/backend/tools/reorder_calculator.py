import math
import pandas as pd
from typing import Optional


class ReorderCalculator:
    """
    Calculates reorder points, safety stock, EOQ, and days of stock remaining.
    """

    def calculate(
        self,
        sku_id: str,
        product_name: str,
        quantity_on_hand: int,
        lead_time_days: int,
        daily_sales: pd.Series,
        unit_cost: float = 10.0,
        holding_cost_pct: float = 0.25,
        order_cost: float = 50.0,
    ) -> dict:
        """
        Calculate full reorder recommendation for a SKU.

        Returns dict with reorder point, quantity, safety stock, days remaining, and risk assessment.
        """
        if len(daily_sales) < 7:
            return self._insufficient_data(sku_id, product_name, quantity_on_hand)

        avg_daily = daily_sales.tail(30).mean()
        std_daily = daily_sales.tail(30).std()

        if avg_daily <= 0:
            return {
                "sku_id": sku_id,
                "product_name": product_name,
                "avg_daily_demand": 0,
                "days_of_stock": float("inf"),
                "safety_stock": 0,
                "reorder_point": 0,
                "eoq": 0,
                "recommended_order_qty": 0,
                "reorder_by_date": "N/A",
                "risk": "none",
                "risk_detail": "No recent demand detected.",
            }

        # Days of stock remaining
        days_of_stock = quantity_on_hand / avg_daily

        # Safety stock (service level ~95%, z=1.65)
        z_score = 1.65
        safety_stock = z_score * std_daily * math.sqrt(lead_time_days)
        safety_stock = max(1, round(safety_stock))

        # Reorder point
        reorder_point = round(avg_daily * lead_time_days + safety_stock)

        # Economic Order Quantity (EOQ)
        annual_demand = avg_daily * 365
        holding_cost = unit_cost * holding_cost_pct
        if holding_cost > 0:
            eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
            eoq = max(1, round(eoq))
        else:
            eoq = round(avg_daily * 30)

        # Risk assessment
        if days_of_stock < lead_time_days:
            risk = "critical"
            risk_detail = f"Stock will run out BEFORE next shipment arrives! Only {days_of_stock:.1f} days left vs {lead_time_days}-day lead time."
        elif days_of_stock < lead_time_days + 5:
            risk = "high"
            risk_detail = f"Cutting it close — {days_of_stock:.1f} days of stock with {lead_time_days}-day lead time. Order immediately."
        elif quantity_on_hand < reorder_point:
            risk = "medium"
            risk_detail = f"Below reorder point ({quantity_on_hand} < {reorder_point}). Place order soon."
        else:
            risk = "low"
            risk_detail = f"Healthy stock levels. {days_of_stock:.1f} days remaining."

        # Recommended order quantity
        recommended_qty = max(eoq, round(avg_daily * 30))

        # Reorder by date
        days_until_reorder = max(0, days_of_stock - lead_time_days - 2)  # 2-day buffer
        from datetime import datetime, timedelta
        reorder_by = datetime.now() + timedelta(days=days_until_reorder)

        return {
            "sku_id": sku_id,
            "product_name": product_name,
            "quantity_on_hand": quantity_on_hand,
            "avg_daily_demand": round(avg_daily, 1),
            "std_daily_demand": round(std_daily, 1),
            "days_of_stock": round(days_of_stock, 1),
            "lead_time_days": lead_time_days,
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "eoq": eoq,
            "recommended_order_qty": recommended_qty,
            "reorder_by_date": reorder_by.strftime("%Y-%m-%d"),
            "risk": risk,
            "risk_detail": risk_detail,
        }

    def check_overstock(
        self, sku_id: str, product_name: str,
        quantity_on_hand: int, avg_daily: float
    ) -> Optional[dict]:
        """Check if a SKU is overstocked."""
        if avg_daily > 0:
            days = quantity_on_hand / avg_daily
            if days > 90:
                return {
                    "sku_id": sku_id,
                    "product_name": product_name,
                    "days_of_stock": round(days, 1),
                    "excess_units": round(quantity_on_hand - avg_daily * 60),
                    "recommendation": f"Consider running a promotion to reduce {product_name} stock. You have ~{round(days)} days of inventory.",
                }
        return None

    def _insufficient_data(self, sku_id, product_name, qty):
        return {
            "sku_id": sku_id,
            "product_name": product_name,
            "quantity_on_hand": qty,
            "avg_daily_demand": 0,
            "days_of_stock": 0,
            "safety_stock": 0,
            "reorder_point": 0,
            "eoq": 0,
            "recommended_order_qty": 0,
            "reorder_by_date": "N/A",
            "risk": "unknown",
            "risk_detail": "Insufficient sales data to calculate reorder metrics.",
        }
