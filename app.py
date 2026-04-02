import reflex as rx

# Import Application States to ensure they register
from state.user_state import UserState
from state.cart_state import CartState
from state.recommendation_state import RecommendationState
from state.payment_state import PaymentState
from state.products_state import ProductsState
from state.wishlist_state import WishlistState

# Import pages (as we build them)
import pages.profile
import pages.home
import pages.login
import pages.signup
import pages.product_detail
import pages.cart
import pages.checkout
import pages.payment
import pages.wishlist
import pages.orders

# Create main Reflex App
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="full",
        accent_color="ruby",
        gray_color="sand"
    ),
    style={
        "background_color": "#FDF8F5",
        "font_family": "Outfit, sans-serif",
        "color": "#4A332C"
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap",
    ],
)

