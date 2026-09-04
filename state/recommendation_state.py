"""UI-facing recommendation state."""

from typing import Any, Dict, List

import pandas as pd

from backend.data_utils import price_for_product
from backend.recommender import get_combined_recommendations
from state.user_state import UserState


class RecommendationState(UserState):
    recommendations: List[Dict[str, Any]] = []
    is_loading: bool = False

    async def fetch_general_recommendations(self):
        async for event in self.fetch_recommendations(current_product_id=None):
            yield event

    async def fetch_recommendations(self, current_product_id: int | None = None):
        self.is_loading = True
        yield
        try:
            from state.products_state import ProductsState

            products_state = await self.get_state(ProductsState)
            recs_df = get_combined_recommendations(
                user_id=self.user_id if self.logged_in else None,
                is_new_user=self.is_new_user,
                current_product_id=current_product_id,
                search_query=products_state.search_query,
                top_n=20,
                use_svd=True,
            )
            if isinstance(recs_df, pd.DataFrame) and not recs_df.empty:
                recs_df = recs_df.sample(frac=1).reset_index(drop=True).head(8).fillna("")
                recs_df["ImageURL"] = recs_df.get("ImageURL", "").map(
                    lambda value: str(value).split(" | ")[0] if str(value).strip() else "/placeholder.jpg"
                )
                recs_df["Price"] = recs_df["ProdID"].map(
                    lambda value: f"{price_for_product(value):.2f}"
                )
                if "Rating" in recs_df.columns:
                    recs_df["Rating"] = recs_df["Rating"].map(
                        lambda value: f"{float(value):.1f}" if str(value).strip() else "N/A"
                    )
                self.recommendations = recs_df.to_dict("records")
            else:
                self.recommendations = []
        except Exception as exc:
            print(f"Failed to fetch recommendations: {exc}")
            self.recommendations = []
        finally:
            self.is_loading = False
            yield
