from abc import ABC, abstractmethod
from typing import Optional


class BaseAgent(ABC):
    """Base interface for all Agnes agents."""

    name: str = "Agent"
    color: str = "#6366f1"
    icon: str = "🤖"
    system_prompt: str = ""

    @abstractmethod
    def process(self, user_message: str, context: Optional[dict] = None) -> dict:
        """
        Process a user query and return a structured response.

        Returns:
            dict with keys:
              - agent: str (agent name)
              - agent_color: str (hex color)
              - agent_icon: str (emoji)
              - message: str (response text)
              - data: optional dict (raw data)
              - chart_type: optional str ("line", "bar", "table")
              - chart_data: optional list (chart data points)
              - table_data: optional list (table rows)
        """
        pass

    def _build_response(
        self,
        message: str,
        data: Optional[dict] = None,
        chart_type: Optional[str] = None,
        chart_data: Optional[list] = None,
        table_data: Optional[list] = None,
    ) -> dict:
        return {
            "agent": self.name,
            "agent_color": self.color,
            "agent_icon": self.icon,
            "message": message,
            "data": data,
            "chart_type": chart_type,
            "chart_data": chart_data,
            "table_data": table_data,
        }
