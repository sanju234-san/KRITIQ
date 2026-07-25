from fastapi.testclient import TestClient
from app.main import app
from fastapi.routing import APIRoute

client = TestClient(app)

print("=" * 60)
print("OpenAPI Schema Checker")
print("=" * 60)

# Compile routes by triggering openapi generation
response = client.get("/openapi.json")
if response.status_code != 200:
    print("[ERROR] Failed to retrieve /openapi.json")
    exit()

openapi = response.json()
print("[SUCCESS] OpenAPI schema generated successfully")

missing_summaries = []
missing_descriptions = []

# Resolve routes recursively
all_routes = []
for r in app.routes:
    if type(r).__name__ == "APIRoute":
        all_routes.append(r)
    elif type(r).__name__ == "_IncludedRouter":
         for sub_r in r.original_router.routes:
              if type(sub_r).__name__ == "APIRoute":
                   all_routes.append(sub_r)

for r in all_routes:
    if r.path in ("/openapi.json", "/docs", "/redoc", "/"):
        continue
    
    if not r.summary or r.summary.strip() == "":
        missing_summaries.append(r.path)
    if not r.description or r.description.strip() == "":
        missing_descriptions.append(r.path)

print(f"\nTotal routes analyzed: {len(all_routes)}")

if missing_summaries:
    print("\n[ERROR] Routes missing Summary:")
    for path in missing_summaries:
        print(f"  - {path}")
else:
    print("[SUCCESS] All routes have summaries")

if missing_descriptions:
    print("\n[ERROR] Routes missing Description:")
    for path in missing_descriptions:
         print(f"  - {path}")
else:
    print("[SUCCESS] All routes have descriptions")
