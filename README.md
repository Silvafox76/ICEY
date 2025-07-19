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
