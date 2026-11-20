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


def summarize_modified_entries(modified_entries: dict[str, list[str]]) -> str | None:
    """Helper function to summarize modified entries, to name a pull request

    :param modified_entries: parents ids of each modified entry, by entry id
    :return: None if there is nothing to summarize
    """
    if not modified_entries:
        return None
    # an entry is common to all changes if each modified entry is this entry or one of its children
    common = set.intersection(
        *({entry_id, *parents} for entry_id, parents in modified_entries.items())
    )
    if common:
        all_parents = {parent for parents in modified_entries.values() for parent in parents}
        # prefer a parent, as a single modified entry is also common to all changes
        return f"edits around {min(common & all_parents or common)}"
    entries_ids = sorted(modified_entries)
    summary = ", ".join(entries_ids[:3])
    if len(entries_ids) > 3:
        summary += f" and {len(entries_ids) - 3} more"
    return summary
