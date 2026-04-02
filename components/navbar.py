import reflex as rx
from state.user_state import UserState
from state.cart_state import CartState
from state.products_state import ProductsState
from components.chatbot import chatbot

def navbar() -> rx.Component:
    """A responsive navigation bar for the e-commerce app."""
    return rx.box(
        rx.hstack(
            rx.link(rx.heading("Shopping Store", size="5", color="#6F3E3F", font_family="Playfair Display", weight="bold"), href="/", underline="none"),
            rx.spacer(),
            rx.hstack(
                rx.link("Home", href="/", color="#4A332C", _hover={"color": "#6F3E3F"}),
                rx.link("Wishlist", href="/wishlist", color="#4A332C", _hover={"color": "#6F3E3F"}),
                rx.link("Orders", href="/orders", color="#4A332C", _hover={"color": "#6F3E3F"}),
                rx.cond(UserState.logged_in, rx.link("Profile", href="/profile", color="#4A332C", _hover={"color": "#6F3E3F"})),
                
                # Amazon-style search bar
                rx.box(
                    rx.form(
                        rx.hstack(
                            rx.input(
                                placeholder="Search products...",
                                name="q",
                                width="250px",
                                border_radius="full",
                                background_color="#FFFFFF",
                                border="1px solid #D6C0B4",
                            ),
                            rx.button(
                                rx.icon(tag="search", color="#6F3E3F"),
                                type="submit",
                                variant="ghost",
                                border_radius="full",
                            ),
                            spacing="0"
                        ),
                        on_submit=ProductsState.handle_search_submit,
                        margin_left="1.5rem"
                    ),
                    display="block"
                ),
                spacing="5"
            ),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.icon(tag="shopping-cart", color="#4A332C"),
                        rx.badge(
                            CartState.cart_items.length(), 
                            background_color="#6F3E3F",
                            color="white",
                            variant="solid", 
                            radius="full",
                            position="absolute",
                            top="-0.5rem",
                            right="-0.5rem"
                        ),
                        variant="outline",
                        position="relative"
                    ),
                    href="/cart"
                ),
                rx.cond(
                    UserState.logged_in,
                    rx.button("Log Out", on_click=UserState.logout, background_color="white", color="#6F3E3F", border="1px solid #6F3E3F", border_radius="full"),
                    rx.link(rx.button("LOGIN", background_color="#6F3E3F", color="white", border_radius="full"), href="/login")
                ),
                spacing="4",
                align_items="center"
            ),
            
            width="100%",
            padding="1rem 2rem",
            border_bottom="1px solid #E8DCD1",
            justify_content="space-between",
            align_items="center",
            position="sticky",
            top="0",
            background_color="rgba(253, 248, 245, 0.95)",
            backdrop_filter="blur(10px)",
            z_index="1000"
        ),
        chatbot()
    )
