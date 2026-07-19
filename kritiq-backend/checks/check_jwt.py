import os
from dotenv import load_dotenv
from app.auth.jwt_handler import create_access_token, decode_access_token

load_dotenv()

secret = os.getenv("JWT_SECRET", "mock-secret")

print("=" * 60)
print("JWT Security Checker")
print("=" * 60)

print(f"JWT_SECRET Length: {len(secret)} bytes")

if len(secret) < 32:
    print("[WARNING] JWT_SECRET is too short!")
    print("   Recommended key length for HMAC-SHA256 is at least 32 bytes (256 bits).")
    print("   A weak key makes your tokens vulnerable to brute-force attacks.")
    print("   Please update your .env with a secure random key.")
else:
    print("[SUCCESS] JWT_SECRET length is secure (>= 32 bytes)")

print("\nTesting Token Lifecycle:")
try:
    test_payload = {"sub": "test@example.com"}
    token = create_access_token(data=test_payload)
    print(f"  Token Generated: {token[:40]}...")
    
    decoded = decode_access_token(token)
    print(f"  Token Decoded: {decoded}")
    
    if decoded and decoded.get("sub") == "test@example.com":
         print("[SUCCESS] JWT Token Lifecycle Works Properly!")
    else:
         print("[ERROR] Decoded payload mismatch or invalid.")
except Exception as e:
    print(f"[ERROR] Error during token verification: {e}")
