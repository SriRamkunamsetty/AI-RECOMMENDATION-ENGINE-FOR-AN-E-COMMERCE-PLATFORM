"""TF-IDF content-based recommendations."""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.data_utils import canonical_products, format_price, load_interactions, price_for_product


def _text_frame(data: pd.DataFrame) -> pd.DataFrame:
    products = canonical_products(data).copy()
    products["SearchText"] = (
        products.get("Tags", "").fillna("").astype(str)
        + " "
        + products.get("Description", "").fillna("").astype(str)
        + " "
        + products.get("Name", "").fillna("").astype(str)
    ).str.strip()
    return products


_TFIDF_CACHE: dict[int, tuple[TfidfVectorizer, object, pd.DataFrame]] = {}


def clear_tfidf_cache() -> None:
    """Clear the cached TF-IDF vectors."""
    _TFIDF_CACHE.clear()


def _get_catalog_tfidf(data_path: str | None = None) -> tuple[TfidfVectorizer, object, pd.DataFrame]:
    data = load_interactions(data_path)
    products = _text_frame(data)
    cache_key = len(products)
    if cache_key in _TFIDF_CACHE:
        cached_vec, cached_mat, cached_df = _TFIDF_CACHE[cache_key]
        if list(cached_df["ProdID"]) == list(products["ProdID"]):
            return cached_vec, cached_mat, cached_df

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(products["SearchText"])
    _TFIDF_CACHE[cache_key] = (vectorizer, matrix, products)
    return vectorizer, matrix, products


def get_content_based_recommendations(
    product_id: int,
    top_n: int = 10,
    data_path: str | None = None,
) -> pd.DataFrame:
    """Return products with text features most similar to ``product_id``."""
    vectorizer, matrix, products = _get_catalog_tfidf(data_path)
    if product_id not in products["ProdID"].values:
        return pd.DataFrame()
    if not products["SearchText"].str.strip().any():
        return pd.DataFrame()

    index = products.index[products["ProdID"] == product_id][0]
    scores = cosine_similarity(matrix[index], matrix).ravel()
    candidates = pd.Series(scores, index=products.index).drop(index).sort_values(ascending=False)
    result = products.loc[candidates.head(max(0, int(top_n))).index].drop(columns=["SearchText"]).copy()
    result["Price"] = result["ProdID"].map(
        lambda value: format_price(price_for_product(value))
    )
    return result.reset_index(drop=True)


def get_content_based_search_recommendations(
    search_query: str,
    top_n: int = 10,
    data_path: str | None = None,
) -> pd.DataFrame:
    """Return products whose catalog text matches a literal search query."""
    query = str(search_query or "").strip()
    if not query:
        return pd.DataFrame()
    vectorizer, matrix, products = _get_catalog_tfidf(data_path)
    if not products["SearchText"].str.strip().any():
        return pd.DataFrame()

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix).ravel()
    indices = pd.Series(scores, index=products.index)
    indices = indices[indices > 0].sort_values(ascending=False).head(max(0, int(top_n)))
    result = products.loc[indices.index].drop(columns=["SearchText"]).copy()
    result["Price"] = result["ProdID"].map(
        lambda value: format_price(price_for_product(value))
    )
    return result.reset_index(drop=True)


if __name__ == "__main__":
    print(get_content_based_recommendations(product_id=2, top_n=5))
