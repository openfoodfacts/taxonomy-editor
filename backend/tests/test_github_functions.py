"""Test helpers used to create pull requests on github, without calling github"""

from editor.github_functions import MAX_PR_TITLE_LENGTH, GithubOperations
from editor.utils import summarize_modified_entries


def test_summarize_no_modified_entries():
    assert summarize_modified_entries({}) is None


def test_summarize_single_entry():
    # the parent gives the context of the change
    assert summarize_modified_entries({"en:french-wines": ["en:wines"]}) == "edits around en:wines"
    # no parent: use the entry itself
    assert summarize_modified_entries({"en:wines": []}) == "edits around en:wines"


def test_summarize_common_parent():
    modified_entries = {
        "en:french-wines": ["en:wines"],
        "en:italian-wines": ["en:wines", "en:italian-products"],
        # the parent itself may also be modified
        "en:wines": ["en:alcoholic-beverages"],
    }
    assert summarize_modified_entries(modified_entries) == "edits around en:wines"


def test_summarize_unrelated_entries():
    modified_entries = {"en:wines": [], "en:beers": ["en:alcoholic-beverages"], "en:ciders": []}
    assert summarize_modified_entries(modified_entries) == "en:beers, en:ciders, en:wines"
    modified_entries.update({"en:sakes": [], "en:meads": []})
    summary = summarize_modified_entries(modified_entries)
    assert summary == "en:beers, en:ciders, en:meads and 2 more"


def test_pr_title():
    github_object = GithubOperations("food_ingredients", "test_branch")
    # no summary: generic title
    assert github_object.get_pr_title() == "taxonomy: Update food_ingredients taxonomy"
    assert github_object.get_pr_title(None) == "taxonomy: Update food_ingredients taxonomy"
    assert (
        github_object.get_pr_title("edits around en:wines")
        == "taxonomy: food_ingredients - edits around en:wines"
    )
    # long titles are truncated
    title = github_object.get_pr_title("edits around en:" + "very-" * 30 + "long-entry")
    assert len(title) == MAX_PR_TITLE_LENGTH
    assert title.startswith("taxonomy: food_ingredients - edits around en:very-very-")
    assert title.endswith("...")
