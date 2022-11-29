"""
Github helper functions for the Taxonomy Editor API
"""
from textwrap import dedent

from github import Github

from .settings import access_token, repo_owner  # Github settings


class GithubOperations:

    """Class for Github operations"""

    def __init__(self, taxonomy_name, branch_name):
        self.taxonomy_name = taxonomy_name
        self.branch_name = branch_name
        self.repo = self.init_driver_and_repo()

    def init_driver_and_repo(self):
        """
        Initalize connection to Github with an access token
        """
        github_driver = Github(access_token)
        repo = github_driver.get_repo(f"{repo_owner}/openfoodfacts-server")
        return repo

    def list_all_branches(self):
        """
        List of all current branches in the "openfoodfacts-server" repo
        """
        result = list(self.repo.get_branches())
        all_branches = [branch.name for branch in result]
        return all_branches

    def checkout_branch(self):
        """
        Create a new branch in the "openfoodfacts-server" repo
        """
        source_branch = self.repo.get_branch("main")
        self.repo.create_git_ref(ref="refs/heads/" + self.branch_name, sha=source_branch.commit.sha)

    def update_file(self, filename):
        """
        Update the taxonomy txt file edited by user using the Taxonomy Editor
        """
        # Find taxonomy text file to be updated
        github_filepath = f"taxonomies/{self.taxonomy_name}.txt"
        commit_message = f"Update {self.taxonomy_name}.txt"

        current_file = self.repo.get_contents(github_filepath)
        with open(filename, "r") as f:
            new_file_contents = f.read()

        # Update the file
        self.repo.update_file(
            github_filepath,
            commit_message,
            new_file_contents,
            current_file.sha,
            branch=self.branch_name,
        )

    def create_pr(self, description):
        """
        Create a pull request to "openfoodfacts-server" repo
        """
        title = f"taxonomy: Update {self.taxonomy_name} taxonomy"
        body = dedent(
            f"""
        ### What
        This is a pull request automatically created using the Taxonomy Editor.

        ### Description
        {description}
        """
        )
        return self.repo.create_pull(title=title, body=body, head=self.branch_name, base="main")
