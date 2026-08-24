"""Per-user wishlist state with Firebase persistence."""

from typing import Any, Dict, List

import reflex as rx

from state.user_state import UserState


class WishlistState(UserState):
    wishlist_items: List[Dict[str, Any]] = []

    def add_to_wishlist(self, product: Dict[str, Any]):
        product_id = product.get("ProdID")
        if not any(item.get("ProdID") == product_id for item in self.wishlist_items):
            self.wishlist_items.append(product.copy())
            self.sync_to_firebase()
            return rx.toast.success("Added to Wishlist!", position="top-right")
        return rx.toast.info("Already in Wishlist!", position="top-right")

    def remove_from_wishlist(self, product_id: int):
        self.wishlist_items = [
            item for item in self.wishlist_items if item.get("ProdID") != product_id
        ]
        self.sync_to_firebase()

    def clear_wishlist(self):
        self.wishlist_items = []
        self.sync_to_firebase()

    def sync_to_firebase(self):
        if self.logged_in and self.firebase_uid:
            try:
                self._get_firebase().database().child("users").child(self.firebase_uid).child(
                    "wishlist"
                ).set(self.wishlist_items)
            except Exception as exc:
                print(f"Firebase wishlist sync failed: {exc}")

    def load_from_firebase(self):
        if self.logged_in and self.firebase_uid:
            try:
                value = (
                    self._get_firebase()
                    .database()
                    .child("users")
                    .child(self.firebase_uid)
                    .child("wishlist")
                    .get()
                    .val()
                )
                self.wishlist_items = [item for item in (value or []) if item]
            except Exception as exc:
                print(f"Firebase wishlist load failed: {exc}")

    @rx.var
    def wishlist_count(self) -> int:
        return len(self.wishlist_items)
