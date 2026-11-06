#!/usr/bin/env bash
# Verifies everything motion-reel needs. Prints a fix for anything missing.
ok=1
for b in ffmpeg ffprobe python3; do
  command -v "$b" >/dev/null || { echo "✗ $b not found  → install it (macOS: brew install ffmpeg python)"; ok=0; }
done
python3 - <<'EOF' || ok=0
import importlib, sys
missing = [m for m in ("numpy", "scipy", "playwright") if importlib.util.find_spec(m) is None]
if missing:
    print("✗ python packages missing:", " ".join(missing), " → python3 -m pip install", " ".join(missing)); sys.exit(1)
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        p.chromium.launch().close()
except Exception as e:
    print("✗ Playwright Chromium not installed → python3 -m playwright install chromium"); sys.exit(1)
print("✓ python: numpy, scipy, playwright + chromium")
EOF
if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264; then echo "✓ ffmpeg with libx264"; else echo "✗ ffmpeg lacks libx264"; ok=0; fi
[ $ok = 1 ] && echo "ready" || { echo "fix the items above"; exit 1; }
