
"""Tests for the BQRC FastAPI health endpoint."""

from fastapi.testclient import TestClient

from bqrc.api.main import app


def test_health_endpoint_returns_200() -> None:
    """The API should report a successful health check."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200


def test_health_endpoint_response_schema() -> None:
    """The health response should contain the expected metadata."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.json() == {
        "status": "ok",
        "service": "bqrc-api",
        "version": "0.1.0",
    }


def test_openapi_schema_is_available() -> None:
    """FastAPI should expose its automatically generated OpenAPI schema."""
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == (
        "BQRC Digital Engineering Platform API"
    )
