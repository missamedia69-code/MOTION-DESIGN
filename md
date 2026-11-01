#!/usr/bin/env bash
# MOTION-DESIGN — point d'entrée du moteur.
# Usage : ./md <commande>   (./md -h pour l'aide)
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m engine.cli "$@"
