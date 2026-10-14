def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_k_returns_422(client):
    response = client.get("/recommendations", params={"session_id": "s1", "k": "abc"})
    assert response.status_code == 422
