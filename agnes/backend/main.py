from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from config import settings
from router import AgnesRouter

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agnes = AgnesRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    agent: str
    agent_color: str
    agent_icon: str
    message: str
    data: Optional[dict] = None
    chart_type: Optional[str] = None
    chart_data: Optional[list] = None
    table_data: Optional[list] = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = agnes.handle(req.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def dashboard():
    """Return summary KPIs for the dashboard panel."""
    from tools.data_loader import DataLoader
    loader = DataLoader()
    products = loader.get_products()
    inventory = loader.get_inventory()
    sales = loader.get_sales_history()

    total_skus = len(products)
    total_stock = int(inventory["quantity_on_hand"].sum())
    avg_daily_sales = float(sales.groupby("date")["quantity_sold"].sum().mean())
    low_stock_count = int((inventory["quantity_on_hand"] < inventory["reorder_point"]).sum())

    recent_sales = sales.groupby("date")["quantity_sold"].sum().tail(14)
    sales_trend = [
        {"date": str(d), "sales": int(v)}
        for d, v in recent_sales.items()
    ]

    top_products = (
        sales.groupby("sku_id")["quantity_sold"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    top_products_list = []
    for sku, qty in top_products.items():
        name_row = products[products["sku_id"] == sku]
        name = name_row["product_name"].values[0] if len(name_row) > 0 else sku
        top_products_list.append({"sku": sku, "name": name, "total_sold": int(qty)})

    return {
        "total_skus": total_skus,
        "total_stock": total_stock,
        "avg_daily_sales": round(avg_daily_sales, 1),
        "low_stock_count": low_stock_count,
        "sales_trend": sales_trend,
        "top_products": top_products_list,
    }


@app.get("/api/inventory")
async def inventory():
    """Return full inventory table."""
    from tools.data_loader import DataLoader
    loader = DataLoader()
    inv = loader.get_inventory()
    products = loader.get_products()
    merged = inv.merge(products[["sku_id", "product_name", "category"]], on="sku_id", how="left")
    merged["status"] = merged.apply(
        lambda r: "critical" if r["quantity_on_hand"] < r["reorder_point"] * 0.5
        else "low" if r["quantity_on_hand"] < r["reorder_point"]
        else "healthy",
        axis=1,
    )
    return merged.to_dict(orient="records")
