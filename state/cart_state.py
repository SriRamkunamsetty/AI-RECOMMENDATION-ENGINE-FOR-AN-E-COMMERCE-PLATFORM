"""Shopping cart state and canonical subtotal calculations."""

from typing import Any, Dict, List

import reflex as rx

from backend.data_utils import format_price, price_for_product
from state.user_state import UserState


def calculate_cart_totals(items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], float]:
    """Normalize cart rows and return rows plus their aggregate subtotal."""
    normalized = []
    for original in items:
        item = original.copy()
        product_id = item.get("ProdID", 0)
        raw_price = item.get("Price")
        if raw_price is not None:
            try:
                unit_price = float(str(raw_price).replace(",", "").strip())
            except (TypeError, ValueError):
                unit_price = price_for_product(product_id)
        else:
            unit_price = price_for_product(product_id)
        quantity = max(1, int(item.get("quantity", 1)))
        item["Price"] = format_price(unit_price)
        item["quantity"] = quantity
        item["line_total"] = format_price(unit_price * quantity)
        normalized.append(item)
    subtotal = round(
        sum(float(str(item["Price"]).replace(",", "")) * int(item["quantity"]) for item in normalized),
        2,
    )
    return normalized, subtotal


class CartState(UserState):
    cart_items: List[Dict[str, Any]] = []
    total_price: float = 0.0

    def _normalize_item(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return calculate_cart_totals([product])[0][0]

    def add_to_cart(self, product: Dict[str, Any]):
        product_id = product.get("ProdID")
        for index, item in enumerate(self.cart_items):
            if item.get("ProdID") == product_id:
                updated = item.copy()
                updated["quantity"] = int(updated.get("quantity", 1)) + 1
                self.cart_items[index] = self._normalize_item(updated)
                break
        else:
            self.cart_items.append(self._normalize_item(product))
        self.calculate_total()
        self.sync_to_firebase()

    def remove_from_cart(self, product_id: int):
        self.cart_items = [item for item in self.cart_items if item.get("ProdID") != product_id]
        self.calculate_total()
        self.sync_to_firebase()

    def calculate_total(self):
        self.cart_items, self.total_price = calculate_cart_totals(self.cart_items)

    def clear_cart_locally(self):
        """Clear session-local cart state without persisting a deletion."""
        self.cart_items = []
        self.total_price = 0.0

    def clear_cart(self):
        self.clear_cart_locally()
        self.sync_to_firebase()

    def sync_to_firebase(self):
        if self.logged_in and self.firebase_uid:
            try:
                self._get_firebase().database().child("users").child(self.firebase_uid).child(
                    "cart"
                ).set(self.cart_items)
            except Exception as exc:
                print(f"Firebase cart sync failed: {exc}")

    def load_from_firebase(self):
        if self.logged_in and self.firebase_uid:
            try:
                value = (
                    self._get_firebase()
                    .database()
                    .child("users")
                    .child(self.firebase_uid)
                    .child("cart")
                    .get()
                    .val()
                )
                self.cart_items = [self._normalize_item(item) for item in (value or []) if item]
                self.calculate_total()
            except Exception as exc:
                print(f"Firebase cart load failed: {exc}")

    @rx.var
    def tax_amount(self) -> float:
        return round(self.total_price * 0.18, 2)

    @rx.var
    def total_payable(self) -> float:
        return round(self.total_price + self.tax_amount, 2)
