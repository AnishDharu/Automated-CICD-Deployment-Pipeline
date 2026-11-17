"""
Tests for the Tasks REST API.
Covers every endpoint + edge cases → well above 70 % coverage.
"""


# ── /health ──────────────────────────────────────────────────────
class TestHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"


# ── GET /tasks ───────────────────────────────────────────────────
class TestGetTasks:
    def test_empty_list(self, client):
        """Fresh database returns an empty JSON list."""
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_created_tasks(self, client):
        """Tasks created via POST show up in GET."""
        client.post("/tasks", json={"title": "First"})
        client.post("/tasks", json={"title": "Second"})
        data = client.get("/tasks").get_json()
        assert len(data) == 2
        assert data[0]["title"] == "First"
        assert data[1]["title"] == "Second"
        # default value of 'done' should be False
        assert data[0]["done"] is False


# ── POST /tasks ──────────────────────────────────────────────────
class TestCreateTask:
    def test_create_returns_201(self, client):
        resp = client.post("/tasks", json={"title": "Write tests"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["title"] == "Write tests"
        assert "id" in body

    def test_missing_title_returns_400(self, client):
        """POST with no 'title' key → 400."""
        resp = client.post("/tasks", json={"description": "oops"})
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "title required"

    def test_empty_body_returns_400(self, client):
        """POST with no JSON body at all → 400."""
        resp = client.post("/tasks", content_type="application/json")
        assert resp.status_code == 400

    def test_empty_title_returns_400(self, client):
        """POST with title="" → 400 (falsy string)."""
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 400


# ── PUT /tasks/<id> ──────────────────────────────────────────────
class TestUpdateTask:
    def test_update_task_done_to_true(self, client):
        """Can update an existing task to done=True."""
        create_resp = client.post("/tasks", json={"title": "Test task"})
        task_id = create_resp.get_json()["id"]

        update_resp = client.put(f"/tasks/{task_id}", json={"done": True})
        assert update_resp.status_code == 200
        assert update_resp.get_json()["done"] is True

    def test_update_nonexistent_task_returns_404(self, client):
        """Updating an ID that doesn't exist returns 404."""
        resp = client.put("/tasks/9999", json={"done": True})
        assert resp.status_code == 404

    def test_update_missing_done_returns_400(self, client):
        """Updating without boolean 'done' returns 400."""
        resp = client.put("/tasks/1", json={"invalid": "field"})
        assert resp.status_code == 400

