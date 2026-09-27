"""Market Basket Analysis & Association Rule Mining for E-Commerce.

Computes product co-occurrence, Support, Confidence, and Lift from user
interaction sessions to power 'Frequently Bought Together' recommendation bundles.
"""

from collections import defaultdict
from typing import Any, Dict, List, Tuple
import pandas as pd

from backend.data_utils import canonical_products, format_price, load_interactions, price_for_product

_ASSOCIATION_CACHE: Dict[str, pd.DataFrame] = {}


def clear_association_cache():
    """Clear in-memory association rules cache."""
    _ASSOCIATION_CACHE.clear()


def mine_product_associations(data_path: str | None = None) -> pd.DataFrame:
    """Mine pairwise association rules (Support, Confidence, Lift) across user baskets."""
    cache_key = str(data_path or "default")
    if cache_key in _ASSOCIATION_CACHE:
        return _ASSOCIATION_CACHE[cache_key].copy()

    data = load_interactions(data_path)
    user_col = "User's ID"
    item_col = "ProdID"

    user_baskets = data.groupby(user_col)[item_col].unique().tolist()
    total_baskets = float(len(user_baskets))
    if total_baskets == 0:
        return pd.DataFrame()

    item_counts: Dict[int, int] = defaultdict(int)
    pair_counts: Dict[Tuple[int, int], int] = defaultdict(int)

    for basket in user_baskets:
        unique_items = sorted(set(basket))
        for item in unique_items:
            item_counts[item] += 1
        for i in range(len(unique_items)):
            for j in range(i + 1, len(unique_items)):
                item_a = unique_items[i]
                item_b = unique_items[j]
                pair_counts[(item_a, item_b)] += 1
                pair_counts[(item_b, item_a)] += 1

    records: List[Dict[str, Any]] = []
    for (item_a, item_b), count_ab in pair_counts.items():
        count_a = item_counts[item_a]
        count_b = item_counts[item_b]
        support = count_ab / total_baskets
        confidence = count_ab / float(count_a) if count_a > 0 else 0.0
        prob_b = count_b / total_baskets
        lift = (confidence / prob_b) if prob_b > 0 else 1.0

        records.append(
            {
                "Item_A": item_a,
                "Item_B": item_b,
                "Co_Occurrence": count_ab,
                "Support": round(support, 5),
                "Confidence": round(confidence, 4),
                "Lift": round(lift, 3),
            }
        )

    if not records:
        return pd.DataFrame(
            columns=["Item_A", "Item_B", "Co_Occurrence", "Support", "Confidence", "Lift"]
        )

    df_rules = pd.DataFrame(records).sort_values(by=["Lift", "Confidence"], ascending=[False, False])
    _ASSOCIATION_CACHE[cache_key] = df_rules.copy()
    return df_rules


def get_frequently_bought_together(
    product_id: int, top_n: int = 2, data_path: str | None = None
) -> List[Dict[str, Any]]:
    """Return complementary products frequently purchased with the target product."""
    data = load_interactions(data_path)
    catalog = canonical_products(data).set_index("ProdID")
    rules = mine_product_associations(data_path)

    matched_ids: List[int] = []
    explanations: Dict[int, str] = {}

    if not rules.empty and product_id in rules["Item_A"].values:
        sub = rules[rules["Item_A"] == product_id].head(top_n)
        for _, row in sub.iterrows():
            cand_id = int(row["Item_B"])
            matched_ids.append(cand_id)
            explanations[cand_id] = (
                f"Frequently bought together (Lift: {row['Lift']:.1f}x)"
            )

    # Fallback to category / top-rated complements if co-occurrence history is sparse
    if len(matched_ids) < top_n and product_id in catalog.index:
        target_cat = catalog.loc[product_id].get("Category", "")
        if target_cat:
            same_cat = catalog[
                (catalog["Category"] == target_cat) & (catalog.index != product_id)
            ]
            for cand_id in same_cat.index:
                if cand_id not in matched_ids:
                    matched_ids.append(cand_id)
                    explanations[cand_id] = f"Popular complement in {target_cat}"
                if len(matched_ids) >= top_n:
                    break

    results: List[Dict[str, Any]] = []
    for pid in matched_ids[:top_n]:
        if pid in catalog.index:
            row = catalog.loc[pid]
            display_name = str(row.get("Product_Display_Name", row.get("Name", "Product")))
            results.append(
                {
                    "ProdID": int(pid),
                    "Name": display_name,
                    "Product_Display_Name": display_name,
                    "Brand": str(row.get("Brand", "")),
                    "Category": str(row.get("Category", "")),
                    "ImageURL": str(row.get("ImageURL", "")).split(" | ")[0] or "/placeholder.jpg",
                    "Price": format_price(price_for_product(pid)),
                    "Price_Num": price_for_product(pid),
                    "Rating": f"{float(row.get('Rating', 0)):.1f}" if pd.notna(row.get("Rating")) else "N/A",
                    "Explanation": explanations.get(pid, "Complementary product"),
                }
            )

    return results
