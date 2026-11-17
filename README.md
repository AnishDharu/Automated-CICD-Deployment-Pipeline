# Tasks API — CI/CD Deployment Pipeline

A Flask REST API with a fully automated CI/CD pipeline built using GitHub Actions, Docker, Trivy, and AWS EC2.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | PostgreSQL |
| Testing | pytest, pytest-cov |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Security | Trivy vulnerability scanner |
| Registry | Docker Hub |
| Deployment | Render (PaaS) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task — body: `{"title": "..."}` |
| PUT | `/tasks/<id>` | Update status — body: `{"done": true}` |

## CI/CD Pipeline

Every push to `main` triggers a 5-stage pipeline:

```
TEST → BUILD → SCAN → PUSH → DEPLOY
```

| Stage | Tool | Action | Fails if |
|-------|------|--------|----------|
| Test | pytest + Postgres service container | Run unit tests with coverage | Coverage < 70% |
| Build | Docker | Build image tagged with commit SHA | Dockerfile error |
| Scan | Trivy | Scan image for vulnerabilities | CRITICAL CVE found |
| Push | Docker Hub | Push SHA-tagged + latest image | Auth failure |
| Deploy | Render deploy hook | Trigger redeploy from GitHub repo | Render unreachable |

### Pipeline Diagram

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  TEST   │────▶│  BUILD  │────▶│  SCAN   │────▶│  PUSH   │────▶│ DEPLOY  │
│ pytest  │     │ docker  │     │  trivy  │     │ docker  │     │  curl   │
│ postgres│     │  build  │     │  scan   │     │  push   │     │ render  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
     ❌              ❌              ❌
  <70% cov      build fail     CRITICAL vuln
  = stop         = stop          = stop
```

## Project Structure

```
├── app.py                        # Flask REST API
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container image (non-root user)
├── docker-compose.yml            # API + Postgres multi-container setup
├── .dockerignore                 # Excludes tests, .git from image
├── .gitignore                    # Excludes .env, __pycache__ from repo
├── ec2-setup.sh                  # One-time EC2 server setup
├── rollback.sh                   # Emergency rollback to previous SHA
├── tests/
│   ├── conftest.py               # Test fixtures + DB cleanup
│   └── test_api.py               # 7 tests covering all endpoints
└── .github/
    └── workflows/
        └── ci.yml                # GitHub Actions CI/CD pipeline
```

## Setup

### Prerequisites
- GitHub account
- Docker Hub account + access token
- Render account (free — [render.com](https://render.com))

### 1. Clone and push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USER/Automated-CICD-Deployment-Pipeline.git
git push -u origin main
```

### 2. Set up Render
1. Create a **PostgreSQL** database (free tier)
2. Create a **Web Service** from this GitHub repo (Docker runtime)
3. Set `DATABASE_URL` environment variable (Internal Database URL)
4. Turn **Auto-Deploy OFF**
5. Copy the **Deploy Hook URL** from Settings

### 3. Add GitHub Secrets
Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USER` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `RENDER_DEPLOY_HOOK` | Render deploy hook URL |

### 4. Trigger the pipeline
```bash
git push origin main
# Watch at: GitHub → Actions tab
```

### 5. Verify
```bash
curl https://tasks-api-xxxx.onrender.com/health
# → {"status": "ok"}
```

## Author

**Anish Dharu** — Final Year MCA
