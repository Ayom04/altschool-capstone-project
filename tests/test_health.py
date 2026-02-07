import pytest


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_returns_ok_status(self, client):
        """Test health endpoint returns ok status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "System is healthy"
    
    def test_health_check_has_required_fields(self, client):
        """Test health endpoint returns all required fields"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Check all required fields are present
        assert "timestamp" in data
        assert "uptime" in data
        assert "environment" in data
        assert "database" in data
        assert "version" in data
    
    def test_health_check_database_status(self, client):
        """Test health endpoint checks database connection"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Check database info
        assert "status" in data["database"]
        assert "url" in data["database"]
        assert data["database"]["status"] == "connected"
    
    def test_health_check_uptime_is_positive(self, client):
        """Test uptime is a positive number"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert isinstance(data["uptime"], (int, float))
        assert data["uptime"] >= 0
    
    def test_health_check_timestamp_format(self, client):
        """Test timestamp is in ISO format"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Check timestamp ends with Z (UTC)
        assert data["timestamp"].endswith("Z")
        # Check it contains T separator
        assert "T" in data["timestamp"]

