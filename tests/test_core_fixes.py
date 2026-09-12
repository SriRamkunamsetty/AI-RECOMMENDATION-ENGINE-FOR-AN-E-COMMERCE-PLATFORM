import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd

from backend.cleaning_data import clean_dataset
from backend.collaborative_filtering import (
    get_collaborative_recommendations,
    get_svd_collaborative_recommendations,
)
from backend.content_filtering import clear_tfidf_cache, get_content_based_recommendations
from backend.data_utils import (
    CORRUPTED_ID,
    canonical_products,
    clear_data_cache,
    load_interactions,
    price_for_product,
)
from backend.evaluation import (
    compute_catalog_coverage,
    compute_hit_rate_at_k,
    compute_map_at_k,
    compute_mrr,
    compute_ndcg_at_k,
    compute_precision_recall_at_k,
    compute_rmse_mae,
    evaluate_model,
    train_test_split_interactions,
)
from backend.rating_based import get_rating_based_recommendations
from backend.recommender import get_combined_recommendations
from state.cart_state import calculate_cart_totals
from state.orders_state import validate_shipping_details
from state.user_state import UserState


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
        result = get_combined_recommendations(
            user_id=999999999, is_new_user=False, top_n=3, fallback_on_empty=False
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    def test_recommendation_falls_back_to_rating_based_for_unknown_user(self):
        result = get_combined_recommendations(
            user_id=999999999, is_new_user=False, top_n=3, fallback_on_empty=True
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)

    def test_canonical_products_handles_missing_optional_metadata(self):
        products = canonical_products(pd.DataFrame({"ProdID": [1, 1], "Name": ["Example", "Example"]}))
        self.assertEqual(products.loc[0, "ImageURL"], "")
        self.assertTrue(pd.isna(products.loc[0, "Rating"]))


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

    def test_cart_handles_prices_above_one_thousand_with_commas(self):
        items, subtotal = calculate_cart_totals(
            [
                {"ProdID": 1500, "Price": "1,500.00", "quantity": 2},
                {"ProdID": 2000, "Price": "2,499.00", "quantity": 1},
            ]
        )
        self.assertEqual(items[0]["line_total"], "3,000.00")
        self.assertEqual(items[1]["line_total"], "2,499.00")
        self.assertEqual(subtotal, 5499.0)

    def test_search_query_can_be_encoded_as_a_query_parameter(self):
        query = "red & blue"
        url = "/?q=" + __import__("urllib.parse", fromlist=["quote_plus"]).quote_plus(query)
        self.assertEqual(parse_qs(urlparse(url).query)["q"], [query])


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


class SearchSessionTests(unittest.TestCase):
    def test_search_history_loader_resets_before_restore(self):
        source = (Path(__file__).parents[1] / "state" / "products_state.py").read_text()
        method = source.split("    def load_search_from_firebase", 1)[1].split("    def ", 1)[0]
        self.assertLess(method.index('self.search_query = ""'), method.index("if self.logged_in"))


class SearchTagTests(unittest.TestCase):
    def test_search_columns_include_tags(self):
        source = (Path(__file__).parents[1] / "state" / "products_state.py").read_text()
        self.assertIn('"Tags"', source)


class PerformanceAndCachingTests(unittest.TestCase):
    def test_interactions_cache_and_clear(self):
        clear_data_cache()
        data1 = load_interactions()
        data2 = load_interactions()
        self.assertTrue(data1.equals(data2))
        clear_data_cache()
        data3 = load_interactions(use_cache=False)
        self.assertEqual(len(data1), len(data3))

    def test_tfidf_cache_and_clear(self):
        clear_tfidf_cache()
        rec1 = get_content_based_recommendations(product_id=2, top_n=3)
        rec2 = get_content_based_recommendations(product_id=2, top_n=3)
        self.assertEqual(len(rec1), len(rec2))
        clear_tfidf_cache()


class SVDCollaborativeFilteringTests(unittest.TestCase):
    def test_svd_recommendations_for_existing_user(self):
        result = get_svd_collaborative_recommendations(user_id=1705, top_n=4)
        self.assertIsInstance(result, pd.DataFrame)
        if not result.empty:
            self.assertIn("ProdID", result.columns)
            self.assertIn("Predicted Rating", result.columns)
            self.assertIn("Price", result.columns)

    def test_recommender_integrates_svd_flag(self):
        result = get_combined_recommendations(user_id=1705, top_n=4, use_svd=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)


class UIAndAuthSafetyTests(unittest.TestCase):
    def test_login_page_has_no_duplicate_inputs_outside_tabs(self):
        login_source = (Path(__file__).parents[1] / "pages" / "login.py").read_text()
        self.assertNotIn('placeholder="name@example.com"', login_source.split("rx.tabs.root(")[0])

    def test_profile_page_includes_navbar(self):
        profile_source = (Path(__file__).parents[1] / "pages" / "profile.py").read_text()
        self.assertIn("navbar()", profile_source)

    def test_firebase_configured_helper(self):
        # When unconfigured or dummy, returns boolean without crashing or instantiating state
        is_conf = UserState._is_firebase_configured()
        self.assertIsInstance(is_conf, bool)


class EvaluationSuiteTests(unittest.TestCase):
    def test_train_test_split_interactions(self):
        data = load_interactions()
        train_df, test_df = train_test_split_interactions(
            data, test_ratio=0.2, min_interactions=2, random_state=42
        )
        self.assertGreater(len(train_df), 0)
        self.assertGreater(len(test_df), 0)
        self.assertEqual(len(train_df) + len(test_df), len(data))
        # Users in test must have interactions remaining in train
        train_users = set(train_df["User's ID"].unique())
        test_users = set(test_df["User's ID"].unique())
        self.assertTrue(test_users.issubset(train_users))

    def test_metric_calculations(self):
        # NDCG@5
        ndcg_hit = compute_ndcg_at_k(actual=[1, 2], predicted=[1, 3, 2, 4, 5], k=5)
        ndcg_miss = compute_ndcg_at_k(actual=[9], predicted=[1, 2, 3], k=5)
        self.assertGreater(ndcg_hit, 0.0)
        self.assertLessEqual(ndcg_hit, 1.0)
        self.assertEqual(ndcg_miss, 0.0)

        # Precision and Recall
        prec, rec = compute_precision_recall_at_k(actual=[1, 2], predicted=[1, 3, 4, 5, 6], k=5)
        self.assertAlmostEqual(prec, 0.2)
        self.assertAlmostEqual(rec, 0.5)

        # Hit Rate
        self.assertEqual(compute_hit_rate_at_k(actual=[1], predicted=[1, 2, 3], k=3), 1.0)
        self.assertEqual(compute_hit_rate_at_k(actual=[99], predicted=[1, 2, 3], k=3), 0.0)

        # MRR
        self.assertAlmostEqual(compute_mrr(actual=[3], predicted=[1, 2, 3, 4]), 1.0 / 3.0)

        # MAP
        map_val = compute_map_at_k(actual=[1, 3], predicted=[1, 2, 3, 4], k=4)
        self.assertGreater(map_val, 0.0)

        # RMSE and MAE
        rmse, mae = compute_rmse_mae(actual=[4.0, 5.0], predicted=[3.0, 5.0])
        self.assertAlmostEqual(rmse, (0.5 ** 0.5))
        self.assertAlmostEqual(mae, 0.5)

        # Catalog Coverage
        coverage = compute_catalog_coverage([[1, 2], [2, 3]], total_catalog_count=10)
        self.assertAlmostEqual(coverage, 0.3)

    def test_evaluate_single_model(self):
        train_data = pd.DataFrame({
            "User's ID": [1, 1, 2, 2],
            "ProdID": [10, 20, 10, 30],
            "Rating": [5, 4, 3, 5],
        })
        test_data = pd.DataFrame({
            "User's ID": [1, 2],
            "ProdID": [20, 30],
            "Rating": [4, 5],
        })
        metrics = evaluate_model(
            recommend_func=lambda uid, k, df: [10, 20, 30][:k],
            test_data=test_data,
            train_data=train_data,
            k=2,
        )
        self.assertIn("NDCG@2", metrics)
        self.assertIn("Precision@2", metrics)
        self.assertIn("Catalog_Coverage", metrics)
        self.assertGreater(metrics["Hit_Rate@2"], 0.0)


class ExplainableAITests(unittest.TestCase):
    def test_recommenders_produce_explanations(self):
        # Combined recommender
        rec_combined = get_combined_recommendations(user_id=1705, top_n=3, use_svd=True)
        self.assertIn("Explanation", rec_combined.columns)
        self.assertTrue((rec_combined["Explanation"].str.len() > 0).all())

        # Rating-based recommender
        rec_rating = get_rating_based_recommendations(top_n=3)
        self.assertIn("Explanation", rec_rating.columns)
        self.assertEqual(rec_rating.iloc[0]["Explanation"], "Top-rated trending bestseller")

        # Collaborative recommender
        rec_collab = get_collaborative_recommendations(user_id=1705, top_n=3)
        if not rec_collab.empty:
            self.assertIn("Explanation", rec_collab.columns)

        # SVD recommender
        rec_svd = get_svd_collaborative_recommendations(user_id=1705, top_n=3)
        if not rec_svd.empty:
            self.assertIn("Explanation", rec_svd.columns)

        # Content recommender
        rec_content = get_content_based_recommendations(product_id=2, top_n=3)
        if not rec_content.empty:
            self.assertIn("Explanation", rec_content.columns)

    def test_product_card_renders_explanation_badge(self):
        source = (Path(__file__).parents[1] / "components" / "product_card.py").read_text()
        self.assertIn('"Explanation"', source)
        self.assertIn('"sparkles"', source)


if __name__ == "__main__":
    unittest.main()
