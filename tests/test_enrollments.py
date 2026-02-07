import pytest


class TestEnrollment:
    """Test enrollment functionality"""
    
    def test_enroll_as_student(self, client, student_token, sample_course):
        """Test successful enrollment as student"""
        course_id = sample_course["id"]
        response = client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["course_id"] == course_id
        assert "created_at" in data
    
    def test_enroll_as_admin_fails(self, client, admin_token, sample_course):
        """Test enrollment as admin fails"""
        course_id = sample_course["id"]
        response = client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 403
        assert "only students" in response.json()["message"].lower()
    
    def test_enroll_duplicate_fails(self, client, student_token, sample_course):
        """Test enrolling in same course twice fails"""
        course_id = sample_course["id"]
        
        # First enrollment
        client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Second enrollment
        response = client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 400
        assert "already enrolled" in response.json()["message"].lower()
    
    def test_enroll_inactive_course_fails(self, client, student_token, admin_token, sample_course):
        """Test enrolling in inactive course fails"""
        course_id = sample_course["id"]
        
        # Deactivate course
        client.patch(
            f"/api/v1/courses/{course_id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Try to enroll
        response = client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 400
        assert "inactive" in response.json()["message"].lower()
    
    def test_enroll_full_course_fails(self, client, admin_token):
        """Test enrolling in full course fails"""
        # Create course with capacity of 1
        course_response = client.post(
            "/api/v1/courses",
            json={
                "title": "Small Course",
                "code": "SMALL101",
                "capacity": 1
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        course_id = course_response.json()["data"]["id"]
        
        # Create first student and enroll
        client.post(
            "/api/v1/users/register",
            json={
                "name": "Student One",
                "email": "student1@test.com",
                "password": "Password@123",
                "role": "student"
            }
        )
        token1_response = client.post( "/api/v1/auth/login", json={"email": "student1@test.com", "password": "Password@123"} )
        token1 = token1_response.json()["data"]["access_token"]
        
        client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # Create second student and try to enroll
        client.post(
            "/api/v1/users/register",
            json={
                "name": "Student Two",
                "email": "student2@test.com",
                "password": "Password@123",
                "role": "student"
            }
        )
        token2_response = client.post( "/api/v1/auth/login", json={"email": "student2@test.com", "password": "Password@123"} )
        token2 = token2_response.json()["data"]["access_token"]
        
        response = client.post(
            "/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 400
        assert "full capacity" in response.json()["message"].lower()
    
    def test_enroll_nonexistent_course(self, client, student_token):
        """Test enrolling in nonexistent course fails"""
        response = client.post(
            "/api/v1/enrollments",
            json={"course_id": 9999},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 404


class TestDeregistration:
    """Test deregistration functionality"""
    
    def test_deregister_by_enrollment_id(self, client, student_token, sample_course):
        """Test deregistering by enrollment ID"""
        # Enroll first
        enroll_response = client.post(
            "/api/v1/enrollments",
            json={"course_id": sample_course["id"]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        enrollment_id = enroll_response.json()["data"]["id"]
        
        # Deregister
        response = client.delete(
            f"/api/v1/enrollments/{enrollment_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 204 or response.status_code == 200
    
    def test_deregister_by_course_id(self, client, student_token, sample_course):
        """Test deregistering by course ID"""
        # Enroll first
        client.post(
            "/api/v1/enrollments",
            json={"course_id": sample_course["id"]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Deregister
        response = client.delete(
            f"/api/v1/enrollments/courses/{sample_course['id']}/deregister",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 204 or response.status_code == 200
    
    def test_deregister_not_enrolled(self, client, student_token, sample_course):
        """Test deregistering when not enrolled fails"""
        response = client.delete(
            f"/api/v1/enrollments/courses/{sample_course['id']}/deregister",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 404


class TestEnrollmentOversight:
    """Test admin enrollment oversight functionality"""
    
    def test_get_all_enrollments_as_admin(self, client, admin_token, student_token, sample_course):
        """Test admin can view all enrollments"""
        # Create enrollment
        client.post(
            "/api/v1/enrollments",
            json={"course_id": sample_course["id"]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Get all enrollments
        response = client.get(
            "/api/v1/enrollments",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        assert "user" in data["items"][0]
        assert "course" in data["items"][0]
        assert "name" in data["items"][0]["user"]
        assert "title" in data["items"][0]["course"]
    
    def test_get_all_enrollments_as_student_fails(self, client, student_token):
        """Test student cannot view all enrollments"""
        response = client.get(
            "/api/v1/enrollments",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
    
    def test_get_enrollments_for_course(self, client, admin_token, student_token, sample_course):
        """Test admin can view enrollments for specific course"""
        # Create enrollment
        client.post(
            "/api/v1/enrollments",
            json={"course_id": sample_course["id"]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Get course enrollments
        response = client.get(
            f"/api/v1/enrollments/courses/{sample_course['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 1
        assert data[0]["course_id"] == sample_course["id"]
    
    def test_admin_remove_student(self, client, admin_token, student_token, sample_course):
        """Test admin can remove student from course"""
        # Create enrollment
        enroll_response = client.post(
            "/api/v1/enrollments",
            json={"course_id": sample_course["id"]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        enrollment_id = enroll_response.json()["data"]["id"]
        
        # Admin removes student
        response = client.delete(
            f"/api/v1/enrollments/admin/{enrollment_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204 or response.status_code == 200
    
    def test_get_my_enrollments(self, client, student_token, sample_course):
        """Test student can view their own enrollments"""
        # Enroll
        client.post(
            "/api/v1/enrollments",
            json={"course_id": sample_course["id"]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Get my enrollments
        response = client.get(
            "/api/v1/enrollments/my-enrollments",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 1
        assert data[0]["course_id"] == sample_course["id"]
