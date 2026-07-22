from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    response = TestClient(app).get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_entry_probe_is_available_without_authentication() -> None:
    response = TestClient(app).get("/v1/entry/probe")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "前置页服务已连接",
    }
