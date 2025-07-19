<!--
  ICEY – Icebreaking Inventory & Field‑Service Platform
  Author: Mr. Dear  ·  2025
-->

<p align="center">
  <img src="https://img.shields.io/badge/Flask-API-red?logo=flask" />
  <img src="https://img.shields.io/badge/React-Front‑End-61DAFB?logo=react" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker" />
  <img src="https://img.shields.io/badge/CI‑ready-✅-success" />
</p>

# ICEY – Inventory & Field‑Service Platform

**ICEY** is a full‑stack web application that lets ice‑breaking and mitigation crews  
track tools, materials, and job assignments in real time – even in remote, frigid  
conditions.

> Built for *ICE Mitigation Services* with future expansion to **JT Walsh Contracting**.

---

## ✨ Features

| Area                | Highlights                                                                    |
| ------------------- | ----------------------------------------------------------------------------- |
| Inventory           | Create / edit items, QR / barcode ready, GPS coords, condition & value fields |
| Check‑in / Check‑out| One‑tap workflow for field techs, audit‑logged                                |
| Jobs & Claims       | Assign inventory to jobs (Xactimate‑style claim IDs)                          |
| Authentication      | JWT + refresh tokens, role‑based (`admin`, `supervisor`, `technician`)        |
| Audit Logging       | Every data mutation recorded to `AuditLog`                                    |
| Reporting           | CSV exports, dashboard stats endpoints                                        |
| Mobile Field UI     | `/field` route – offline‑first PWA style                                      |
| DevOps              | Dockerised API & UI, pytest suite, ready for GitHub Actions CI                |

---

## 🏗️ Tech Stack

| Layer     | Tech                                                                             |
| --------- | -------------------------------------------------------------------------------- |
| Frontend  | **React 18** (Vite), Tailwind CSS, ShadCN UI, React‑Router                        |
| Backend   | **Flask 3** REST API, Flask‑JWT‑Extended, Flask‑CORS                              |
| Database  | SQLite (dev) – swap for Postgres in prod                                         |
| AuthN/Z   | JWT access + refresh tokens, custom RBAC decorator                               |
| Container | Docker & Docker Compose (multi‑service)                                          |
| Testing   | Pytest + pytest‑flask                                                            |

---

## 🚀 Quick Start (Dev)

> Requires **Docker Desktop** or plain Docker CLI.

```bash
# clone & run
git clone https://github.com/<your‑org>/ICEY.git
cd ICEY
docker compose up --build
http://localhost:5173 → React app

http://localhost:5000/api → Flask API

Default admin credentials

vbnet
Copy
Edit
username: admin
password: admin123         # change me in production!
🛠️ Local Dev (no Docker)
Backend
bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=src/main.py
flask run
Frontend
bash
Copy
Edit
cd frontend
npm ci
npm run dev

🔐 Environment Variables
Key	Purpose	Default
SECRET_KEY	Flask session secret	dev‑secret
JWT_SECRET_KEY	JWT signing key	jwt‑secret
JWT_ACCESS_TOKEN_EXPIRES	Minutes / hours	3600 (1 hr)
JWT_REFRESH_TOKEN_EXPIRES	Days	30
SQLALCHEMY_DATABASE_URI	DB connection string	sqlite:///…

In Docker, override via docker-compose.override.yml or .env.

🧪 Tests
bash
Copy
Edit
pytest -v
Outputs coverage & green/red indicator.
CI can be wired by dropping the following in .github/workflows/ci.yml.

yaml
Copy
Edit
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest -q
📈 Roadmap
Rate limiting for auth routes (flask-limiter)

Postgres and automatic migrations (Alembic)

QR/Barcode scanner in Field UI (react‑qr‑scanner)

Docusketch / Hover integrations (future)

GitHub Actions → Fly.io/AWS deploy pipeline

🤝 Contributing
Pull Requests are welcome!
Please open an issue first for major changes or feature proposals.

Fork → Branch (feat/xyz)

Commit with conventional messages

pytest must pass

Create PR, fill template, request review

© License
MIT – see LICENSE for details.
© 2025 ICE Mitigation Services & Mr. Dear.

pgsql
Copy
Edit

### How to use

1. In your GitHub repo UI, click **Add file → Create new file → name it `README.md`**  
2. Paste everything inside the code‑block (omit the triple‑backticks).  
3. Commit directly to `main` **or** open a PR if you follow branch flow.  
4. Refresh repo – new README with badges & tables is live.
