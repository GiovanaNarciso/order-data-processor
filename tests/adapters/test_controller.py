import os
import pytest
import app.use_cases.order_service as service_module
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from main import app
from app.database.session import get_db

client = TestClient(app)


def fixture_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "fixtures", filename)


def test_post_orders_accepts_valid_file():
    path = fixture_path("sample.txt")
    with open(path, "rb") as f:
        resp = client.post(
            "/api/orders",
            files={"file": ("sample.txt", f, "text/plain")}
            )

    assert resp.status_code == 204

    get_resp = client.get("/api/orders")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert isinstance(data, list)
    assert any(u["user_id"] == 70 for u in data)


def test_post_orders_rejects_malformed_file():
    path = fixture_path("invalid_sample.txt")
    with open(path, "rb") as f:
        resp = client.post(
            "/api/orders",
            files={"file": ("invalid.txt", f, "text/plain")}
            )

    assert resp.status_code == 500
    assert resp.json()["detail"] == (
        "Internal server error while processing file."
    )


@pytest.mark.parametrize("query, predicate", [
    ("order_id=753", lambda u, o: o["order_id"] == 753),
    ("start_date=2021-09-01&end_date=2021-12-31",
     lambda u, o: "2021-09-01" <= o["date"] <= "2021-12-31"),
])
def test_get_orders_with_filters(query, predicate):
    path = fixture_path("sample.txt")
    with open(path, "rb") as f:
        client.post(
            "/api/orders",
            files={"file": ("sample.txt", f, "text/plain")}
            )

    resp = client.get(f"/api/orders?{query}")
    assert resp.status_code in (200, 204)
    if resp.status_code == 200:
        for user in resp.json():
            for order in user["orders"]:
                assert predicate(user, order)


def test_post_orders_empty_file_returns_204():
    resp = client.post(
        "/api/orders",
        files={"file": ("empty.txt", b"", "text/plain")}
        )
    assert resp.status_code == 204


def test_get_orders_no_data_returns_404_for_specific_order():
    resp = client.get("/api/orders?order_id=999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Order with ID 999999 not found"


def test_get_orders_no_data_returns_204_for_general_query():
    resp = client.get("/api/orders?start_date=2099-01-01")
    assert resp.status_code == 204


def test_get_orders_handles_unexpected_exception(monkeypatch):
    class FakeDatetime:
        @staticmethod
        def strptime(*args, **kwargs):
            raise Exception("unexpected")

    monkeypatch.setattr(service_module, "datetime", FakeDatetime)

    resp = client.get("/api/orders?start_date=2023-01-01")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error."


def test_get_orders_handles_sqlalchemy_error():
    class BrokenSession:
        def query(self, *args, **kwargs):
            raise SQLAlchemyError("Fake DB error")

    app.dependency_overrides[get_db] = lambda: BrokenSession()

    resp = client.get("/api/orders")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Database error."

    app.dependency_overrides.clear()
