"""Shared catalog loading, cleaning, and pricing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from config import DATA_PATH

CORRUPTED_ID = -2147483648
PRODUCT_TEXT_COLUMNS = ("Category", "Brand", "Name", "Description", "Tags")


def resolve_data_path(data_path: str | Path | None = None) -> Path:
    """Resolve a catalog path independently of the process working directory."""
    return Path(data_path) if data_path is not None else Path(DATA_PATH)


_DATA_CACHE: dict[str, pd.DataFrame] = {}


def clear_data_cache() -> None:
    """Clear the in-memory catalog cache."""
    _DATA_CACHE.clear()


def load_interactions(data_path: str | Path | None = None, use_cache: bool = True) -> pd.DataFrame:
    """Load and validate interaction data, removing known corrupt identifiers."""
    path = resolve_data_path(data_path)
    cache_key = str(path.resolve())
    if use_cache and cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    if not path.exists():
        raise FileNotFoundError(f"Catalog dataset not found: {path}")

    data = pd.read_csv(path)
    required = {"User's ID", "ProdID", "Rating"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    data["User's ID"] = pd.to_numeric(data["User's ID"], errors="coerce")
    data["ProdID"] = pd.to_numeric(data["ProdID"], errors="coerce")
    data["Rating"] = pd.to_numeric(data["Rating"], errors="coerce")
    data = data[~data["User's ID"].isin([CORRUPTED_ID])]
    data = data[~data["ProdID"].isin([CORRUPTED_ID])]
    data = data.dropna(subset=["User's ID", "ProdID"]).copy()
    data["User's ID"] = data["User's ID"].astype("int64")
    data["ProdID"] = data["ProdID"].astype("int64")
    for column in PRODUCT_TEXT_COLUMNS:
        if column in data.columns:
            data[column] = data[column].fillna("").astype(str)
    if use_cache:
        _DATA_CACHE[cache_key] = data.copy()
    return data


def canonical_products(data: pd.DataFrame) -> pd.DataFrame:
    """Build deterministic one-row-per-product metadata from interaction rows."""
    data = data.copy()
    if "ProdID" not in data.columns:
        raise ValueError("Dataset is missing required column: ProdID")

    def first_non_empty(values: Iterable[object]) -> str:
        for value in values:
            if pd.notna(value) and str(value).strip():
                return str(value).strip()
        return ""

    aggregations = {column: first_non_empty for column in PRODUCT_TEXT_COLUMNS if column in data.columns}
    if aggregations:
        products = data.groupby("ProdID", as_index=False, sort=True).agg(aggregations)
    else:
        products = data[["ProdID"]].drop_duplicates().sort_values("ProdID").reset_index(drop=True)
    if "Product_Display_Name" not in products.columns:
        products["Product_Display_Name"] = products.apply(
            lambda row: first_non_empty(
                [row.get("Name", ""), f"{row.get('Brand', '')} {row.get('Category', '')}"]
            ),
            axis=1,
        )
    if "ImageURL" in data.columns:
        images = data.groupby("ProdID")["ImageURL"].agg(first_non_empty)
        products = products.merge(images.rename("ImageURL"), on="ProdID", how="left")
    else:
        products["ImageURL"] = ""
    if "Rating" in data.columns:
        ratings = data.groupby("ProdID")["Rating"].mean().rename("Rating")
        products = products.merge(ratings, on="ProdID", how="left")
    else:
        products["Rating"] = pd.NA
    products["ImageURL"] = products["ImageURL"].fillna("").astype(str).str.split(" | ").str[0]
    return products


def price_for_product(product_id: int | str) -> float:
    """Return the single demo price formula used consistently throughout the app."""
    value = int(float(product_id))
    return float((value % 2500) + 499)


def format_price(value: float | int | str) -> str:
    """Format a rupee amount without introducing locale-dependent behavior."""
    return f"{float(value):,.2f}"
