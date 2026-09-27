"""Orchestration for the recommendation strategies."""

import pandas as pd

from backend.content_filtering import (
    get_content_based_recommendations,
    get_content_based_search_recommendations,
)
from backend.rating_based import get_rating_based_recommendations
from backend.collaborative_filtering import (
    get_collaborative_recommendations,
    get_svd_collaborative_recommendations,
)


def reciprocal_rank_fusion(
    ranked_frames: list[tuple[pd.DataFrame, float]],
    k0: int = 60,
    top_n: int = 5,
) -> pd.DataFrame:
    """Combine multiple ranked recommendation lists using Reciprocal Rank Fusion (RRF).

    Formula:
        RRF_Score(item) = sum_{model} ( weight_model / (k0 + rank_model(item)) )
    """
    valid_pairs = [(df, w) for df, w in ranked_frames if isinstance(df, pd.DataFrame) and not df.empty]
    if not valid_pairs:
        return pd.DataFrame()

    rrf_scores: dict[int, float] = {}
    item_metadata: dict[int, dict] = {}
    item_explanations: dict[int, str] = {}

    for df, weight in valid_pairs:
        for rank, (_, row) in enumerate(df.iterrows(), start=1):
            pid = int(row["ProdID"])
            score_increment = float(weight) / (k0 + rank)
            rrf_scores[pid] = rrf_scores.get(pid, 0.0) + score_increment
            if pid not in item_metadata:
                item_metadata[pid] = row.to_dict()
            if pid not in item_explanations and pd.notna(row.get("Explanation")) and row.get("Explanation"):
                item_explanations[pid] = str(row["Explanation"])

    sorted_pids = sorted(rrf_scores.keys(), key=lambda p: rrf_scores[p], reverse=True)[:top_n]
    result_rows = []
    for pid in sorted_pids:
        row = item_metadata[pid].copy()
        row["RRF_Score"] = round(rrf_scores[pid], 6)
        if pid in item_explanations:
            row["Explanation"] = item_explanations[pid]
        result_rows.append(row)

    return pd.DataFrame(result_rows).reset_index(drop=True)


def _combine(*frames: pd.DataFrame, top_n: int) -> pd.DataFrame:
    valid = [frame for frame in frames if isinstance(frame, pd.DataFrame) and not frame.empty]
    if not valid:
        return pd.DataFrame()
    return (
        pd.concat(valid, ignore_index=True)
        .drop_duplicates(subset=["ProdID"])
        .head(max(0, int(top_n)))
        .reset_index(drop=True)
    )


def get_combined_recommendations(
    user_id: int | None = None,
    is_new_user: bool = False,
    current_product_id: int | None = None,
    search_query: str | None = None,
    top_n: int = 5,
    data_path: str | None = None,
    fallback_on_empty: bool = True,
    use_svd: bool = False,
    use_rrf: bool = True,
) -> pd.DataFrame:
    """Combine cold-start, collaborative, content, and search recommendations using RRF."""
    if is_new_user or user_id is None:
        return get_rating_based_recommendations(top_n=top_n, min_reviews=2, data_path=data_path)

    if use_svd:
        collaborative = get_svd_collaborative_recommendations(
            user_id=user_id, top_n=top_n, data_path=data_path
        )
        if collaborative.empty:
            collaborative = get_collaborative_recommendations(
                user_id=user_id, top_n=top_n, data_path=data_path
            )
    else:
        collaborative = get_collaborative_recommendations(
            user_id=user_id, top_n=top_n, data_path=data_path
        )
    content = (
        get_content_based_recommendations(
            product_id=current_product_id, top_n=top_n, data_path=data_path
        )
        if current_product_id is not None
        else pd.DataFrame()
    )
    search = (
        get_content_based_search_recommendations(
            search_query=search_query, top_n=top_n, data_path=data_path
        )
        if search_query
        else pd.DataFrame()
    )

    ranked_sources: list[tuple[pd.DataFrame, float]] = []
    if not search.empty:
        ranked_sources.append((search, 1.2))
    if not content.empty:
        ranked_sources.append((content, 1.0))
    if not collaborative.empty:
        ranked_sources.append((collaborative, 1.1))

    if use_rrf and ranked_sources:
        combined = reciprocal_rank_fusion(ranked_sources, k0=60, top_n=top_n)
    else:
        combined = _combine(search, content, collaborative, top_n=top_n)

    if combined.empty and fallback_on_empty:
        return get_rating_based_recommendations(top_n=top_n, min_reviews=2, data_path=data_path)
    if not combined.empty and "Explanation" in combined.columns:
        combined["Explanation"] = combined["Explanation"].fillna("Recommended for you")
    return combined


if __name__ == "__main__":
    print(get_combined_recommendations(is_new_user=True))
