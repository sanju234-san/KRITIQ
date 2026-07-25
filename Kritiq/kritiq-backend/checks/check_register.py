from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.post(
    "/auth/register",
    json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password@123"
    }
)

print(response.status_code)
print(response.json())
