#!/usr/bin/env python3
"""
Build script to generate static files for Vercel deployment.
This creates a standalone viewer with all data pre-generated.
"""

import os
import json
import shutil
from pathlib import Path
import base64

# Configure paths
BASE_DIR = Path(__file__).parent
IMAGE_DIR = BASE_DIR / "_gdrive"
METADATA_DIR = BASE_DIR / "out"
OUTPUT_DIR = BASE_DIR / "public"
IMAGES_OUTPUT_DIR = OUTPUT_DIR / "images"

def main():
    print("=" * 60)
    print("🚀 Building static site for Vercel deployment")
    print("=" * 60)
    
    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_OUTPUT_DIR.mkdir(exist_ok=True)
    
    items = []
    
    # Process all JSON files
    if METADATA_DIR.exists():
        for json_file in sorted(METADATA_DIR.glob("*.loc15.json")):
            base_name = json_file.stem.replace(".loc15", "")
            
            # Check if corresponding image exists and copy it
            image_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                img_file = IMAGE_DIR / f"{base_name}{ext}"
                if img_file.exists():
                    # Copy image to public/images
                    dest_file = IMAGES_OUTPUT_DIR / f"{base_name}{ext}"
                    shutil.copy2(img_file, dest_file)
                    image_path = f"images/{base_name}{ext}"
                    print(f"✓ Copied: {base_name}{ext}")
                    break
            
            # Read metadata
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                items.append({
                    'id': base_name,
                    'image': image_path,
                    'metadata': data.get('metadata', {}),
                    'context': data.get('context', {}),
                    'filename': base_name
                })
            except Exception as e:
                print(f"✗ Error reading {json_file}: {e}")
    
    # Write items data to JSON
    data_file = OUTPUT_DIR / "data.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    print(f"\n📦 Generated data.json with {len(items)} items")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🖼️  Images copied: {len(list(IMAGES_OUTPUT_DIR.glob('*')))}")
    print("\n✅ Build complete! Ready for Vercel deployment.")
    print("\nNext steps:")
    print("1. Copy public/index.html to public/ (will be created next)")
    print("2. Run: vercel deploy")
    print("=" * 60)

if __name__ == '__main__':
    main()
