import reflex as rx
import pandas as pd
import os
from typing import List, Dict, Any
from config import DATA_PATH

from state.user_state import UserState

class ProductsState(UserState):
    """Local state for fetching global catalog of products."""
    all_products: List[Dict[str, Any]] = []
    search_query: str = ""
    sort_order: str = "default" # default, low_to_high, high_to_low
    
    def fetch_products(self):
        # Extract query from URL if visiting via search redirect
        params = self.router.page.params
        if "q" in params:
            self.search_query = params["q"]
        else:
            self.search_query = ""
            
        try:
            if os.path.exists(DATA_PATH):
                data = pd.read_csv(DATA_PATH)
                unique_products = data.drop_duplicates(subset=['ProdID']).copy()
                
                # Pre-calculate prices for sorting (since they are synthetic)
                unique_products["Price_Num"] = unique_products["ProdID"].astype(int).apply(lambda x: (x % 2500) + 499)
                
                # Filter
                if self.search_query:
                    mask = (
                        unique_products['Brand'].str.contains(self.search_query, case=False, na=False) |
                        unique_products['Category'].str.contains(self.search_query, case=False, na=False) |
                        unique_products['Description'].str.contains(self.search_query, case=False, na=False)
                    )
                    unique_products = unique_products[mask]
                
                # Sort
                if self.sort_order == "low_to_high":
                    unique_products = unique_products.sort_values("Price_Num", ascending=True)
                elif self.sort_order == "high_to_low":
                    unique_products = unique_products.sort_values("Price_Num", ascending=False)
                
                # Cap and Fill
                unique_products = unique_products.head(48).fillna('')
                unique_products["Price"] = unique_products["Price_Num"].apply(lambda x: f"{x}.00")
                
                if "ImageURL" in unique_products.columns:
                    unique_products["ImageURL"] = unique_products["ImageURL"].apply(lambda x: str(x).split(" | ")[0] if pd.notnull(x) and str(x) != "" else "/placeholder.jpg")
                if "Rating" in unique_products.columns:
                    unique_products["Rating"] = unique_products["Rating"].apply(lambda x: f"{float(x):.1f}" if pd.notnull(x) and str(x) != "" else "N/A")
                
                self.all_products = unique_products.to_dict('records')
        except Exception as e:
            print(f"Error fetching products: {e}")

    def update_sort(self, val: str):
        self.sort_order = val
        return self.fetch_products()

    def update_search(self, q: str):
        self.search_query = q
        self.sync_search_to_firebase(q)
        return self.fetch_products()
    
    def handle_search_submit(self, form_data: Dict[str, Any]):
        query = form_data.get("q", "")
        self.search_query = query
        self.sync_search_to_firebase(query)
        # Force a redirect to the home page with the query
        return rx.redirect(f"/?q={query}")

    def sync_search_to_firebase(self, q: str):
        """Save search history to Firebase."""
        if self.logged_in and self.firebase_uid and q.strip():
            try:
                db = self._get_firebase().database()
                db.child("users").child(self.firebase_uid).child("search_history").push(q)
            except Exception as e:
                print("Firebase search sync failed:", e)

    def load_search_from_firebase(self):
        """Loads last search query from Firebase."""
        if self.logged_in and self.firebase_uid:
            try:
                db = self._get_firebase().database()
                history = db.child("users").child(self.firebase_uid).child("search_history").order_by_key().limit_to_last(1).get().val()
                if history:
                    # history is a dict {key: val}
                    last_search = list(history.values())[-1]
                    self.search_query = last_search
            except Exception as e:
                print("Firebase search load failed:", e)
