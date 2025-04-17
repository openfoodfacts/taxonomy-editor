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
    "beauty_ingredients",
    "beauty_labels",
    "beauty_abbreviations",
    "beauty_allergens",
    "beauty_body_parts",
    "beauty_brands",
    "beauty_eu_lists",
    "beauty_inci_functions",
    "beauty_safety",
    "beauty_special_ingredients",
    "beauty_warnings",
    "product_categories",
    "product_labels",
    "petfood_ingredients",
    "petfood_categories",
}


def taxonomy_path_in_repository(taxonomy_name):
    """Helper function to get the path of a taxonomy in the repository"""
    path = taxonomy_name
    # hacky for now until we restructure better
    if path in SPLIT_WITH_SLASH:
        path = path.replace("_", "/")
    return f"taxonomies/{path}.txt"
