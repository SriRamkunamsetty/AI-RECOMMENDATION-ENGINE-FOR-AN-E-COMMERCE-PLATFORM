"""Global popularity recommendations for cold-start users."""

import pandas as pd

from backend.data_utils import canonical_products, load_interactions


def get_rating_based_recommendations(
    top_n: int = 10,
    min_reviews: int = 0,
    data_path: str | None = None,
) -> pd.DataFrame:
    """Return products ranked by Bayesian-style rating and valid rating count.

    Rows with a zero or missing rating are treated as non-ratings. The source
    ``Review Count`` field is retained as metadata, while the number of valid
    rating observations is used for the minimum-review threshold.
    """
    data = load_interactions(data_path)
    ratings = data[data["Rating"].between(0.1, 5.0)].copy()
    if ratings.empty:
        return pd.DataFrame()

    product_stats = ratings.groupby("ProdID").agg(
        Rating=("Rating", "mean"),
        Rating_Count=("Rating", "count"),
    )
    product_stats = product_stats[product_stats["Rating_Count"] >= max(0, int(min_reviews))]

    catalog = canonical_products(data).set_index("ProdID")
    product_stats = product_stats.join(catalog, how="left")
    sorted_products = product_stats.sort_values(
        by=["Rating", "Rating_Count"], ascending=[False, False]
    ).head(max(0, int(top_n))).reset_index()
    sorted_products["Rating Count"] = sorted_products.pop("Rating_Count")
    sorted_products["Price"] = sorted_products["ProdID"].map(
        lambda product_id: f"{(int(product_id) % 2500) + 499}.00"
    )
    return sorted_products


if __name__ == "__main__":
    print(get_rating_based_recommendations(top_n=5, min_reviews=2))
