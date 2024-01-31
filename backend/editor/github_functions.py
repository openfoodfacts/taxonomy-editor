"""
Github helper functions for the Taxonomy Editor API
"""
import base64
from textwrap import dedent

from fastapi import HTTPException
from githubkit import GitHub
from githubkit.exception import RequestFailed
from githubkit.versions.latest.models import BranchWithProtection, ContentFile, PullRequest

from . import settings


class GithubOperations:

    """Class for Github operations"""

    def __init__(self, taxonomy_name: str, branch_name: str):
        self.taxonomy_name = taxonomy_name
        self.branch_name = branch_name
        self.repo_info = self.get_repo_info()
        self.connection = self.init_connection()

    def get_repo_info(self) -> tuple[str, str]:
        repo_uri = settings.repo_uri
        if not repo_uri:
            raise HTTPException(
                status_code=400, detail="repo_uri is not set. Please add your access token in .env"
            )
        repo_owner, repo_name = repo_uri.split("/")
        return repo_owner, repo_name

    def init_connection(self) -> GitHub:
        """
        Initalize connection to Github with an access token
        """
        access_token = settings.access_token
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Access token is not set. Please add your access token in .env",
            )
        repo_uri = settings.repo_uri
        if not repo_uri:
            raise HTTPException(
                status_code=400, detail="repo_uri is not set. Please add your access token in .env"
            )
        github = GitHub(access_token)
        return github

    async def get_branch(self, branch_name: str) -> BranchWithProtection | None:
        """
        Get a branch in the "openfoodfacts-server" repo
        """
        try:
            result = await self.connection.rest.repos.async_get_branch(
                *self.repo_info, branch=branch_name
            )
        except RequestFailed as e:
            if e.response.status_code == 404:
                return None
            raise e
        return result.parsed_data

    async def get_file_sha(self) -> str:
        """
        Get the contents of a file in the "openfoodfacts-server" repo
        """
        github_filepath = f"taxonomies/{self.taxonomy_name}.txt"
        file_contents: ContentFile = (
            await self.connection.rest.repos.async_get_content(
                *self.repo_info, path=github_filepath
            )
        ).parsed_data

        return file_contents.sha

    async def checkout_branch(self, commit_sha: str) -> None:
        """
        Create a new branch in the "openfoodfacts-server" repo from a given sha
        """
        await self.connection.rest.git.async_create_ref(
            *self.repo_info, ref="refs/heads/" + self.branch_name, sha=commit_sha
        )

    async def update_file(self, filename: str, file_sha: str) -> None:
        """
        Update the taxonomy txt file edited by user using the Taxonomy Editor
        """
        # Find taxonomy text file to be updated
        github_filepath = f"taxonomies/{self.taxonomy_name}.txt"
        commit_message = f"Update {self.taxonomy_name}.txt"
        try:
            with open(filename, "r") as f:
                new_file_contents = f.read()
            # Update the file
            (
                await self.connection.rest.repos.async_create_or_update_file_contents(
                    *self.repo_info,
                    path=github_filepath,
                    message=commit_message,
                    content=base64.b64encode(new_file_contents.encode("utf-8")),
                    sha=file_sha,
                    branch=self.branch_name,
                )
            ).parsed_data
        except RequestFailed as e:
            # Handle GitHub API-related exceptions: result.parsed_data raises a ValidationError
            # if the response is not valid
            raise Exception(f"GitHub API error: {e}") from e
        except FileNotFoundError as e:
            # Handle file not found error (e.g., when 'filename' does not exist)
            raise Exception(f"File not found: {filename}") from e
        except Exception as e:
            # Handle any other unexpected exceptions
            raise Exception(f"An error occurred: {e}") from e

    async def create_pr(self, description) -> PullRequest:
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
        return (
            await self.connection.rest.pulls.async_create(
                *self.repo_info, title=title, body=body, head=self.branch_name, base="main"
            )
        ).parsed_data
