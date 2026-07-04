# Sayeed domain - Hashing and verification utils
# TODO: Integrate passlib or bcrypt for secure hashing

def hash_password(password: str) -> str:
    # Placeholder return of string
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return f"hashed_{plain_password}" == hashed_password
