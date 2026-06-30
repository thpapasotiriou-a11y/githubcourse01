from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    activity = activities[activity_name]
    original_participants = list(activity["participants"])
    email = "student@example.com"

    try:
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        assert signup_response.status_code == 200
        assert email in activity["participants"]

        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )
        assert unregister_response.status_code == 200
        assert email not in activity["participants"]
    finally:
        activity["participants"] = original_participants
