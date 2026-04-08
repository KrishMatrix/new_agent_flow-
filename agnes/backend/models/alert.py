from pydantic import BaseModel
from typing import Optional


class AnomalyAlert(BaseModel):
    sku_id: str
    product_name: str
    alert_type: str  # "sales_spike", "sales_drop", "return_spike", "channel_mismatch", "slow_moving"
    severity: str    # "low", "medium", "high", "critical"
    description: str
    metric_value: float
    expected_value: float
    deviation_pct: float
    recommendation: Optional[str] = None
