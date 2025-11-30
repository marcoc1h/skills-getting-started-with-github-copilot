import importlib
import urllib.parse

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Reload the app module to reset in-memory state between tests
    import src.app as app_module
    importlib.reload(app_module)
    return TestClient(app_module.app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Check a known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister(client):
    email = "tester@example.com"
    activity = "Chess Club"
    encoded_activity = urllib.parse.quote(activity, safe="")

    # Sign up
    res = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert res.status_code == 200
    payload = res.json()
    assert "Signed up" in payload.get("message", "")

    # Verify participant present
    res2 = client.get("/activities")
    participants = res2.json()[activity]["participants"]
    assert email in participants

    # Attempt duplicate signup -> should fail
    res_dup = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert res_dup.status_code == 400

    # Unregister
    res_un = client.delete(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert res_un.status_code == 200
    assert "Unregistered" in res_un.json().get("message", "")

    # Verify removed
    res3 = client.get("/activities")
    participants_after = res3.json()[activity]["participants"]
    assert email not in participants_after
