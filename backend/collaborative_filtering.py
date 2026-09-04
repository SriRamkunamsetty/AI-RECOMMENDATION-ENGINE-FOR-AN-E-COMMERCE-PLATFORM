"""User-user collaborative filtering recommendations."""

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

from backend.data_utils import canonical_products, format_price, load_interactions, price_for_product


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
        lambda product_id: format_price(price_for_product(product_id))
    )
    return result




def get_svd_collaborative_recommendations(
    user_id: int,
    top_n: int = 5,
    n_components: int = 15,
    data_path: str | None = None,
) -> pd.DataFrame:
    """Model-based collaborative filtering using Truncated SVD Matrix Factorization."""
    data = load_interactions(data_path)
    if user_id not in data["User's ID"].values:
        return pd.DataFrame()

    ratings = data[data["Rating"].between(0.1, 5.0)].copy()
    user_item_matrix = ratings.pivot_table(
        index="User's ID", columns="ProdID", values="Rating", fill_value=0
    )
    if user_id not in user_item_matrix.index:
        return pd.DataFrame()

    components = min(n_components, user_item_matrix.shape[1] - 1, user_item_matrix.shape[0] - 1)
    if components < 1:
        return get_collaborative_recommendations(user_id=user_id, top_n=top_n, data_path=data_path)

    svd = TruncatedSVD(n_components=components, random_state=42)
    user_factors = svd.fit_transform(user_item_matrix)
    reconstructed = np.dot(user_factors, svd.components_)
    pred_df = pd.DataFrame(reconstructed, index=user_item_matrix.index, columns=user_item_matrix.columns)

    unrated_mask = user_item_matrix.loc[user_id] == 0
    unrated_preds = pred_df.loc[user_id, unrated_mask].sort_values(ascending=False).head(max(0, int(top_n)))
    if unrated_preds.empty:
        return pd.DataFrame()

    catalog = canonical_products(data).set_index("ProdID")
    result = catalog.reindex(unrated_preds.index).dropna(how="all").reset_index()
    result["Predicted Rating"] = result["ProdID"].map(unrated_preds)
    result["Price"] = result["ProdID"].map(
        lambda product_id: format_price(price_for_product(product_id))
    )
    return result


if __name__ == "__main__":
    print(get_collaborative_recommendations(user_id=1705, top_n=5))
