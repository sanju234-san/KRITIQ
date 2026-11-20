import httpx
c = httpx.Client(follow_redirects=False, timeout=5)

r = c.get("http://127.0.0.1:8000/")
print("ROOT HTTP", r.status_code, ":", r.text)

r2 = c.get("http://127.0.0.1:8000/auth/github")
print("/auth/github HTTP", r2.status_code)
loc = r2.headers.get("location")
print("  Location:", loc)

# email/password login smoke
import uuid, json
email = "local-test-" + uuid.uuid4().hex[:8] + "@example.com"
pwd = "Test1234!"
name = "Local Test"
r_reg = c.post("http://127.0.0.1:8000/auth/register", json={"name":name,"email":email,"password":pwd})
print("REGISTER HTTP", r_reg.status_code, ":", r_reg.text[:200])
if r_reg.status_code == 200:
    tok = r_reg.json()["access_token"]
    print("  Token len:", len(tok))
    r_prof = c.get("http://127.0.0.1:8000/auth/profile", headers={"Authorization":"Bearer " + tok})
    print("PROFILE HTTP", r_prof.status_code, ":", r_prof.text[:200])

    r_logout = c.post("http://127.0.0.1:8000/auth/logout")
    print("LOGOUT HTTP", r_logout.status_code, ":", r_logout.text[:120])

    # After logout token still works (JWT stateless) for remaining lifetime, that's expected.
    # Try without auth:
    r_nopro = c.get("http://127.0.0.1:8000/auth/profile")
    print("PROFILE (no token) HTTP", r_nopro.status_code, ":", r_nopro.text[:200])

    # Re-login
    r_login = c.post("http://127.0.0.1:8000/auth/login", json={"email":email,"password":pwd})
    print("RE-LOGIN HTTP", r_login.status_code, ":", r_login.text[:120])

    # Protected /repositories/ with auth
    tok2 = r_login.json()["access_token"] if r_login.status_code == 200 else tok
    r_repo = c.get("http://127.0.0.1:8000/repositories/", headers={"Authorization":"Bearer " + tok2})
    print("/repositories (auth) HTTP", r_repo.status_code, ":", r_repo.text[:200])

    # /repositories/ without auth
    r_norepo = c.get("http://127.0.0.1:8000/repositories/")
    print("/repositories (no auth) HTTP", r_norepo.status_code, ":", r_norepo.text[:200])

# CORS preflight
h = {"Origin":"http://localhost:5173", "Access-Control-Request-Method":"POST", "Access-Control-Request-Headers":"content-type,authorization"}
r3 = c.options("http://127.0.0.1:8000/auth/login", headers=h)
print("OPTIONS /auth/login HTTP", r3.status_code)
print("  ACAO:", r3.headers.get("access-control-allow-origin"))
print("  ACAC:", r3.headers.get("access-control-allow-credentials"))
print("  ACAM:", r3.headers.get("access-control-allow-methods"))

# OTC exchange with bad code
r_bad_otc = c.post("http://127.0.0.1:8000/auth/github/exchange", json={"code":"kr-not-valid-xyz"})
print("/auth/github/exchange (junk) HTTP", r_bad_otc.status_code, ":", r_bad_otc.text[:200])

# Clean up
try:
    from app.db.mongo_client import db_client
    db_client.get_collection("users").delete_one({"email": email})
    print("CLEANUP: deleted user", email)
except Exception:
    pass
print("\nALL BACKEND API SMOKE TESTS COMPLETE")
