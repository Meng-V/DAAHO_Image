# mini_loc15

Tiny, modular pipeline for extracting OCR + Dublin Core–aligned LOC15 metadata from images/PDFs, with Google Drive download support.

## Setup

### 1. Environment Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
Copy the example files and configure them:
```bash
cp .env.example .env
cp .config/client_secret.json.example .config/client_secret.json
```

Edit `.env` and set:
- **`OPENAI_API_KEY`**: Your OpenAI API key (required)
- **`GDRIVE_FOLDER_ID`**: Google Drive folder ID (optional, for Google Drive downloads)

Edit `.config/client_secret.json` with your Google OAuth credentials (only needed for Google Drive support):
- Get credentials from [Google Cloud Console](https://console.cloud.google.com/)
- Enable Google Drive API
- Create OAuth 2.0 credentials (Desktop app)

## Usage

### Option A: Process local files
```bash
python -m app.main --in ./samples --out ./out
```

### Option B: Pull from Google Drive
```bash
python -m app.main --gdrive --out ./out
```

### Additional Options
```bash
python -m app.main --in ./samples --out ./out \
  --model gpt-4o \
  --collection "My Collection" \
  --repository "My Repository" \
  --permalink "https://example.com"
```

## Viewing Metadata

Once you have extracted metadata to the `out/` folder, you can view it with the included web viewer:

```bash
python3 viewer.py
```

Then open **http://localhost:5000** in your browser.

### Features:
- 🖼️ **Image thumbnails** with attached metadata display
- 🔍 **Live search** across all metadata fields
- 📋 **Collapsible accordions** for long text fields (transcript, text_reading)
- 📊 **Confidence scores** and model information
- 🎨 **Modern, responsive UI** that works on all devices

## Notes
- Keeps code small and split into focused modules.
- OCR uses Tesseract; if OCR is empty/weak and an image is available, it falls back to a model transcription call.
- AI extraction is constrained to a compact LOC15 schema and returns an envelope: `{ "metadata": {...}, "context": {...} }`.
- The `.config/` folder and `.env` file contain sensitive credentials and are gitignored.

## File path (Google Drive)

NHPTC Planning/Pilot Projects/Digital Collections/Asian American Experience