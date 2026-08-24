"""Explicit demo-payment flow; real provider credentials are not stored in source."""

import asyncio

import reflex as rx

from state.cart_state import CartState
from state.orders_state import OrderState


class PaymentState(CartState):
    payment_status: str = "idle"
    payment_error: str = ""
    current_order_id: str = ""

    async def start_demo_payment(self):
        """Complete a clearly labelled local demo payment after creating an order."""
        self.payment_error = ""
        order_state = await self.get_state(OrderState)
        if not self.cart_items:
            self.payment_error = "Your cart is empty."
            return
        if not order_state.validate_checkout():
            self.payment_error = order_state.checkout_error
            return

        self.payment_status = "processing"
        yield
        order_id = order_state.create_pending_order(self.cart_items, self.total_payable)
        if not order_id:
            self.payment_status = "failed"
            self.payment_error = order_state.checkout_error or "Unable to create order."
            return

        self.current_order_id = order_id
        await asyncio.sleep(1)
        order_state.mark_order_paid(order_id)
        self.payment_status = "succeeded"
        self.clear_cart()
        yield rx.redirect("/orders")
