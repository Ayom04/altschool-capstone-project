import pytest


class TestCourseRetrieval:
    """Test course retrieval functionality"""
    
    def test_get_all_courses_public(self, client, sample_course):
        """Test getting all courses without authentication"""
        response = client.get("/api/v1/courses")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["code"] == "PY101"
    
    def test_get_course_by_id(self, client, sample_course):
        """Test getting a specific course"""
        course_id = sample_course["id"]
        response = client.get(f"/api/v1/courses/{course_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == course_id
        assert data["code"] == "PY101"
    
    def test_get_nonexistent_course(self, client):
        """Test getting nonexistent course returns 404"""
        response = client.get("/api/v1/courses/9999")
        assert response.status_code == 404


class TestCourseCreation:
    """Test course creation functionality"""
    
    def test_create_course_as_admin(self, client, admin_token):
        """Test creating course as admin"""
        response = client.post(
            "/api/v1/courses",
            json={
                "title": "Advanced Python",
                "code": "PY201",
                "capacity": 25
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["code"] == "PY201"
        assert data["capacity"] == 25
        assert data["is_active"] is True
    
    def test_create_course_as_student_fails(self, client, student_token):
        """Test creating course as student fails"""
        response = client.post(
            "/api/v1/courses",
            json={
                "title": "Test Course",
                "code": "TEST101",
                "capacity": 20
            },
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
    
    def test_create_course_duplicate_code(self, client, admin_token, sample_course):
        """Test creating course with duplicate code fails"""
        response = client.post(
            "/api/v1/courses",
            json={
                "title": "Another Python Course",
                "code": "PY101",  # Duplicate code
                "capacity": 20
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["message"].lower()
    
    def test_create_course_zero_capacity(self, client, admin_token):
        """Test creating course with zero capacity fails"""
        response = client.post(
            "/api/v1/courses",
            json={
                "title": "Test Course",
                "code": "TEST101",
                "capacity": 0
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
    
    def test_create_course_negative_capacity(self, client, admin_token):
        """Test creating course with negative capacity fails"""
        response = client.post(
            "/api/v1/courses",
            json={
                "title": "Test Course",
                "code": "TEST101",
                "capacity": -5
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422


class TestCourseUpdate:
    """Test course update functionality"""
    
    def test_update_course_as_admin(self, client, admin_token, sample_course):
        """Test updating course as admin"""
        course_id = sample_course["id"]
        response = client.put(
            f"/api/v1/courses/{course_id}",
            json={"title": "Updated Python Course"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Python Course"
    
    def test_update_course_as_student_fails(self, client, student_token, sample_course):
        """Test updating course as student fails"""
        course_id = sample_course["id"]
        response = client.put(
            f"/api/v1/courses/{course_id}",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
    
    def test_deactivate_course(self, client, admin_token, sample_course):
        """Test deactivating a course"""
        course_id = sample_course["id"]
        response = client.patch(
            f"/api/v1/courses/{course_id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["is_active"] is False
    
    def test_activate_course(self, client, admin_token, sample_course):
        """Test activating a course"""
        course_id = sample_course["id"]
        # First deactivate
        client.patch(
            f"/api/v1/courses/{course_id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Then activate
        response = client.patch(
            f"/api/v1/courses/{course_id}/activate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["is_active"] is True


class TestCourseDelete:
    """Test course deletion functionality"""
    
    def test_delete_course_as_admin(self, client, admin_token, sample_course):
        """Test deleting (deactivating) course as admin"""
        course_id = sample_course["id"]
        response = client.delete(
            f"/api/v1/courses/{course_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204 or response.status_code == 200
        
        # Verify course is deactivated
        get_response = client.get(f"/api/v1/courses/{course_id}")
        assert get_response.json()["data"]["is_active"] is False
    
    def test_delete_course_as_student_fails(self, client, student_token, sample_course):
        """Test deleting course as student fails"""
        course_id = sample_course["id"]
        response = client.delete(
            f"/api/v1/courses/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
