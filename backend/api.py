"""Standalone REST API Microservice for the AI Recommendation Engine.

Exposes RESTful endpoints for real-time recommendations, content similarity,
market basket complementary bundles, model benchmarks, and OpenAPI / Swagger documentation.
"""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from backend.association_rules import get_frequently_bought_together
from backend.content_filtering import get_content_based_recommendations
from backend.evaluation import benchmark_all_models
from backend.recommender import get_combined_recommendations


async def health_endpoint(request: Request) -> JSONResponse:
    """Service health and readiness check."""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "AI-Recommendation-Engine-Microservice",
            "version": "1.0.0",
            "endpoints": [
                "/api/v1/recommend",
                "/api/v1/similar/{product_id}",
                "/api/v1/basket/{product_id}",
                "/api/v1/benchmark",
                "/docs",
            ],
        }
    )


async def recommend_endpoint(request: Request) -> JSONResponse:
    """Generate multi-strategy recommendations for a given user.

    JSON payload:
        {
            "user_id": int | null,
            "top_n": int (default: 5),
            "use_svd": bool (default: true),
            "use_rrf": bool (default: true),
            "current_product_id": int | null,
            "search_query": str | null
        }
    """
    try:
        body = await request.json() if request.method == "POST" else {}
    except Exception:
        body = {}

    user_id = body.get("user_id")
    top_n = int(body.get("top_n", 5))
    use_svd = bool(body.get("use_svd", True))
    use_rrf = bool(body.get("use_rrf", True))
    current_product_id = body.get("current_product_id")
    search_query = body.get("search_query")

    recs_df = get_combined_recommendations(
        user_id=int(user_id) if user_id is not None else None,
        top_n=top_n,
        use_svd=use_svd,
        use_rrf=use_rrf,
        current_product_id=int(current_product_id) if current_product_id is not None else None,
        search_query=str(search_query) if search_query else None,
    )

    items = recs_df.to_dict("records") if not recs_df.empty else []
    return JSONResponse(
        {
            "user_id": user_id,
            "count": len(items),
            "strategy": "Reciprocal Rank Fusion" if use_rrf else "Concatenation",
            "recommendations": items,
        }
    )


async def similar_endpoint(request: Request) -> JSONResponse:
    """Return content-similar products for a specified product ID."""
    product_id = int(request.path_params["product_id"])
    top_n = int(request.query_params.get("top_n", 5))

    recs_df = get_content_based_recommendations(product_id=product_id, top_n=top_n)
    items = recs_df.to_dict("records") if not recs_df.empty else []
    return JSONResponse(
        {
            "product_id": product_id,
            "count": len(items),
            "similar_products": items,
        }
    )


async def basket_endpoint(request: Request) -> JSONResponse:
    """Return complementary 'Frequently Bought Together' products mined via association rules."""
    product_id = int(request.path_params["product_id"])
    top_n = int(request.query_params.get("top_n", 2))

    bundle = get_frequently_bought_together(product_id=product_id, top_n=top_n)
    return JSONResponse(
        {
            "target_product_id": product_id,
            "bundle_size": len(bundle),
            "frequently_bought_together": bundle,
        }
    )


async def benchmark_endpoint(request: Request) -> JSONResponse:
    """Return live evaluation metrics across all 6 recommendation algorithms."""
    users = int(request.query_params.get("users", 20))
    k = int(request.query_params.get("k", 5))

    df_results = benchmark_all_models(k=k, max_test_users=users)
    return JSONResponse(
        {
            "metric_k": k,
            "evaluated_users": users,
            "benchmark_results": df_results.round(4).to_dict("index"),
        }
    )


async def swagger_ui(request: Request) -> HTMLResponse:
    """Interactive Swagger / OpenAPI documentation UI."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Recommendation Engine API - Swagger UI</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            const spec = {
                openapi: "3.0.0",
                info: {
                    title: "AI Recommendation Engine API",
                    version: "1.0.0",
                    description: "RESTful microservice for E-Commerce Recommendation, Similarity, and Association Rules."
                },
                paths: {
                    "/api/v1/health": {
                        get: { summary: "Check service health", responses: { 200: { description: "Healthy" } } }
                    },
                    "/api/v1/recommend": {
                        post: {
                            summary: "Get combined recommendations with RRF and SVD",
                            requestBody: {
                                content: {
                                    "application/json": {
                                        schema: {
                                            type: "object",
                                            properties: {
                                                user_id: { type: "integer", example: 1705 },
                                                top_n: { type: "integer", example: 5 },
                                                use_svd: { type: "boolean", example: true },
                                                use_rrf: { type: "boolean", example: true }
                                            }
                                        }
                                    }
                                }
                            },
                            responses: { 200: { description: "Recommendations list" } }
                        }
                    },
                    "/api/v1/similar/{product_id}": {
                        get: {
                            summary: "Get TF-IDF content-similar products",
                            parameters: [{ name: "product_id", in: "path", required: true, schema: { type: "integer" } }],
                            responses: { 200: { description: "Similar products" } }
                        }
                    },
                    "/api/v1/basket/{product_id}": {
                        get: {
                            summary: "Get Frequently Bought Together bundle",
                            parameters: [{ name: "product_id", in: "path", required: true, schema: { type: "integer" } }],
                            responses: { 200: { description: "Bundle complements" } }
                        }
                    },
                    "/api/v1/benchmark": {
                        get: {
                            summary: "Get live algorithm benchmark comparison metrics",
                            responses: { 200: { description: "Model comparison matrix" } }
                        }
                    }
                }
            };
            SwaggerUIBundle({
                spec: spec,
                dom_id: '#swagger-ui',
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html_content)


routes = [
    Route("/api/v1/health", health_endpoint, methods=["GET"]),
    Route("/api/v1/recommend", recommend_endpoint, methods=["POST", "GET"]),
    Route("/api/v1/similar/{product_id:int}", similar_endpoint, methods=["GET"]),
    Route("/api/v1/basket/{product_id:int}", basket_endpoint, methods=["GET"]),
    Route("/api/v1/benchmark", benchmark_endpoint, methods=["GET"]),
    Route("/docs", swagger_ui, methods=["GET"]),
    Route("/api/v1/docs", swagger_ui, methods=["GET"]),
]

api_app = Starlette(debug=True, routes=routes)


if __name__ == "__main__":
    import granian

    print("Starting AI Recommendation Engine API on port 8000...")
    print("Swagger docs available at http://127.0.0.1:8000/docs")
    granian.Granian("backend.api:api_app", address="127.0.0.1", port=8000).serve()
