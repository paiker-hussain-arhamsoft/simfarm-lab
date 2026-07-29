#!/usr/bin/env python3
from __future__ import annotations
"""GFPGAN face-restoration wrapper for simfarm-lab.

Supports images and video files. For video, frames are extracted with ffmpeg,
each frame is enhanced, and the result is re-encoded with the original audio.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import cv2
from gfpgan import GFPGANer


VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv"}


def is_video(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in VIDEO_EXTS


def video_fps(path: str) -> float:
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    cap.release()
    return fps


def run_ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)


def extract_frames(video_path: str, out_dir: str) -> None:
    run_ffmpeg(["-i", video_path, "-q:v", "1", os.path.join(out_dir, "%08d.png")])


def extract_audio(video_path: str, audio_path: str) -> bool:
    try:
        run_ffmpeg(["-i", video_path, "-vn", "-c:a", "copy", audio_path])
        return os.path.exists(audio_path) and os.path.getsize(audio_path) > 0
    except Exception:
        return False


def encode_frames(frame_dir: str, output_path: str, fps: float, audio_path: str | None) -> None:
    first_frame = os.path.join(frame_dir, sorted(os.listdir(frame_dir))[0])
    img = cv2.imread(first_frame)
    if img is None:
        raise ValueError("Cannot read output frames")

    frame_pattern = os.path.join(frame_dir, "%08d.png")
    video_input = ["-framerate", str(fps), "-i", frame_pattern]

    if audio_path:
        run_ffmpeg(
            ["-i", audio_path] + video_input
            + [
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "copy",
                "-shortest",
                output_path,
            ]
        )
    else:
        run_ffmpeg(
            video_input
            + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", output_path]
        )


def process_image(input_path: str, output_path: str, scale: int) -> None:
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Cannot read input image: {input_path}")

    restorer = GFPGANer(
        model_path="/app/gfpgan/weights/GFPGANv1.4.pth",
        upscale=scale,
        arch="clean",
        channel_multiplier=2,
        bg_upsampler=None,
    )
    _, _, restored = restorer.enhance(
        img, has_aligned=False, only_center_face=False, paste_back=True
    )
    cv2.imwrite(output_path, restored)


def process_video(input_path: str, output_path: str, scale: int) -> None:
    fps = video_fps(input_path)
    tmp = tempfile.mkdtemp(prefix="gfpgan_")
    try:
        frames_dir = os.path.join(tmp, "frames")
        out_frames_dir = os.path.join(tmp, "out")
        audio_path = os.path.join(tmp, "audio.m4a")
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(out_frames_dir, exist_ok=True)

        extract_frames(input_path, frames_dir)
        has_audio = extract_audio(input_path, audio_path)

        restorer = GFPGANer(
            model_path="/app/gfpgan/weights/GFPGANv1.4.pth",
            upscale=scale,
            arch="clean",
            channel_multiplier=2,
            bg_upsampler=None,
        )

        for fname in sorted(os.listdir(frames_dir)):
            frame = cv2.imread(os.path.join(frames_dir, fname))
            if frame is None:
                continue
            _, _, restored = restorer.enhance(
                frame, has_aligned=False, only_center_face=False, paste_back=True
            )
            cv2.imwrite(os.path.join(out_frames_dir, fname), restored)

        encode_frames(
            out_frames_dir,
            output_path,
            fps,
            audio_path if has_audio else None,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="GFPGAN face restoration wrapper")
    parser.add_argument("--input", required=True, help="Input image or video")
    parser.add_argument("--output", required=True, help="Output image or video")
    parser.add_argument("--scale", type=int, default=2, help="Upscale factor")
    args = parser.parse_args()

    if is_video(args.input):
        process_video(args.input, args.output, args.scale)
    else:
        process_image(args.input, args.output, args.scale)

    if not os.path.exists(args.output):
        raise RuntimeError("GFPGAN did not produce an output file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
