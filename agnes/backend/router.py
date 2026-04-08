import re
from typing import Optional

from agents.forecaster import ForecasterAgent
from agents.scout import ScoutAgent
from agents.optimizer import OptimizerAgent
from config import settings

try:
    import anthropic
    HAS_ANTHROPIC = bool(settings.anthropic_api_key)
except ImportError:
    HAS_ANTHROPIC = False


# Keywords for intent classification fallback
FORECAST_KEYWORDS = [
    "forecast", "predict", "projection", "demand", "sales next",
    "expect", "trend", "how many will sell", "next week", "next month",
    "sales prediction", "upcoming", "future sales",
]
ANOMALY_KEYWORDS = [
    "anomal", "unusual", "spike", "drop", "alert", "flag",
    "return rate", "returns", "weird", "strange", "problem",
    "issue", "wrong", "mismatch", "slow moving", "monitor",
    "warning", "scan", "check for issues",
]
OPTIMIZE_KEYWORDS = [
    "reorder", "replenish", "stock level", "safety stock", "inventory",
    "how much to order", "when to order", "days of stock", "overstock",
    "understock", "optimize", "eoq", "lead time", "run out",
    "stockout", "how long will stock last",
]


class AgnesRouter:
    """
    Central orchestrator that classifies user intent
    and routes to the appropriate agent.
    """

    def __init__(self):
        self.forecaster = ForecasterAgent()
        self.scout = ScoutAgent()
        self.optimizer = OptimizerAgent()

    def handle(self, message: str) -> dict:
        """Classify the message and route to the correct agent."""
        route = self._classify(message)

        if route == "FORECAST":
            return self.forecaster.process(message)
        elif route == "ANOMALY":
            return self.scout.process(message)
        elif route == "OPTIMIZE":
            return self.optimizer.process(message)
        else:
            return self._handle_general(message)

    def _classify(self, message: str) -> str:
        """Classify user intent — uses Claude if available, falls back to keywords."""
        if HAS_ANTHROPIC:
            try:
                return self._classify_with_llm(message)
            except Exception:
                pass

        return self._classify_with_keywords(message)

    def _classify_with_llm(self, message: str) -> str:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            system="""You are Agnes, an AI supply chain manager. Classify the user's question into exactly one category.
Respond with ONLY one word:
- FORECAST: demand predictions, sales projections, trends, how many will sell
- ANOMALY: unusual patterns, spikes, drops, alerts, returns issues, scan for problems
- OPTIMIZE: reorder, replenishment, stock levels, safety stock, when to order
- GENERAL: greetings, explanations, help, or anything that doesn't fit above""",
            messages=[{"role": "user", "content": message}],
        )
        result = response.content[0].text.strip().upper()
        if result in ("FORECAST", "ANOMALY", "OPTIMIZE", "GENERAL"):
            return result
        return "GENERAL"

    def _classify_with_keywords(self, message: str) -> str:
        msg_lower = message.lower()

        scores = {"FORECAST": 0, "ANOMALY": 0, "OPTIMIZE": 0}

        for kw in FORECAST_KEYWORDS:
            if kw in msg_lower:
                scores["FORECAST"] += 1
        for kw in ANOMALY_KEYWORDS:
            if kw in msg_lower:
                scores["ANOMALY"] += 1
        for kw in OPTIMIZE_KEYWORDS:
            if kw in msg_lower:
                scores["OPTIMIZE"] += 1

        max_score = max(scores.values())
        if max_score == 0:
            return "GENERAL"

        return max(scores, key=scores.get)

    def _handle_general(self, message: str) -> dict:
        """Handle general/greeting messages."""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["hi", "hello", "hey", "help", "what can you do"]):
            response = (
                "👋 **Hey there! I'm Agnes, your AI supply chain manager.**\n\n"
                "I coordinate three specialist agents to help you manage your inventory:\n\n"
                "📊 **Forecaster** — Ask me about demand predictions, sales trends, and future projections\n"
                "🔍 **Scout** — I'll detect anomalies: sales spikes, return rate issues, and channel mismatches\n"
                "⚙️ **Optimizer** — I'll calculate reorder points, safety stock, and tell you when to replenish\n\n"
                "**Try asking something like:**\n"
                "• _\"What's the forecast for blue sneakers next week?\"_\n"
                "• _\"Any anomalies in our sales data?\"_\n"
                "• _\"When should I reorder red t-shirts?\"_\n"
                "• _\"Give me a full stock optimization report\"_"
            )
        elif "status" in msg_lower or "overview" in msg_lower or "summary" in msg_lower:
            # Quick overview combining all agents
            response = (
                "📋 **Quick Status Check**\n\n"
                "Let me get you a full picture. Try asking:\n"
                "• _\"Forecast my top products\"_ for demand outlook\n"
                "• _\"Scan for anomalies\"_ for any issues\n"
                "• _\"Optimize stock levels\"_ for reorder recommendations\n\n"
                "Or ask about a specific product by name or SKU!"
            )
        else:
            if HAS_ANTHROPIC:
                try:
                    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                    resp = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=200,
                        system="You are Agnes, a friendly AI supply chain manager. Answer the user's question briefly. If it's about supply chain, mention that you can forecast demand, detect anomalies, and optimize stock.",
                        messages=[{"role": "user", "content": message}],
                    )
                    response = resp.content[0].text
                except Exception:
                    response = "I'm not sure I understood that. I can help with **demand forecasting**, **anomaly detection**, and **stock optimization**. Try asking about a specific product!"
            else:
                response = "I'm not sure I understood that. I can help with **demand forecasting**, **anomaly detection**, and **stock optimization**. Try asking about a specific product!"

        return {
            "agent": "Agnes",
            "agent_color": "#8b5cf6",
            "agent_icon": "🏭",
            "message": response,
            "data": None,
            "chart_type": None,
            "chart_data": None,
            "table_data": None,
        }
