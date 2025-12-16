#!/usr/bin/env bash
set -euo pipefail

# Generates a printable PDF bundle for the EHS documentation.
# Requirements:
# - Node.js with mermaid-cli (mmdc) OR Docker available
# - Pandoc OR md-to-pdf (npm) OR typst installed
# - wkhtmltopdf or Chromium for HTML to PDF
# This script tries to use Docker containers to avoid local installs.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/build-docs"
DOCS_DIR="$ROOT_DIR/docs"

mkdir -p "$OUT_DIR"

# 1) Render Mermaid diagrams to SVG (two separate files) using mermaid-cli in Docker (with sudo fallback)
if command -v docker >/dev/null 2>&1; then
  echo "Rendering diagrams using mermaid-cli (Docker)..."
  # Use sudo to ensure access to docker daemon; map user ids to avoid root-owned files
  if [ -f "$DOCS_DIR/ehs-arch.mmd" ]; then
    sudo docker run --rm -v "$DOCS_DIR":/data -u $(id -u):$(id -g) minlag/mermaid-cli -i /data/ehs-arch.mmd -o /data/ehs-arch.svg -b transparent || true
  fi
  if [ -f "$DOCS_DIR/ehs-approval.mmd" ]; then
    sudo docker run --rm -v "$DOCS_DIR":/data -u $(id -u):$(id -g) minlag/mermaid-cli -i /data/ehs-approval.mmd -o /data/ehs-approval.svg -b transparent || true
  fi
else
  echo "Docker not found. Optionally install mermaid-cli locally (npm i -g @mermaid-js/mermaid-cli) and run:"
  echo "mmdc -i $DOCS_DIR/ehs-arch.mmd -o $DOCS_DIR/ehs-arch.svg -b transparent"
  echo "mmdc -i $DOCS_DIR/ehs-approval.mmd -o $DOCS_DIR/ehs-approval.svg -b transparent"
fi

# 2) Concatenate markdown into a single HTML using Pandoc (or fallback)
if command -v pandoc >/dev/null 2>&1; then
  echo "Building HTML with Pandoc..."
  pandoc \
    "$DOCS_DIR/ehs-executive-brief.md" \
    "$DOCS_DIR/ehs-technical-spec.md" \
    "$DOCS_DIR/ehs-workflow-guide.md" \
    "$DOCS_DIR/ehs-slide-deck.md" \
    -s --resource-path="$DOCS_DIR" --self-contained \
    -c https://cdn.jsdelivr.net/npm/water.css@2/out/water.css \
    -o "$OUT_DIR/ehs-docs.html"
else
  echo "Pandoc not found. Attempting md-to-pdf fallback (requires Node)."
  if command -v npx >/dev/null 2>&1; then
    npx md-to-pdf "$DOCS_DIR/ehs-executive-brief.md" --dest "$OUT_DIR/ehs-executive-brief.pdf"
    npx md-to-pdf "$DOCS_DIR/ehs-technical-spec.md" --dest "$OUT_DIR/ehs-technical-spec.pdf"
    npx md-to-pdf "$DOCS_DIR/ehs-slide-deck.md" --dest "$OUT_DIR/ehs-slide-deck.pdf"
  else
    echo "No PDF generator found. Please install Pandoc or use Docker-based toolchain."
    exit 1
  fi
fi

# 3) Convert HTML to PDF (if we produced HTML)
if [ -f "$OUT_DIR/ehs-docs.html" ]; then
  if command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "Converting HTML to PDF with wkhtmltopdf..."
    wkhtmltopdf "$OUT_DIR/ehs-docs.html" "$OUT_DIR/ehs-docs.pdf"
  elif command -v chromium >/dev/null 2>&1; then
    echo "Converting HTML to PDF with Chromium..."
    chromium --headless --disable-gpu --print-to-pdf="$OUT_DIR/ehs-docs.pdf" "$OUT_DIR/ehs-docs.html"
  else
    echo "No HTML-to-PDF engine found; leaving HTML at $OUT_DIR/ehs-docs.html"
  fi
fi

echo "Artifacts saved in $OUT_DIR"

