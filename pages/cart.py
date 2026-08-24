import reflex as rx

from components.navbar import navbar
from state.cart_state import CartState


def cart_item_row(item: dict) -> rx.Component:
    """Render one cart row using the normalized state values."""
    img_url = rx.cond(item.contains("ImageURL"), item["ImageURL"], "/placeholder.jpg")
    brand = rx.cond(item.contains("Brand"), item["Brand"], "Brand")
    category = rx.cond(item.contains("Category"), item["Category"], "Category")
    quantity = rx.cond(item.contains("quantity"), item["quantity"].to_string(), "1")
    unit_price = rx.cond(item.contains("Price"), item["Price"], "0.00")
    line_total = rx.cond(item.contains("line_total"), item["line_total"], "0.00")

    return rx.hstack(
        rx.image(src=img_url, width="60px", height="60px", object_fit="cover", border_radius="md"),
        rx.vstack(
            rx.text(brand, font_weight="bold", size="4"),
            rx.text(category, color="gray", size="2"),
            rx.text("Unit price: ₹", unit_price, color="gray", size="1"),
        ),
        rx.spacer(),
        rx.text("Qty: ", quantity, weight="medium"),
        rx.spacer(),
        rx.text("₹", line_total, font_weight="bold", color="blue.600", size="4"),
        rx.button(
            rx.icon("trash"),
            color_scheme="red",
            variant="ghost",
            on_click=lambda: CartState.remove_from_cart(item["ProdID"]),
        ),
        width="100%",
        padding="1.5rem",
        align_items="center",
        border_bottom="1px solid #eaeaea",
    )


@rx.page(route="/cart", title="Shopping Cart")
def cart() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Your Shopping Cart", size="8", margin_top="3rem", margin_bottom="2rem"),
                rx.cond(
                    CartState.cart_items.length() > 0,
                    rx.card(
                        rx.vstack(
                            rx.foreach(CartState.cart_items, cart_item_row),
                            rx.divider(margin_y="2rem"),
                            rx.hstack(
                                rx.heading("Total:", size="6"),
                                rx.spacer(),
                                rx.heading("₹", CartState.total_price.to_string(), size="7", color="blue.600"),
                                width="100%",
                                padding_x="1rem",
                            ),
                            rx.hstack(
                                rx.button(
                                    "Clear Cart",
                                    on_click=CartState.clear_cart,
                                    color_scheme="gray",
                                    variant="outline",
                                    size="3",
                                ),
                                rx.spacer(),
                                rx.link(
                                    rx.button("Proceed to Checkout", color_scheme="green", size="3"),
                                    href="/checkout",
                                ),
                                width="100%",
                                padding="1rem",
                                margin_top="2rem",
                            ),
                            width="100%",
                        ),
                        width="100%",
                        padding="0",
                    ),
                    rx.vstack(
                        rx.icon(tag="shopping-cart", size=60, color="gray"),
                        rx.heading("Your cart is empty", size="6", color="gray", margin_top="1rem"),
                        rx.link(
                            rx.button("Continue Shopping", margin_top="2rem", size="3"),
                            href="/",
                        ),
                        margin_top="10vh",
                    ),
                ),
                width="100%",
                align_items="center",
            ),
            size="3",
        ),
    )
