# Environnement de rendu HyperFrames 0.8.82 dans le sandbox Arena.
# Source : . studio-59s/env.sh
export PATH="/tmp/hfbin:$PATH"
export LD_LIBRARY_PATH="/tmp/hfbin/lib:${LD_LIBRARY_PATH:-}"
export HYPERFRAMES_BROWSER_PATH="/tmp/hfbin/chromium"
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1
export HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_UPDATE_CHECK=1
