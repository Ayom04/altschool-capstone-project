#!/usr/bin/env python3
"""
Demo script to showcase the LMS API functionality
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_response(response):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def main():
    print_section("LMS API Demo")
    
    # 1. Health Check
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    
    # 2. Register Admin
    print_section("2. Register Admin User")
    admin_data = {
        "name": "Admin User",
        "email": "admin@lms.com",
        "password": "admin123",
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/api/v1/users/register", json=admin_data)
    print_response(response)
    
    # 3. Register Student
    print_section("3. Register Student User")
    student_data = {
        "name": "Alice Student",
        "email": "alice@lms.com",
        "password": "student123",
        "role": "student"
    }
    response = requests.post(f"{BASE_URL}/api/v1/users/register", json=student_data)
    print_response(response)
    
    # 4. Admin Login
    print_section("4. Admin Login")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login-json",
        json={"email": "admin@lms.com", "password": "admin123"}
    )
    print_response(response)
    admin_token = response.json()["access_token"]
    
    # 5. Student Login
    print_section("5. Student Login")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login-json",
        json={"email": "alice@lms.com", "password": "student123"}
    )
    print_response(response)
    student_token = response.json()["access_token"]
    
    # 6. Create Courses (Admin)
    print_section("6. Create Courses (Admin)")
    courses = [
        {"title": "Introduction to Python", "code": "PY101", "capacity": 30},
        {"title": "Web Development with FastAPI", "code": "WEB201", "capacity": 25},
        {"title": "Database Design", "code": "DB301", "capacity": 20}
    ]
    
    for course in courses:
        response = requests.post(
            f"{BASE_URL}/api/v1/courses",
            json=course,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Creating course: {course['title']}")
        print_response(response)
    
    # 7. View All Courses (Public)
    print_section("7. View All Courses (Public)")
    response = requests.get(f"{BASE_URL}/api/v1/courses")
    print_response(response)
    courses_list = response.json()
    
    # 8. Enroll in Courses (Student)
    print_section("8. Student Enrolls in Courses")
    if courses_list:
        for i in range(min(2, len(courses_list))):
            course = courses_list[i]
            response = requests.post(
                f"{BASE_URL}/api/v1/enrollments",
                json={"course_id": course["id"]},
                headers={"Authorization": f"Bearer {student_token}"}
            )
            print(f"Enrolling in: {course['title']}")
            print_response(response)
    
    # 9. View Student's Enrollments
    print_section("9. View Student's Enrollments")
    response = requests.get(
        f"{BASE_URL}/api/v1/enrollments/my-enrollments",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    print_response(response)
    
    # 10. Admin Views All Enrollments
    print_section("10. Admin Views All Enrollments")
    response = requests.get(
        f"{BASE_URL}/api/v1/enrollments",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print_response(response)
    
    # 11. Update Course (Admin)
    print_section("11. Update Course (Admin)")
    if courses_list:
        course_id = courses_list[0]["id"]
        response = requests.put(
            f"{BASE_URL}/api/v1/courses/{course_id}",
            json={"capacity": 35},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Updating course capacity")
        print_response(response)
    
    # 12. Deactivate Course (Admin)
    print_section("12. Deactivate Course (Admin)")
    if len(courses_list) > 1:
        course_id = courses_list[1]["id"]
        response = requests.patch(
            f"{BASE_URL}/api/v1/courses/{course_id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Deactivating course")
        print_response(response)
    
    # 13. Try to enroll in inactive course (should fail)
    print_section("13. Try to Enroll in Inactive Course (Should Fail)")
    if len(courses_list) > 1:
        course_id = courses_list[1]["id"]
        response = requests.post(
            f"{BASE_URL}/api/v1/enrollments",
            json={"course_id": course_id},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        print_response(response)
    
    print_section("Demo Complete!")
    print("All operations completed successfully!")
    print("\nYou can now:")
    print("  - View interactive docs: http://localhost:8000/api/docs")
    print("  - View ReDoc: http://localhost:8000/api/redoc")
    print("  - Run tests: pytest tests/ -v")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Please make sure the server is running:")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\nError: {e}")

