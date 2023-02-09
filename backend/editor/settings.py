"""
Settings for Neo4J
"""
import os

uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
access_token = "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"
repo_uri = os.environ.get("REPO_URI", "openfoodfacts/openfoodfacts-server")
