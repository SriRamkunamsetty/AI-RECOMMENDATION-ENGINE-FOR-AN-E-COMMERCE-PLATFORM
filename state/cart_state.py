import reflex as rx
from typing import List, Dict, Any

from state.user_state import UserState

class CartState(UserState):
    """
    State for managing the shopping cart.
    Stores cart items and total price.
    """
    # List of products in cart
    cart_items: List[Dict[str, Any]] = []
    
    # Track the total price of all cart items
    total_price: float = 0.0
    
    def add_to_cart(self, product: Dict[str, Any]):
        """
        Add a product to cart or increment its quantity if it exists.
        Expects a dictionary with at least 'ProdID' and optionally 'Price'.
        """
        product_id = product.get('ProdID')
        
        item_exists = False
        for i, item in enumerate(self.cart_items):
            if item.get('ProdID') == product_id:
                # Increment quantity
                # We do this by creating a new dict and assigning it to trigger state update correctly in reflex
                new_item = item.copy()
                new_item['quantity'] = new_item.get('quantity', 1) + 1
                self.cart_items[i] = new_item
                item_exists = True
                break
                
        if not item_exists:
            new_item = product.copy()
            new_item['quantity'] = 1
            # Default price mock if missing
            if 'Price' not in new_item:
                new_item['Price'] = f"{(int(new_item.get('ProdID', 0)) % 2500) + 499}.00"
            self.cart_items.append(new_item)
            
        self.calculate_total()
        self.sync_to_firebase()
        
    def remove_from_cart(self, product_id: int):
        """
        Remove an item from the cart using its ProdID.
        """
        self.cart_items = [item for item in self.cart_items if item.get('ProdID') != product_id]
        self.calculate_total()
        self.sync_to_firebase()
        
    def calculate_total(self):
        """
        Iterate over the cart to recalculate total price.
        """
        total = sum(float(item.get('Price', 0)) * item.get('quantity', 1) for item in self.cart_items)
        self.total_price = round(total, 2)
        
    def clear_cart(self):
        """
        Empty the entire cart.
        """
        self.cart_items = []
        self.total_price = 0.0
        self.sync_to_firebase()
        
    def sync_to_firebase(self):
        """Pushes current cart state to Firebase."""
        if self.logged_in and self.firebase_uid:
            try:
                db = self._get_firebase().database()
                db.child("users").child(self.firebase_uid).child("cart").set(self.cart_items)
            except Exception as e:
                print("Firebase cart sync failed:", e)

    def load_from_firebase(self):
        """Loads cart state from Firebase."""
        if self.logged_in and self.firebase_uid:
            try:
                db = self._get_firebase().database()
                cart_data = db.child("users").child(self.firebase_uid).child("cart").get().val()
                if cart_data:
                    self.cart_items = [item for item in cart_data if item] # Filter out 'None' elements that firebase arrays might return
                    self.calculate_total()
            except Exception as e:
                print("Firebase cart load failed:", e)

    @rx.var
    def tax_amount(self) -> float:
        """Computed property for 18% GST."""
        return round(self.total_price * 0.18, 2)
        
    @rx.var
    def total_payable(self) -> float:
        """Computed property for Total including tax."""
        return round(self.total_price * 1.18, 2)

    @rx.var
    def direct_payment_url(self) -> str:
        """Computed property for the personal Razorpay payment link."""
        return "https://razorpay.me/@sanjaykrishnankarthikeyan"
