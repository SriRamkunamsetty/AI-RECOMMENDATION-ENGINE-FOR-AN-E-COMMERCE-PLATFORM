"""Orchestration for the recommendation strategies."""

import pandas as pd

from backend.content_filtering import (
    get_content_based_recommendations,
    get_content_based_search_recommendations,
)
from backend.rating_based import get_rating_based_recommendations
from backend.collaborative_filtering import get_collaborative_recommendations


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
) -> pd.DataFrame:
    """Combine cold-start, collaborative, content, and search recommendations."""
    if is_new_user or user_id is None:
        return get_rating_based_recommendations(top_n=top_n, min_reviews=2, data_path=data_path)

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
    return _combine(search, content, collaborative, top_n=top_n)


if __name__ == "__main__":
    print(get_combined_recommendations(is_new_user=True))
