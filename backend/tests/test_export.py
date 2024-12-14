"""Test export feature

The idea is to see if changes made through the api are then correctly reflected in the exported file.
We use plain text export to avoid dealing with github
"""

import pytest

from fastapi import UploadFile

from editor.controllers import project_controller
from editor.entries import TaxonomyGraph
from editor import graph_db

from .utils import FakeBackgroundTask


@pytest.fixture()
async def test_taxonomy(database_lifespan):
    """We will import a project to work with

    We cache the project by fully duplicating it so that setup is faster
    """
    from .utils import clean_neo4j_db
    # TEMPORARY
    await clean_neo4j_db(database_lifespan)
    with open("tests/data/test.txt", "rb") as test_file:
        async with graph_db.TransactionCtx() as session:
            # clean the test project
            await project_controller.delete_project("p_test_branch")
            taxonomy = TaxonomyGraph("template", "test")
            if not await taxonomy.does_project_exist():
                # if the template project is not there, we create it
                background_tasks = FakeBackgroundTask()
                await taxonomy.import_taxonomy("test taxonomy", "unknown", background_tasks, UploadFile(file=test_file, filename="test.txt"))
        # this runs in its own transaction
        await background_tasks.run()
        async with graph_db.TransactionCtx() as session:
            # clone template project as test project
            await project_controller.clone_project("template", "test", "branch")
    return TaxonomyGraph("branch", "test")


@pytest.mark.anyio
async def test_no_modification(test_taxonomy):
    background_tasks = FakeBackgroundTask()
    file_path = test_taxonomy.dump_taxonomy(background_tasks)
    assert open(file_path).read() == open("tests/data/test.txt").read()
    # clean files
    background_tasks.run()
