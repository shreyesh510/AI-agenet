import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
import config

router = APIRouter()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

REDIRECT_URI = "http://localhost:8000/auth/google/callback"
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")


def _build_flow():
    """Build OAuth2 Flow from .env credentials."""
    client_config = {
        "web": {
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


@router.get("/auth/google")
async def google_auth():
    """Redirect to Google OAuth2 consent screen."""
    flow = _build_flow()
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    return RedirectResponse(authorization_url)


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    """Handle OAuth2 callback and save tokens."""
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing authorization code"},
        )

    try:
        flow = _build_flow()
        flow.fetch_token(code=code)
        creds = flow.credentials

        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes),
        }

        with open(TOKEN_PATH, "w") as f:
            json.dump(token_data, f, indent=2)

        return JSONResponse(content={
            "message": "Gmail authentication successful! You can close this window.",
            "scopes": list(creds.scopes),
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Token exchange failed: {str(e)}"},
        )
