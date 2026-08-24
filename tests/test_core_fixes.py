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
