"""Offline Evaluation and Benchmarking Suite for Recommendation Algorithms.

Provides IEEE-standard ranking, accuracy, and coverage metrics for comparing
Popularity baseline, Collaborative Filtering, Truncated SVD, Content-Based,
and Hybrid recommendation models.
"""

from typing import Any, Callable, Dict, List, Set, Tuple
import math
import numpy as np
import pandas as pd

from backend.data_utils import canonical_products, load_interactions
from backend.rating_based import get_rating_based_recommendations
from backend.collaborative_filtering import (
    get_collaborative_recommendations,
    get_svd_collaborative_recommendations,
)
from backend.content_filtering import get_content_based_recommendations
from backend.recommender import get_combined_recommendations


def train_test_split_interactions(
    data: pd.DataFrame,
    test_ratio: float = 0.2,
    min_interactions: int = 2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split user interactions into train and test sets using stratified sampling per user."""
    data = data.copy()
    user_col = "User's ID"
    user_counts = data[user_col].value_counts()
    eligible_users = set(user_counts[user_counts >= min_interactions].index)

    rng = np.random.RandomState(random_state)
    test_indices: List[int] = []

    for user_id in eligible_users:
        user_rows = data[data[user_col] == user_id].index.tolist()
        num_test = max(1, int(round(len(user_rows) * test_ratio)))
        # Do not leave train set completely empty
        num_test = min(num_test, len(user_rows) - 1)
        selected = rng.choice(user_rows, size=num_test, replace=False).tolist()
        test_indices.extend(selected)

    test_idx_set = set(test_indices)
    test_df = data.loc[list(test_idx_set)].copy().reset_index(drop=True)
    train_df = data.loc[~data.index.isin(test_idx_set)].copy().reset_index(drop=True)
    return train_df, test_df


def compute_ndcg_at_k(actual: List[Any], predicted: List[Any], k: int = 5) -> float:
    """Compute Normalized Discounted Cumulative Gain at rank cutoff K (binary relevance)."""
    if not actual or not predicted or k <= 0:
        return 0.0

    actual_set = set(actual)
    pred_k = predicted[:k]
    dcg = 0.0
    for idx, item in enumerate(pred_k):
        if item in actual_set:
            dcg += 1.0 / math.log2(idx + 2)

    idcg = sum(1.0 / math.log2(idx + 2) for idx in range(min(k, len(actual_set))))
    return (dcg / idcg) if idcg > 0 else 0.0


def compute_precision_recall_at_k(
    actual: List[Any], predicted: List[Any], k: int = 5
) -> Tuple[float, float]:
    """Compute Precision@K and Recall@K."""
    if not actual or not predicted or k <= 0:
        return 0.0, 0.0

    pred_k = predicted[:k]
    hits = len(set(pred_k).intersection(set(actual)))
    precision = hits / float(k)
    recall = hits / float(len(actual))
    return precision, recall


def compute_hit_rate_at_k(actual: List[Any], predicted: List[Any], k: int = 5) -> float:
    """Compute Hit Rate@K (1.0 if at least one actual item was recommended, else 0.0)."""
    if not actual or not predicted or k <= 0:
        return 0.0
    return 1.0 if any(item in set(actual) for item in predicted[:k]) else 0.0


def compute_mrr(actual: List[Any], predicted: List[Any]) -> float:
    """Compute Mean Reciprocal Rank (MRR) based on the first relevant item."""
    if not actual or not predicted:
        return 0.0
    actual_set = set(actual)
    for idx, item in enumerate(predicted):
        if item in actual_set:
            return 1.0 / float(idx + 1)
    return 0.0


def compute_map_at_k(actual: List[Any], predicted: List[Any], k: int = 5) -> float:
    """Compute Mean Average Precision at rank cutoff K."""
    if not actual or not predicted or k <= 0:
        return 0.0
    actual_set = set(actual)
    pred_k = predicted[:k]
    score = 0.0
    num_hits = 0
    for idx, item in enumerate(pred_k):
        if item in actual_set:
            num_hits += 1
            score += num_hits / float(idx + 1)
    return (score / min(len(actual_set), k)) if actual_set else 0.0


def compute_rmse_mae(
    actual: List[float], predicted: List[float]
) -> Tuple[float, float]:
    """Compute Root Mean Squared Error (RMSE) and Mean Absolute Error (MAE)."""
    if not actual or not predicted or len(actual) != len(predicted):
        return 0.0, 0.0
    act = np.array(actual, dtype=float)
    pred = np.array(predicted, dtype=float)
    rmse = float(np.sqrt(np.mean((act - pred) ** 2)))
    mae = float(np.mean(np.abs(act - pred)))
    return rmse, mae


def compute_catalog_coverage(
    all_recommendations: List[List[Any]], total_catalog_count: int
) -> float:
    """Compute percentage of unique catalog items ever recommended across test users."""
    if not all_recommendations or total_catalog_count <= 0:
        return 0.0
    unique_recommended: Set[Any] = set()
    for rec_list in all_recommendations:
        unique_recommended.update(rec_list)
    return len(unique_recommended) / float(total_catalog_count)


def evaluate_model(
    recommend_func: Callable[[int, int, pd.DataFrame], List[int]],
    test_data: pd.DataFrame,
    train_data: pd.DataFrame,
    k: int = 5,
    max_test_users: int = 100,
    random_state: int = 42,
) -> Dict[str, float]:
    """Evaluate a single recommendation function against held-out test data."""
    user_col = "User's ID"
    item_col = "ProdID"
    grouped_test = test_data.groupby(user_col)[item_col].apply(list).to_dict()

    user_ids = list(grouped_test.keys())
    if len(user_ids) > max_test_users:
        rng = np.random.RandomState(random_state)
        user_ids = rng.choice(user_ids, size=max_test_users, replace=False).tolist()

    precisions: List[float] = []
    recalls: List[float] = []
    hit_rates: List[float] = []
    ndcgs: List[float] = []
    mrrs: List[float] = []
    maps: List[float] = []
    all_recs: List[List[int]] = []

    for uid in user_ids:
        actual_items = grouped_test[uid]
        try:
            preds = recommend_func(uid, k, train_data)
        except Exception:
            preds = []

        all_recs.append(preds)
        p, r = compute_precision_recall_at_k(actual_items, preds, k=k)
        precisions.append(p)
        recalls.append(r)
        hit_rates.append(compute_hit_rate_at_k(actual_items, preds, k=k))
        ndcgs.append(compute_ndcg_at_k(actual_items, preds, k=k))
        mrrs.append(compute_mrr(actual_items, preds))
        maps.append(compute_map_at_k(actual_items, preds, k=k))

    total_catalog = len(canonical_products(train_data))
    coverage = compute_catalog_coverage(all_recs, total_catalog)

    return {
        f"Precision@{k}": float(np.mean(precisions)) if precisions else 0.0,
        f"Recall@{k}": float(np.mean(recalls)) if recalls else 0.0,
        f"Hit_Rate@{k}": float(np.mean(hit_rates)) if hit_rates else 0.0,
        f"NDCG@{k}": float(np.mean(ndcgs)) if ndcgs else 0.0,
        f"MAP@{k}": float(np.mean(maps)) if maps else 0.0,
        "MRR": float(np.mean(mrrs)) if mrrs else 0.0,
        "Catalog_Coverage": coverage,
    }


def benchmark_all_models(
    k: int = 5,
    max_test_users: int = 100,
    data_path: str | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Run full benchmark comparing Popularity, Collab, SVD, Content, and Hybrid engines."""
    data = load_interactions(data_path)
    train_data, test_data = train_test_split_interactions(
        data, test_ratio=0.2, min_interactions=2, random_state=random_state
    )

    # Temporary file for train data so recommendation functions load train interactions
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        train_path = tmp.name
    try:
        train_data.to_csv(train_path, index=False)

        # 1. Popularity Baseline
        def recommend_popularity(uid: int, top_n: int, df: pd.DataFrame) -> List[int]:
            recs = get_rating_based_recommendations(top_n=top_n, data_path=train_path)
            return recs["ProdID"].tolist() if not recs.empty else []

        # 2. Collaborative Filtering (User-User Cosine)
        def recommend_collab(uid: int, top_n: int, df: pd.DataFrame) -> List[int]:
            recs = get_collaborative_recommendations(user_id=uid, top_n=top_n, data_path=train_path)
            return recs["ProdID"].tolist() if not recs.empty else []

        # 3. Truncated SVD Matrix Factorization
        def recommend_svd(uid: int, top_n: int, df: pd.DataFrame) -> List[int]:
            recs = get_svd_collaborative_recommendations(user_id=uid, top_n=top_n, data_path=train_path)
            return recs["ProdID"].tolist() if not recs.empty else []

        # 4. Content-Based Filtering (based on user's last interaction in train)
        def recommend_content(uid: int, top_n: int, df: pd.DataFrame) -> List[int]:
            user_items = df[df["User's ID"] == uid]["ProdID"].tolist()
            if not user_items:
                return []
            last_item = user_items[-1]
            recs = get_content_based_recommendations(product_id=last_item, top_n=top_n, data_path=train_path)
            return recs["ProdID"].tolist() if not recs.empty else []

        # 5. Hybrid Recommender
        def recommend_hybrid(uid: int, top_n: int, df: pd.DataFrame) -> List[int]:
            user_items = df[df["User's ID"] == uid]["ProdID"].tolist()
            last_item = user_items[-1] if user_items else None
            recs = get_combined_recommendations(
                user_id=uid,
                current_product_id=last_item,
                top_n=top_n,
                data_path=train_path,
                use_svd=True,
            )
            return recs["ProdID"].tolist() if not recs.empty else []

        models: Dict[str, Callable[[int, int, pd.DataFrame], List[int]]] = {
            "Rating-Based (Popularity)": recommend_popularity,
            "User-User Cosine Collab": recommend_collab,
            "Truncated SVD Latent Factor": recommend_svd,
            "Content-Based (TF-IDF)": recommend_content,
            "Hybrid Multi-Strategy": recommend_hybrid,
        }

        results: Dict[str, Dict[str, float]] = {}
        for name, func in models.items():
            results[name] = evaluate_model(
                recommend_func=func,
                test_data=test_data,
                train_data=train_data,
                k=k,
                max_test_users=max_test_users,
                random_state=random_state,
            )

        summary_df = pd.DataFrame.from_dict(results, orient="index")
        return summary_df
    finally:
        Path(train_path).unlink(missing_ok=True)


if __name__ == "__main__":
    print("Running recommendation algorithms offline benchmark...")
    df_results = benchmark_all_models(k=5, max_test_users=50)
    print("\n" + "=" * 78)
    print("RECOMMENDER ALGORITHMS BENCHMARK COMPARISON (IEEE EVALUATION SUITE)")
    print("=" * 78)
    print(df_results.round(4).to_string())
    print("=" * 78)
