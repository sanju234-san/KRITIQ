# KRITIQ API Contract

This document provides the official REST API contract for the KRITIQ backend.

---

## Base URL
`http://127.0.0.1:8000`

---

## Authentication
Protected endpoints require a JWT token passed in the `Authorization` header:
`Authorization: Bearer <access_token>`

---

## API Summary

| Category | Endpoint | Method | Auth Required | Description |
|---|---|---|---|---|
| **Auth** | `/auth/register` | `POST` | No | Create a new user profile and issue JWT. |
| **Auth** | `/auth/login` | `POST` | No | Authenticate credentials and issue JWT. |
| **Auth** | `/auth/profile` | `GET` | Yes | Retrieve caller's profile. |
| **Reviews** | `/reviews/` | `POST` | Yes | Run code review on a snippet. |
| **Reviews** | `/reviews/{review_id}` | `GET` | Yes | Fetch a code review by ID. |
| **Translations** | `/translations/` | `POST` | Yes | Translate code between languages. |
| **Translations** | `/translations/{translation_id}` | `GET` | Yes | Fetch a translation by ID. |
| **Explanations** | `/explanations/explain` | `POST` | Yes | Explain code block in plain English. |
| **History** | `/history/` | `GET` | Yes | Paginated activity history list. |
| **History** | `/history/reviews` | `GET` | Yes | Paginated review history list. |
| **History** | `/history/translations` | `GET` | Yes | Paginated translation history list. |

---

## Endpoints Detail

### 1. Register User
* **URL**: `/auth/register`
* **Method**: `POST`
* **Auth Required**: No
* **Request JSON**:
  ```json
  {
    "name": "Sayeed Ahmed",
    "email": "sayeed@example.com",
    "password": "securepwd123"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
* **Error Responses**:
  * **400 Bad Request** (Email already exists):
    ```json
    { "detail": "Email already registered" }
    ```
  * **422 Unprocessable Entity** (Weak password / Invalid email):
    ```json
    { "detail": [{"msg": "String should have at least 8 characters", "loc": ["body", "password"]}] }
    ```
* **Example cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"name": "Sayeed Ahmed", "email": "sayeed@example.com", "password": "securepwd123"}'
  ```

---

### 2. Login User
* **URL**: `/auth/login`
* **Method**: `POST`
* **Auth Required**: No
* **Request JSON**:
  ```json
  {
    "email": "sayeed@example.com",
    "password": "securepwd123"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
* **Error Responses**:
  * **401 Unauthorized** (Wrong password/email):
    ```json
    { "detail": "Invalid email or password" }
    ```
* **Example cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "sayeed@example.com", "password": "securepwd123"}'
  ```

---

### 3. Get User Profile
* **URL**: `/auth/profile`
* **Method**: `GET`
* **Auth Required**: Yes
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (200 OK)**:
  ```json
  {
    "id": "60fe2ffb-4023-4fd1-8fcd-ceae6c10612d",
    "name": "Sayeed Ahmed",
    "email": "sayeed@example.com"
  }
  ```
* **Error Responses**:
  * **401 Unauthorized**:
    ```json
    { "detail": "Could not validate credentials" }
    ```
* **Example cURL**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/auth/profile" \
    -H "Authorization: Bearer <access_token>"
  ```

---

### 4. Submit Code Review
* **URL**: `/reviews/`
* **Method**: `POST`
* **Auth Required**: Yes
* **Headers**: `Authorization: Bearer <token>`
* **Request JSON**:
  ```json
  {
    "code": "def test(): pass",
    "language": "python",
    "filename": "test.py"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "review_id": "aa82e389-9831-4e0d-a02c-7b94b0dfa12d",
    "summary": "High-level summary of code health",
    "issues": [
      {
        "title": "Redundant function pass statement",
        "explanation": "Empty function with only pass is redundant",
        "suggested_fix": null,
        "severity": "low",
        "line": 1
      }
    ],
    "raw_output": "Summary: ... Issues: ..."
  }
  ```
* **Error Responses**:
  * **401 Unauthorized**: Token missing or invalid.
  * **422 Unprocessable Entity**: Code field is empty or language is unsupported.
* **Example cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/reviews/" \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"code": "def test(): pass", "language": "python", "filename": "test.py"}'
  ```

---

### 5. Get Review by ID
* **URL**: `/reviews/{review_id}`
* **Method**: `GET`
* **Auth Required**: Yes
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (200 OK)**:
  ```json
  {
    "review_id": "aa82e389-9831-4e0d-a02c-7b94b0dfa12d",
    "summary": "Summary details",
    "issues": [],
    "raw_output": "..."
  }
  ```
* **Error Responses**:
  * **404 Not Found**: Review record does not exist.
* **Example cURL**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/reviews/aa82e389-9831-4e0d-a02c-7b94b0dfa12d" \
    -H "Authorization: Bearer <access_token>"
  ```

---

### 6. Translate Code
* **URL**: `/translations/`
* **Method**: `POST`
* **Auth Required**: Yes
* **Headers**: `Authorization: Bearer <token>`
* **Request JSON**:
  ```json
  {
    "source_code": "print('hello')",
    "source_language": "python",
    "target_language": "java"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "translation_id": "df61e389-9831-4e0d-a02c-7b94b0dfa72d",
    "translated_code": "System.out.println(\"hello\");",
    "notes": "Successfully translated from python to java."
  }
  ```
* **Error Responses**:
  * **422 Unprocessable Entity**: Invalid source/target language or identical languages requested.
* **Example cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/translations/" \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"source_code": "print('\''hello'\'')", "source_language": "python", "target_language": "java"}'
  ```

---

### 7. Explain Code
* **URL**: `/explanations/explain`
* **Method**: `POST`
* **Auth Required**: Yes
* **Headers**: `Authorization: Bearer <token>`
* **Request JSON**:
  ```json
  {
    "code": "[x*2 for x in range(5)]",
    "language": "python"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "explanation": "Generates a list of doubled square numbers..."
  }
  ```
* **Example cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/explanations/explain" \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"code": "[x*2 for x in range(5)]", "language": "python"}'
  ```

---

### 8. Get Paginated History
* **URL**: `/history/`
* **Method**: `GET`
* **Auth Required**: Yes
* **Headers**: `Authorization: Bearer <token>`
* **Parameters**:
  * `limit` (int, default=20, max=100)
  * `skip` (int, default=0)
  * `type` (string, optional - review, translation, explanation)
* **Success Response (200 OK)**:
  ```json
  {
    "history": [
      {
        "id": "history-uuid",
        "type": "review",
        "timestamp": "2026-07-16T19:51:47Z",
        "summary": "Reviewed python file: test.py",
        "details": {
          "review_id": "review-uuid",
          "issues_count": 1
        }
      }
    ]
  }
  ```
* **Example cURL**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/history/?limit=5&skip=0" \
    -H "Authorization: Bearer <access_token>"
  ```
