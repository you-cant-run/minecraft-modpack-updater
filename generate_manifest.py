name: Generate and Push Manifest

on:
  push:
    paths:
      - 'your-modpack-repo/mods/**'
      - '.github/workflows/generate_manifest.yml'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install requirements
        run: pip install -r requirements.txt || true

      - name: Generate manifest
        run: python generate_manifest.py

      - name: Commit and push manifest
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add manifest.json
          git commit -m "Auto-update manifest"
          git push https://x-access-token:${{ secrets.MY_GITHUB_TOKEN }}@github.com/${{ github.repository }} HEAD:main
