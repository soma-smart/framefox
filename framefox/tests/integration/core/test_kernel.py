import pytest
from fastapi.testclient import TestClient
from framefox.core.kernel import Kernel

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


@pytest.fixture
def client():
    kernel = Kernel()
    return TestClient(kernel.app)


def test_app_startup(client):
    response = client.get("/")
    assert response.status_code != 500
