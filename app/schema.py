from typing import Any, Dict

LOC15_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title":  {"type": ["string", "null"], "maxLength": 240},
        "creator":{"type": ["string", "null"], "maxLength": 200},
        "contributors":{"type": ["array", "null"], "items": {"type": "string"}, "maxItems": 8},
        "correspondents":{"type": ["array", "null"], "items": {"type": "string"}, "maxItems": 12},
        "publisher":{"type": ["string", "null"], "maxLength": 160},
        "date":   {"type": ["string", "null"], "pattern": r"^(\\d{4}(-\\d{2}(-\\d{2})?)?|undated)$"},
        "place":  {"type": ["string", "null"], "maxLength": 160},
        "language":{"type": ["string", "null"], "maxLength": 80},

        "subjects": {"type": ["array", "null"], "items": {"type": "string", "maxLength": 80}, "maxItems": 8},
        "theme": {"type": ["array", "null"], "items": {"type": "string", "maxLength": 80}, "maxItems": 6},
        "genre": {"type": ["array", "null"], "items": {"type": "string", "maxLength": 80}, "maxItems": 6},

        "description": {"type": ["string", "null"], "maxLength": 1000},
        "collection":  {"type": ["string", "null"], "maxLength": 200},
        "series":      {"type": ["string", "null"], "maxLength": 200},
        "folder":      {"type": ["string", "null"], "maxLength": 120},
        "box":         {"type": ["string", "null"], "maxLength": 120},

        "format":      {"type": ["string", "null"], "maxLength": 80},
        "medium":      {"type": ["string", "null"], "maxLength": 120},
        "type":        {"type": ["string", "null"], "maxLength": 120},
        "rights":      {"type": ["string", "null"], "maxLength": 240},
        "repository":  {"type": ["string", "null"], "maxLength": 200},

        "identifier":  {"type": ["string", "null"], "maxLength": 160},
        "call_number": {"type": ["string", "null"], "maxLength": 120},
        "digital_identifier":  {"type": ["string", "null"], "maxLength": 160},
        "reproduction_number": {"type": ["string", "null"], "maxLength": 160},
        "permalink":           {"type": ["string", "null"], "maxLength": 240},

        "digital_collection": {"type": ["string", "null"], "maxLength": 200},
        "digital_publisher":  {"type": ["string", "null"], "maxLength": 200},
        "digitized":          {"type": ["boolean", "null"]},

        "transcript":     {"type": ["string", "null"]},
        "text_reading":   {"type": ["string", "null"]},
        "generated_title":{"type": ["string", "null"], "maxLength": 240},
        "field_confidence": {"type": ["object", "null"], "additionalProperties": {"type": "integer", "minimum": 0, "maximum": 100}},
    },
    "required": [
        "title","creator","contributors","correspondents","publisher","date","place","language",
        "subjects","theme","genre","description","collection","series","folder","box",
        "format","medium","type","rights","repository",
        "identifier","call_number","digital_identifier","reproduction_number","permalink",
        "digital_collection","digital_publisher","digitized",
        "transcript","text_reading","generated_title","field_confidence"
    ]
}

MAX_OCR_CHARS = 12000
MAX_OUTPUT_TOKENS = 4096
DEFAULT_MODEL = "gpt-4o"
