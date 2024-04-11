"""
Settings for Neo4J
"""
import os

uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
access_token = os.environ.get("GITHUB_PAT")
repo_uri = os.environ.get("REPO_URI", "openfoodfacts/openfoodfacts-server")
frontend_url = os.environ.get("FRONTEND_URL", "PLEASE_PROVIDE_FRONTEND_URL_ENV")

EXTERNAL_TAXONOMIES = {
    "food_ingredients": [
        "additives_classes",
        "additives",
        "minerals",
        "vitamins",
        "nucleotides",
        "other_nutritional_substances",
    ],
}
