import os
import json
import hashlib

MODS_DIR = "mods"
MANIFEST_FILE = "manifest.json"
BASE_URL = "https://raw.githubusercontent.com/you-cant-run/minecraft-modpack-updater/main/mods/"

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest():
    manifest = {}
    for filename in os.listdir(MODS_DIR):
        if filename.endswith(".jar"):
            filepath = os.path.join(MODS_DIR, filename)
            file_hash = calculate_sha256(filepath)
            manifest[filename] = {
                "url": BASE_URL + filename,
                "sha256": file_hash
            }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=4)
    print(f"Manifest generated with {len(manifest)} mods.")

if __name__ == "__main__":
    generate_manifest()
