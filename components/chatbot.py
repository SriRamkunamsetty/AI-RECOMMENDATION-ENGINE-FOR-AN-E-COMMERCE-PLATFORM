"""Groq-powered shopping assistant with grounded catalog context."""

import os

import reflex as rx

from backend.data_utils import canonical_products, load_interactions, price_for_product


def _relevant_products_context(user_query: str = "", top_n: int = 8) -> str:
    """Return catalog context relevant to the user query, with safe fallback."""
    try:
        data = load_interactions()
        products = canonical_products(data)
        products["Price_Num"] = products["ProdID"].map(price_for_product)
        query = str(user_query or "").strip()
        if query:
            mask = False
            for column in ("Brand", "Category", "Description", "Name", "Tags"):
                if column in products.columns:
                    mask = mask | products[column].str.contains(
                        query, case=False, na=False, regex=False
                    )
            filtered = products[mask]
            if not filtered.empty:
                products = filtered
        products = products.sort_values(["Rating", "Price_Num"], ascending=[False, True]).head(top_n)
        if products.empty:
            return "No matching products were found in the catalog."

        lines = []
        for _, row in products.iterrows():
            name = str(row.get("Product_Display_Name", "Product"))[:80]
            lines.append(
                f"ProdID: {int(row['ProdID'])} | Name: {name} | "
                f"Brand: {row.get('Brand', '')} | Price: ₹{price_for_product(row['ProdID']):,.2f} | "
                f"Rating: {float(row.get('Rating', 0)):.1f}"
            )
        return "Relevant products in our dataset:\n" + "\n".join(lines)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Unable to load chatbot catalog context: {exc}")
        return "Catalog context is temporarily unavailable. Do not invent product details or prices."


class ChatState(rx.State):
    is_open: bool = False
    messages: list[dict[str, str]] = [
        {
            "role": "assistant",
            "content": "Hi! I'm your AI shopping assistant. Ask me about products or recommendations!",
        }
    ]
    current_input: str = ""

    def set_current_input(self, value: str):
        self.current_input = value

    def toggle_chat(self):
        self.is_open = not self.is_open

    def send_message(self):
        if not self.current_input.strip():
            return
        user_text = self.current_input.strip()
        self.messages.append({"role": "user", "content": user_text})
        self.current_input = ""
        yield

        target_key = os.getenv("GROQ_API_KEY", "")
        if not target_key:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": "The AI assistant is not configured. Set GROQ_API_KEY before using it.",
                }
            )
            return

        try:
            import groq

            client = groq.Groq(api_key=target_key)
            system_prompt = (
                "You are a helpful AI shopping assistant for an Indian e-commerce store. "
                "Use Indian Rupees for prices, do not invent catalog facts, and include "
                "Markdown links in the form [View Product](/product/PROD_ID) when listing products. "
                "Keep responses concise.\n\n"
                + _relevant_products_context(user_text)
            )
            completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}] + self.messages,
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            )
            self.messages.append(
                {"role": "assistant", "content": completion.choices[0].message.content}
            )
        except Exception as exc:
            print(f"Groq request failed: {exc}")
            self.messages.append(
                {"role": "assistant", "content": "The AI assistant is temporarily unavailable."}
            )


def chatbot() -> rx.Component:
    """Floating AI assistant for the e-commerce app."""
    return rx.box(
        rx.cond(
            ChatState.is_open,
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="bot", color="blue"),
                        rx.heading("AI Assistant", size="4"),
                        rx.spacer(),
                        rx.button(rx.icon("x"), size="1", variant="ghost", on_click=ChatState.toggle_chat),
                        width="100%",
                        border_bottom="1px solid #eaeaea",
                        padding_bottom="0.5rem",
                    ),
                    rx.vstack(
                        rx.foreach(
                            ChatState.messages,
                            lambda message: rx.box(
                                rx.markdown(message["content"]),
                                background_color=rx.cond(
                                    message["role"] == "user", "blue.100", "gray.100"
                                ),
                                padding="0.75rem",
                                border_radius="lg",
                                max_width="85%",
                            ),
                        ),
                        width="100%",
                        height="380px",
                        overflow_y="auto",
                        padding_y="1rem",
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Ask about products...",
                            value=ChatState.current_input,
                            on_change=ChatState.set_current_input,
                            width="100%",
                        ),
                        rx.button(rx.icon("send"), on_click=ChatState.send_message, color_scheme="blue"),
                        width="100%",
                    ),
                    width="100%",
                ),
                position="fixed",
                bottom="5rem",
                right="2rem",
                width="390px",
                z_index="2000",
            ),
        ),
        rx.button(
            rx.icon(tag="message-circle", size=24),
            position="fixed",
            bottom="2rem",
            right="2rem",
            size="4",
            border_radius="full",
            color_scheme="indigo",
            on_click=ChatState.toggle_chat,
            z_index="2000",
        ),
    )
