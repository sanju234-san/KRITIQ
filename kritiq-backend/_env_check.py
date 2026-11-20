import os
from dotenv import load_dotenv

load_dotenv(".env")

keys = [
    "MONGODB_URI", "DATABASE_NAME",
    "GEMINI_API_KEY", "GROQ_API_KEY", "GITHUB_TOKEN",
    "JWT_SECRET", "JWT_ALGORITHM", "TOKEN_EXPIRE_MINUTES",
    "FRONTEND_URL",
    "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET",
    "GITHUB_REDIRECT_URI", "GITHUB_OAUTH_SCOPES",
    "PORT", "HOST",
]

for k in keys:
    v = os.environ.get(k)
    if v:
        status = "CONFIGURED"
        if k == "GITHUB_REDIRECT_URI":
            status += f" (value: {v})"
        print(f"{k}: {status}")
    else:
        print(f"{k}: MISSING")
