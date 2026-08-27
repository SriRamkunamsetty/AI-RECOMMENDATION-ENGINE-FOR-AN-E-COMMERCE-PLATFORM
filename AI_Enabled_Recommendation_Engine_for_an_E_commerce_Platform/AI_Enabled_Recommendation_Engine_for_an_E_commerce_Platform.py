"""Main Application Entry Point."""

import reflex as rx

# Application State Imports
from state.user_state import UserState  # noqa: F401
from state.cart_state import CartState  # noqa: F401
from state.recommendation_state import RecommendationState  # noqa: F401
from state.products_state import ProductsState  # noqa: F401
from state.payment_state import PaymentState  # noqa: F401
from state.wishlist_state import WishlistState  # noqa: F401
from state.orders_state import OrderState  # noqa: F401

# Import all pages to ensure their routes are registered via their decorators
import pages.home
import pages.login
import pages.signup
import pages.product_detail
import pages.cart
import pages.checkout
import pages.payment
import pages.profile
import pages.wishlist
import pages.orders  # noqa: F401

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="blue",
    )
)
