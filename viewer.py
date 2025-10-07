#!/usr/bin/env python3
"""
Flask-based metadata viewer for LOC15 JSON files and their corresponding images.
Usage: python3 viewer.py
Then open http://localhost:5000 in your browser
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory

app = Flask(__name__)

# Configure paths
IMAGE_DIR = Path(__file__).parent / "_gdrive"
METADATA_DIR = Path(__file__).parent / "out"

@app.route('/')
def index():
    """Main viewer page"""
    return render_template('viewer.html')

@app.route('/api/items')
def get_items():
    """Get all items with metadata"""
    items = []
    
    # Iterate through all JSON files in the output directory
    if METADATA_DIR.exists():
        for json_file in sorted(METADATA_DIR.glob("*.loc15.json")):
            # Extract the base filename (e.g., BC-0692_Recto)
            base_name = json_file.stem.replace(".loc15", "")
            
            # Check if corresponding image exists
            image_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                img_file = IMAGE_DIR / f"{base_name}{ext}"
                if img_file.exists():
                    image_path = f"/images/{base_name}{ext}"
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
                print(f"Error reading {json_file}: {e}")
    
    return jsonify(items)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images from the _gdrive directory"""
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🖼️  LOC15 Metadata Viewer")
    print("=" * 60)
    print(f"Images: {IMAGE_DIR}")
    print(f"Metadata: {METADATA_DIR}")
    print("\n📂 Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(debug=True, port=5000)
