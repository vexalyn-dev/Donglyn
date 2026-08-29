#!/bin/bash
# build.sh — Render build script

echo "=== Building Tailwind CSS ==="
npx tailwindcss -i ./frontend/static/src/input.css -o ./frontend/static/css/output.css --minify --postcss

echo "=== Installing Playwright browser ==="
npx playwright install chromium

echo "=== Build complete ==="
