"""Authentication and per-user session state."""

from __future__ import annotations

import hashlib
import os

import pandas as pd
import reflex as rx
from dotenv import load_dotenv

from config import DATA_PATH

load_dotenv()


class UserState(rx.State):
    """Manage Firebase authentication and a stable recommendation identity."""

    user_id: int = -1
    logged_in: bool = False
    is_new_user: bool = True
    firebase_uid: str = ""
    full_name: str = ""
    email: str = ""
    password: str = ""
    auth_error: str = ""

    def _get_firebase(self):
        from pyrebase import initialize_app

        required = {
            "FIREBASE_API_KEY": os.getenv("FIREBASE_API_KEY"),
            "FIREBASE_AUTH_DOMAIN": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "FIREBASE_PROJECT_ID": os.getenv("FIREBASE_PROJECT_ID"),
            "FIREBASE_STORAGE_BUCKET": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "FIREBASE_SENDER_ID": os.getenv("FIREBASE_SENDER_ID"),
            "FIREBASE_APP_ID": os.getenv("FIREBASE_APP_ID"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Firebase is not configured. Missing: " + ", ".join(sorted(missing))
            )
        firebase_config = {
            "apiKey": required["FIREBASE_API_KEY"],
            "authDomain": required["FIREBASE_AUTH_DOMAIN"],
            "projectId": required["FIREBASE_PROJECT_ID"],
            "storageBucket": required["FIREBASE_STORAGE_BUCKET"],
            "messagingSenderId": required["FIREBASE_SENDER_ID"],
            "appId": required["FIREBASE_APP_ID"],
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL", ""),
        }
        return initialize_app(firebase_config)

    def set_full_name(self, value: str):
        self.full_name = value

    def set_email(self, value: str):
        self.email = value

    def set_password(self, value: str):
        self.password = value

    @staticmethod
    def _dataset_user_id(uid: str) -> int:
        """Map a Firebase UID deterministically outside the historical ID range."""
        digest = hashlib.sha256(uid.encode("utf-8")).digest()
        return 1_000_000_000 + int.from_bytes(digest[:8], "big") % 1_000_000_000

    def signup_with_firebase(self):
        if not self.email or not self.password:
            self.auth_error = "Please enter both email and password."
            return
        try:
            user = self._get_firebase().auth().create_user_with_email_and_password(
                self.email, self.password
            )
            yield from self._handle_successful_login(user["localId"])
            yield rx.redirect("/")
        except Exception as exc:
            self.auth_error = f"Registration failed: {exc}"

    def login_with_firebase(self):
        if not self.email or not self.password:
            self.auth_error = "Please enter both email and password."
            return
        try:
            user = self._get_firebase().auth().sign_in_with_email_and_password(
                self.email, self.password
            )
            yield from self._handle_successful_login(user["localId"])
            yield rx.redirect("/")
        except Exception:
            self.auth_error = "Login failed. Please check your credentials."

    def _handle_successful_login(self, uid: str):
        self.firebase_uid = uid
        self.logged_in = True
        self.auth_error = ""
        self.user_id = self._dataset_user_id(uid)
        self._sync_or_load_profile()

        from state.cart_state import CartState
        from state.products_state import ProductsState
        from state.wishlist_state import WishlistState
        from state.orders_state import OrderState

        yield CartState.load_from_firebase
        yield WishlistState.load_from_firebase
        yield ProductsState.load_search_from_firebase
        yield OrderState.load_orders

        try:
            data = pd.read_csv(DATA_PATH, usecols=["User's ID"])
            self.is_new_user = self.user_id not in data["User's ID"].values
        except (OSError, ValueError, KeyError):
            self.is_new_user = True

    def _sync_or_load_profile(self):
        try:
            database = self._get_firebase().database().child("users").child(self.firebase_uid)
            profile = database.child("profile").get().val() or {}
            if profile.get("full_name") and not self.full_name:
                self.full_name = str(profile["full_name"])
            elif self.full_name.strip():
                database.child("profile").set(
                    {"full_name": self.full_name.strip(), "user_id": self.user_id}
                )
        except Exception as exc:
            print(f"Firebase profile sync failed: {exc}")

    def check_login(self):
        if not self.logged_in:
            return rx.redirect("/login")

    def logout(self):
        from state.cart_state import CartState
        from state.wishlist_state import WishlistState

        yield CartState.clear_cart_locally
        yield WishlistState.clear_wishlist_locally
        self.user_id = -1
        self.logged_in = False
        self.is_new_user = True
        self.firebase_uid = ""
        self.full_name = ""
        self.email = ""
        self.password = ""

    @rx.var
    def customer_display_name(self) -> str:
        if self.full_name.strip():
            return self.full_name.strip()
        return f"Customer: {self.email}" if self.email else "Customer: Guest"
