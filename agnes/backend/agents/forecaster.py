import re
from typing import Optional

from agents.base_agent import BaseAgent
from tools.data_loader import DataLoader
from tools.demand_forecast import DemandForecaster
from config import settings

try:
    import anthropic
    HAS_ANTHROPIC = bool(settings.anthropic_api_key)
except ImportError:
    HAS_ANTHROPIC = False


class ForecasterAgent(BaseAgent):
    name = "Forecaster"
    color = "#3b82f6"
    icon = "📊"
    system_prompt = """You are the Forecaster agent, also known as "The Strategist".
You predict demand for e-commerce products. You receive sales history data and return predictions with explanations.
Always explain WHY you predict what you predict (seasonality, trend, promotions).
Be precise with numbers. Speak like a calm, wise strategist.
Keep responses concise — 2-3 short paragraphs max."""

    def __init__(self):
        self.loader = DataLoader()
        self.forecaster = DemandForecaster()

    def process(self, user_message: str, context: Optional[dict] = None) -> dict:
        # Extract SKU or product from message
        sku_id = self._extract_sku(user_message)
        horizon = self._extract_horizon(user_message)

        if sku_id:
            return self._forecast_sku(sku_id, horizon, user_message)
        else:
            return self._forecast_overview(horizon, user_message)

    def _forecast_sku(self, sku_id: str, horizon: int, user_message: str) -> dict:
        product_name = self.loader.get_product_name(sku_id)
        sales_data = self.loader.get_sku_sales(sku_id)
        result = self.forecaster.forecast(sales_data, horizon, sku_id, product_name)

        # Build chart data
        chart_data = [
            {"date": p["date"], "predicted": p["predicted_sales"],
             "lower": p["lower_bound"], "upper": p["upper_bound"]}
            for p in result.get("forecast", [])
        ]

        # Add historical data points for context
        recent_history = sales_data.tail(14)
        history_points = [
            {"date": row["date"].strftime("%Y-%m-%d"), "actual": int(row["quantity_sold"])}
            for _, row in recent_history.iterrows()
        ]

        # Generate natural language response
        message = self._generate_message(result, user_message)

        return self._build_response(
            message=message,
            data=result,
            chart_type="forecast",
            chart_data=history_points + chart_data,
        )

    def _forecast_overview(self, horizon: int, user_message: str) -> dict:
        """Forecast top 5 SKUs by sales volume."""
        sales = self.loader.get_sales_history()
        top_skus = (
            sales.groupby("sku_id")["quantity_sold"].sum()
            .sort_values(ascending=False).head(5).index
        )

        summaries = []
        for sku in top_skus:
            name = self.loader.get_product_name(sku)
            sku_sales = self.loader.get_sku_sales(sku)
            result = self.forecaster.forecast(sku_sales, horizon, sku, name)
            trend_emoji = {"up": "📈", "down": "📉", "stable": "➡️"}.get(result["trend"], "")
            summaries.append(
                f"• **{name}** ({sku}): ~{result['total_predicted']:.0f} units over {horizon} days {trend_emoji} (trend: {result['trend']})"
            )

        message = f"Here's my forecast for your top sellers over the next **{horizon} days**:\n\n" + "\n".join(summaries)
        if any("up" in s for s in summaries):
            message += "\n\n💡 Some products are trending upward — consider boosting stock before the surge."

        return self._build_response(message=message)

    def _generate_message(self, result: dict, user_message: str) -> str:
        """Generate a natural language forecast message."""
        if HAS_ANTHROPIC:
            try:
                client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                data_summary = (
                    f"SKU: {result['sku_id']} ({result['product_name']})\n"
                    f"Forecast horizon: {result['horizon_days']} days\n"
                    f"Total predicted: {result['total_predicted']} units\n"
                    f"Trend: {result['trend']}\n"
                    f"7-day avg: {result.get('ma7', 'N/A')}, 30-day avg: {result.get('ma30', 'N/A')}\n"
                    f"Seasonal note: {result.get('seasonal_note', 'None')}"
                )
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    system=self.system_prompt,
                    messages=[{
                        "role": "user",
                        "content": f"User asked: '{user_message}'\n\nHere's the forecast data:\n{data_summary}\n\nProvide a concise, insightful response."
                    }]
                )
                return response.content[0].text
            except Exception:
                pass

        # Fallback: template-based response
        trend_word = {"up": "trending upward", "down": "declining", "stable": "holding steady"}.get(result["trend"], "")
        msg = f"📊 **Forecast for {result['product_name']}** ({result['sku_id']})\n\n"
        msg += f"Over the next **{result['horizon_days']} days**, I predict approximately **{result['total_predicted']:.0f} units** in sales. "
        msg += f"Demand is currently {trend_word}.\n\n"
        msg += f"• 7-day average: **{result.get('ma7', 0):.0f}** units/day\n"
        msg += f"• 30-day average: **{result.get('ma30', 0):.0f}** units/day\n"
        if result.get("seasonal_note"):
            msg += f"\n🔔 {result['seasonal_note']}"
        return msg

    def _extract_sku(self, message: str) -> Optional[str]:
        # Try SKU pattern first
        match = re.search(r'SKU\d{3}', message, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        # Try product name lookup
        return self.loader.find_sku(message)

    def _extract_horizon(self, message: str) -> int:
        match = re.search(r'(\d+)\s*days?', message, re.IGNORECASE)
        if match:
            return min(int(match.group(1)), 90)
        if "week" in message.lower():
            return 7
        if "month" in message.lower():
            return 30
        return 14
