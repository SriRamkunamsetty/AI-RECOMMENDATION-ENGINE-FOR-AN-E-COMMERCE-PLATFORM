"""Catalog loading, filtering, sorting, and search-history state."""

from typing import Any, Dict, List
from urllib.parse import quote_plus

import reflex as rx

from backend.data_utils import canonical_products, load_interactions, price_for_product
from state.user_state import UserState


class ProductsState(UserState):
    all_products: List[Dict[str, Any]] = []
    search_query: str = ""
    sort_order: str = "default"

    def fetch_products(self):
        try:
            params = self.router.page.params
            self.search_query = str(params.get("q", ""))
            data = load_interactions()
            products = canonical_products(data)
            products["Price_Num"] = products["ProdID"].map(price_for_product)
            if self.search_query:
                query = self.search_query.strip()
                mask = False
                for column in ("Brand", "Category", "Description", "Name"):
                    if column in products.columns:
                        mask = mask | products[column].str.contains(query, case=False, na=False, regex=False)
                products = products[mask]
            if self.sort_order == "low_to_high":
                products = products.sort_values("Price_Num", ascending=True)
            elif self.sort_order == "high_to_low":
                products = products.sort_values("Price_Num", ascending=False)

            products = products.head(48).fillna("")
            products["Price"] = products["Price_Num"].map(lambda value: f"{float(value):.2f}")
            products["ImageURL"] = products["ImageURL"].map(
                lambda value: str(value).split(" | ")[0] if str(value).strip() else "/placeholder.jpg"
            )
            products["Rating"] = products["Rating"].map(
                lambda value: f"{float(value):.1f}" if str(value).strip() else "N/A"
            )
            self.all_products = products.to_dict("records")
        except Exception as exc:
            print(f"Error fetching products: {exc}")
            self.all_products = []

    def update_sort(self, value: str):
        self.sort_order = value
        return self.fetch_products()

    def update_search(self, query: str):
        self.search_query = query
        self.sync_search_to_firebase(query)
        return self.fetch_products()

    def handle_search_submit(self, form_data: Dict[str, Any]):
        query = str(form_data.get("q", "")).strip()
        self.search_query = query
        self.sync_search_to_firebase(query)
        return rx.redirect(f"/?q={quote_plus(query)}")

    def sync_search_to_firebase(self, query: str):
        if self.logged_in and self.firebase_uid and query.strip():
            try:
                self._get_firebase().database().child("users").child(self.firebase_uid).child(
                    "search_history"
                ).push(query)
            except Exception as exc:
                print(f"Firebase search sync failed: {exc}")

    def load_search_from_firebase(self):
        # Reset first so account switches cannot retain the previous user’s query.
        self.search_query = ""
        if self.logged_in and self.firebase_uid:
            try:
                history = (
                    self._get_firebase()
                    .database()
                    .child("users")
                    .child(self.firebase_uid)
                    .child("search_history")
                    .order_by_key()
                    .limit_to_last(1)
                    .get()
                    .val()
                )
                if history:
                    self.search_query = str(list(history.values())[-1])
            except Exception as exc:
                print(f"Firebase search load failed: {exc}")
