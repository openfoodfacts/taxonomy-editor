"""
Settings for Neo4J
"""
import os

uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
access_token = os.environ.get("GITHUB_PAT", "<Add personal access token here>")
repo_owner = os.environ.get("REPO_OWNER", "openfoodfacts")
