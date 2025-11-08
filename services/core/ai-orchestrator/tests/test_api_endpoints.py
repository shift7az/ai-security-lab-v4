"""
Tests for API Endpoints
"""

from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_dashboard_overview(self, client: TestClient):
        """Test dashboard overview endpoint."""
        response = client.get("/api/dashboard/overview")
        # May fail if services not initialized, but should not crash
        assert response.status_code in [200, 503]

    def test_dashboard_cameras(self, client: TestClient):
        """Test cameras endpoint."""
        response = client.get("/api/dashboard/cameras")
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_settings_list(self, client: TestClient):
        """Test settings list endpoint."""
        response = client.get("/api/settings/")
        assert response.status_code in [200, 503]

    def test_settings_categories(self, client: TestClient):
        """Test settings categories endpoint."""
        response = client.get("/api/settings/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# Note: These are basic smoke tests.
# Full integration tests would require running services.
