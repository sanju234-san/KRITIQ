import random
import sys
import requests

BASE_URL = "http://localhost:8000"


def print_step_header(step_num: int, description: str):
    print("\n" + "=" * 60)
    print(f"=== STEP {step_num}: {description} ===")
    print("=" * 60)


def main():
    steps_total = 8
    steps_passed = 0
    steps_failed = []

    # 1. Reachability Check
    print_step_header(1, "Confirm the server is reachable")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        response.raise_for_status()
        print(f"Server is reachable. Response: {response.json()}")
        steps_passed += 1
    except Exception as e:
        print(f"[FATAL] Server is not reachable at {BASE_URL}. Exception: {e}")
        print("Please start Sayeed's server first using 'uvicorn app.main:app --reload' in a separate terminal.")
        sys.exit(1)

    # Generate a randomized test user email to ensure uniqueness
    test_email = f"test_{random.randint(100000, 999999)}@example.com"
    test_password = "securepassword123"
    token = None

    # 2. Register User
    print_step_header(2, "Register a new test user")
    try:
        payload = {
            "name": "Integration Test User",
            "email": test_email,
            "password": test_password
        }
        print(f"Sending payload: {payload}")
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        steps_passed += 1
    except Exception as e:
        print(f"[FAILED] Register User. Error: {e}")
        steps_failed.append("Register User")

    # 3. Log In
    print_step_header(3, "Log in to retrieve JWT token")
    try:
        payload = {
            "email": test_email,
            "password": test_password
        }
        print(f"Sending payload: {payload}")
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        
        token_data = response.json()
        token = token_data.get("access_token")
        if token:
            print(f"Success: Received token (first 15 chars): {token[:15]}...")
            steps_passed += 1
        else:
            print("[FAILED] Access token not present in login response.")
            steps_failed.append("Login User (Missing Token)")
    except Exception as e:
        print(f"[FAILED] Login User. Error: {e}")
        steps_failed.append("Login User")

    # Create headers if token is present
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 4. Auth Profile
    print_step_header(4, "Retrieve user profile using Bearer token")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        steps_passed += 1
    except Exception as e:
        print(f"[FAILED] Retrieve Profile. Error: {e}")
        steps_failed.append("Retrieve Profile")

    # 5. Submit Review
    print_step_header(5, "Submit a code review request")
    try:
        review_payload = {
            "language": "python",
            "source": "upload",
            "code_content": (
                "def calculate_discount(price, discount_percent):\n"
                "    unused_var = \"debug\"\n"
                "    discount_amount = price * discount_percent / 100\n"
                "    discounted = price - discount_amount\n"
                "    # missing return statement\n"
            ),
            "request_translation": False
        }
        print(f"Sending payload: {review_payload}")
        response = requests.post(f"{BASE_URL}/reviews/", json=review_payload, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        
        resp_json = response.json()
        summary_present = "summary" in resp_json
        issues_present = "issues" in resp_json
        print(f"Checks: 'summary' present = {summary_present}, 'issues' present = {issues_present}")
        
        if summary_present and issues_present:
            steps_passed += 1
        else:
            print("[FAILED] Response is missing 'summary' or 'issues' fields.")
            steps_failed.append("Submit Review (Invalid Schema)")
    except Exception as e:
        print(f"[FAILED] Submit Review. Error: {e}")
        steps_failed.append("Submit Review")

    # 6. Submit Translation
    print_step_header(6, "Submit a translation request")
    try:
        translation_payload = {
            "source_language": "python",
            "target_language": "java",
            "source": "upload",
            "file_name": "sample.py",
            "code_content": "def add(a, b):\n    return a+b\n"
        }
        print(f"Sending payload: {translation_payload}")
        response = requests.post(f"{BASE_URL}/translations/", json=translation_payload, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        steps_passed += 1
    except Exception as e:
        print(f"[FAILED] Submit Translation. Error: {e}")
        steps_failed.append("Submit Translation")

    # 7. Submit Explanation
    print_step_header(7, "Submit an explanation request")
    try:
        params = {"issue_id": "test-issue-123"}
        response = requests.post(f"{BASE_URL}/explanations/explain", params=params, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        steps_passed += 1
    except Exception as e:
        print(f"[FAILED] Submit Explanation. Error: {e}")
        steps_failed.append("Submit Explanation")

    # 8. Retrieve History
    print_step_header(8, "Retrieve history logs")
    try:
        response = requests.get(f"{BASE_URL}/history/", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        steps_passed += 1
    except Exception as e:
        print(f"[FAILED] Retrieve History. Error: {e}")
        steps_failed.append("Retrieve History")

    # Final Summary
    print("\n" + "=" * 60)
    print("=== FINAL INTEGRATION TEST SUMMARY ===")
    print("=" * 60)
    print(f"Total Steps Executed: {steps_total}")
    print(f"Steps Passed: {steps_passed}")
    print(f"Steps Failed: {len(steps_failed)}")
    if steps_failed:
        print("Failed Steps:")
        for failed in steps_failed:
            print(f" - {failed}")
    else:
        print("All steps completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
