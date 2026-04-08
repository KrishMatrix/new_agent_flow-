import re
from typing import Optional

from agents.base_agent import BaseAgent
from tools.data_loader import DataLoader
from tools.reorder_calculator import ReorderCalculator
from config import settings

try:
    import anthropic
    HAS_ANTHROPIC = bool(settings.anthropic_api_key)
except ImportError:
    HAS_ANTHROPIC = False


class OptimizerAgent(BaseAgent):
    name = "Optimizer"
    color = "#10b981"
    icon = "⚙️"
    system_prompt = """You are the Optimizer agent, also known as "The Builder".
You recommend stock actions. Given current inventory, lead times, and forecasted demand, calculate:
- Reorder point, reorder quantity, days of stock remaining, overstock/understock risk.
Be practical and direct. Give specific numbers and deadlines. Keep responses concise and actionable."""

    def __init__(self):
        self.loader = DataLoader()
        self.calculator = ReorderCalculator()

    def process(self, user_message: str, context: Optional[dict] = None) -> dict:
        sku_id = self._extract_sku(user_message)

        if sku_id:
            return self._optimize_sku(sku_id, user_message)
        else:
            return self._optimize_overview(user_message)

    def _optimize_sku(self, sku_id: str, user_message: str) -> dict:
        product_name = self.loader.get_product_name(sku_id)
        products = self.loader.get_products()
        inventory = self.loader.get_inventory()
        sales = self.loader.get_sku_sales(sku_id)

        inv_row = inventory[inventory["sku_id"] == sku_id]
        prod_row = products[products["sku_id"] == sku_id]

        if inv_row.empty:
            return self._build_response(
                message=f"I couldn't find inventory data for {sku_id}. Check if this SKU exists."
            )

        inv = inv_row.iloc[0]
        price = prod_row.iloc[0]["price"] if not prod_row.empty else 10.0
        lead_time = prod_row.iloc[0]["lead_time_days"] if not prod_row.empty else 5

        result = self.calculator.calculate(
            sku_id=sku_id,
            product_name=product_name,
            quantity_on_hand=int(inv["quantity_on_hand"]),
            lead_time_days=int(lead_time),
            daily_sales=sales["quantity_sold"],
            unit_cost=float(price),
        )

        message = self._generate_message(result, user_message)

        table_data = [
            {"metric": "📦 On Hand", "value": str(result["quantity_on_hand"])},
            {"metric": "📊 Avg Daily Demand", "value": f"{result['avg_daily_demand']} units"},
            {"metric": "⏰ Days of Stock", "value": f"{result['days_of_stock']} days"},
            {"metric": "🛡️ Safety Stock", "value": f"{result['safety_stock']} units"},
            {"metric": "🎯 Reorder Point", "value": f"{result['reorder_point']} units"},
            {"metric": "📋 Recommended Order", "value": f"{result['recommended_order_qty']} units"},
            {"metric": "📅 Order By", "value": result["reorder_by_date"]},
            {"metric": "⚡ Risk Level", "value": result["risk"].upper()},
        ]

        return self._build_response(
            message=message,
            data=result,
            chart_type="metrics",
            table_data=table_data,
        )

    def _optimize_overview(self, user_message: str) -> dict:
        """Scan all SKUs and highlight those needing action."""
        products = self.loader.get_products()
        inventory = self.loader.get_inventory()
        sales = self.loader.get_sales_history()

        action_items = []
        all_results = []

        for _, inv_row in inventory.iterrows():
            sku = inv_row["sku_id"]
            prod_row = products[products["sku_id"] == sku]
            if prod_row.empty:
                continue

            name = prod_row.iloc[0]["product_name"]
            price = prod_row.iloc[0]["price"]
            lead_time = prod_row.iloc[0]["lead_time_days"]

            sku_sales = self.loader.get_sku_sales(sku)
            result = self.calculator.calculate(
                sku_id=sku, product_name=name,
                quantity_on_hand=int(inv_row["quantity_on_hand"]),
                lead_time_days=int(lead_time),
                daily_sales=sku_sales["quantity_sold"],
                unit_cost=float(price),
            )
            all_results.append(result)

            if result["risk"] in ("critical", "high"):
                risk_emoji = "🚨" if result["risk"] == "critical" else "⚠️"
                action_items.append(
                    f"{risk_emoji} **{name}** ({sku}): {result['days_of_stock']} days left → Order **{result['recommended_order_qty']} units** by {result['reorder_by_date']}"
                )

        if action_items:
            message = f"⚙️ **Stock Optimization Report**\n\n**{len(action_items)} SKUs need attention:**\n\n" + "\n".join(action_items)
        else:
            message = "✅ All SKUs are at healthy stock levels! No immediate reorders needed."

        table_data = [
            {
                "sku": r["sku_id"],
                "product": r["product_name"],
                "on_hand": r["quantity_on_hand"],
                "days_left": r["days_of_stock"],
                "reorder_point": r["reorder_point"],
                "risk": r["risk"],
            }
            for r in sorted(all_results, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["risk"], 4))
        ]

        return self._build_response(
            message=message,
            data={"results": all_results},
            chart_type="table",
            table_data=table_data,
        )

    def _generate_message(self, result: dict, user_message: str) -> str:
        if HAS_ANTHROPIC:
            try:
                client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                data_summary = (
                    f"SKU: {result['sku_id']} ({result['product_name']})\n"
                    f"On hand: {result['quantity_on_hand']} units\n"
                    f"Avg daily demand: {result['avg_daily_demand']}\n"
                    f"Days of stock: {result['days_of_stock']}\n"
                    f"Lead time: {result['lead_time_days']} days\n"
                    f"Safety stock: {result['safety_stock']}\n"
                    f"Reorder point: {result['reorder_point']}\n"
                    f"Recommended order: {result['recommended_order_qty']} units\n"
                    f"Order by: {result['reorder_by_date']}\n"
                    f"Risk: {result['risk']} — {result['risk_detail']}"
                )
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    system=self.system_prompt,
                    messages=[{
                        "role": "user",
                        "content": f"User asked: '{user_message}'\n\nOptimization data:\n{data_summary}\n\nProvide a direct, actionable response."
                    }]
                )
                return response.content[0].text
            except Exception:
                pass

        # Fallback template
        risk_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🔶", "low": "✅"}.get(result["risk"], "")
        msg = f"⚙️ **Stock Report for {result['product_name']}** ({result['sku_id']})\n\n"
        msg += f"{risk_emoji} **Risk Level: {result['risk'].upper()}**\n"
        msg += f"{result['risk_detail']}\n\n"
        msg += f"📦 Current stock: **{result['quantity_on_hand']}** units\n"
        msg += f"📊 Daily demand: **{result['avg_daily_demand']}** units/day\n"
        msg += f"⏰ Days remaining: **{result['days_of_stock']}** days\n"
        msg += f"🛡️ Safety stock: **{result['safety_stock']}** units\n\n"
        msg += f"**→ Recommendation:** Order **{result['recommended_order_qty']} units** by **{result['reorder_by_date']}**"
        return msg

    def _extract_sku(self, message: str) -> Optional[str]:
        match = re.search(r'SKU\d{3}', message, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return self.loader.find_sku(message)
