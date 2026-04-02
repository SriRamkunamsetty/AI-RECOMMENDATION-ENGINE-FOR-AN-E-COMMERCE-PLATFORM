import reflex as rx
from state.wishlist_state import WishlistState

def product_card(product: dict) -> rx.Component:
    """
    A reusable product card component.
    Expects a dictionary representing a product from our dataset.
    """
    # Safe fallback values for UI
    img_url = rx.cond(product.contains("ImageURL"), product["ImageURL"], "/placeholder.jpg")
    brand = rx.cond(product.contains("Brand"), product["Brand"], "Brand")
    display_name = rx.cond(product.contains("Product_Display_Name"), product["Product_Display_Name"], brand)
    description = product["Description"]
    
    return rx.card(
        rx.vstack(
            rx.image(
                src=img_url, 
                height="150px", 
                width="100%", 
                object_fit="cover",
                fallback="https://via.placeholder.com/150"
            ),
            rx.box(
                rx.text(display_name, font_weight="bold", font_size="md", no_of_lines=1, font_family="Playfair Display", color="#4A332C"),
                rx.text(description, color="gray", font_size="xs", no_of_lines=2, margin_top="0.25rem"),
                margin_top="0.5rem"
            ),
            rx.hstack(
                # Use dataset rating if available
                rx.text(f"★ {product.get('Rating', 'N/A')}", font_size="sm", color="#B59288"),
                rx.spacer(),
                rx.text(f"₹{product['Price']}", font_weight="bold", color="#6F3E3F"),
                width="100%",
                padding_top="0.5rem"
            ),
            rx.hstack(
                rx.link(
                    rx.button("VIEW", width="100%", background_color="#6F3E3F", color="white", border_radius="full"),
                    href=f"/product/{product['ProdID']}",
                    flex="1"
                ),
                rx.button(
                    rx.icon("heart", color="#6F3E3F"),
                    background_color="white",
                    border="1px solid #D6C0B4",
                    border_radius="full",
                    on_click=WishlistState.add_to_wishlist(product)
                ),
                width="100%",
                margin_top="1rem",
                spacing="2"
            ),
            
            align_items="start",
            height="100%",
            justify_content="space-between"
        ),
        shadow="sm",
        border="1px solid #E8DCD1",
        _hover={"border_color": "#6F3E3F", "transition": "all 0.2s"},
        overflow="hidden",
        border_radius="2xl",
        background_color="#FFFFFF",
        width="100%"
    )
