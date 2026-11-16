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
| Deployment | AWS EC2 (Ubuntu) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task — body: `{"title": "..."}` |

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
| Deploy | SSH into EC2 | Pull new image, `docker compose up -d` | EC2 unreachable |

### Pipeline Diagram

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  TEST   │────▶│  BUILD  │────▶│  SCAN   │────▶│  PUSH   │────▶│ DEPLOY  │
│ pytest  │     │ docker  │     │  trivy  │     │ docker  │     │  ssh    │
│ postgres│     │  build  │     │  scan   │     │  push   │     │ ec2     │
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
- AWS account with an EC2 instance (Ubuntu, t2.micro)

### 1. Clone and push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USER/tasks-api.git
git push -u origin main
```

### 2. Add GitHub Secrets
Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USER` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EC2_HOST` | EC2 public IP address |
| `EC2_SSH_KEY` | Contents of `.pem` private key |
| `DB_PASSWORD` | PostgreSQL password |

### 3. Set up EC2
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
chmod +x ec2-setup.sh && ./ec2-setup.sh
nano ~/tasks-api/.env   # set real values
```

### 4. Trigger the pipeline
```bash
git push origin main
# Watch at: GitHub → Actions tab
```

### 5. Verify
```bash
curl http://YOUR_EC2_IP/health
# → {"status": "ok"}
```

## Rollback

To revert to a previous version on EC2:
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
./rollback.sh <commit-sha>
```

Find old SHAs in the GitHub Actions tab or with `git log --oneline`.

## Author

**Anish Dharu** — Final Year MCA
