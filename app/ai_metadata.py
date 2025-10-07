import os, json, base64
from typing import Dict, Any, List, Optional
from .schema import LOC15_SCHEMA, MAX_OCR_CHARS, MAX_OUTPUT_TOKENS, DEFAULT_MODEL

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

SYSTEM_INSTRUCTIONS = (
    "You are a meticulous academic-library cataloger and metadata specialist. "
    "Extract Library of Congress–style metadata aligned with Dublin Core practice. "
    "Ground every field strictly in the provided image and OCR text; do not invent data. "
    "Normalize dates to ISO (YYYY or YYYY-MM-DD) or 'undated'. "
    "Subjects/Theme/Genre are concise topical strings (1–5 words, singular). "
    "If multiple values reasonably apply where the schema is an array, include a short list; otherwise choose the most primary. "
    "If unknown, use null (or 'undated' / default rights). "
    "\n\n"
    "IMPORTANT TITLE INSTRUCTIONS: "
    "If the document has a clear date or year visible, incorporate it into the generated_title (e.g., 'Letter from X to Y, June 2, 1942'). "
    "This helps with chronological identification. "
    "\n\n"
    "HANDWRITTEN CONTENT: "
    "Identify any handwritten text separately. Place all handwritten text in the 'transcript' field with clear [HANDWRITTEN] markers. "
    "The 'text_reading' field should contain the clean, linear reading text (typed + handwritten combined) for analysis purposes. "
    "\n\n"
    "Return ONLY a JSON object that validates against the schema."
)

USER_FIELD_RULES = (
    "CSV-ALIGNED FIELDS TO POPULATE WHEN POSSIBLE (matching schema keys):\n"
    "• title, generated_title, creator, contributors[], correspondents[], publisher, date, place, language\n"
    "• subjects[], theme[], genre[], description, collection, series, folder, box\n"
    "• format, medium, type, rights, repository\n"
    "• identifier, call_number, digital_identifier, reproduction_number, permalink\n"
    "• digital_collection, digital_publisher, digitized (true/false)\n"
    "• transcript, text_reading, field_confidence\n"
    "\n"
    "CRITICAL FIELD DIFFERENCES:\n"
    "• 'transcript': Cleanest verbatim transcription with special markers:\n"
    "  - Use [HANDWRITTEN: text] to clearly mark any handwritten portions\n"
    "  - Use [ILLEGIBLE] or [UNCLEAR] for unreadable parts\n"
    "  - Preserve line breaks and original formatting\n"
    "  - This field helps librarians identify document structure and handwritten vs typed content\n"
    "• 'text_reading': Linear, simplified reading text for computational analysis:\n"
    "  - Clean, flowing text without special markers\n"
    "  - Combine typed and handwritten into continuous text\n"
    "  - Remove formatting, preserve only content\n"
    "  - Used for search and AI processing\n"
    "• 'generated_title': Should include date/year if visible (e.g., 'Letter from X to Y, 1942')\n"
    "\n"
    "Other Rules:\n"
    "• Use on-item evidence. Prefer labelled data (e.g., 'Author:', 'Date:').\n"
    "• Keep subjects/theme/genre short and specific; avoid punctuation and subfields like '—'.\n"
    "• Rights: use printed if present; else 'Rights status not determined'.\n"
    "• field_confidence: 0–100 integers for each populated field; 0 if null\n"
)

def _get_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("openai not installed. pip install openai")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI()

def _image_to_data_url(img_bytes: bytes) -> str:
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def transcribe_with_model(img_bytes: bytes, max_chars: int = MAX_OCR_CHARS, model: str = DEFAULT_MODEL) -> str:
    client = _get_client()
    data_url = _image_to_data_url(img_bytes)
    resp = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcribe ALL visible text. Preserve line breaks; prefix clearly handwritten lines with '[handwritten] '. Use '[illegible]'/'[unclear]' for unreadable parts. Return PLAIN TEXT only."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }],
        temperature=0,
        max_tokens=900,
    )
    text = (resp.choices[0].message.content or "").strip()
    return text[:max_chars]

def extract_metadata(img_bytes: bytes, ocr_text: str, filename: str, model: str = DEFAULT_MODEL, known_collection: str = "", known_repository: str = "", known_permalink: str = "") -> Dict[str, Any]:
    client = _get_client()
    data_url = _image_to_data_url(img_bytes)
    ocr_text = (ocr_text or "").strip()[:MAX_OCR_CHARS]

    hints = []
    if known_collection: hints.append(f"default.collection={known_collection}")
    if known_repository: hints.append(f"default.repository={known_repository}")
    if known_permalink:  hints.append(f"default.permalink={known_permalink}")

    content: List[Dict[str, Any]] = [
        {"type": "text", "text": f"FILENAME: {filename}\n\n{USER_FIELD_RULES}"},
        {"type": "image_url", "image_url": {"url": data_url}},
        {"type": "text", "text": f"OCR TEXT:\n{ocr_text if ocr_text else '(none)'}"}
    ]
    if hints:
        content.append({"type": "text", "text": "HINTS:\n" + "\n".join(hints)})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_INSTRUCTIONS},
                      {"role": "user", "content": content}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "loc15_metadata",
                    "schema": LOC15_SCHEMA,
                    "strict": True,
                },
            },
            max_tokens=MAX_OUTPUT_TOKENS,
        )
        raw = resp.choices[0].message.content or "{}"
        try:
            parsed = json.loads(raw)
            if not parsed or len(parsed) == 0:
                print(f"WARNING: API returned empty metadata for {filename}. Raw response: {raw[:200]}")
            return parsed
        except Exception as parse_err:
            print(f"WARNING: JSON parse error for {filename}: {parse_err}")
            i, j = raw.find("{"), raw.rfind("}")
            return json.loads(raw[i:j+1]) if i >= 0 and j > i else {}
    except Exception as e:
        print(f"ERROR extracting metadata for {filename}: {e}")
        return {}
