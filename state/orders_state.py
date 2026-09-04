"""Per-user order lifecycle and history."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

import reflex as rx

from state.user_state import UserState


def validate_shipping_details(name: str, phone: str, address: str) -> str:
    """Return a user-facing validation error, or an empty string when valid."""
    if not name.strip():
        return "Full name is required."
    normalized_phone = phone.strip().replace("+", "").replace(" ", "")
    if not normalized_phone.isdigit() or len(normalized_phone) < 10:
        return "Enter a valid phone number."
    if not address.strip():
        return "Delivery address is required."
    return ""


class OrderState(UserState):
    orders: List[Dict[str, Any]] = []
    checkout_name: str = ""
    checkout_phone: str = ""
    checkout_address: str = ""
    checkout_error: str = ""

    def set_checkout_name(self, value: str):
        self.checkout_name = value

    def set_checkout_phone(self, value: str):
        self.checkout_phone = value

    def set_checkout_address(self, value: str):
        self.checkout_address = value

    def validate_checkout(self) -> bool:
        self.checkout_error = validate_shipping_details(
            self.checkout_name, self.checkout_phone, self.checkout_address
        )
        return not self.checkout_error

    def create_pending_order(self, cart_items: List[Dict[str, Any]], total: float) -> str:
        if not self.validate_checkout():
            return ""
        order_id = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        order = {
            "id": order_id,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "items": [item.copy() for item in cart_items],
            "total": round(float(total), 2),
            "name": self.checkout_name.strip(),
            "phone": self.checkout_phone.strip(),
            "address": self.checkout_address.strip(),
        }
        self.orders = [order] + self.orders
        self.sync_orders()
        return order_id

    def mark_order_paid(self, order_id: str):
        self.orders = [
            {**order, "status": "paid"} if order.get("id") == order_id else order
            for order in self.orders
        ]
        self.sync_orders()

    def mark_order_failed(self, order_id: str):
        self.orders = [
            {**order, "status": "failed"} if order.get("id") == order_id else order
            for order in self.orders
        ]
        self.sync_orders()

    def sync_orders(self):
        if self._is_firebase_configured() and self.logged_in and self.firebase_uid:
            try:
                self._get_firebase().database().child("users").child(self.firebase_uid).child(
                    "orders"
                ).set(self.orders)
            except Exception as exc:
                print(f"Firebase order sync failed: {exc}")

    def load_orders(self):
        if self._is_firebase_configured() and self.logged_in and self.firebase_uid:
            try:
                value = (
                    self._get_firebase()
                    .database()
                    .child("users")
                    .child(self.firebase_uid)
                    .child("orders")
                    .get()
                    .val()
                )
                self.orders = [order for order in (value or []) if order]
            except Exception as exc:
                print(f"Firebase order load failed: {exc}")

    def submit_checkout(self):
        if self.validate_checkout():
            return rx.redirect("/payment")

    def reset_checkout(self):
        self.checkout_name = ""
        self.checkout_phone = ""
        self.checkout_address = ""
        self.checkout_error = ""
