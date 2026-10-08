# Kritiq review parsing fix

This patch fixes malformed AI review issue rendering.

## What changed
- AI review prompt now requires strict JSON.
- Gemini requests JSON MIME output.
- Groq requests JSON object output.
- Added Pydantic validation for structured AI review data.
- Added a robust parser with legacy Markdown fallback.
- Added regression tests for structured JSON, fenced JSON, null lines, multiple issues, and the malformed Markdown shown in the UI.
- Added frontend title sanitization as a defensive compatibility layer for older stored reviews.

## Apply
Copy the files in this package into the corresponding paths in the Kritiq project.

## Verification
- `tests/test_review_parser.py`: 5/5 passed in the provided environment.
- Full backend route test collection could not run in this container because `pymongo` is not installed.
- Frontend build could not complete in this container because the supplied `node_modules` is missing Rollup's Linux optional native package. Run `npm install`/`npm ci` in `kritiq-frontend` on the development machine, then `npm run build`.

No `.env`, secrets, `.git`, `node_modules`, or build artifacts are included in this patch.
