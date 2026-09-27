import reflex as rx
from components.navbar import navbar
from state.user_state import UserState

@rx.page(route="/profile", title="User Profile")
def profile() -> rx.Component:
    """Displays user info, authentication identity, and session controls."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Customer Profile", size="8", margin_top="2rem", margin_bottom="1rem", color="#6F3E3F", font_family="Playfair Display"),
                rx.cond(
                    UserState.logged_in,
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.avatar(fallback="U", size="6"),
                                rx.vstack(
                                    rx.heading(UserState.customer_display_name, size="5"),
                                    rx.text(UserState.email, color="gray", size="2"),
                                    align_items="start",
                                ),
                                spacing="4",
                                align_items="center",
                                margin_bottom="1.5rem",
                            ),
                            rx.divider(margin_bottom="1rem"),
                            rx.hstack(
                                rx.text("Account Status:", font_weight="bold"),
                                rx.spacer(),
                                rx.badge(
                                    rx.cond(UserState.is_new_user, "New Customer", "Returning Customer"),
                                    color_scheme=rx.cond(UserState.is_new_user, "green", "blue"),
                                ),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("Recommendation ID:", font_weight="bold"),
                                rx.spacer(),
                                rx.text(UserState.user_id.to_string(), color="gray"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("Firebase UID:", font_weight="bold"),
                                rx.spacer(),
                                rx.text(UserState.firebase_uid, color="gray", size="1"),
                                width="100%",
                            ),
                            rx.divider(margin_y="1.5rem"),
                            rx.hstack(
                                rx.link(rx.button(rx.icon("package"), " My Orders", color_scheme="blue", variant="outline", size="2"), href="/orders"),
                                rx.link(rx.button(rx.icon("heart"), " My Wishlist", color_scheme="pink", variant="outline", size="2"), href="/wishlist"),
                                spacing="3",
                                width="100%",
                                justify="center",
                            ),
                            rx.button("Log Out", on_click=UserState.logout, color_scheme="red", variant="solid", width="100%", margin_top="1rem"),
                            align_items="start",
                            width="100%",
                        ),
                        width="100%",
                        max_width="480px",
                        padding="2rem",
                        shadow="md",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.icon("user-x", size=48, color="gray"),
                            rx.heading("You are not logged in", size="5"),
                            rx.text("Sign in to view your orders, wishlist, and recommendations.", color="gray"),
                            rx.link(rx.button("Go to Login", color_scheme="blue", size="3"), href="/login"),
                            spacing="4",
                            align_items="center",
                            padding="2rem",
                        ),
                        max_width="400px",
                        width="100%",
                    ),
                ),
                padding_top="2rem",
                padding_bottom="4rem",
                align_items="center",
                width="100%",
            ),
            size="3",
            margin="auto",
        ),
        background_color="#FDF8F5",
        min_height="100vh",
    )
