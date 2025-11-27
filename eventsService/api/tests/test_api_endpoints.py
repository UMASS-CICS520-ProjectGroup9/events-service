import pytest
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.backends import TokenBackend

from base.models import Event

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def token_backend():
    return TokenBackend(
        signing_key=settings.SIMPLE_JWT["SIGNING_KEY"],
        algorithm=settings.SIMPLE_JWT["ALGORITHM"],
    )


@pytest.fixture
def auth_headers(token_backend):
    def _make(role="STUDENT", user_id=1):
        payload = {"user_id": user_id, "role": role}
        token = token_backend.encode(payload)
        return {"HTTP_AUTHORIZATION": f"bearer {token}"}

    return _make


@pytest.fixture
def make_event():
    def _create(**overrides):
        now = timezone.now()
        defaults = {
            "creator_id": 1,
            "title": "Sample Event",
            "description": "Desc",
            "creator": "creator@example.com",
            "eventType": "Workshop",
            "location": "Campus",
            "capacity": 50,
            "image_url": "",
            "link": "",
            "zoom_link": "",
            "hosted_by": "CS Department",
            "registered_students": [],
            "event_start_date": now + timedelta(days=1),
            "event_end_date": now + timedelta(days=2),
        }
        defaults.update(overrides)
        return Event.objects.create(**defaults)

    return _create


def event_payload_from_instance(event, **overrides):
    payload = {
        "eventID": event.eventID,
        "creator_id": event.creator_id,
        "title": event.title,
        "description": event.description,
        "creator": event.creator,
        "eventType": event.eventType,
        "location": event.location,
        "capacity": event.capacity,
        "image_url": event.image_url,
        "link": event.link,
        "zoom_link": event.zoom_link,
        "hosted_by": event.hosted_by,
        "registered_students": event.registered_students,
        "event_start_date": event.event_start_date.isoformat(),
        "event_end_date": event.event_end_date.isoformat(),
    }
    payload.update(overrides)
    return payload


def test_api_overview(api_client):
    response = api_client.get("/api/")
    assert response.status_code == 200
    assert "getEvents" in response.data


def test_list_events_sorted_by_end_date(api_client, make_event):
    early = make_event(title="Early", event_end_date=timezone.now() + timedelta(days=1))
    late = make_event(title="Late", event_end_date=timezone.now() + timedelta(days=3))

    response = api_client.get("/api/events/")
    assert response.status_code == 200
    titles = [e["title"] for e in response.data]
    assert titles == [early.title, late.title]


def test_get_event_detail(api_client, make_event):
    event = make_event(title="Detail Event")
    response = api_client.get(f"/api/events/{event.eventID}/")
    assert response.status_code == 200
    assert response.data["title"] == "Detail Event"


def test_get_events_by_creator_id_requires_valid_role(api_client, make_event, auth_headers):
    make_event(creator_id=7, title="Owned One")
    make_event(creator_id=7, title="Owned Two")

    ok = api_client.get("/api/events/7/creator_id/", **auth_headers(role="STUDENT", user_id=7))
    assert ok.status_code == 200
    assert {e["title"] for e in ok.data} == {"Owned One", "Owned Two"}

    forbidden = api_client.get("/api/events/7/creator_id/", **auth_headers(role="GUEST", user_id=9))
    assert forbidden.status_code == 403


def test_create_event_sets_creator_id_from_token(api_client, auth_headers):
    now = timezone.now()
    payload = {
        "title": "Created Event",
        "description": "New event",
        "creator": "creator@example.com",
        "eventType": "Seminar",
        "location": "Library",
        "capacity": 25,
        "image_url": "",
        "link": "",
        "zoom_link": "",
        "hosted_by": "Math Dept",
        "registered_students": [],
        "event_start_date": (now + timedelta(days=2)).isoformat(),
        "event_end_date": (now + timedelta(days=3)).isoformat(),
    }
    response = api_client.post(
        "/api/events/create/",
        data=payload,
        format="json",
        **auth_headers(user_id=42, role="STUDENT"),
    )
    assert response.status_code == 201
    assert response.data["creator_id"] == 42
    assert Event.objects.filter(title="Created Event", creator_id=42).exists()


def test_update_event_allows_owner(api_client, make_event, auth_headers):
    event = make_event(creator_id=5, title="Original")
    payload = event_payload_from_instance(event, title="Updated")

    response = api_client.put(
        f"/api/events/{event.eventID}/update/",
        data=payload,
        format="json",
        **auth_headers(user_id=5, role="STUDENT"),
    )
    assert response.status_code == 200
    event.refresh_from_db()
    assert event.title == "Updated"


def test_update_event_blocks_non_owner(api_client, make_event, auth_headers):
    event = make_event(creator_id=5, title="Keep Me")
    payload = event_payload_from_instance(event, title="Should Not Update")

    response = api_client.put(
        f"/api/events/{event.eventID}/update/",
        data=payload,
        format="json",
        **auth_headers(user_id=8, role="STUDENT"),
    )
    assert response.status_code == 404
    event.refresh_from_db()
    assert event.title == "Keep Me"


def test_delete_event_owner_only(api_client, make_event, auth_headers):
    event = make_event(creator_id=10)
    response = api_client.delete(
        f"/api/events/{event.eventID}/delete/",
        **auth_headers(user_id=10, role="STUDENT"),
    )
    assert response.status_code == 204
    assert not Event.objects.filter(eventID=event.eventID).exists()


def test_register_and_unregister_student(api_client, make_event, auth_headers):
    event = make_event(creator_id=2, registered_students=[1])

    register = api_client.post(
        f"/api/events/{event.eventID}/register/",
        data={"student_id": 5},
        format="json",
        **auth_headers(user_id=2, role="STUDENT"),
    )
    assert register.status_code == 200
    event.refresh_from_db()
    assert 5 in event.registered_students

    unregister = api_client.post(
        f"/api/events/{event.eventID}/unregister/",
        data={"student_id": 5},
        format="json",
        **auth_headers(user_id=2, role="STUDENT"),
    )
    assert unregister.status_code == 200
    event.refresh_from_db()
    assert 5 not in event.registered_students


def test_registered_students_listing(api_client, make_event):
    event = make_event(registered_students=[3, 4, 5])
    response = api_client.get(f"/api/events/{event.eventID}/registered_students/")
    assert response.status_code == 200
    assert response.data["registered_students"] == [3, 4, 5]


def test_full_and_available_events(api_client, make_event):
    full_event = make_event(title="Full", capacity=2, registered_students=[1, 2])
    open_event = make_event(title="Open", capacity=3, registered_students=[1])

    full_response = api_client.get("/api/events/full/")
    assert full_response.status_code == 200
    assert {e["title"] for e in full_response.data} == {"Full"}

    available_response = api_client.get("/api/events/available/")
    assert available_response.status_code == 200
    assert {e["title"] for e in available_response.data} == {"Open"}


def test_sorted_by_creation_and_update_dates(api_client, make_event):
    newer = make_event(title="Newer")
    older = make_event(title="Older")

    now = timezone.now()
    Event.objects.filter(pk=newer.pk).update(created_at=now, updated_at=now + timedelta(hours=1))
    Event.objects.filter(pk=older.pk).update(created_at=now - timedelta(days=1), updated_at=now)

    creation = api_client.get("/api/events/sorted_by_creation_date/")
    assert creation.status_code == 200
    assert [e["title"] for e in creation.data][:2] == ["Newer", "Older"]

    updated = api_client.get("/api/events/sorted_by_update_date/")
    assert updated.status_code == 200
    assert [e["title"] for e in updated.data][:2] == ["Newer", "Older"]


def test_sorted_by_start_and_end_dates(api_client, make_event):
    event_a = make_event(title="A", event_start_date=timezone.now() + timedelta(days=1), event_end_date=timezone.now() + timedelta(days=2))
    event_b = make_event(title="B", event_start_date=timezone.now() + timedelta(days=3), event_end_date=timezone.now() + timedelta(days=4))

    start_sorted = api_client.get("/api/events/sorted_by_start_date/")
    assert start_sorted.status_code == 200
    assert [e["title"] for e in start_sorted.data][:2] == ["A", "B"]

    end_sorted = api_client.get("/api/events/sorted_by_end_date/")
    assert end_sorted.status_code == 200
    assert [e["title"] for e in end_sorted.data][:2] == ["A", "B"]


def test_filters_endpoint(api_client, make_event):
    make_event(title="Match", creator="alice", eventType="Seminar", location="Campus Hall", hosted_by="Club", capacity=100)
    make_event(title="Non-Match", creator="bob", eventType="Workshop", location="Downtown", hosted_by="Org", capacity=10)

    response = api_client.get(
        "/api/events/filters/",
        {
            "creator": "alice",
            "eventType": "Seminar",
            "location": "Campus",
            "host": "Club",
            "min_capacity": 50,
        },
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Match"


def test_event_count(api_client, make_event):
    make_event()
    make_event()
    response = api_client.get("/api/events/count/")
    assert response.status_code == 200
    assert response.data["event_count"] == 2


def test_upcoming_and_past_events(api_client, make_event):
    make_event(title="Future", event_start_date=timezone.now() + timedelta(days=5), event_end_date=timezone.now() + timedelta(days=6))
    make_event(title="Past", event_start_date=timezone.now() - timedelta(days=3), event_end_date=timezone.now() - timedelta(days=2))

    upcoming = api_client.get("/api/events/upcoming/")
    assert upcoming.status_code == 200
    assert {e["title"] for e in upcoming.data} == {"Future"}

    past = api_client.get("/api/events/past/")
    assert past.status_code == 200
    assert {e["title"] for e in past.data} == {"Past"}


def test_search_and_targeted_filters(api_client, make_event):
    make_event(title="Machine Learning 101", description="Intro course", eventType="Class", hosted_by="AI Lab", creator="alice", location="Campus Center")
    make_event(title="Cooking Night", description="Food", eventType="Social", hosted_by="Club", creator="bob", location="Downtown")

    search = api_client.get("/api/events/search/", {"q": "machine"})
    assert search.status_code == 200
    assert {e["title"] for e in search.data} == {"Machine Learning 101"}

    by_host = api_client.get("/api/events/by_host/AI Lab/")
    assert by_host.status_code == 200
    assert {e["title"] for e in by_host.data} == {"Machine Learning 101"}

    by_type = api_client.get("/api/events/by_type/Class/")
    assert by_type.status_code == 200
    assert {e["title"] for e in by_type.data} == {"Machine Learning 101"}

    by_location = api_client.get("/api/events/by_location/Campus/")
    assert by_location.status_code == 200
    assert {e["title"] for e in by_location.data} == {"Machine Learning 101"}

    by_creator = api_client.get("/api/events/by_creator/alice/")
    assert by_creator.status_code == 200
    assert {e["title"] for e in by_creator.data} == {"Machine Learning 101"}


def test_events_by_date_range(api_client, make_event):
    now = timezone.now()
    inside = make_event(
        title="Inside",
        event_start_date=now + timedelta(days=1),
        event_end_date=now + timedelta(days=2),
    )
    make_event(
        title="Outside",
        event_start_date=now + timedelta(days=10),
        event_end_date=now + timedelta(days=11),
    )
    response = api_client.get(
        "/api/events/by_date_range/",
        {
            "start_date": (now + timedelta(hours=12)).isoformat(),
            "end_date": (now + timedelta(days=3)).isoformat(),
        },
    )
    assert response.status_code == 200
    assert {e["title"] for e in response.data} == {inside.title}


def test_events_by_capacity(api_client, make_event):
    make_event(title="Large", capacity=200)
    make_event(title="Small", capacity=10)
    response = api_client.get("/api/events/by_capacity/50/")
    assert response.status_code == 200
    assert {e["title"] for e in response.data} == {"Large"}


def test_recent_events(api_client, make_event):
    recent = make_event(title="Recent")
    old = make_event(title="Old")
    now = timezone.now()
    Event.objects.filter(pk=recent.pk).update(created_at=now - timedelta(days=1))
    Event.objects.filter(pk=old.pk).update(created_at=now - timedelta(days=10))

    response = api_client.get("/api/events/recent/5/")
    assert response.status_code == 200
    assert {e["title"] for e in response.data} == {"Recent"}


def test_events_with_links_and_zoom_links(api_client, make_event):
    make_event(title="Has Links", link="https://example.com")
    make_event(title="Has Zoom", zoom_link="https://zoom.us/j/123")
    make_event(title="No Links", link="", zoom_link="")

    with_links = api_client.get("/api/events/with_links/")
    assert with_links.status_code == 200
    assert {e["title"] for e in with_links.data} == {"Has Links"}

    with_zoom = api_client.get("/api/events/with_zoom_links/")
    assert with_zoom.status_code == 200
    assert {e["title"] for e in with_zoom.data} == {"Has Zoom"}


def test_events_by_keyword(api_client, make_event):
    make_event(title="AI Intro", description="learn AI basics")
    make_event(title="Cooking", description="learn recipes")

    missing_keyword = api_client.get("/api/events/by_keyword/")
    assert missing_keyword.status_code == 400

    response = api_client.get("/api/events/by_keyword/", {"keyword": "AI"})
    assert response.status_code == 200
    assert {e["title"] for e in response.data} == {"AI Intro"}


def test_health_info_and_welcome(api_client):
    health = api_client.get("/api/health/")
    assert health.status_code == 200
    assert health.data["status"] == "API is running"

    info = api_client.get("/api/info/")
    assert info.status_code == 200
    assert info.data["name"] == "Events Service API"

    welcome = api_client.get("/api/welcome/")
    assert welcome.status_code == 200
    assert welcome.data["message"].startswith("Welcome")
