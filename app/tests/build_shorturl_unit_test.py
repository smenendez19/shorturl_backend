import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.database import get_session
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.sqlite"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_build_successful(client: TestClient):
    response = client.post("/v1/shorturl/build", json={"url": "https://www.google.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "ShortURL created successfully"


def test_build_required_body(client: TestClient):
    response = client.post("/v1/shorturl/build")
    assert response.status_code == 422
    assert response.json()["errors"][0]["loc"] == "body"
    assert response.json()["errors"][0]["type"] == "missing"


def test_build_invalid_url(client: TestClient):
    response = client.post("/v1/shorturl/build", json={"url": "w.google"})
    assert response.status_code == 422
    assert response.json()["errors"][0]["loc"] == "body.url"
    assert response.json()["errors"][0]["type"] == "value_error"


def test_build_expiration_date_in_past(client: TestClient):
    response = client.post("/v1/shorturl/build", json={"url": "https://www.google.com", "expires_at": "2020-01-01T00:00:00"})
    assert response.status_code == 422
    assert response.json()["errors"][0]["loc"] == "body.expires_at"
    assert response.json()["errors"][0]["type"] == "value_error"
