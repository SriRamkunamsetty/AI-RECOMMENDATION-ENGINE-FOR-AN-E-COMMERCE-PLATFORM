import reflex as rx

from components.navbar import navbar
from state.orders_state import OrderState


def order_row(order: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(order["id"], weight="bold"),
                rx.spacer(),
                rx.badge(order["status"], color_scheme="green"),
                width="100%",
            ),
            rx.text("Total: ₹", order["total"].to_string()),
            rx.text("Placed: ", order["created_at"], color="gray", size="2"),
            rx.text("Delivering to: ", order["name"], " — ", order["address"], color="gray", size="2"),
            width="100%",
            align_items="start",
        ),
        width="100%",
        max_width="800px",
    )


@rx.page(route="/orders", title="Order History", on_load=OrderState.load_orders)
def orders() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Order History", size="8", margin_top="3rem"),
                rx.cond(
                    OrderState.orders.length() > 0,
                    rx.vstack(rx.foreach(OrderState.orders, order_row), width="100%"),
                    rx.vstack(
                        rx.text("No orders yet.", color="gray", size="4"),
                        rx.link(rx.button("Browse Products", color_scheme="blue"), href="/"),
                        spacing="4",
                        padding_top="4rem",
                    ),
                ),
                width="100%",
                align_items="center",
            ),
            size="3",
        ),
    )
