import asyncio
import contextlib
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .controllers.project_controller import delete_project, get_projects_by_status
from .github_functions import GithubOperations
from .graph_db import TransactionCtx
from .models.project_models import Project, ProjectStatus

log = logging.getLogger(__name__)


async def delete_merged_projects():
    async with TransactionCtx():
        exported_projects = await get_projects_by_status(ProjectStatus.EXPORTED)
        results = await asyncio.gather(
            *map(delete_merged_project, exported_projects), return_exceptions=True
        )
        for exception_result in filter(lambda x: x is not None, results):
            log.warn(exception_result)


async def delete_merged_project(exported_project: Project):
    pr_number = exported_project.github_pr_url and exported_project.github_pr_url.rsplit("/", 1)[-1]
    if not pr_number:
        log.warning(f"PR number not found for project {exported_project.id}")
        return

    github_object = GithubOperations(exported_project.taxonomy_name, exported_project.branch_name)
    if await github_object.is_pr_merged(int(pr_number)):
        await delete_project(exported_project.id)


@contextlib.contextmanager
def scheduler_lifespan():
    scheduler = AsyncIOScheduler()
    try:
        scheduler.add_job(delete_merged_projects, "interval", hours=24)
        scheduler.start()
        yield
    finally:
        scheduler.shutdown()
