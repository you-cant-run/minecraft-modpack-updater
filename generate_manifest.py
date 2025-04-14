import os
import json

MODS_DIR = "your-modpack-repo/mods"  # Updated to the correct subfolder path

def generate_manifest():
    mods = []

    # Ensure the mods folder exists
    if not os.path.exists(MODS_DIR):
        print(f"Error: The folder {MODS_DIR} does not exist!")
        return

    # Read the mods in the specified directory
    for filename in os.listdir(MODS_DIR):
        if filename.endswith(".jar"):
            mod_name = filename  # Using just the filename here
            mods.append(mod_name)

    # Create manifest data
    manifest = {
        "version": "1.0",
        "mods": mods
    }

    # Write manifest to file
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
    print("Manifest has been updated!")

# Run the manifest generation
generate_manifest()
