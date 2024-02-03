import contextlib
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .graph_db import TransactionCtx


from .github_functions import GithubOperations

from .models.project_models import ProjectStatus

from .controllers.project_controller import get_projects_by_status, delete_project

log = logging.getLogger(__name__)


async def delete_merged_projects():
    async with TransactionCtx():
        exported_projects = await get_projects_by_status(ProjectStatus.EXPORTED)
        for project in exported_projects:
            pr_number = project.github_pr_url and project.github_pr_url.split("/")[-1]
            if not pr_number:
                log.warning(f"PR number not found for project {project.id}")
                continue
            github_object = GithubOperations(project.taxonomy_name, project.branch_name)
            if await github_object.is_pr_merged(int(pr_number)):
                await delete_project(project.id)


@contextlib.contextmanager
def scheduler_lifespan():
    scheduler = AsyncIOScheduler()
    try:
        scheduler.add_job(delete_merged_projects, "interval", hours=24)
        scheduler.start()
        yield
    finally:
        scheduler.shutdown()
