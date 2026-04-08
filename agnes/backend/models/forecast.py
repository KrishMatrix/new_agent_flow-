from pydantic import BaseModel
from typing import List, Optional


class ForecastPoint(BaseModel):
    date: str
    predicted_sales: float
    lower_bound: float
    upper_bound: float


class ForecastResult(BaseModel):
    sku_id: str
    product_name: str
    horizon_days: int
    forecast: List[ForecastPoint]
    trend: str  # "up", "down", "stable"
    seasonal_note: Optional[str] = None
    total_predicted: float
