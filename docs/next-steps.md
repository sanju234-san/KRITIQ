# Next Steps & Implementation Roadmap

This document outlines the immediate implementation roadmap for each team member (**Dev**, **Sayeed**, and **Sanjeevni**) following the successful setup of JWT authentication and base scaffolding.

---

## 1. Member 1 — Dev (Frontend Tasks)

### Connect Authentication Flow
* Integrate the visual stubs in `Login.jsx` and `Register.jsx` to call `authApi.login` and `authApi.register`.
* Save the returned JWT token to `localStorage` (via the `AuthContext.jsx` state manager) so that Axios interceptors automatically attach it to authenticated API requests.

### Form Submissions & Results
* **Review Submission**: Wire the `ReviewSubmit.jsx` page to accept code inputs (via Monaco Editor), select target languages, and POST to the backend `/reviews` endpoint. Display outputs dynamically in `ReviewResult.jsx` utilizing the `IssueList` component.
* **Translation**: Wire `TranslationSubmit.jsx` to accept code inputs, choose source/target language maps, POST to `/translations`, and render outputs inside `TranslationResult.jsx` utilizing Monaco Editor.
* **History Page**: Connect `History.jsx` to fetch recent activities from the backend `/history` endpoint and render them in a clean table layout.

---

## 2. Member 2 — Sayeed (Backend Tasks)

### Database Repositories
* **Implement Repositories**: Complete PyMongo write/read queries in `app/db/` for:
  * `repositories_repo.py` (fetching/adding GitHub connections)
  * `reviews_repo.py` (saving and fetching review logs)
  * `translations_repo.py` (saving and fetching translation outputs)
  * `history_repo.py` (storing user activity log events)

### Route Implementations
* **Review Route (`review_routes.py`)**: Update the endpoint to call Sanjeevni's `review_service.run_review(code, language)`. Once completed:
  1. Save results to the database using `reviews_repo.save_review`.
  2. Log the activity using `history_repo.log_activity`.
  3. Return the response.
* **Translation Route (`translation_routes.py`)**: Update to call Sanjeevni's `translation_service.run_translation(code, source_lang, target_lang)`. Save to `translations_repo`, log to history, and return.
* **Explanation Route (`explanation_routes.py`)**: Connect to Sanjeevni's `explanation_service.run_explanation(code, issue_id)`.

---

## 3. Member 3 — Sanjeevni (AI, RAG, & Tools Tasks)

### RAG Pipeline & Custom Dataset
* **Dataset entries**: Populate JSON arrays under `dataset/processed/` (such as `bugs.json`, `security.json`, etc.) with good and bad coding practice snippets.
* **Retriever (`rag_pipeline/retriever.py`)**: Write queries to search the MongoDB `dataset_examples` collection for top-k matching code snippets based on vector embeddings similarity.
* **Grounding Prompts**: Integrate the retrieved RAG examples and MCP file contents inside prompt constructions in `review_service.py` and `translation_service.py` to grounding Gemini's reasoning.

### Repository Integration
* Complete GitPython cloning operations in `repo_integration/local_clone.py` to pull repository branches and list directory contents dynamically for private repos (using the `GITHUB_TOKEN` credentials).

---

## 4. Collaborative Sync Points
1. **anyio Conflict**: Coordinate on requirement conflicts in `requirements.txt` to align pins for deployment.
2. **Staging Merges**: Raise pull requests from personal branches to the `dev` branch daily, checking for folder structure boundaries and resolving file conflicts locally.
