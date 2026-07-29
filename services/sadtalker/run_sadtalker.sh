#!/bin/sh
set -e

AUDIO=""
IMAGE=""
OUTPUT=""
STILL="--still"
EXPR="1.0"
CPU_FLAG="--cpu"

while [ $# -gt 0 ]; do
  case "$1" in
    --driven_audio) AUDIO="$2"; shift 2;;
    --source_image) IMAGE="$2"; shift 2;;
    --output) OUTPUT="$2"; shift 2;;
    --still) STILL="--still"; shift;;
    --expression_scale) EXPR="$2"; shift 2;;
    --no-cpu) CPU_FLAG=""; shift;;
    *) shift;;
  esac
done

if [ -z "$AUDIO" ] || [ -z "$IMAGE" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: $0 --driven_audio <path> --source_image <path> --output <path>" >&2
  exit 1
fi

TMPDIR=$(mktemp -d)
cd /app/SadTalker
python3 inference.py --driven_audio "$AUDIO" --source_image "$IMAGE" --result_dir "$TMPDIR" --expression_scale "$EXPR" $STILL $CPU_FLAG

VIDEO=$(find "$TMPDIR" -name '*.mp4' -print -quit)
if [ -z "$VIDEO" ]; then
  echo "SadTalker did not produce a video" >&2
  exit 1
fi
cp "$VIDEO" "$OUTPUT"
