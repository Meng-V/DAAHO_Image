import os
from io import BytesIO
from typing import List, Tuple
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except Exception:
    pass  # Fall back to system env vars if python-dotenv not available

# Minimal Drive helper that mirrors the user's pattern.

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def _get_creds() -> Credentials:
    creds = None
    token = os.getenv("GOOGLE_TOKEN_JSON", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET_JSON", "")
    if token and Path(token).exists():
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret or not Path(client_secret).exists():
                raise RuntimeError("Provide GOOGLE_CLIENT_SECRET_JSON (path) and optionally GOOGLE_TOKEN_JSON")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
            if token:
                with open(token, "w") as f:
                    f.write(creds.to_json())
    return creds

def pull_files_from_folder(folder_id: str, out_dir: str, mime_types: Tuple[str, ...] = (
    "application/pdf", "image/png", "image/jpeg", "image/tiff", "image/bmp", "image/gif", "image/webp"
)) -> List[str]:
    """Download files from Drive folder to out_dir. Returns list of local paths.
    
    Args:
        folder_id: Google Drive folder ID
        out_dir: Local directory to save files
        mime_types: Tuple of MIME types to download
    """
    os.makedirs(out_dir, exist_ok=True)
    service = build("drive", "v3", credentials=_get_creds())
    mime_q = " or ".join([f"mimeType='{m}'" for m in mime_types])
    query = f"'{folder_id}' in parents and ({mime_q})"
    page_token = None
    saved = []
    while True:
        resp = service.files().list(q=query, pageToken=page_token, pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()
        for f in resp.get("files", []):
            name = f["name"]
            file_id = f["id"]
            path = Path(out_dir) / name
            
            # Skip if file already exists
            if path.exists():
                print(f"⊘ Skipping {name} (already exists)")
                saved.append(str(path))
                continue
            
            print(f"→ Downloading {name} …")
            request = service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            with open(path, "wb") as o:
                o.write(fh.getvalue())
            saved.append(str(path))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    
    print(f"✓ Downloaded {len(saved)} files from folder {folder_id}")
    return saved
