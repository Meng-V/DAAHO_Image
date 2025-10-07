import os, json, argparse
from pathlib import Path
from typing import List, Dict, Any

from .schema import LOC15_SCHEMA
from .ocr import tesseract_ocr, pil_bytes
from .ai_metadata import extract_metadata, transcribe_with_model
from .gdrive import pull_files_from_folder

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except Exception:
    pass  # Fall back to system env vars if python-dotenv not available

try:
    from jsonschema import Draft7Validator
except Exception:
    Draft7Validator = None

def _validate(obj: Dict[str, Any]) -> str:
    if Draft7Validator is None:
        return ""
    v = Draft7Validator(LOC15_SCHEMA)
    errs = sorted(v.iter_errors(obj), key=lambda e: e.path)
    return "; ".join([f"{'.'.join(map(str, e.path))}: {e.message}" for e in errs])

def process_path(path: str, out_dir: str, collection: str, repository: str, permalink: str, model: str) -> None:
    p = Path(path)
    if not p.exists():
        print(f"Skip missing: {p}")
        return
    
    # Check if output already exists
    out = Path(out_dir) / f"{p.stem}.loc15.json"
    if out.exists():
        print(f"⊘ Skipping {p.name} (already processed)")
        return
    
    # OCR first
    text, conf = tesseract_ocr(str(p))
    img_bytes = pil_bytes(str(p))
    if len(text.strip()) < 25:
        try:
            t = transcribe_with_model(img_bytes, model=model)
            if len(t) > len(text):
                text = t
                conf = max(conf, 85.0)
        except Exception:
            pass
    # AI metadata
    md = extract_metadata(img_bytes, text, filename=p.name, model=model, known_collection=collection, known_repository=repository, known_permalink=permalink)
    # Envelope & validate
    envelope = {"metadata": md, "context": {"filename": p.name, "processing_confidence": float(conf), "model": model}}
    err = _validate(md)
    if err:
        envelope["context"]["validation_error"] = err
    # write
    os.makedirs(out_dir, exist_ok=True)
    out.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {p.name} -> {out}")

def is_supported(name: str) -> bool:
    name = name.lower()
    return name.endswith((".png",".jpg",".jpeg",".tif",".tiff",".bmp",".gif",".webp",".pdf"))

def main():
    ap = argparse.ArgumentParser(description="mini_loc15: tiny OCR + AI LOC15 metadata pipeline")
    ap.add_argument("--in", dest="inp", default="", help="Local file or directory")
    ap.add_argument("--out", dest="out_dir", default="./out", help="Output directory")
    ap.add_argument("--gdrive", action="store_true", help="Fetch from Google Drive folder (env GDRIVE_FOLDER_ID) to a temp dir first")
    ap.add_argument("--model", default="gpt-4o", help="OpenAI model (default: gpt-4o)")
    ap.add_argument("--collection", default="", help="Known collection (optional)")
    ap.add_argument("--repository", default="", help="Known repository (optional)")
    ap.add_argument("--permalink", default="", help="Known permalink (optional)")
    ap.add_argument("--dltemp", default="./_gdrive", help="Temp dir for Google Drive downloads")
    args = ap.parse_args()

    paths: List[str] = []

    if args.gdrive:
        folder_id = os.getenv("GDRIVE_FOLDER_ID", "")
        if not folder_id:
            raise RuntimeError("Set GDRIVE_FOLDER_ID when using --gdrive")
        dl = pull_files_from_folder(folder_id, args.dltemp)
        paths.extend([p for p in dl if is_supported(p)])

    if args.inp:
        p = Path(args.inp)
        if p.is_file() and is_supported(str(p)):
            paths.append(str(p))
        elif p.is_dir():
            for x in p.rglob("*"):
                if x.is_file() and is_supported(str(x)):
                    paths.append(str(x))

    if not paths:
        print("No inputs. Use --in <path> and/or --gdrive.")
        return

    for path in paths:
        try:
            process_path(path, args.out_dir, args.collection, args.repository, args.permalink, args.model)
        except Exception as e:
            print(f"✗ {path}: {e}")

if __name__ == "__main__":
    main()
