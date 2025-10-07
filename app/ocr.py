import io
from typing import Tuple
from PIL import Image, ImageOps
try:
    import pytesseract
except ImportError:
    pytesseract = None

def pil_bytes(img_path: str) -> bytes:
    with Image.open(img_path) as im:
        if im.mode not in ("RGB","RGBA"):
            im = im.convert("RGB")
        bio = io.BytesIO()
        im.save(bio, format="PNG")
        return bio.getvalue()

def tesseract_ocr(img_path: str) -> Tuple[str, float]:
    if pytesseract is None:
        return "", 0.0
    try:
        with Image.open(img_path) as im:
            gray = ImageOps.grayscale(im)
            text = pytesseract.image_to_string(gray)
            alnum = sum(c.isalnum() for c in text)
            conf = min(95.0, max(5.0, (alnum / max(1, len(text))) * 100.0)) if text else 0.0
            return text, conf
    except Exception:
        return "", 0.0
