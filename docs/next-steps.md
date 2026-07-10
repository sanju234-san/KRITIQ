# Next Steps & Implementation Roadmap

Now that the **Backend Core (JWT Auth, MongoDB Repositories, Review/Translation/Explanation Routes, and Unit Tests)** is fully completed, here are the updated tasks for each team member:

---

## 1. Dev (Frontend Tasks) — Priority: High
The backend endpoints are ready and fully tested. Dev should now wire the React frontend to the backend:

### Authentication Integration
* **Login & Register**: Wire `Login.jsx` and `Register.jsx` to make POST requests to `/auth/login` and `/auth/register`. On success, store the JWT token in `localStorage`.
* **Session Restoration**: On app load, check for the token, fetch `/auth/profile`, and update the state in `AuthContext.jsx`.

### Core Features Integration
* **Code Review**: Connect `ReviewSubmit.jsx` to POST code and language to `/reviews/`. Render the structured issues from `ReviewResponse` (e.g. mapping severity, lines, explanation, and title) on `ReviewResult.jsx`.
* **Code Translation**: Connect `TranslationSubmit.jsx` to POST source code and target language configurations to `/translations/`. Display the generated translation in the target Monaco Editor on `TranslationResult.jsx`.
* **Activity & History**: Connect `History.jsx` to fetch and render user records from `/history`, `/history/reviews`, and `/history/translations` in a clean dashboard table.

---

## 2. Sanjeevni (AI, RAG, & Git Integration Tasks) — Priority: High
With the core AI route skeletons fully operational, Sanjeevni should now build out the AI context gathering layers:

### Vector RAG Pipeline
* **Local Embeddings**: Implement vector embedding Generation for raw dataset items in `rag_pipeline/embeddings.py`.
* **Context Retriever**: Code similarity-search matches in `rag_pipeline/retriever.py` to fetch top-k similar coding examples from the database to ground Gemini prompts.
* **Integrate with Services**: Update the Gemini prompts in `review_service.py` to inject these matched examples dynamically.

### GitHub Repository Integration
* **Local Cloner**: Complete the GitPython clone logic in `repo_integration/local_clone.py` to download target branches locally.
* **GitHub API Reader**: Use the `GITHUB_TOKEN` to read private repo files/branches inside `repo_integration/github_api.py`.

---

## 3. Sayeed (Backend Tasks) — Priority: Support
The backend core routes, repositories, JWT flow, and unit tests are complete:
* Sayeed should push the branch changes, and stand by to help **Sanjeevni** merge her cloner/RAG pipeline or assist **Dev** with any endpoint questions or frontend integration issues.
