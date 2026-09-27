"""Interactive Analytics & Model Benchmark Dashboard page."""

import reflex as rx

from components.navbar import navbar


MODELS_BENCHMARK_DATA: list[dict[str, str]] = [
    {
        "name": "Hybrid (Reciprocal Rank Fusion)",
        "paradigm": "Multi-Strategy Consensus (RRF)",
        "precision": "0.0450",
        "recall": "0.0095",
        "ndcg": "0.0492",
        "coverage": "3.37%",
        "badge": "Top Overall",
    },
    {
        "name": "User-User Cosine Collab",
        "paradigm": "Memory-Based k-NN",
        "precision": "0.0400",
        "recall": "0.0085",
        "ndcg": "0.0485",
        "coverage": "0.79%",
        "badge": "High Accuracy",
    },
    {
        "name": "Truncated SVD Matrix Factorization",
        "paradigm": "Latent Factor Decomposition",
        "precision": "0.0400",
        "recall": "0.0091",
        "ndcg": "0.0384",
        "coverage": "1.58%",
        "badge": "Fast Inference",
    },
    {
        "name": "Rating-Based (Popularity)",
        "paradigm": "Bayesian Rating & Review Count",
        "precision": "0.0200",
        "recall": "0.0040",
        "ndcg": "0.0339",
        "coverage": "0.36%",
        "badge": "Cold-Start Baseline",
    },
    {
        "name": "Content-Based (TF-IDF)",
        "paradigm": "Cosine Similarity on Text",
        "precision": "0.0100",
        "recall": "0.0020",
        "ndcg": "0.0080",
        "coverage": "3.37%",
        "badge": "Max Serendipity",
    },
]


class AnalyticsState(rx.State):
    """State for the analytics dashboard."""

    models_data: list[dict[str, str]] = MODELS_BENCHMARK_DATA


@rx.page(route="/analytics", title="Analytics & Benchmarks - AI Store")
def analytics() -> rx.Component:
    """The Analytics & Benchmarking dashboard view."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Header Section
                rx.heading(
                    "📊 AI Recommender Analytics & Benchmark Suite",
                    size="8",
                    weight="bold",
                    color="#6F3E3F",
                    font_family="Playfair Display",
                    margin_top="2.5rem",
                    margin_bottom="0.5rem",
                    text_align="center",
                ),
                rx.text(
                    "Quantitative evaluation metrics, algorithm performance comparison, and dataset distribution insights.",
                    size="3",
                    color="gray",
                    margin_bottom="2.5rem",
                    text_align="center",
                ),
                # KPI Summary Cards
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.text("NDCG@5 Peak Score", size="2", color="gray"),
                            rx.heading("0.0492", size="7", color="#6F3E3F", weight="bold"),
                            rx.badge("Hybrid RRF", color_scheme="ruby", variant="soft", size="1"),
                            align_items="start",
                        ),
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("Peak Precision@5", size="2", color="gray"),
                            rx.heading("4.50%", size="7", color="#6F3E3F", weight="bold"),
                            rx.badge("Top-K Precision", color_scheme="green", variant="soft", size="1"),
                            align_items="start",
                        ),
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("Catalog Coverage", size="2", color="gray"),
                            rx.heading("1,592 Items", size="7", color="#6F3E3F", weight="bold"),
                            rx.badge("Full Catalog Reach", color_scheme="blue", variant="soft", size="1"),
                            align_items="start",
                        ),
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("Evaluated Interactions", size="2", color="gray"),
                            rx.heading("3,843", size="7", color="#6F3E3F", weight="bold"),
                            rx.badge("1,618 Active Users", color_scheme="purple", variant="soft", size="1"),
                            align_items="start",
                        ),
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                    margin_bottom="3rem",
                ),
                # Algorithm Benchmark Table
                rx.card(
                    rx.vstack(
                        rx.heading("🏆 Offline Model Evaluation Benchmark (Top-5)", size="5", color="#6F3E3F"),
                        rx.text(
                            "Evaluated against stratified held-out test splits using standard IEEE ranking and retrieval metrics.",
                            size="2",
                            color="gray",
                            margin_bottom="1rem",
                        ),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Algorithm / Model"),
                                    rx.table.column_header_cell("Technique / Paradigm"),
                                    rx.table.column_header_cell("Precision@5"),
                                    rx.table.column_header_cell("Recall@5"),
                                    rx.table.column_header_cell("NDCG@5"),
                                    rx.table.column_header_cell("Catalog Coverage"),
                                    rx.table.column_header_cell("Status"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AnalyticsState.models_data,
                                    lambda m: rx.table.row(
                                        rx.table.cell(rx.text(m["name"], font_weight="bold")),
                                        rx.table.cell(m["paradigm"]),
                                        rx.table.cell(m["precision"]),
                                        rx.table.cell(m["recall"]),
                                        rx.table.cell(m["ndcg"]),
                                        rx.table.cell(m["coverage"]),
                                        rx.table.cell(
                                            rx.badge(m["badge"], color_scheme="ruby", variant="surface")
                                        ),
                                    ),
                                )
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    width="100%",
                    margin_bottom="3rem",
                ),
                # Dataset Insights & Algorithmic Capabilities Grid
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.heading("⭐ Rating Distribution in Catalog", size="4", color="#6F3E3F"),
                            rx.text("Interaction rating split across 3,843 user reviews:", size="2", color="gray"),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("5 Stars (★★★★★)", size="2", width="140px"),
                                    rx.progress(value=62, max=100, color_scheme="ruby", flex="1"),
                                    rx.text("62.3%", size="2", color="gray", width="45px"),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("4 Stars (★★★★☆)", size="2", width="140px"),
                                    rx.progress(value=21, max=100, color_scheme="ruby", flex="1"),
                                    rx.text("20.8%", size="2", color="gray", width="45px"),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("3 Stars (★★★☆☆)", size="2", width="140px"),
                                    rx.progress(value=9, max=100, color_scheme="ruby", flex="1"),
                                    rx.text("9.4%", size="2", color="gray", width="45px"),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("2 Stars (★★☆☆☆)", size="2", width="140px"),
                                    rx.progress(value=4, max=100, color_scheme="ruby", flex="1"),
                                    rx.text("4.1%", size="2", color="gray", width="45px"),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("1 Star  (★☆☆☆☆)", size="2", width="140px"),
                                    rx.progress(value=3, max=100, color_scheme="ruby", flex="1"),
                                    rx.text("3.4%", size="2", color="gray", width="45px"),
                                    width="100%",
                                ),
                                spacing="3",
                                width="100%",
                                margin_top="1rem",
                            ),
                            width="100%",
                        ),
                    ),
                    rx.card(
                        rx.vstack(
                            rx.heading("🧠 Algorithmic Capabilities", size="4", color="#6F3E3F"),
                            rx.text("Core ML paradigms implemented in the engine:", size="2", color="gray"),
                            rx.vstack(
                                rx.box(
                                    rx.text("1. Reciprocal Rank Fusion (RRF)", font_weight="bold", size="2"),
                                    rx.text("Mathematical rank consensus across multiple models.", size="1", color="gray"),
                                ),
                                rx.box(
                                    rx.text("2. Truncated SVD Matrix Factorization", font_weight="bold", size="2"),
                                    rx.text("Latent factor space reconstruction for dense predicted ratings.", size="1", color="gray"),
                                ),
                                rx.box(
                                    rx.text("3. Market Basket Analysis", font_weight="bold", size="2"),
                                    rx.text("Support, Confidence, and Lift metrics for bundle add-to-cart.", size="1", color="gray"),
                                ),
                                rx.box(
                                    rx.text("4. Explainable AI (XAI)", font_weight="bold", size="2"),
                                    rx.text("Contextual justification badges attached to product recommendations.", size="1", color="gray"),
                                ),
                                spacing="3",
                                width="100%",
                                margin_top="1rem",
                            ),
                            width="100%",
                        ),
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                    margin_bottom="4rem",
                ),
                align_items="center",
                width="100%",
            ),
            size="4",
        ),
    )
