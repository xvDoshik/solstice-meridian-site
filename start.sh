#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT/_tools/lib.sh"
CMD="${1:-preview}"
case "$CMD" in
  preview) preview_site ;;
  deploy) deploy_site ;;
  setup) setup_server ;;
  build) build_site; echo "built public/" ;;
  package) python3 "$ROOT/_tools/make_delivery.py" ;;
  *)
    echo "usage: ./start.sh [preview|deploy|setup|build|package]"
    exit 1
    ;;
esac
