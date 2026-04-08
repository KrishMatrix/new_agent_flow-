from pydantic import BaseModel
from typing import Optional


class InventoryLevel(BaseModel):
    sku_id: str
    quantity_on_hand: int
    reorder_point: int
    reorder_quantity: int
    warehouse_location: str
    last_restock_date: str
