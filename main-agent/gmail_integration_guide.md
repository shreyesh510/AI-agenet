# Gmail Integration Guide

## Overview

This integration adds Gmail functionality to the Python agent:
- **Read emails** — Cron job fetches unread order emails every 5 minutes
- **Send emails** — Agent sends order confirmation emails via `send_gmail` tool
- **Auto-process** — Unread emails are automatically processed through the agent and marked as read

## Architecture

```
Gmail Inbox
    │
    ▼ (every 5 min)
cron_job.py ──► fetch unread emails (gmail_service.py)
    │
    ▼ (for each email)
mainAgent.py ──► process order (find customer, verify product, create order)
    │
    ▼ (after order created)
send_gmail tool ──► send confirmation email (gmail_service.py)
    │
    ▼
mark email as read (gmail_service.py)
```

## Prerequisites

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth2 Credentials** (Client ID + Client Secret) from Google Cloud Console
3. Add `http://localhost:8000/auth/google/callback` as an authorized redirect URI in Google Cloud Console

## Setup Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `google-auth` — Google authentication
- `google-auth-oauthlib` — OAuth2 flow
- `google-api-python-client` — Gmail API client
- `apscheduler` — Background job scheduler

### Step 2: Configure Environment

Add to `.env`:
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Step 3: Start the Server

```bash
uvicorn main:app --reload --port 8000
```

The cron scheduler starts automatically on server startup.

### Step 4: Authenticate Gmail

1. Open browser: `http://localhost:8000/auth/google`
2. Login with your Google account
3. Grant Gmail permissions (read, send, modify)
4. You'll see: `"Gmail authentication successful!"`
5. A `token.json` file is created — this stores your access & refresh tokens

**Note:** You only need to do this once. The token auto-refreshes.

### Step 5: Test

Send an order email to the authenticated Gmail account (format like the templates in `template/` folder). The cron job will:
1. Pick it up within 5 minutes
2. Process the order through the agent
3. Send a confirmation email to the customer
4. Mark the original email as read

Check server logs for processing details.

## Files Created/Modified

### New Files
| File | Purpose |
|------|---------|
| `gmail_service.py` | Core Gmail API layer (fetch, send, mark as read) |
| `auth_routes.py` | OAuth2 endpoints (`/auth/google`, `/auth/google/callback`) |
| `tools/gmail_tools.py` | `send_gmail` LangChain tool for the agent |
| `cron_job.py` | APScheduler background job (every 5 min) |

### Modified Files
| File | Change |
|------|--------|
| `main.py` | Added auth router + scheduler lifespan |
| `config.py` | Added `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| `.env` | Added Google OAuth2 credentials |
| `tools/__init__.py` | Registered `send_gmail` in `ALL_TOOLS` |
| `prompts/system_prompt.py` | Added `send_gmail` tool + Step 8 (send confirmation) |
| `requirements.txt` | Added 4 new packages |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/auth/google` | Redirect to Google OAuth2 login |
| GET | `/auth/google/callback` | Handle OAuth2 callback, save token |
| GET | `/` | Health check (existing) |
| POST | `/chat` | Chat endpoint (existing) |

## Gmail Scopes Used

- `gmail.readonly` — Read emails from inbox
- `gmail.send` — Send emails
- `gmail.modify` — Mark emails as read (remove UNREAD label)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `token.json not found` | Visit `http://localhost:8000/auth/google` to authenticate |
| Token expired errors | Token auto-refreshes. If refresh token is revoked, re-authenticate via `/auth/google` |
| Cron not running | Check server logs for `"Email processing scheduler started"` on startup |
| Emails not being picked up | Ensure emails are unread and in the inbox (not spam/promotions) |
| `GOOGLE_CLIENT_ID` empty | Check `.env` file has the correct values |
