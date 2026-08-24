import reflex as rx

from components.navbar import navbar
from state.cart_state import CartState
from state.orders_state import OrderState
from state.payment_state import PaymentState


@rx.page(route="/payment", title="Demo Payment")
def payment() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Demo Payment", size="8", margin_top="2rem", margin_bottom="1rem"),
                rx.callout(
                    "This repository is configured for a local demo payment only. No real charge is made.",
                    icon="info",
                    color_scheme="orange",
                    width="100%",
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Order Summary", size="4"),
                        rx.hstack(
                            rx.text("Subtotal", color="gray"),
                            rx.spacer(),
                            rx.text("₹", CartState.total_price.to_string()),
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("Tax (GST 18%)", color="gray"),
                            rx.spacer(),
                            rx.text("₹", CartState.tax_amount.to_string()),
                            width="100%",
                        ),
                        rx.divider(),
                        rx.hstack(
                            rx.text("Total Payable", size="5", weight="bold"),
                            rx.spacer(),
                            rx.text("₹", CartState.total_payable.to_string(), size="5", weight="bold"),
                            width="100%",
                        ),
                        rx.text(
                            "Delivering to: ",
                            OrderState.checkout_name,
                            " — ",
                            OrderState.checkout_address,
                            color="gray",
                            size="2",
                        ),
                        rx.cond(
                            PaymentState.payment_error != "",
                            rx.text(PaymentState.payment_error, color="red", size="2"),
                        ),
                        rx.button(
                            rx.cond(
                                PaymentState.payment_status == "processing",
                                "Processing…",
                                "Complete Demo Payment",
                            ),
                            on_click=PaymentState.start_demo_payment,
                            disabled=PaymentState.payment_status == "processing",
                            color_scheme="blue",
                            size="4",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    padding="2rem",
                    width="100%",
                    max_width="600px",
                ),
                width="100%",
                align_items="center",
            ),
            size="3",
        ),
        background_color="#f2f5f7",
        min_height="100vh",
    )
