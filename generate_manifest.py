import os
import json
import hashlib

MODS_DIR = 'your-modpack-repo/mods'
CONFIG_DIR = 'your-modpack-repo/config'

def compute_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def collect_files(directory):
    entries = []
    for filename in os.listdir(directory):
        if filename.endswith(".jar"):
            filepath = os.path.join(directory, filename)
            entries.append({
                "name": filename,
                "file": f"{directory}/{filename}",
                "sha256": compute_sha256(filepath)
            })
    return entries

def generate_manifest():
    manifest = {
        "modpack": {
            "name": "My Modpack",
            "version": "1.0.0",
            "mods": collect_files(MODS_DIR),
            "config": collect_files(CONFIG_DIR)
        }
    }

    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)

if __name__ == "__main__":
    generate_manifest()
