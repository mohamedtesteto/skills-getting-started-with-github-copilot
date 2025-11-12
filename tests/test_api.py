from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect some known activities to exist
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_cycle(client):
    activity_name = "Chess Club"
    test_email = "test_student@example.com"

    # Ensure test_email is not in participants initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert test_email not in resp.json()[activity_name]["participants"]

    # Sign up
    signup_resp = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Confirm participant present
    resp_after = client.get("/activities")
    assert test_email in resp_after.json()[activity_name]["participants"]

    # Unregister
    unregister_resp = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
    assert unregister_resp.status_code == 200
    assert "Unregistered" in unregister_resp.json().get("message", "")

    # Confirm removed
    resp_final = client.get("/activities")
    assert test_email not in resp_final.json()[activity_name]["participants"]

    # Removing again should return 400
    second_remove = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
    assert second_remove.status_code == 400
