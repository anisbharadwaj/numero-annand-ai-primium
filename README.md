# Study Dashboard Flask App

This repository contains a Flask web application with educational resources and a project deployment dashboard.

## Features

- **StudyIQ Learning Center:** Embed YouTube playlists, searchable study resources, bookmarks.
- **Project Dashboard:** Monitor Vercel deployments (status, logs), system metrics (CPU, memory via `psutil`), alerts.
- **QR Payment System:** Generate UPI QR codes (server and JS fallback), with PNG download and UPI ID copy.
- **Security:** User authentication, 2FA (TOTP via PyOTP), CSRF protection, HTTPS enforcement, secure cookies.
- **Error Handling:** Custom 404/500 pages, clear error messages, integration with Sentry for exception reporting.
- **UI/UX:** Bootstrap 5 responsive design, sidebar navigation, dark mode toggle.
- **Future-Proofing:** Modular structure (Blueprints), SQLite with SQLAlchemy/migrations, structured logging, and monitoring.

## Setup (Local)

1. **Clone** this repo.
2. **Create a Python virtualenv** and activate it.
3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
