import reflex as rx
from state.user_state import UserState
from state.recommendation_state import RecommendationState
from state.products_state import ProductsState
from components.navbar import navbar
from components.product_card import product_card

@rx.page(route="/", title="Home - AI Store", on_load=[RecommendationState.fetch_general_recommendations, ProductsState.fetch_products])
def home() -> rx.Component:
    """The landing page. Shows different headings based on user type, or search results."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Welcome to Your AI-Powered Store!", size="8", weight="bold", margin_top="3rem", margin_bottom="1rem", text_align="center", color="#6F3E3F", font_family="Playfair Display"),
                rx.text("Discover products perfectly tailored for you using Machine Learning.", size="4", color="gray", margin_bottom="3rem", text_align="center"),
                
                rx.cond(
                    ProductsState.search_query != "",
                    # If user searched for something
                    rx.box(
                        rx.heading(f"Search Results for '{ProductsState.search_query}'", size="6", margin_bottom="1rem", color="#6F3E3F", font_family="Playfair Display"),
                        rx.grid(
                            rx.foreach(ProductsState.all_products, lambda p: product_card(p)),
                            columns="4",
                            spacing="4",
                            width="100%"
                        ),
                        width="100%"
                    ),
                    # Display recommendations if no search
                    rx.vstack(
                        rx.cond(
                            (~UserState.logged_in) | UserState.is_new_user,
                            # If new user or not logged in -> rating based heading
                            rx.heading("Top Rated Items", size="6", margin_bottom="1rem", color="#6F3E3F", font_family="Playfair Display"),
                            # If existing logged in user -> recommender
                            rx.heading("Your Recommended Products", size="6", margin_bottom="1rem", color="#6F3E3F", font_family="Playfair Display") 
                        ),
                        
                        rx.button(
                            "Load My Recommendations", 
                            on_click=RecommendationState.fetch_general_recommendations, 
                            size="3", 
                            background_color="#6F3E3F",
                            color="white",
                            border_radius="full",
                            margin_bottom="2rem"
                        ),
                        
                        rx.cond(
                            RecommendationState.is_loading,
                            rx.spinner(size="3"),
                            rx.grid(
                                rx.foreach(RecommendationState.recommendations, lambda p: product_card(p)),
                                columns="4",
                                spacing="4",
                                width="100%"
                            )
                        ),
                        width="100%",
                        align_items="center"
                    )
                ),
                
                padding_bottom="4rem",
                width="100%",
                align_items="center"
            ),
            size="4"
        )
    )
