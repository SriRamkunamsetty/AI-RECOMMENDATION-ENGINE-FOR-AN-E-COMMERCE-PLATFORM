"""User-user collaborative filtering recommendations."""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from backend.data_utils import canonical_products, load_interactions


def get_collaborative_recommendations(
    user_id: int,
    top_n: int = 5,
    data_path: str | None = None,
) -> pd.DataFrame:
    """Recommend unseen products using ratings from similar users."""
    data = load_interactions(data_path)
    if user_id not in data["User's ID"].values:
        return pd.DataFrame()

    ratings = data[data["Rating"].between(0.1, 5.0)].copy()
    user_item_matrix = ratings.pivot_table(
        index="User's ID", columns="ProdID", values="Rating", fill_value=0
    )
    if user_id not in user_item_matrix.index or len(user_item_matrix.index) < 2:
        return pd.DataFrame()

    similarity = cosine_similarity(user_item_matrix)
    similarity_df = pd.DataFrame(
        similarity, index=user_item_matrix.index, columns=user_item_matrix.index
    )
    sim_scores = similarity_df[user_id].drop(user_id).sort_values(ascending=False)
    similar_users = sim_scores.head(max(1, int(top_n))).index
    unrated = user_item_matrix.loc[user_id]
    unrated_products = unrated[unrated == 0].index
    if len(unrated_products) == 0:
        return pd.DataFrame()

    neighbor_ratings = user_item_matrix.loc[similar_users, unrated_products].replace(0, np.nan)
    predictions = neighbor_ratings.mean().dropna().sort_values(ascending=False).head(max(0, int(top_n)))
    if predictions.empty:
        return pd.DataFrame()

    catalog = canonical_products(data).set_index("ProdID")
    result = catalog.reindex(predictions.index).dropna(how="all").reset_index()
    result["Predicted Rating"] = result["ProdID"].map(predictions)
    result["Price"] = result["ProdID"].map(
        lambda product_id: f"{(int(product_id) % 2500) + 499}.00"
    )
    return result


if __name__ == "__main__":
    print(get_collaborative_recommendations(user_id=1705, top_n=5))
