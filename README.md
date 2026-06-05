# KRITIQ — Project Document

**The autonomous code review & fixer agent**

- Timeline: 2–3 weeks
- Stack: FastAPI · LangGraph · Groq · React
- Storage: MongoDB Atlas
- Deployment: Render.com · GitHub Pages
- Cost: 100% free

---

## 1. Overview

**Code reviewer** — Fetches every file in a GitHub repo, analyzes each for bugs, code smells, and anti-patterns using Llama 3 via Groq. Flags issues with file path, line number, severity, and suggested fix.

**Security auditor** — Runs in parallel with the reviewer. Scans for hardcoded secrets, SQL/command injections, insecure dependencies, and OWASP Top 10 patterns.

**Auto fixer** — For each flagged issue, generates a validated fix, applies it to the file, and commits it back to the repo branch via PyGithub with a conventional commit message.

**README writer** — Generates a production-grade README.md with project description, setup instructions, tech stack, live screenshots, and the auto-generated UML diagram embedded inline.

**Screenshot + UML** — Captures a screenshot of the live deployed URL using Playwright headless Chromium. Generates Mermaid UML syntax from the codebase and renders it to PNG, then commits both to the repo.

**Summary report** — Produces a structured ReviewReport saved to MongoDB and streamed to the React dashboard. Posts a formatted review comment on the GitHub PR with all flags, fixes, and links.

---

## 2. Tech Stack

**Agent core:** Python 3.11, LangGraph (state machine), LangChain (LLM wrappers), Groq API (Llama 3.3-70B free), Pydantic v2

**Backend:** FastAPI, Uvicorn, Motor (async MongoDB), PyGithub, python-dotenv

**Capture:** Playwright, Mermaid CLI, Chromium (headless)

**Frontend:** React 18 + Vite, TypeScript, Tailwind CSS, Zustand, TanStack Query

**Storage:** MongoDB Atlas (free 512MB), Motor async driver. Ensure to set MONGODB_URI as an environment variable for secure credential handling.

**Deploy:** Docker, Render.com (free backend), GitHub Pages (free frontend), GitHub Actions (CI)

---

## 3. UML Diagrams

### UML 01 — Class Diagram

12 classes. `BaseAgent` is abstract — 5 agents extend it. `ReviewReport` is the central output aggregating all flags, fixes, screenshots, and UML path. `MongoRepository` and `GitHubService` are infrastructure adapters kept outside the agent layer.

```mermaid
classDiagram
    direction TB

    class GitHubWebhook {
        +parse_payload() WebhookPayload
        +validate_signature() bool
    }
    class WebhookPayload {
        +String repo_url
        +String commit_sha
        +String live_url
    }
    class KritiqOrchestrator {
        +run_pipeline() ReviewReport
        +route_agents()
    }
    class BaseAgent {
        <<abstract>>
        +run(LangGraphState) LangGraphState
    }
    class CodeReviewerAgent {
        +analyze_file() List~FlaggedIssue~
    }
    class SecurityAuditorAgent {
        +scan_secrets() List~FlaggedIssue~
        +check_injections() List~FlaggedIssue~
    }
    class AutoFixerAgent {
        +generate_fix(FlaggedIssue) Fix
        +commit_fix(Fix) String
    }
    class ReadmeWriterAgent {
        +generate_readme() String
    }
    class ScreenshotUMLAgent {
        +capture_screenshot() String
        +generate_mermaid() String
    }
    class FlaggedIssue {
        +String file_path
        +int line_number
        +String severity
        +String category
    }
    class Fix {
        +String original_code
        +String fixed_code
        +String commit_sha
    }
    class ReviewReport {
        +List~FlaggedIssue~ flags
        +List~Fix~ fixes
        +String uml_path
        +String summary
    }
    class MongoRepository {
        +save_report(ReviewReport)
        +get_report(String) ReviewReport
    }
    class GitHubService {
        +fetch_files() List~str~
        +commit_readme()
        +post_review_comment()
    }

    GitHubWebhook --> WebhookPayload : parses
    WebhookPayload --> KritiqOrchestrator : triggers
    KritiqOrchestrator --> GitHubService : uses
    KritiqOrchestrator --> MongoRepository : uses
    KritiqOrchestrator --> ReviewReport : produces
    BaseAgent <|-- CodeReviewerAgent
    BaseAgent <|-- SecurityAuditorAgent
    BaseAgent <|-- AutoFixerAgent
    BaseAgent <|-- ReadmeWriterAgent
    BaseAgent <|-- ScreenshotUMLAgent
    KritiqOrchestrator --> BaseAgent : orchestrates
    CodeReviewerAgent --> FlaggedIssue : produces
    SecurityAuditorAgent --> FlaggedIssue : produces
    AutoFixerAgent --> Fix : produces
    ReviewReport --> FlaggedIssue : contains
    ReviewReport --> Fix : contains
    MongoRepository --> ReviewReport : persists
    GitHubService --> Fix : commits
```

---

### UML 02 — Sequence Diagram

24 numbered steps from GitHub webhook to final 200 OK. The `alt/else` block models the conditional fixer path — if no issues are flagged the AutoFixerAgent is skipped entirely and the pipeline continues to screenshot and README generation.

```mermaid
sequenceDiagram
    autonumber
    participant GH as GitHub
    participant API as FastAPI
    participant OR as Orchestrator
    participant Agents as Agents (CR + SA)
    participant AF as AutoFixer
    participant SU as Screenshot+UML
    participant RW as ReadmeWriter
    participant GS as GitHubService
    participant DB as MongoDB

    GH->>API: POST /webhook
    API->>API: validate HMAC signature
    API->>OR: trigger_pipeline(payload)
    OR->>GS: fetch_files(repo_url)
    GS-->>OR: List[FileContent]

    OR->>Agents: run CodeReviewer + SecurityAuditor (parallel)
    Agents-->>OR: List[FlaggedIssue]

    alt issues found
        OR->>AF: generate_fix() per issue
        AF->>GS: commit_fix()
        GS-->>AF: commit_sha
        AF-->>OR: List[Fix]
    else no issues
        OR->>OR: skip AutoFixer
    end

    OR->>SU: capture_screenshot + generate_mermaid
    SU-->>OR: screenshot_paths + uml_path

    OR->>RW: generate_readme (with screenshots + UML)
    RW-->>OR: readme_content

    OR->>GS: commit_readme + commit_uml
    OR->>GS: post_review_comment(flags + fixes)

    OR->>DB: save_report(ReviewReport)
    DB-->>OR: report_id
    OR-->>API: ReviewReport
    API-->>GH: 200 OK + report_id
```

---

### UML 03 — Activity Diagram

Full branching logic. CodeReviewer and SecurityAuditor fork in parallel via LangGraph. AutoFixer has a retry loop — if a generated fix fails validation it regenerates. Screenshot capture is conditional on whether a live URL was provided. All paths converge before MongoDB save and React dashboard stream.

```mermaid
flowchart TD
    START([GitHub push or PR event]) --> WH[FastAPI receives webhook]
    WH --> VS{Signature valid?}
    VS -- No --> REJ([Reject 401])
    VS -- Yes --> FP[Parse WebhookPayload]
    FP --> FF[GitHubService fetch all repo files]
    FF --> IG[Filter ignored files .gitignore]
    IG --> FORK1[ ]
    FORK1 --> CR[CodeReviewerAgent runs per file]
    FORK1 --> SA[SecurityAuditorAgent scans secrets and injections]
    CR --> CRR[List of FlaggedIssues — code quality]
    SA --> SAR[List of FlaggedIssues — security]
    CRR --> JOIN1[ ]
    SAR --> JOIN1
    JOIN1 --> AF1{Any issues flagged?}
    AF1 -- No --> SKIP[Skip AutoFixerAgent]
    AF1 -- Yes --> AF[AutoFixerAgent per issue]
    AF --> GF[generate_fix via Groq Llama 3]
    GF --> VF{Fix valid?}
    VF -- No, retry --> GF
    VF -- Yes --> CF[commit_fix to GitHub branch]
    CF --> FL[List of Fix objects with commit SHA]
    SKIP --> MERGE1[ ]
    FL --> MERGE1
    MERGE1 --> SU[ScreenshotUMLAgent]
    SU --> GM[generate_mermaid syntax from codebase]
    GM --> RP[render_uml_png via Playwright]
    RP --> LU{Live URL provided?}
    LU -- Yes --> SC[capture_screenshot via Playwright headless]
    LU -- No --> NSC[Skip screenshot step]
    SC --> MERGE2[ ]
    NSC --> MERGE2
    MERGE2 --> RW[ReadmeWriterAgent]
    RW --> GR[generate_readme from LangGraphState]
    GR --> ES[embed_screenshots into README]
    ES --> EU[embed_uml diagram into README]
    EU --> CR2[commit README to repo via GitHubService]
    CR2 --> CU[commit UML PNG to repo via GitHubService]
    CU --> PC[post_review_comment on PR with flags and fixes]
    PC --> BR[build ReviewReport object]
    BR --> MG[save_report to MongoDB Atlas]
    MG --> RS[stream report to React Dashboard]
    RS --> END([Pipeline complete])
```

---

## 4. Build Timeline

**Week 01 — Days 1–7: Foundation**
- Day 1–2: Init monorepo — FastAPI skeleton, Vite + React frontend, docker-compose.yml, .env.example
- Day 2–3: GitHub webhook endpoint — validate HMAC signature, parse WebhookPayload with Pydantic, test with ngrok
- Day 3–4: GitHubService — fetch all repo files via PyGithub, filter .gitignore patterns, commit back helper
- Day 4–5: BaseAgent abstract class + CodeReviewerAgent — Groq client, streaming prompt, Pydantic output parsing
- Day 5–6: SecurityAuditorAgent — secret patterns, injection checks, parallel run with reviewer via LangGraph fork
- Day 6–7: MongoDB Atlas setup, MongoRepository with Motor async, save and retrieve FlaggedIssue documents
- Deliverable: webhook triggers, files fetched, flags saved to MongoDB

**Week 02 — Days 8–14: Core agents**
- Day 8–9: AutoFixerAgent — generate fix prompt, validate with retry loop (max 3), commit fix via GitHubService
- Day 9–10: LangGraph full state machine — wire all 5 agents, implement conditional routing, test end-to-end pipeline locally
- Day 10–11: ScreenshotUMLAgent — Playwright install, capture_screenshot() with full-page PNG, generate_mermaid() from LangGraph state via Llama 3
- Day 11–12: Mermaid CLI render pipeline — LLM outputs Mermaid syntax → mmdc CLI renders PNG → save to temp → commit to docs/uml.png
- Day 12–13: ReadmeWriterAgent — full README template, embed screenshots and UML, commit as README.md
- Day 13–14: Post GitHub PR review comment via PyGithub create_review()
- Deliverable: full pipeline runs end-to-end on a real GitHub repo

**Week 03 — Days 15–21: Dashboard, deployment, polish**
- Day 15–16: React dashboard — repo input, trigger KRITIQ manually, Zustand store, TanStack Query polling
- Day 16–17: Dashboard UI — live agent progress stepper, flagged issues table, fixes diff view
- Day 17–18: FastAPI streaming endpoint — GET /pipeline/stream using StreamingResponse + Server-Sent Events, React useEventSource hook
- Day 18–19: Dockerfile — multi-stage build, install Playwright + Chromium inside container, test on Render.com
- Day 19–20: GitHub Actions CI — on push to main: run tests, build Docker image, deploy to Render.com; deploy React to GitHub Pages
- Day 20–21: Final testing on 3 real repos, README polish, record demo GIF, add to portfolio
- Deliverable: KRITIQ live at Render URL, dashboard on GitHub Pages, tested on real repos

---

## 5. Project Structure

```
kritiq/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/webhooks.py        # GitHub webhook handler
│   │   │   └── v1/reports.py         # ReviewReport CRUD + stream
│   │   ├── agents/
│   │   │   ├── base.py               # BaseAgent abstract class
│   │   │   ├── code_reviewer.py
│   │   │   ├── security_auditor.py
│   │   │   ├── auto_fixer.py
│   │   │   ├── readme_writer.py
│   │   │   └── screenshot_uml.py
│   │   ├── core/
│   │   │   ├── config.py             # pydantic-settings
│   │   │   └── orchestrator.py       # LangGraph state machine
│   │   ├── services/
│   │   │   ├── github_service.py     # PyGithub wrapper
│   │   │   └── mongo_repository.py   # Motor async MongoDB
│   │   ├── schemas/
│   │   │   ├── webhook.py            # WebhookPayload
│   │   │   ├── issue.py              # FlaggedIssue, Fix
│   │   │   └── report.py             # ReviewReport
│   │   └── main.py                   # FastAPI app, lifespan, routers
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/               # AgentStepper, IssueTable, DiffView
│   │   ├── pages/                    # Dashboard.tsx, Report.tsx
│   │   ├── hooks/                    # useEventSource, useReport
│   │   ├── store/                    # Zustand pipeline state
│   │   └── types/                    # ReviewReport, FlaggedIssue TS types
│   ├── vite.config.ts
│   └── package.json
├── .github/
│   └── workflows/
│       └── deploy.yml                # CI — test, build, deploy
├── docker-compose.yml
├── .env.example
└── README.md                         # auto-generated by KRITIQ itself
```

---

## 6. API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /webhook/github | POST | Receives GitHub push/PR webhook, validates HMAC, triggers pipeline |
| /pipeline/run | POST | Manual trigger — accepts repo_url + optional live_url, runs full pipeline |
| /pipeline/stream/{report_id} | GET | SSE stream — emits agent step events as pipeline runs in background |
| /reports | GET | List all ReviewReports for a repo, paginated, sorted by created_at desc |
| /reports/{report_id} | GET | Fetch a single ReviewReport with all flags, fixes, paths |
| /reports/{report_id}/summary | GET | Returns LLM-generated plain-English summary of the review |
| /health | GET | Health check — returns status of MongoDB, Groq API, GitHub token |

---

## 7. MongoDB Schema

**Collection: review_reports**

| Field | Type | Description |
|---|---|---|
| _id | ObjectId | auto-generated |
| repo_url | String | GitHub repo full URL |
| commit_sha | String | SHA that triggered the review |
| flags | Array[FlaggedIssue] | embedded documents |
| fixes | Array[Fix] | embedded documents |
| readme_path | String | path in repo to committed README |
| screenshot_paths | Array[String] | paths in repo to committed PNGs |
| uml_path | String | path in repo to committed UML PNG |
| summary | String | LLM-generated plain-English summary |
| status | Enum | pending · running · complete · failed |
| created_at | DateTime | UTC timestamp |

**Embedded: FlaggedIssue**

| Field | Type | Description |
|---|---|---|
| id | String | uuid4 |
| file_path | String | relative path in repo |
| line_number | Int | line where issue starts |
| severity | Enum | critical · high · medium · low · info |
| category | Enum | security · bug · style · performance · docs |
| description | String | human-readable explanation |
| suggested_fix | String | LLM suggested fix before auto-fixer runs |

---

## 8. Environment Variables

```
# Groq (free tier — llama-3.3-70b-versatile)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# GitHub Personal Access Token (repo + webhook scope)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# MongoDB Atlas (free cluster)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/kritiq
MONGODB_DB_NAME=kritiq

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:5173
```

---

*Blueprint v1.0 · Sanjeevni Dhir · 2026*
