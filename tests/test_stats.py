"""
Unit tests for analytics and statistics API endpoints.
"""


def test_stats_summary(client):
    res = client.get("/api/stats/summary")
    assert res.status_code == 200
    data = res.get_json()

    assert "metrics" in data
    assert data["metrics"]["total_events"] > 0
    assert data["metrics"]["total_students"] > 0
    assert data["metrics"]["total_registrations"] > 0

    assert "category_breakdown" in data
    cats = {c["category"] for c in data["category_breakdown"]}
    assert {"Technical", "Cultural", "Sports", "Workshops"}.issubset(cats)

    assert "popular_events" in data
    assert len(data["popular_events"]) > 0
