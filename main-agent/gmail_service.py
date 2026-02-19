import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import config

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")


def get_gmail_service():
    """Build and return an authenticated Gmail API service object."""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(
            "token.json not found. Please authenticate via /auth/google first."
        )

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_unread_emails(max_results=1):
    """Fetch unread emails from Gmail inbox."""
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread label:inbox",
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return []

    emails = []
    for msg in messages:
        email_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = email_data.get("payload", {}).get("headers", [])
        subject = ""
        from_email = ""
        for header in headers:
            if header["name"].lower() == "subject":
                subject = header["value"]
            elif header["name"].lower() == "from":
                from_email = header["value"]

        body = _extract_body(email_data.get("payload", {}))

        emails.append({
            "id": msg["id"],
            "thread_id": email_data.get("threadId", ""),
            "subject": subject,
            "from_email": from_email,
            "body": body,
            "snippet": email_data.get("snippet", ""),
        })

    return emails


def send_email(to: str, subject: str, body: str):
    """Send an email via Gmail API."""
    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    return {"success": True, "message_id": result.get("id", "")}


def mark_as_read(message_id: str):
    """Mark a Gmail message as read by removing the UNREAD label."""
    service = get_gmail_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()

    return True


def _extract_body(payload):
    """Extract plain text body from email payload."""
    # Single-part message
    if "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    # Multipart message
    parts = payload.get("parts", [])
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    # Fallback: try HTML part
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/html" and part.get("body", {}).get("data"):
            html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            import re
            return re.sub(r"<[^>]+>", "", html)

    # Nested multipart
    for part in parts:
        if part.get("parts"):
            result = _extract_body(part)
            if result:
                return result

    return ""
