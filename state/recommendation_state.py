import reflex as rx
from typing import List, Dict, Any
import pandas as pd
from state.user_state import UserState
from backend.recommender import get_combined_recommendations

class RecommendationState(UserState):
    """
    State for handling and displaying product recommendations.
    Uses UserState properties to conditionally fetch ML models.
    """
    # UI format dictionary representing recommendations
    recommendations: List[Dict[str, Any]] = []
    is_loading: bool = False
    
    async def fetch_general_recommendations(self):
        """Helper to fetch without passing the click event args to the integer parameter."""
        async for event in self.fetch_recommendations(current_product_id=None):
            yield event
        
    async def fetch_recommendations(self, current_product_id: int = None):
        """
        Check user_type, call respective model, convert result -> UI format.
        Takes an optional `current_product_id` to blend content filtering.
        """
        self.is_loading = True
        # yield allows the UI to update the loading indicator before the heavy ML task blocks
        yield 
        
        try:
            from state.products_state import ProductsState
            products_state = await self.get_state(ProductsState)
            search_hist = products_state.search_query
            
            # Call combined approach from recommender.py
            recs_df = get_combined_recommendations(
                user_id=self.user_id if self.logged_in else None,
                is_new_user=self.is_new_user,
                current_product_id=current_product_id,
                search_query=search_hist,
                top_n=20
            )
            
            # Convert DataFrame result to native python list of dictionaries for Reflex UI rendering
            if isinstance(recs_df, pd.DataFrame):
                # Shuffle so 'Fetch Fresh Recommendations' gives different results
                recs_df = recs_df.sample(frac=1).reset_index(drop=True).head(8)
                
                # Fill NaN with empty strings to prevent UI JSON parsing errors
                recs_df = recs_df.fillna("")
                
                # Fix ImageURL containing multiple piped links
                if "ImageURL" in recs_df.columns:
                    recs_df["ImageURL"] = recs_df["ImageURL"].apply(lambda x: str(x).split(" | ")[0] if pd.notnull(x) and str(x) != "" else "/placeholder.jpg")
                
                if "ProdID" in recs_df.columns:
                    recs_df["Price"] = recs_df["ProdID"].astype(int).apply(lambda x: f"{(x % 2500) + 499}.00")
                
                if "Rating" in recs_df.columns:
                    recs_df["Rating"] = recs_df["Rating"].apply(lambda x: f"{float(x):.1f}" if pd.notnull(x) and str(x) != "" else "N/A")
                    
                self.recommendations = recs_df.to_dict('records')
            else:
                print(f"Engine returned an error or simple string: {recs_df}")
                self.recommendations = []
                
        except Exception as e:
            print(f"Failed to fetch recommendations: {e}")
            self.recommendations = []
            
        finally:
            self.is_loading = False
            yield
