import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd

from backend.cleaning_data import clean_dataset
from backend.data_utils import CORRUPTED_ID, load_interactions, price_for_product
from backend.recommender import get_combined_recommendations
from state.cart_state import calculate_cart_totals
from state.orders_state import validate_shipping_details


class DataAndRecommendationTests(unittest.TestCase):
    def test_clean_dataset_removes_numeric_corrupted_ids(self):
        raw = pd.DataFrame(
            {
                "User's ID": [1, CORRUPTED_ID],
                "ProdID": [2, 3],
                "Rating": [5, 4],
                "Review Count": [1, 1],
                "Category": ["a", "b"],
                "Brand": ["x", "y"],
                "Name": ["one", "two"],
                "ImageURL": ["a | b", "c"],
                "Description": ["d", "e"],
                "Tags": ["a", "b"],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "raw.csv"
            target = Path(directory) / "clean.csv"
            raw.to_csv(source, index=False)
            cleaned = clean_dataset(source, target)
            self.assertEqual(len(cleaned), 1)
            self.assertFalse((cleaned["User's ID"] == CORRUPTED_ID).any())
            self.assertEqual(cleaned.iloc[0]["ImageURL"], "a")

    def test_catalog_loader_is_independent_of_working_directory(self):
        data = load_interactions()
        self.assertGreater(len(data), 0)
        self.assertNotIn(CORRUPTED_ID, data["ProdID"].values)
        self.assertNotIn(CORRUPTED_ID, data["User's ID"].values)

    def test_price_formula_is_canonical(self):
        self.assertEqual(price_for_product(2), 501.0)
        self.assertEqual(price_for_product(2500), 499.0)

    def test_recommendation_returns_dataframe_for_unknown_user(self):
        result = get_combined_recommendations(user_id=999999999, is_new_user=False, top_n=3)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class CartAndCheckoutTests(unittest.TestCase):
    def test_cart_line_totals_match_aggregate(self):
        items, subtotal = calculate_cart_totals(
            [
                {"ProdID": 2, "Price": "501.00", "quantity": 2},
                {"ProdID": 4, "Price": "503.00", "quantity": 1},
            ]
        )
        self.assertEqual(items[0]["line_total"], "1,002.00")
        self.assertEqual(subtotal, 1505.0)
        self.assertEqual(
            subtotal,
            sum(float(item["line_total"].replace(",", "")) for item in items),
        )

    def test_checkout_validation_rejects_missing_and_accepts_valid_data(self):
        error = validate_shipping_details("", "", "")
        self.assertIn("name", error.lower())
        self.assertEqual(
            validate_shipping_details("Test Customer", "9876543210", "1 Main Street"),
            "",
        )

    def test_search_query_can_be_encoded_as_a_query_parameter(self):
        query = "red & blue"
        url = "/?q=" + __import__("urllib.parse", fromlist=["quote_plus"]).quote_plus(query)
        self.assertEqual(parse_qs(urlparse(url).query)["q"], [query])


if __name__ == "__main__":
    unittest.main()


class SessionSafetyTests(unittest.TestCase):
    def test_local_only_clear_methods_do_not_sync(self):
        cart_source = (Path(__file__).parents[1] / "state" / "cart_state.py").read_text()
        wishlist_source = (Path(__file__).parents[1] / "state" / "wishlist_state.py").read_text()
        cart_local = cart_source.split("    def clear_cart_locally", 1)[1].split("    def clear_cart", 1)[0]
        wishlist_local = wishlist_source.split("    def clear_wishlist_locally", 1)[1].split("    def clear_wishlist", 1)[0]
        self.assertNotIn("sync_to_firebase", cart_local)
        self.assertNotIn("sync_to_firebase", wishlist_local)

    def test_logout_uses_local_only_clear_events(self):
        source = (Path(__file__).parents[1] / "state" / "user_state.py").read_text()
        self.assertIn("yield CartState.clear_cart_locally", source)
        self.assertIn("yield WishlistState.clear_wishlist_locally", source)
        self.assertNotIn("yield CartState.clear_cart\n", source)
        self.assertNotIn("yield WishlistState.clear_wishlist\\n", source)


class EntrypointParityTests(unittest.TestCase):
    def test_secondary_entrypoint_registers_catalog_and_payment_states(self):
        source = (
            Path(__file__).parents[1]
            / "AI_Enabled_Recommendation_Engine_for_an_E_commerce_Platform"
            / "AI_Enabled_Recommendation_Engine_for_an_E_commerce_Platform.py"
        ).read_text()
        self.assertIn("from state.products_state import ProductsState", source)
        self.assertIn("from state.payment_state import PaymentState", source)
