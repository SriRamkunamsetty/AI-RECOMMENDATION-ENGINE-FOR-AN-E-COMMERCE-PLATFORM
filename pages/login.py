import reflex as rx
from state.user_state import UserState
from components.navbar import navbar

@rx.page(route="/login", title="Log In")
def login() -> rx.Component:
    """Authentication login page simulated heavily for Reflex without active Firebase listeners."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Log In to Your Account", size="8", margin_bottom="1rem", color="#6F3E3F", font_family="Playfair Display"),
                rx.text("Access your personalized AI recommendations.", color="gray", margin_bottom="2rem"),
                
                rx.card(
                    rx.vstack(
                        rx.cond(
                            UserState.auth_error != "",
                            rx.text(UserState.auth_error, color="red", size="2", margin_bottom="1rem")
                        ),
                        
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger("Existing User", value="login", width="50%"),
                                rx.tabs.trigger("New User", value="signup", width="50%"),
                                width="100%",
                                margin_bottom="1.5rem"
                            ),
                            rx.tabs.content(
                                rx.vstack(
                                    rx.input(placeholder="Email Address", width="100%", size="3", on_change=UserState.set_email),
                                    rx.input(placeholder="Password", type="password", width="100%", size="3", margin_bottom="1rem", on_change=UserState.set_password),
                                    rx.button("LOGIN", on_click=UserState.login_with_firebase, width="100%", background_color="#6F3E3F", color="white", size="3"),
                                    width="100%"
                                ),
                                value="login"
                            ),
                            rx.tabs.content(
                                rx.vstack(
                                    rx.input(placeholder="Email Address", width="100%", size="3", on_change=UserState.set_email),
                                    rx.input(placeholder="Create Password", type="password", width="100%", size="3", margin_bottom="1rem", on_change=UserState.set_password),
                                    rx.button("REGISTER", on_click=UserState.signup_with_firebase, width="100%", background_color="#6F3E3F", color="white", size="3"),
                                    width="100%"
                                ),
                                value="signup"
                            ),
                            default_value="login",
                            width="100%"
                        ),
                        
                        rx.divider(margin_y="1rem"),
                        rx.button(
                            rx.icon("chrome", size=20, margin_right="0.5rem"),
                            "Sign in with Google", 
                            width="100%", 
                            variant="outline", 
                            color="#6F3E3F", 
                            size="3",
                            on_click=rx.window_alert("Google Sign-In requires Firebase JS SDK configuration across your domain.")
                        ),
                    ),
                    padding="3rem",
                    width="100%",
                    max_width="450px",
                    shadow="sm",
                    border_radius="2xl",
                    border="1px solid #E8DCD1",
                    background_color="#FFFFFF"
                ),
                
                padding_top="10vh",
                width="100%",
                align_items="center"
            ),
            size="4"
        ),
        background_color="#FDF8F5",
        min_height="100vh"
    )
