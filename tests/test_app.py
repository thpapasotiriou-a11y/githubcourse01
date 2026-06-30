import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity_name in payload
    assert payload[expected_activity_name]["schedule"] == activities[expected_activity_name]["schedule"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    registered_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": registered_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {registered_email} from {activity_name}"}
    assert registered_email not in activities[activity_name]["participants"]


def test_unregister_unknown_participant_returns_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    unknown_email = "missing@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": unknown_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}
