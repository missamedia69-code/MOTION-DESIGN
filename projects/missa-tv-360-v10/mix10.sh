#!/usr/bin/env bash
# MISSA TV 360 v10 — mixage final (depuis la racine du dépôt).
# Entrées : .cache/rendus/v10-{16x9,9x16}-video.mp4 (rendu HyperFrames muet),
#           .cache/audio10/{vo,music,sfx}.wav (build10.py --vo, audio10.py)
# Sorties : livrables/missa-tv-360-v10-{16x9,9x16}.mp4 (+ version légère 720p) et .srt
set -euo pipefail
cd "$(dirname "$0")/../.."
A=.cache/audio10
OUT=livrables
mkdir -p "$OUT"

# 1) bande son : la musique baisse sous la voix (sidechain), effets par-dessus, -14 LUFS
ffmpeg -loglevel error -y -i "$A/vo.wav" -i "$A/music.wav" -i "$A/sfx.wav" -filter_complex "
[0:a]aresample=44100,aformat=channel_layouts=stereo,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=10:release=200,volume=1.6,asplit=2[vo][key];
[1:a]volume=0.55[mus];
[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck];
[2:a]volume=0.7[fx];
[vo][duck][fx]amix=inputs=3:normalize=0,atrim=0:60,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.82:level=false[a]" -map "[a]" -ar 48000 "$A/mix.wav"

for F in 16x9 9x16; do
  ffmpeg -loglevel error -y -i ".cache/rendus/v10-$F-video.mp4" -i "$A/mix.wav" -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT/missa-tv-360-v10-$F.mp4"
done
# 2) export léger (connexion limitée) : 720p, ~1,5 Mb/s
ffmpeg -loglevel error -y -i "$OUT/missa-tv-360-v10-16x9.mp4" -vf scale=1280:720 -c:v libx264 -preset slow -b:v 1400k -maxrate 1600k -bufsize 3000k \
  -c:a aac -b:a 96k -movflags +faststart "$OUT/missa-tv-360-v10-16x9-leger-720p.mp4"
ffmpeg -loglevel error -y -i "$OUT/missa-tv-360-v10-9x16.mp4" -vf scale=720:1280 -c:v libx264 -preset slow -b:v 1400k -maxrate 1600k -bufsize 3000k \
  -c:a aac -b:a 96k -movflags +faststart "$OUT/missa-tv-360-v10-9x16-leger-720p.mp4"
cp projects/missa-tv-360-v10/missa-tv-360-v10.srt "$OUT/"
ls -la "$OUT"
