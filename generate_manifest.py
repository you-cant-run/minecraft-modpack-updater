import os
import json

# Directory where mods are stored
MODS_DIR = 'your-modpack-repo/mods'

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
            mod = {
                "name": filename,
                "version": "1.0.0",  # You can add version info here if applicable
                "file": f"{MODS_DIR}/{filename}"
            }
            manifest["modpack"]["mods"].append(mod)

    # Save the manifest to a JSON file
    with open('manifest.json', 'w') as manifest_file:
        json.dump(manifest, manifest_file, indent=4)

if __name__ == '__main__':
    generate_manifest()
