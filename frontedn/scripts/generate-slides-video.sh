#!/usr/bin/env bash
set -euo pipefail

# Generate a narrated-ready slides video from Markdown using Marp (slides) and FFmpeg (video).
# Prerequisites:
# - Option A (recommended): Docker installed
# - Option B: Node (for npx @marp-team/marp-cli) and ffmpeg installed locally
# - Optional: voiceover audio file (WAV/MP3) to mux with the slides video

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DOCS_DIR="$ROOT_DIR/docs"
OUT_DIR="$ROOT_DIR/build-docs"
SLIDES_MD="$DOCS_DIR/ehs-slide-deck.md"
SLIDES_IMG_DIR="$OUT_DIR/slides-images"
VIDEO_OUT="$OUT_DIR/ehs-slides.mp4"
AUDIO_IN="${1:-}" # optional path to voiceover audio to mux

mkdir -p "$OUT_DIR" "$SLIDES_IMG_DIR"

# 1) Render slides to PNG images
if command -v docker >/dev/null 2>&1; then
  echo "Rendering slides to PNG via Marp (Docker)..."
  docker run --rm -v "$DOCS_DIR":/home/marp/app/ -v "$SLIDES_IMG_DIR":/out ghcr.io/marp-team/marp-cli \
    /home/marp/app/ehs-slide-deck.md --images png --image-scale 2 --allow-local-files --output /out/slide.png
else
  echo "Docker not found. Trying local npx Marp..."
  if command -v npx >/dev/null 2>&1; then
    npx -y @marp-team/marp-cli@latest "$SLIDES_MD" --images png --image-scale 2 --allow-local-files --output "$SLIDES_IMG_DIR/slide.png"
  else
    echo "No Marp available. Please install Docker or run: npx -y @marp-team/marp-cli@latest"
    exit 1
  fi
fi

# 2) Build a video from PNG images
#   - 6 seconds per slide (adjust -framerate to change duration: framerate = 1/duration)
#   - Output: H.264 MP4
if command -v ffmpeg >/dev/null 2>&1; then
  echo "Generating video from slides with ffmpeg..."
  ffmpeg -y -framerate 1/6 -pattern_type glob -i "$SLIDES_IMG_DIR/*.png" -c:v libx264 -pix_fmt yuv420p "$VIDEO_OUT"
else
  echo "ffmpeg not found. If you have Docker:"
  echo "  docker run --rm -v $OUT_DIR:/work -w /work jrottenberg/ffmpeg:4.4-alpine \" \
       -framerate 1/6 -pattern_type glob -i slides-images/*.png -c:v libx264 -pix_fmt yuv420p ehs-slides.mp4"
  exit 1
fi

# 3) Optional: Mux voiceover audio if provided
if [[ -n "$AUDIO_IN" && -f "$AUDIO_IN" ]]; then
  echo "Muxing voiceover: $AUDIO_IN"
  ffmpeg -y -i "$VIDEO_OUT" -i "$AUDIO_IN" -c:v copy -c:a aac -shortest "$OUT_DIR/ehs-slides-with-audio.mp4"
  echo "Created: $OUT_DIR/ehs-slides-with-audio.mp4"
else
  echo "Created: $VIDEO_OUT"
fi

echo "Done. Artifacts in $OUT_DIR"
