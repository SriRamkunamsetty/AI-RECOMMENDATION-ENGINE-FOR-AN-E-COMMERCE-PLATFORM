import reflex as rx

from components.navbar import navbar
from state.orders_state import OrderState
from state.cart_state import CartState


@rx.page(route="/checkout", title="Checkout")
def checkout() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Secure Checkout", size="8", margin_top="3rem", margin_bottom="2rem"),
                rx.card(
                    rx.form(
                        rx.vstack(
                            rx.input(
                                placeholder="Full Name",
                                name="name",
                                value=OrderState.checkout_name,
                                on_change=OrderState.set_checkout_name,
                                required=True,
                                width="100%",
                                size="3",
                            ),
                            rx.input(
                                placeholder="Phone Number",
                                name="phone",
                                value=OrderState.checkout_phone,
                                on_change=OrderState.set_checkout_phone,
                                required=True,
                                width="100%",
                                size="3",
                            ),
                            rx.text_area(
                                placeholder="Delivery Address",
                                name="address",
                                value=OrderState.checkout_address,
                                on_change=OrderState.set_checkout_address,
                                required=True,
                                width="100%",
                                size="3",
                            ),
                            rx.cond(
                                OrderState.checkout_error != "",
                                rx.text(OrderState.checkout_error, color="red", size="2"),
                            ),
                            rx.text(
                                "Subtotal: ₹",
                                CartState.total_price.to_string(),
                                color="gray",
                            ),
                            rx.button(
                                "Proceed to Demo Payment",
                                type="submit",
                                color_scheme="blue",
                                size="3",
                                width="100%",
                                margin_top="1rem",
                            ),
                            width="100%",
                        ),
                        on_submit=OrderState.submit_checkout,
                    ),
                    padding="2rem",
                    width="100%",
                    max_width="500px",
                    shadow="lg",
                ),
                width="100%",
                align_items="center",
            ),
            size="3",
        ),
    )
