from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    sku_id: str
    product_name: str
    category: str
    price: float
    supplier: str
    lead_time_days: int
