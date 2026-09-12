import reflex as rx

from state.wishlist_state import WishlistState


def product_card(product: dict, allow_remove: bool = False) -> rx.Component:
    """Render a product card with add or remove wishlist behavior."""
    image_url = rx.cond(product.contains("ImageURL"), product["ImageURL"], "/placeholder.jpg")
    brand = rx.cond(product.contains("Brand"), product["Brand"], "Brand")
    display_name = rx.cond(
        product.contains("Product_Display_Name"), product["Product_Display_Name"], brand
    )
    description = rx.cond(
        product.contains("Description"), product["Description"], "No description available."
    )
    price = rx.cond(
        product.contains("Price"), product["Price"], "0.00"
    )
    wishlist_action = (
        WishlistState.remove_from_wishlist(product["ProdID"])
        if allow_remove
        else WishlistState.add_to_wishlist(product)
    )

    return rx.card(
        rx.vstack(
            rx.image(
                src=image_url,
                height="150px",
                width="100%",
                object_fit="cover",
                fallback="https://via.placeholder.com/150",
            ),
            rx.box(
                rx.cond(
                    product.contains("Explanation"),
                    rx.cond(
                        product["Explanation"] != "",
                        rx.badge(
                            rx.icon("sparkles", size=12),
                            product["Explanation"],
                            color_scheme="ruby",
                            variant="surface",
                            size="1",
                            margin_bottom="0.25rem",
                        ),
                    ),
                ),
                rx.text(display_name, font_weight="bold", font_size="md", no_of_lines=1),
                rx.text(description, color="gray", font_size="xs", no_of_lines=2),
                margin_top="0.5rem",
                width="100%",
            ),
            rx.hstack(
                rx.text(
                    "★ ",
                    rx.cond(product.contains("Rating"), product["Rating"], "N/A"),
                    font_size="sm",
                    color="#B59288",
                ),
                rx.spacer(),
                rx.text("₹", price, font_weight="bold", color="#6F3E3F"),
                width="100%",
            ),
            rx.hstack(
                rx.link(
                    rx.button("VIEW", width="100%", background_color="#6F3E3F", color="white"),
                    href=f"/product/{product['ProdID']}",
                    flex="1",
                ),
                rx.button(
                    rx.icon("trash-2" if allow_remove else "heart", color="#6F3E3F"),
                    aria_label="Remove from wishlist" if allow_remove else "Add to wishlist",
                    on_click=wishlist_action,
                ),
                width="100%",
                margin_top="1rem",
            ),
            align_items="start",
            height="100%",
            justify_content="space-between",
        ),
        width="100%",
    )
