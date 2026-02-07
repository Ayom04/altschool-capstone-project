import pytest


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_student_success(self, client):
        """Test successful student registration"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "name": "John Doe",
                "email": "john@test.com",
                "password": "Password@123",
                "role": "student"
            }
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["email"] == "john@test.com"
        assert data["name"] == "John Doe"
        assert data["role"] == "student"
        assert data["is_active"] is True
        assert "id" in data
    
    def test_register_admin_success(self, client):
        """Test successful admin registration"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "name": "Admin User",
                "email": "admin@test.com",
                "password": "Password@123",
                "role": "admin"
            }
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["role"] == "admin"
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails"""
        # First registration
        client.post(
            "/api/v1/users/register",
            json={
                "name": "User One",
                "email": "duplicate@test.com",
                "password": "Password@123",
                "role": "student"
            }
        )
        
        # Second registration with same email
        response = client.post(
            "/api/v1/users/register",
            json={
                "name": "User Two",
                "email": "duplicate@test.com",
                "password": "Password@456",
                "role": "student"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["message"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "name": "Test User",
                "email": "invalid-email",
                "password": "Password@123",
                "role": "student"
            }
        )
        assert response.status_code == 422
    
    def test_register_short_password(self, client):
        """Test registration with short password fails"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "name": "Test User",
                "email": "test@test.com",
                "password": "123",
                "role": "student"
            }
        )
        assert response.status_code == 422


class TestUserAuthentication:
    """Test user authentication functionality"""
    
    def test_login_success(self, client):
        client.post( "/api/v1/users/register", json={"name": "Test User", "email": "test@test.com", "password": "Password@123", "role": "student"} )
        response = client.post( "/api/v1/auth/login", json={"email": "test@test.com", "password": "Password@123"} )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client):
        client.post( "/api/v1/users/register", json={"name": "Test User", "email": "test@test.com", "password": "Password@123", "role": "student"} )
        response = client.post( "/api/v1/auth/login", json={"email": "test@test.com", "password": "wrongpassword"} )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        response = client.post( "/api/v1/auth/login", json={"email": "nonexistent@test.com", "password": "Password@123"} )
        assert response.status_code == 401
    



class TestUserProfile:
    """Test user profile functionality"""
    
    def test_get_profile_authenticated(self, client, student_token):
        """Test getting profile when authenticated"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["email"] == "student@test.com"
    
    def test_get_profile_unauthenticated(self, client):
        """Test getting profile without authentication fails"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials provided
    
    def test_update_profile(self, client, student_token):
        """Test updating profile"""
        response = client.put(
            "/api/v1/users/me",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Updated Name"
