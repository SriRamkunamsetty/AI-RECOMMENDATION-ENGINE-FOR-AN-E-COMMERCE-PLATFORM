import reflex as rx
from components.navbar import navbar
from components.product_card import product_card
from state.wishlist_state import WishlistState

@rx.page(route="/wishlist", title="My Wishlist")
def wishlist() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("My Wishlist", size="8", margin_top="3rem"),
                rx.text(
                    WishlistState.wishlist_count.to_string() + " item(s) saved",
                    color="gray",
                    margin_top="0.5rem",
                    margin_bottom="2rem"
                ),
                rx.cond(
                    WishlistState.wishlist_count > 0,
                    rx.grid(
                        rx.foreach(
                            WishlistState.wishlist_items,
                            lambda p: product_card(p, allow_remove=True)
                        ),
                        columns="4",
                        spacing="4",
                        width="100%"
                    ),
                    rx.vstack(
                        rx.icon("heart-off", size=48, color="gray"),
                        rx.text("Your wishlist is empty.", color="gray", size="4"),
                        rx.link(
                            rx.button("Browse Products", color_scheme="blue"),
                            href="/"
                        ),
                        align="center",
                        spacing="4",
                        padding_top="4rem"
                    )
                ),
                width="100%",
                align_items="start"
            ),
            size="4"
        )
    )
