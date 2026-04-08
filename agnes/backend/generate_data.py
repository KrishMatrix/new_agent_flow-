"""Generate 90 days of realistic sales history for all SKUs."""
import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)

SKUS = [f"SKU{str(i).zfill(3)}" for i in range(1, 21)]

# Base daily sales per SKU (some sell more than others)
BASE_SALES = {
    "SKU001": 22, "SKU002": 35, "SKU003": 18, "SKU004": 10,
    "SKU005": 8,  "SKU006": 28, "SKU007": 15, "SKU008": 7,
    "SKU009": 20, "SKU010": 6,  "SKU011": 12, "SKU012": 9,
    "SKU013": 25, "SKU014": 5,  "SKU015": 4,  "SKU016": 11,
    "SKU017": 9,  "SKU018": 30, "SKU019": 16, "SKU020": 8,
}

start_date = datetime(2026, 1, 7)
rows = []

for day_offset in range(90):
    date = start_date + timedelta(days=day_offset)
    date_str = date.strftime("%Y-%m-%d")
    day_of_week = date.weekday()
    # Weekend boost
    weekend_mult = 1.3 if day_of_week >= 5 else 1.0
    # Monthly trend: slight upward
    trend_mult = 1.0 + (day_offset / 90) * 0.15

    for sku in SKUS:
        base = BASE_SALES[sku]
        # Add seasonality for March (spring spike for apparel/footwear)
        month = date.month
        seasonal = 1.4 if month == 3 and sku in ["SKU001", "SKU002", "SKU003", "SKU006"] else 1.0

        daily_sales = int(
            base * weekend_mult * trend_mult * seasonal
            * random.uniform(0.6, 1.5)
        )
        daily_sales = max(0, daily_sales)

        # Returns: ~3% normally, anomaly for SKU002 in late March
        if sku == "SKU002" and date >= datetime(2026, 3, 20):
            returns = int(daily_sales * random.uniform(0.12, 0.20))
        else:
            returns = int(daily_sales * random.uniform(0.0, 0.06))

        rows.append({
            "date": date_str,
            "sku_id": sku,
            "quantity_sold": daily_sales,
            "returns": returns,
        })

output_path = os.path.join(os.path.dirname(__file__), "data", "sales_history.csv")
with open(output_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "sku_id", "quantity_sold", "returns"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} rows → {output_path}")
