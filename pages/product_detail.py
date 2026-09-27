import reflex as rx
from components.navbar import navbar
from state.cart_state import CartState
from state.recommendation_state import RecommendationState
from components.product_card import product_card
from backend.data_utils import load_interactions, price_for_product


class ProductDetailState(rx.State):
    """Local state for product details; Reflex injects the dynamic ``pid`` argument."""
    current_product: dict = {
        "ProdID": 999, 
        "Brand": "Loading...", 
        "Category": "...", 
        "Price": "0.00", 
        "ImageURL": "/placeholder.jpg", 
        "Description": "Please wait while we fetch product details."
    }

    def load_product(self):
        try:
            if not self.pid:
                return
            target_id = int(self.pid)
            data = load_interactions()
            match = data[data["ProdID"] == target_id]
            if match.empty:
                raise LookupError(f"Product {target_id} was not found")

            item = match.iloc[0].fillna("").to_dict()
            image_url = str(item.get("ImageURL", "")).split(" | ")[0]
            item["ImageURL"] = image_url or "/placeholder.jpg"
            item["Price"] = f"{price_for_product(item['ProdID']):.2f}"
            try:
                item["Rating"] = f"{float(item.get('Rating', 0)):.1f}"
            except (TypeError, ValueError):
                item["Rating"] = "N/A"
            item["Description"] = item.get("Description") or "No detailed description available for this product."
            self.current_product = item
            return
        except (ValueError, LookupError, OSError, KeyError) as exc:
            print(f"Error loading product detail: {exc}")
            
        self.current_product = {
            "ProdID": 999, 
            "Brand": "Product Not Found", 
            "Category": "N/A", 
            "Price": "0.00", 
            "ImageURL": "/placeholder.jpg", 
            "Description": "Could not locate this product in the dataset."
        }

    bundle_items: list[dict] = []
    bundle_total_price: str = "0.00"

    def load_product_with_recommendations(self):
        """Loads product details, frequently bought together bundle, then recommendations."""
        self.load_product()
        product_id = self.current_product.get("ProdID")
        if product_id and product_id != 999:
            from backend.association_rules import get_frequently_bought_together
            from backend.data_utils import format_price, price_for_product
            associated = get_frequently_bought_together(int(product_id), top_n=1)
            self.bundle_items = associated
            if associated:
                total_val = price_for_product(int(product_id)) + float(associated[0]["Price_Num"])
                self.bundle_total_price = format_price(total_val)
            else:
                self.bundle_total_price = format_price(price_for_product(int(product_id)))
            yield RecommendationState.fetch_recommendations(int(product_id))

    def add_bundle_to_cart(self):
        """Add both current product and associated bundle complement to cart."""
        yield CartState.add_to_cart(self.current_product)
        for item in self.bundle_items:
            yield CartState.add_to_cart(item)

@rx.page(route="/product/[pid]", title="Product Detail", on_load=ProductDetailState.load_product_with_recommendations)
def product_detail() -> rx.Component:
    """Dynamic routing page for individual product inspection."""
    return rx.box(
        navbar(),
        rx.container(
            rx.hstack(
                rx.image(
                    src=ProductDetailState.current_product["ImageURL"], 
                    height="400px", 
                    width="400px", 
                    object_fit="cover", 
                    border_radius="xl",
                    shadow="lg",
                    fallback="https://via.placeholder.com/400"
                ),
                
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            ProductDetailState.current_product.contains("Product_Display_Name"),
                            ProductDetailState.current_product["Product_Display_Name"],
                            ProductDetailState.current_product["Brand"]
                        ), 
                        size="8"
                    ),
                    # Removing the keyword-filled category badge as per user request
                    rx.text(f"₹{ProductDetailState.current_product['Price']}", size="7", font_weight="bold", color="blue", margin_bottom="1rem"),
                    
                    rx.box(
                        rx.heading("Product Overview", size="4", margin_bottom="0.5rem", color="indigo"),
                        rx.divider(margin_bottom="1rem"),
                        rx.text(ProductDetailState.current_product["Description"], color="slate", size="4", line_height="1.6"),
                        margin_bottom="2rem",
                        width="100%"
                    ),
                    
                    rx.button(
                        rx.icon(tag="shopping-cart"),
                        " Add to Cart", 
                        size="4", 
                        color_scheme="orange", 
                        on_click=lambda: CartState.add_to_cart(ProductDetailState.current_product)
                    ),
                    rx.link(rx.button("Buy Now", size="4", color_scheme="green", variant="solid", margin_top="1rem"), href="/checkout"),
                    
                    align_items="start",
                    width="100%",
                    padding_left="3rem"
                ),
                width="100%",
                margin_top="5rem",
                align_items="start"
            ),
            
            rx.cond(
                ProductDetailState.bundle_items.length() > 0,
                rx.card(
                    rx.vstack(
                        rx.heading("🛒 Frequently Bought Together", size="5", color="#6F3E3F"),
                        rx.text("Customers who bought this item frequently purchased it together with:", size="2", color="gray"),
                        rx.hstack(
                            rx.hstack(
                                rx.image(src=ProductDetailState.current_product["ImageURL"], height="80px", width="80px", object_fit="cover", border_radius="md"),
                                rx.text("+", font_weight="bold", size="6", color="#6F3E3F", align_self="center"),
                                rx.foreach(
                                    ProductDetailState.bundle_items,
                                    lambda item: rx.hstack(
                                        rx.image(src=item["ImageURL"], height="80px", width="80px", object_fit="cover", border_radius="md"),
                                        rx.vstack(
                                            rx.link(rx.text(item["Name"], font_weight="bold", size="2", no_of_lines=1), href=f"/product/{item['ProdID']}"),
                                            rx.text("₹", item["Price"], color="#6F3E3F", font_weight="bold", size="2"),
                                            rx.badge(item["Explanation"], color_scheme="ruby", variant="soft", size="1"),
                                            align_items="start",
                                            spacing="1",
                                        ),
                                        spacing="3",
                                    )
                                ),
                                spacing="4",
                                align_items="center",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Bundle Total: ", size="3", color="gray"),
                                    rx.text("₹", ProductDetailState.bundle_total_price, font_weight="bold", size="5", color="#6F3E3F"),
                                ),
                                rx.button(
                                    rx.icon("package-plus", size=16),
                                    "Add Bundle to Cart",
                                    background_color="#6F3E3F",
                                    color="white",
                                    size="3",
                                    on_click=ProductDetailState.add_bundle_to_cart,
                                ),
                                align_items="end",
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    margin_top="3rem",
                    margin_bottom="1rem",
                    width="100%",
                ),
            ),

            rx.divider(margin_top="3rem", margin_bottom="2rem"),
            
            rx.vstack(
                rx.heading("You May Also Like", size="6", margin_bottom="1rem", text_align="center"),
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
                align_items="center",
                width="100%",
                padding_bottom="4rem"
            ),
            
            size="4"
        )
    )
