# KRITIQ Developer Workflows Guide

This guide is designed for frontend developers and other contributors integrating with the KRITIQ backend REST APIs.

---

## 1. Authentication & JWT Session Flow

All protected endpoints require callers to pass a JSON Web Token (JWT) using the HTTP standard `Authorization` header.

### Authorization Header Format:
```http
Authorization: Bearer <access_token_value>
```

### JWT Expiration & Lifespan:
* Access tokens expire by default after **15 minutes** (configured via `TOKEN_EXPIRE_MINUTES` in the `.env` settings file).
* If a token is expired, malformed, or has an invalid signature, the backend will return a `401 Unauthorized` status response.

---

## 2. Typical Integration Workflows

### Workflow A: Registration & Session Initialization
1. Send a request containing display name, email, and password to `/auth/register`.
2. Backend validates that email is unique and password is at least 8 characters.
3. Hashed password is saved in MongoDB and a session token is issued instantly.
4. Store the returned `access_token` in local storage or session context.

#### Register Request JSON:
```json
{
  "name": "User Name",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Register Response JSON:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Workflow B: Traditional User Login
1. Submit email and password to `/auth/login`.
2. If authenticated, extract the returned `access_token` and configure your API header client.

#### Login Request JSON:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Login Response JSON:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Workflow C: Review Code & Log History
1. Perform a `POST` request to `/reviews/` with code, language, and filename.
2. Backend calls the Gemini AI Review service, parses code quality issues, saves the review record, and automatically inserts an activity log in the user's history collection.
3. Use the returned `review_id` to link to the detailed review page, or fetch it again later using `GET /reviews/{review_id}`.

#### Code Review Request JSON:
```json
{
  "code": "def check(val):\n  if val == None: return False",
  "language": "python",
  "filename": "checker.py"
}
```

#### Code Review Response JSON:
```json
{
  "review_id": "aa82e389-9831-4e0d-a02c-7b94b0dfa12d",
  "summary": "Found 1 naming issue and 1 comparison suggestion.",
  "issues": [
    {
      "title": "Use is comparison",
      "explanation": "Compare to None using 'is' instead of '=='",
      "suggested_fix": "if val is None:",
      "severity": "low",
      "line": 2
    }
  ],
  "raw_output": "Summary: ... Issues: ..."
}
```

---

### Workflow D: Translate Code
1. Perform a `POST` request to `/translations/` specifying source/target languages and code.
2. The AI translates the logic, returns the code, and creates an activity log.

#### Translate Request JSON:
```json
{
  "source_code": "print('hello')",
  "source_language": "python",
  "target_language": "java"
}
```

#### Translate Response JSON:
```json
{
  "translation_id": "df61e389-9831-4e0d-a02c-7b94b0dfa72d",
  "translated_code": "System.out.println(\"hello\");",
  "notes": "Successfully translated from python to java."
}
```

---

### Workflow E: Explain Code Block
1. Perform a `POST` request to `/explanations/explain`.
2. Hitting the endpoint registers an activity log and returns a detailed string.

#### Explanation Request JSON:
```json
{
  "code": "y = list(filter(lambda x: x % 2 == 0, range(10)))",
  "language": "python"
}
```

#### Explanation Response JSON:
```json
{
  "explanation": "This python snippet filters numbers from 0 to 9, returning only the even elements inside a list..."
}
```

---

### Workflow F: View User Activity History Logs
1. Fetch `GET /history/?limit=10&skip=0` to list all code review, explanation, and translation activities performed by the user.
2. You can query `details.review_id` or `details.translation_id` inside each item to fetch the corresponding full analytical payloads from `/reviews/{review_id}` or `/translations/{translation_id}`.

#### History Response JSON:
```json
{
  "history": [
    {
      "id": "history-uuid-1",
      "type": "review",
      "timestamp": "2026-07-16T19:51:47Z",
      "summary": "Reviewed python file: checker.py",
      "details": {
        "review_id": "aa82e389-9831-4e0d-a02c-7b94b0dfa12d",
        "issues_count": 1
      }
    }
  ]
}
```
