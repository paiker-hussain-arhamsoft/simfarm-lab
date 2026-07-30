#!/bin/sh
set -e

FACE=""
AUDIO=""
OUTPUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --face) FACE="$2"; shift 2;;
    --audio) AUDIO="$2"; shift 2;;
    --outfile|--output) OUTPUT="$2"; shift 2;;
    *) shift;;
  esac
done

if [ -z "$FACE" ] || [ -z "$AUDIO" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: $0 --face <path> --audio <path> --output <path>" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
cd /video-retalking
python3 inference.py --face "$FACE" --audio "$AUDIO" --outfile "$OUTPUT"
