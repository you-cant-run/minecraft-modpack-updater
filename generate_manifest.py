import os
import json
import hashlib

# Directory where mods are stored
MODS_DIR = 'your-modpack-repo/mods'

def compute_sha256(filepath):
    """Compute SHA256 of a local file"""
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
            "mods": []
        }
    }

    # Loop through the mods folder and add them to the manifest
    for filename in os.listdir(MODS_DIR):
        if filename.endswith('.jar'):
            mod_path = os.path.join(MODS_DIR, filename)
            mod = {
                "name": filename,
                "version": "1.0.0",  # You can add version info here if applicable
                "file": f"{MODS_DIR}/{filename}",
                "sha256": compute_sha256(mod_path)  # Add SHA256 hash
            }
            manifest["modpack"]["mods"].append(mod)

    # Save the manifest to a JSON file
    with open('manifest.json', 'w') as manifest_file:
        json.dump(manifest, manifest_file, indent=4)

if __name__ == '__main__':
    generate_manifest()
