"""
AylinOS — Google Drive Integration
-------------------------------------
Saves generated prep packages, tailored resumes, and company briefs
to Google Drive under a structured AylinOS folder hierarchy.

Folder structure created automatically:
  AylinOS/
  ├── PrepPackages/
  │   └── [Company]/
  │       └── [Role] — [Date].txt
  ├── Resumes/
  │   └── [Company] — [Role] — [Date].txt
  └── CompanyResearch/
      └── [Company] — [Date].txt

Setup (one-time):
  1. Go to console.cloud.google.com
  2. Create project "AylinOS"
  3. Enable Google Drive API
  4. Create OAuth 2.0 credentials → Desktop App
  5. Download as credentials.json → place in aylinos/
  6. Run: python3 -m integrations.drive --auth
     (opens browser, log in as aylinos.agentic@gmail.com, approve)
  7. token.json is saved — all future runs use it automatically

Requirements:
  pip install google-auth google-auth-oauthlib google-api-python-client reportlab
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# ── Google API imports (graceful if not installed yet) ─────────────────────────
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def _get_service():
    if not GOOGLE_AVAILABLE:
        raise RuntimeError(
            "Google libraries not installed.\n"
            "Run: pip install google-auth google-auth-oauthlib google-api-python-client"
        )
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {CREDENTIALS_FILE}\n"
            "Download it from Google Cloud Console → APIs & Services → Credentials"
        )

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def _get_or_create_folder(service, name: str, parent_id: str = None) -> str:
    """Return folder ID, creating it if it doesn't exist."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def _ensure_folder_structure(service) -> dict:
    """Create AylinOS folder hierarchy, return dict of folder IDs."""
    root_id = _get_or_create_folder(service, "AylinOS")
    prep_id = _get_or_create_folder(service, "PrepPackages", root_id)
    resume_id = _get_or_create_folder(service, "Resumes", root_id)
    research_id = _get_or_create_folder(service, "CompanyResearch", root_id)

    return {
        "root": root_id,
        "prep": prep_id,
        "resumes": resume_id,
        "research": research_id,
    }


def _upload_text(service, content: str, filename: str, parent_id: str) -> str:
    """Upload plain text content as a Google Doc. Returns file URL."""
    content_bytes = content.encode("utf-8")
    media = MediaInMemoryUpload(content_bytes, mimetype="text/plain", resumable=False)

    metadata = {
        "name": filename,
        "parents": [parent_id],
        "mimeType": "application/vnd.google-apps.document",
    }

    file = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    return file.get("webViewLink", "")


def save_prep_package(company: str, role: str, brief: str, stars: str, questions: str) -> str:
    """
    Save interview prep package to Drive.
    Returns the Google Doc URL.
    """
    try:
        service = _get_service()
        folders = _ensure_folder_structure(service)

        # Create company subfolder under PrepPackages
        company_folder_id = _get_or_create_folder(service, company, folders["prep"])

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{company} — {role[:50]} — {date_str}"

        content = f"""AYLINOS — INTERVIEW PREP PACKAGE
Generated: {datetime.now().strftime("%B %d, %Y")}
{'='*60}

ROLE: {role}
COMPANY: {company}

{'='*60}
COMPANY BRIEF
{'='*60}

{brief}

{'='*60}
STAR STORIES
{'='*60}

{stars}

{'='*60}
LIKELY INTERVIEW QUESTIONS
{'='*60}

{questions}
"""
        url = _upload_text(service, content, filename, company_folder_id)
        print(f"[Drive] Prep package saved → {url}")
        return url

    except Exception as e:
        print(f"[Drive] Could not save prep package: {e}")
        return ""


def save_company_research(company: str, research: dict) -> str:
    """Save company research brief to Drive. Returns URL."""
    try:
        service = _get_service()
        folders = _ensure_folder_structure(service)

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{company} — Research — {date_str}"

        content = f"""AYLINOS — COMPANY RESEARCH
Generated: {datetime.now().strftime("%B %d, %Y")}
{'='*60}

COMPANY: {company}

BRIEF
{research.get('brief', 'N/A')}

INVESTORS & FUNDING
{research.get('investors', 'N/A')}

LEADERSHIP
{research.get('leadership', 'N/A')}

VISA SPONSORSHIP
{research.get('sponsorship', 'N/A')}

AI ANGLE
{research.get('ai_angle', 'N/A')}

HIRING CULTURE
{research.get('hiring_culture', 'N/A')}

RECENT NEWS
{research.get('recent_news', 'N/A')}
"""
        url = _upload_text(service, content, filename, folders["research"])
        print(f"[Drive] Research saved → {url}")
        return url

    except Exception as e:
        print(f"[Drive] Could not save research: {e}")
        return ""


def save_resume(company: str, role: str, content: str) -> str:
    """Save tailored resume to Drive. Returns URL."""
    try:
        service = _get_service()
        folders = _ensure_folder_structure(service)

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{company} — {role[:50]} — Resume — {date_str}"

        url = _upload_text(service, content, filename, folders["resumes"])
        print(f"[Drive] Resume saved → {url}")
        return url

    except Exception as e:
        print(f"[Drive] Could not save resume: {e}")
        return ""


def auth():
    """Run OAuth flow. Call once after placing credentials.json."""
    print("Starting Google OAuth flow...")
    print("A browser window will open. Log in as aylinos.agentic@gmail.com")
    service = _get_service()
    folders = _ensure_folder_structure(service)
    print(f"\n✓ Authenticated successfully.")
    print(f"✓ AylinOS folder structure created in Google Drive.")
    print(f"  Root folder ID: {folders['root']}")
    print(f"\nYou can now find your files at:")
    print(f"  drive.google.com → My Drive → AylinOS")


if __name__ == "__main__":
    if "--auth" in sys.argv:
        auth()
    else:
        print("Usage: python3 -m integrations.drive --auth")
        print("       (run once to authenticate with Google Drive)")
