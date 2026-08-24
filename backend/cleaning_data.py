"""Clean the raw interaction dataset into the runtime catalog dataset."""

from pathlib import Path

import numpy as np
import pandas as pd

from config import PROJECT_ROOT
from backend.data_utils import CORRUPTED_ID


INPUT_PATH = Path(PROJECT_ROOT) / "clean_data.csv"
OUTPUT_PATH = Path(PROJECT_ROOT) / "cleaned_data.csv"


def clean_dataset(input_path: str | Path = INPUT_PATH, output_path: str | Path = OUTPUT_PATH) -> pd.DataFrame:
    data = pd.read_csv(input_path)
    for column in ("ProdID", "User's ID"):
        if column in data.columns:
            numeric = pd.to_numeric(data[column], errors="coerce")
            data[column] = numeric.replace(CORRUPTED_ID, np.nan)

    data = data.dropna(subset=["User's ID", "ProdID"]).copy()
    data["User's ID"] = data["User's ID"].astype("int64")
    data["ProdID"] = data["ProdID"].astype("int64")

    if "Review Count" in data.columns:
        data["Review Count"] = pd.to_numeric(data["Review Count"], errors="coerce").fillna(0).astype("int64")
    for column in ("Category", "Brand", "Description", "Tags"):
        if column in data.columns:
            data[column] = data[column].fillna("")
    if "ImageURL" in data.columns:
        data["ImageURL"] = data["ImageURL"].fillna("").astype(str).str.split("|").str[0].str.strip()
    if "Image URL" in data.columns:
        data["Image URL"] = data["Image URL"].fillna("").astype(str).str.split("|").str[0].str.strip()

    output_path = Path(output_path)
    data.to_csv(output_path, index=False)
    return data


if __name__ == "__main__":
    cleaned = clean_dataset()
    print(f"Wrote {len(cleaned)} rows to {OUTPUT_PATH}")
