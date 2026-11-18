import pytest

from app.llm import FakeLLM
from app.main import create_app


@pytest.fixture
def fake_llm():
    return FakeLLM(reply="fake answer")


@pytest.fixture
def client(fake_llm):
    app = create_app(llm=fake_llm)
    app.config["TESTING"] = True
    return app.test_client()
