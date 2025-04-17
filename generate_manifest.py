import os
import json
import hashlib

MODS_DIR = 'your-modpack-repo/mods'
CONFIG_DIR = 'your-modpack-repo/config'
CONFIG_EXTS = ('.json', '.cfg', '.yml', '.yaml', '.properties', '.toml')

def compute_sha256(filepath):
    """Compute SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest():
    manifest = {
        "modpack": {
            "name": "My Modpack",
            "version": "1.0.0",
            "mods": [],
            "configs": []  # New configs section
        }
    }

    # Process mod files
    for filename in os.listdir(MODS_DIR):
        if filename.endswith('.jar'):
            filepath = os.path.join(MODS_DIR, filename)
            manifest["modpack"]["mods"].append({
                "name": filename,
                "file": f"mods/{filename}",
                "sha256": compute_sha256(filepath)
            })

    # Process config files (including subfolders)
    for root, _, files in os.walk(CONFIG_DIR):
        for filename in files:
            if filename.endswith(CONFIG_EXTS):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(root, 'your-modpack-repo')
                manifest["modpack"]["configs"].append({
                    "name": filename,
                    "path": f"{rel_path}/{filename}",
                    "sha256": compute_sha256(filepath)
                })

    # Save manifest
    with open('manifest.json', 'w') as f:
        json.dump(manifest, f, indent=4)

if __name__ == '__main__':
    generate_manifest()
