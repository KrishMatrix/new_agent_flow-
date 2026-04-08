import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class DataLoader:
    """Loads and caches CSV data for all agents."""

    _cache = {}

    def _load(self, filename: str) -> pd.DataFrame:
        if filename not in self._cache:
            path = os.path.join(DATA_DIR, filename)
            self._cache[filename] = pd.read_csv(path)
        return self._cache[filename].copy()

    def get_products(self) -> pd.DataFrame:
        return self._load("products.csv")

    def get_sales_history(self) -> pd.DataFrame:
        df = self._load("sales_history.csv")
        df["date"] = pd.to_datetime(df["date"])
        return df

    def get_inventory(self) -> pd.DataFrame:
        return self._load("inventory_levels.csv")

    def get_channels(self) -> pd.DataFrame:
        df = self._load("channels.csv")
        df["date"] = pd.to_datetime(df["date"])
        return df

    def get_product_name(self, sku_id: str) -> str:
        products = self.get_products()
        match = products[products["sku_id"] == sku_id]
        if len(match) > 0:
            return match["product_name"].values[0]
        return sku_id

    def get_sku_sales(self, sku_id: str) -> pd.DataFrame:
        """Get daily aggregated sales for a specific SKU."""
        sales = self.get_sales_history()
        sku_sales = sales[sales["sku_id"] == sku_id].copy()
        daily = sku_sales.groupby("date").agg(
            quantity_sold=("quantity_sold", "sum"),
            returns=("returns", "sum"),
        ).reset_index().sort_values("date")
        return daily

    def get_all_skus(self) -> list:
        return self.get_products()["sku_id"].tolist()

    def find_sku(self, query: str) -> str | None:
        """Fuzzy match a query to a SKU ID or product name."""
        products = self.get_products()
        query_lower = query.lower()

        # Direct SKU match
        for sku in products["sku_id"].values:
            if sku.lower() in query_lower or query_lower in sku.lower():
                return sku

        # Product name match
        for _, row in products.iterrows():
            if query_lower in row["product_name"].lower():
                return row["sku_id"]

        # Category match — return first in category
        for _, row in products.iterrows():
            if query_lower in row["category"].lower():
                return row["sku_id"]

        return None
