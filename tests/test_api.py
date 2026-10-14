def test_recommendations_change_after_event(client):
    before = client.get("/recommendations", params={"session_id": "s1", "k": 2}).json()
    client.post("/events", json={"session_id": "s1", "product_id": 1, "event_type": "view"})
    after = client.get("/recommendations", params={"session_id": "s1", "k": 2}).json()

    assert [r["product_id"] for r in before] == [9, 8]  # empty session -> popular
    assert [r["product_id"] for r in after] == [2, 3]  # related to product 1
