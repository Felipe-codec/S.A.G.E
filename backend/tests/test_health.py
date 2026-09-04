def test_health_check_endpoint(client):
    """Verifica se o endpoint GET /health responde com 200 e status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_env" in data


def test_health_ready_endpoint(client, monkeypatch):
    """Verifica se o endpoint GET /health/ready responde adequadamente com base no banco."""
    # Testa sucesso
    monkeypatch.setattr("app.api.routes.health.check_db_connection", lambda: True)
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"

    # Testa indisponibilidade (503)
    monkeypatch.setattr("app.api.routes.health.check_db_connection", lambda: False)
    response_fail = client.get("/health/ready")
    assert response_fail.status_code == 503
    data_fail = response_fail.json()
    assert data_fail["status"] == "unavailable"
