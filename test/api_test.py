from fastapi.testclient import TestClient

from test.helpers import InvestifiTestCase
from src.api import app


class TestHelloWorldRoute(InvestifiTestCase):
    """
    Example of how to write a integration test with FastApi in a dockerized container.
    NOTE: Make sure to have your classes inherit from InvestifiTestCase in order to take
    advantage of a predefined test suite framework
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = TestClient(app)
        cls.url = "/"

    def test_hello_world_route(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})


"""
TODO [OPTIONAL]
Write more tests for your work. These can be unit tests for specfic classes or
integration tests that actually make api calls like the example above.
"""
