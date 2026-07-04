# Git Workflow & Branch Management Guide

This guide outlines how our team members (**Dev**, **Sayeed**, and **Sanjeevni**) should coordinate developments, manage branches, and safely integrate updates without causing conflicts.

---

## 1. Branch Structure & Roles

We maintain five primary branches in the repository:

| Branch Name | Type | Purpose | Owner / Contributor |
| :--- | :--- | :--- | :--- |
| `main` | Protected | Production-ready stable codebase. | All (Release only) |
| `dev` | Integration | Active staging/integration branch where team features meet. | All |
| `dev-frontend` | Feature | Frontend developments. | Dev |
| `sayeed-backend` | Feature | Core FastAPI application & database developments. | Sayeed |
| `sanjeevni-ai` | Feature | AI agents, prompts, RAG client, MCP server, and CLI tools. | Sanjeevni |

---

## 2. Directory Boundaries (Who Works Where)

To prevent code overrides and merge conflicts, each member must strictly stick to their designated folder scopes:

* **Dev Domain**:
  * `kritiq-frontend/**`
* **Sayeed Domain**:
  * `kritiq-backend/app/**`
* **Sanjeevni Domain**:
  * `kritiq-backend/ai_agent/**`
  * `kritiq-backend/mcp_server/**`
  * `kritiq-backend/rag_pipeline/**`
  * `kritiq-backend/dataset/**`
  * `kritiq-backend/repo_integration/**`
  * `kritiq-backend/cli/**`

### Shared Files (Requires Discussion Before Modifying)
Avoid changing these files without aligning with other members:
* `.gitignore`
* `README.md`
* `docs/**`
* `kritiq-backend/requirements.txt`
* `kritiq-backend/.env.example`
* `kritiq-backend/app/main.py` (FastAPI router registrations)

---

## 3. Daily Git Workflow

Follow these steps every day to keep your local environment up to date and push features safely.

### Step A: Sync your local `dev` branch
Before writing any code, fetch the latest changes from other team members:
```bash
git checkout dev
git pull origin dev
```

### Step B: Merge `dev` into your personal branch
Switch to your working branch and bring in any new updates:
```bash
# Replace with: dev-frontend, sayeed-backend, or sanjeevni-ai
git checkout sayeed-backend  
git merge dev
```
*Resolve any conflicts locally in your editor.*

### Step C: Build and Commit your changes
Work only within your designated folders. Commit with clean, descriptive messages:
```bash
git add kritiq-backend/app/routes/review_routes.py
git commit -m "feat(routes): Add review route handler stub"
```

### Step D: Push changes to GitHub
Push your local branch commits to the remote:
```bash
git push origin sayeed-backend
```

---

## 4. Pull Requests (PR) & Merging

When your features are ready for integration:

1. **Open a PR on GitHub**:
   * Target branch: `dev`
   * Source branch: Your feature branch (e.g. `sayeed-backend` $\rightarrow$ `dev`)
2. **Review & Approve**:
   * Have at least one other team member check your changes (specifically checking that you did not accidentally modify files outside your domain).
3. **Merge**:
   * Once approved, merge the PR into `dev`.
4. **Deploy Staging / Verification**:
   * Verify that the combined code on `dev` compiles and runs successfully.
5. **Release to `main`**:
   * Once features are tested and stable on `dev`, merge `dev` $\rightarrow$ `main` to create a production release.
