#!/usr/bin/env bash
# Recrée l'environnement de rendu HyperFrames 0.8.82 pour « TON ÉCRAN MÉRITE MIEUX ».
# Uniquement les hôtes autorisés : registry.npmjs.org (+ github.com pour le dépôt de méthode).
# Usage : bash studio-59s/setup.sh   puis   . studio-59s/env.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
T=/tmp/hftools
B=/tmp/hfbin
F=missa-tv-360-pub-59s/assets/fonts
mkdir -p "$T" "$B/lib" "$F"

echo "→ .env vide (aucune clé)"
[ -f .env ] || cp .env.example .env

echo "→ npm ci : CLI figé 0.8.82"
[ -d node_modules ] || PUPPETEER_SKIP_DOWNLOAD=1 PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
  npm ci --no-audit --no-fund

echo "→ 7 polices SIL OFL (jsDelivr est bloqué : on passe par @fontsource sur npm)"
for p in instrument-sans space-mono big-shoulders; do
  tgz="$T/fontsource-$p-5.3.0.tgz"
  [ -f "$tgz" ] || npm pack "@fontsource/$p@5.3.0" --silent --pack-destination "$T" >/dev/null
  rm -rf "$T/x-$p" && mkdir -p "$T/x-$p" && tar -xzf "$tgz" -C "$T/x-$p"
done
for w in 400 500 600 700; do cp "$T/x-instrument-sans/package/files/instrument-sans-latin-$w-normal.woff2" "$F/InstrumentSans-$w.woff2"; done
for w in 400 700; do cp "$T/x-space-mono/package/files/space-mono-latin-$w-normal.woff2" "$F/SpaceMono-$w.woff2"; done
cp "$T/x-big-shoulders/package/files/big-shoulders-latin-800-normal.woff2" "$F/BigShoulders-800.woff2"

echo "→ Chromium 153 (npm @sparticuz/chromium) + libs NSS/NSPR"
tgz="$T/sparticuz-chromium-153.0.0.tgz"
[ -f "$tgz" ] || npm pack '@sparticuz/chromium@153.0.0' --silent --pack-destination "$T" >/dev/null
rm -rf "$T/x-chromium" && mkdir -p "$T/x-chromium" && tar -xzf "$tgz" -C "$T/x-chromium"
node -e '
const fs=require("fs"), z=require("zlib"), d="/tmp/hftools/x-chromium/package/bin/";
fs.writeFileSync("/tmp/hfbin/chromium", z.brotliDecompressSync(fs.readFileSync(d+"chromium.br")));
fs.writeFileSync("/tmp/hftools/al2023.tar", z.brotliDecompressSync(fs.readFileSync(d+"al2023.tar.br")));
'
chmod 755 "$B/chromium"
rm -rf "$T/al2023" && mkdir -p "$T/al2023" && tar -xf "$T/al2023.tar" -C "$T/al2023"
cp "$T/al2023/lib/"* "$B/lib/"

echo "→ ffprobe (npm) et ffmpeg (imageio-ffmpeg)"
tgz="$T/ffprobe-installer-linux-x64-5.1.0.tgz"
[ -f "$tgz" ] || npm pack '@ffprobe-installer/linux-x64@5.1.0' --silent --pack-destination "$T" >/dev/null
rm -rf "$T/x-ffprobe" && mkdir -p "$T/x-ffprobe" && tar -xzf "$tgz" -C "$T/x-ffprobe"
cp "$T/x-ffprobe/package/ffprobe" "$B/ffprobe" && chmod 755 "$B/ffprobe"
ln -sf "$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" "$B/ffmpeg"

cat > env.sh <<'EOF'
# Environnement de rendu HyperFrames 0.8.82 dans le sandbox Arena.
# Source : . studio-59s/env.sh
export PATH="/tmp/hfbin:$PATH"
export LD_LIBRARY_PATH="/tmp/hfbin/lib:${LD_LIBRARY_PATH:-}"
export HYPERFRAMES_BROWSER_PATH="/tmp/hfbin/chromium"
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1
export HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_UPDATE_CHECK=1
EOF

echo "→ vérification"
. ./env.sh
npx hyperframes --version
npx hyperframes doctor 2>/dev/null | grep -E 'FFmpeg|FFprobe|Chrome|Version' || true
echo "✅ Environnement prêt. Pour rendre : . studio-59s/env.sh && cd studio-59s && npx hyperframes render missa-tv-360-pub-59s -o renders/missa-tv-360-pub-59s_9x16.mp4 --quality looks"
