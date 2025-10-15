from fastapi.testclient import TestClient
from app.main import app, engine
from sqlmodel import SQLModel


client = TestClient(app)


def setup_module(module):
    # Ensure a fresh schema for tests (drop existing tables then create)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_commodity_and_plan():
    # create commodity
    r = client.post("/warehouse/commodities", json={"name": "Blankets", "quantity": 0})
    assert r.status_code == 200
    c = r.json()
    cid = c["id"]

    # add stock via ttn
    r = client.post("/warehouse/ttn", json={"commodity_id": cid, "qty": 100})
    assert r.status_code == 200

    # create plan requiring 10 -> should succeed
    plan = {"name": "Plan A", "items": [{"commodity_id": cid, "qty": 10}]}
    r = client.post("/planning/plans", json=plan)
    assert r.status_code == 200
