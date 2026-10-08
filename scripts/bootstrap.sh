#!/usr/bin/env bash
# Bootstrap complet du moteur MOTION-DESIGN (idempotent).
# Dépendances Python + Node + binaires ffmpeg/ffprobe + Chromium embarqué.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── 1/4 Dépendances Python ──"
pip3 install --break-system-packages -q imageio-ffmpeg pillow numpy av || \
  pip3 install -q imageio-ffmpeg pillow numpy av

echo "── 2/4 Dépendances Node (hyperframes + chromium embarqué) ──"
npm install --no-audit --no-fund

echo "── 3/4 ffmpeg / ffprobe sur PATH ──"
SUDO=""; command -v sudo >/dev/null 2>&1 && SUDO="sudo -n"
if ! command -v ffmpeg >/dev/null 2>&1; then
  FFIO=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
  $SUDO ln -sf "$FFIO" /usr/local/bin/ffmpeg && echo "ffmpeg → /usr/local/bin (imageio statique)"
fi
if ! command -v ffprobe >/dev/null 2>&1; then
  if [ ! -x .cache/ffv5/linux/ffprobe ]; then
    echo "téléchargement ffprobe (codeload.github.com)…"
    mkdir -p .cache/ffv5
    curl -sSL -o .cache/ffbins.tar.gz https://codeload.github.com/zackees/ffmpeg_bins/tar.gz/refs/heads/main
    tar xzf .cache/ffbins.tar.gz -C /tmp --strip-components=0 2>/dev/null || true
    python3 - <<'EOF'
import zipfile, os
os.makedirs(".cache/ffv5", exist_ok=True)
# le tarball contient ffmpeg_bins-main/v5.0/linux.zip
for root, dirs, files in os.walk("/tmp"):
    if "linux.zip" in files and "v5.0" in root:
        zipfile.ZipFile(os.path.join(root, "linux.zip")).extractall(".cache/ffv5")
        break
EOF
  fi
  $SUDO install -m 755 .cache/ffv5/linux/ffprobe /usr/local/bin/ffprobe && echo "ffprobe → /usr/local/bin (build statique v5)"
fi
ffmpeg -version | head -1
ffprobe -version | head -1

echo "── 4/4 Chromium embarqué (HyperFrames) ──"
node scripts/ensure-browser.mjs >/dev/null && echo "Chromium déployé : /tmp/chromium"

echo ""
echo "✅ Bootstrap terminé. Diagnostics :"
./md doctor
./scripts/hf doctor --json | python3 -c "import json,sys; d=json.load(sys.stdin); print('hyperframes ok =', d['ok'])" || true
