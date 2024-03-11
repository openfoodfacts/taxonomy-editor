import logging
import os

log = logging.getLogger(__name__)


def file_cleanup(filepath):
    """
    Helper function to delete a taxonomy file from local storage
    """
    try:
        os.remove(filepath)
    except FileNotFoundError:
        log.warn(f"Taxonomy file {filepath} not found for deletion")


def taxonomy_path_in_repository(taxonomy_name):
    """Helper function to get the path of a taxonomy in the repository"""
    path = taxonomy_name
    # hacky for now until we restructure better
    if path in ("food_ingredients", "food_categories"):
        path = path.replace("_", "/")
    return f"taxonomies/{path}.txt"
