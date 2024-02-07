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
