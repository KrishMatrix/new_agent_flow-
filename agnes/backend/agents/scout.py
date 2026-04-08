import re
from typing import Optional

from agents.base_agent import BaseAgent
from tools.data_loader import DataLoader
from tools.anomaly_detector import AnomalyDetector
from config import settings

try:
    import anthropic
    HAS_ANTHROPIC = bool(settings.anthropic_api_key)
except ImportError:
    HAS_ANTHROPIC = False


class ScoutAgent(BaseAgent):
    name = "Scout"
    color = "#ef4444"
    icon = "🔍"
    system_prompt = """You are the Scout agent, also known as "The Lookout".
You detect anomalies in supply chain data. Flag anything unusual: sales spikes, return rate jumps,
channel mismatches, slow-moving stock. Be alert and slightly dramatic — you're the early warning system.
Always suggest a next step when you flag something. Keep responses concise and impactful."""

    def __init__(self):
        self.loader = DataLoader()
        self.detector = AnomalyDetector()

    def process(self, user_message: str, context: Optional[dict] = None) -> dict:
        sku_id = self._extract_sku(user_message)

        sales = self.loader.get_sales_history()
        products = self.loader.get_products()
        inventory = self.loader.get_inventory()
        channels = self.loader.get_channels()

        if sku_id:
            alerts = self.detector.detect_for_sku(sku_id, sales, products, inventory, channels)
        else:
            alerts = self.detector.detect_all(sales, products, inventory, channels)

        if not alerts:
            if sku_id:
                name = self.loader.get_product_name(sku_id)
                message = f"🟢 All clear for **{name}** ({sku_id})! No anomalies detected. Sales, returns, and channel performance all look normal. I'll keep watching."
            else:
                message = "🟢 All systems nominal! I've scanned all SKUs across sales, returns, and channels — no anomalies detected right now. I'll keep my eyes peeled."
            return self._build_response(message=message)

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda a: severity_order.get(a["severity"], 4))

        # Generate response
        message = self._generate_message(alerts, sku_id, user_message)

        # Build table data for display
        table_data = [
            {
                "sku": a["sku_id"],
                "product": a["product_name"],
                "type": a["alert_type"].replace("_", " ").title(),
                "severity": a["severity"],
                "deviation": f"{a['deviation_pct']:+.1f}%",
            }
            for a in alerts[:10]
        ]

        return self._build_response(
            message=message,
            data={"alerts": alerts},
            chart_type="table",
            table_data=table_data,
        )

    def _generate_message(self, alerts: list, sku_id: Optional[str], user_message: str) -> str:
        if HAS_ANTHROPIC:
            try:
                client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                alerts_summary = "\n".join(
                    f"- [{a['severity'].upper()}] {a['description']}" for a in alerts[:8]
                )
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=400,
                    system=self.system_prompt,
                    messages=[{
                        "role": "user",
                        "content": f"User asked: '{user_message}'\n\nAnomalies detected:\n{alerts_summary}\n\nProvide a dramatic but concise alert summary with recommendations."
                    }]
                )
                return response.content[0].text
            except Exception:
                pass

        # Fallback template
        severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🔶", "low": "🔵"}
        lines = []
        count_by_severity = {}
        for a in alerts:
            count_by_severity[a["severity"]] = count_by_severity.get(a["severity"], 0) + 1

        header = f"**🔍 Scout Report: {len(alerts)} anomal{'y' if len(alerts) == 1 else 'ies'} detected!**\n"
        lines.append(header)

        for a in alerts[:5]:
            emoji = severity_emoji.get(a["severity"], "")
            lines.append(f"{emoji} **[{a['severity'].upper()}]** {a['description']}")
            if a.get("recommendation"):
                lines.append(f"   → _{a['recommendation']}_\n")

        if len(alerts) > 5:
            lines.append(f"\n...and {len(alerts) - 5} more alerts. ")

        return "\n".join(lines)

    def _extract_sku(self, message: str) -> Optional[str]:
        match = re.search(r'SKU\d{3}', message, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return self.loader.find_sku(message)
