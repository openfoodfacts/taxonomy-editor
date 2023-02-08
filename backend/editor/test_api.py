from datetime import datetime

from fastapi.testclient import TestClient

from .api import app

client = TestClient(app)


"""
@app.get("/ping")
async def pong(response: Response):
    pong = datetime.now()
    return {"ping": "pong @ %s" % pong}
"""


def test_ping():
    response = client.get("/404")
    assert response.status_code == 404
