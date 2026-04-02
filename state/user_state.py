import reflex as rx
import pandas as pd
import os
from dotenv import load_dotenv
from config import DATA_PATH

load_dotenv()


class UserState(rx.State):
    """
    State managing the user's session.
    Stores user_id, logged_in status, and user_type.
    """
    user_id: int = -1
    logged_in: bool = False
    is_new_user: bool = True
    firebase_uid: str = ""
    
    email: str = ""
    password: str = ""
    auth_error: str = ""
    
    def _get_firebase(self):
        from pyrebase import initialize_app
        firebase_config = {
            "apiKey": os.getenv("FIREBASE_API_KEY", "placeholder"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "placeholder"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID", "placeholder"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "placeholder"),
            "messagingSenderId": os.getenv("FIREBASE_SENDER_ID", "placeholder"),
            "appId": os.getenv("FIREBASE_APP_ID", "placeholder"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "")
        }
        return initialize_app(firebase_config)

    def signup_with_firebase(self):
        """Register a new user with Firebase using email/password."""
        if not self.email or not self.password:
            self.auth_error = "Please enter both email and password."
            return
            
        try:
            firebase = self._get_firebase()
            auth = firebase.auth()
            
            user = auth.create_user_with_email_and_password(self.email, self.password)
            yield from self._handle_successful_login(user['localId'])
            yield rx.redirect("/")
        except Exception as e:
            # Simple error parsing for UI
            self.auth_error = "Registration failed. " + str(e)
            
    def login_with_firebase(self):
        """Login an existing user with Firebase."""
        if not self.email or not self.password:
            self.auth_error = "Please enter both email and password."
            return
            
        try:
            firebase = self._get_firebase()
            auth = firebase.auth()
            
            user = auth.sign_in_with_email_and_password(self.email, self.password)
            yield from self._handle_successful_login(user['localId'])
            yield rx.redirect("/")
        except Exception as e:
            self.auth_error = "Login failed. Please check credentials."

    def _handle_successful_login(self, uid: str):
        """Common logic upon successful authentication."""
        self.firebase_uid = uid
        self.logged_in = True
        self.auth_error = ""
        
        # Real-world mapping logic: (Mocking map to 1705 like before)
        mapped_numeric_id = 1705  
        self.user_id = mapped_numeric_id
        
        # Load user data from Firebase asynchronously
        from state.cart_state import CartState
        from state.products_state import ProductsState
        yield CartState.load_from_firebase
        yield ProductsState.load_search_from_firebase
        
        # Check if user exists in the dataset
        try:
            if os.path.exists(DATA_PATH):
                data = pd.read_csv(DATA_PATH, usecols=["User's ID"])
                if self.user_id in data["User's ID"].values:
                    self.is_new_user = False
                else:
                    self.is_new_user = True
            else:
                self.is_new_user = True
        except Exception as e:
            self.is_new_user = True
            
    def check_login(self):
        """Redirect to login if not authenticated."""
        if not self.logged_in:
            return rx.redirect("/login")

    def logout(self):
        """Reset state on logout."""
        self.user_id = -1
        self.logged_in = False
        self.is_new_user = True
        self.firebase_uid = ""

    @rx.var
    def customer_display_name(self) -> str:
        """Computed property for customer identity."""
        return f"Customer: {self.email}" if self.email else "Customer: Guest"
