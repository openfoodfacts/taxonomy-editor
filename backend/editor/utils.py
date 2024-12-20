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


SPLIT_WITH_SLASH = {
    "food_ingredients",
    "food_categories",
    "beauty_categories",
    "beauty_labels",
    "product_categories",
    "product_labels",
}


def taxonomy_path_in_repository(taxonomy_name):
    """Helper function to get the path of a taxonomy in the repository"""
    path = taxonomy_name
    # hacky for now until we restructure better
    if path in SPLIT_WITH_SLASH:
        path = path.replace("_", "/")
    return f"taxonomies/{path}.txt"
