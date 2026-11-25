#!/usr/bin/env bash
# Mixage d'exemple : voix off (segments de vo.json) posée sur la vidéo rendue.
set -euo pipefail
ffmpeg -loglevel error -y -i .cache/rendus/demo-voix-master.mp4 -i .cache/vo-demo/s1.mp3 -i .cache/vo-demo/s2.mp3 -i .cache/vo-demo/s3.mp3 -i .cache/vo-demo/s4.mp3 -i .cache/vo-demo/s5.mp3 -i .cache/vo-demo/s6.mp3 -filter_complex "[1:a]adelay=200|200,volume=1.1[v1];[2:a]adelay=8350|8350,volume=1.1[v2];[3:a]adelay=13970|13970,volume=1.1[v3];[4:a]adelay=22520|22520,volume=1.1[v4];[5:a]adelay=31700|31700,volume=1.1[v5];[6:a]adelay=38200|38200,volume=1.1[v6];[v1][v2][v3][v4][v5][v6]amix=inputs=6:normalize=0,apad,atrim=0:47[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k .cache/rendus/demo-voix.mp4
