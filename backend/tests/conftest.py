from fastapi.testclient import TestClient
import pytest

from editor.api import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
