"""Wan2.1 video generation adapter for the Bee-Gravity orchestrator.

Prefers a WAN2_COMMAND external hook (created by the all-in-one Dockerfile),
falls back to in-process diffusers if available, and raises otherwise.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shlex
import shutil
import uuid
from pathlib import Path

from . import config


def is_available() -> bool:
    """Return True when a Wan2.1 command hook or local diffusers is usable."""
    if config.WAN2_COMMAND:
        first = shlex.split(config.WAN2_COMMAND)[0]
        if shutil.which(first) or Path(first).exists():
            return True
    try:
        import diffusers  # noqa: F401
        return True
    except Exception:
        return False


def _parse_duration(duration: str) -> int:
    """Convert '5s' or '60' into an integer number of seconds."""
    digits = "".join(ch for ch in (duration or "5s") if ch.isdigit())
    return max(1, int(digits or 5))


async def _generate_in_process(script: str, duration: str, output_dir: str) -> str:
    """Run Wan2.1 1.3B directly in this process (requires diffusers>=0.33)."""
    import torch
    from diffusers import AutoencoderKLWan, WanPipeline
    from diffusers.utils import export_to_video

    model_name = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
    negative_prompt = (
        "Bright tones, overexposed, static, blurred details, subtitles, style, works, "
        "paintings, images, static, overall gray, worst quality, low quality, JPEG "
        "compression residue, ugly, incomplete, extra fingers, poorly drawn hands, "
        "poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, "
        "still picture, messy background, three legs, many people in the background, "
        "walking backwards"
    )

    if torch.cuda.is_available():
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    else:
        dtype = torch.float32

    vae = await asyncio.to_thread(
        AutoencoderKLWan.from_pretrained,
        model_name,
        subfolder="vae",
        torch_dtype=torch.float32,
    )
    pipe = await asyncio.to_thread(
        WanPipeline.from_pretrained,
        model_name,
        vae=vae,
        torch_dtype=dtype,
    )
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    else:
        pipe = pipe.to("cpu")

    seconds = _parse_duration(duration)
    num_frames = min(max(5, seconds * 15), 81)
    num_frames = max(5, (num_frames // 4) * 4 + 1)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{uuid.uuid4()}.mp4")

    frames = await asyncio.to_thread(
        pipe,
        prompt=script,
        negative_prompt=negative_prompt,
        height=480,
        width=832,
        num_frames=num_frames,
        guidance_scale=5.0,
        num_inference_steps=30,
    )
    await asyncio.to_thread(export_to_video, frames.frames[0], out_path, fps=15)
    return out_path


async def generate_video(
    script: str,
    duration: str = "5s",
    output_dir: str = config.ARTIFACT_DIR,
) -> dict:
    """Generate an MP4 with Wan2.1 and return artifact metadata."""
    os.makedirs(output_dir, exist_ok=True)

    if config.WAN2_COMMAND:
        tokens = shlex.split(config.WAN2_COMMAND)
        has_placeholders = any("{script}" in t or "{duration}" in t for t in tokens)

        if has_placeholders:
            mapping = {
                "script": shlex.quote(script),
                "duration": shlex.quote(duration),
            }
            cmd = [
                re.sub(r"\{([a-zA-Z_]+)\}", lambda m: mapping.get(m.group(1), m.group(0)), t)
                for t in tokens
            ]
            # Make sure we can control the output destination.
            if "--output-dir" not in " ".join(cmd):
                cmd.extend(["--output-dir", shlex.quote(output_dir)])
            else:
                cmd.extend(["--output-dir", shlex.quote(output_dir)])
        else:
            cmd = [
                *tokens,
                "--script", script,
                "--duration", duration,
                "--output-dir", output_dir,
            ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=config.WAN2_TIMEOUT
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"WAN2_COMMAND failed (exit {proc.returncode}): {stderr.decode()[:500]}"
            )

        text = stdout.decode()
        payload: dict = {}
        for line in reversed(text.strip().splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    payload = json.loads(line)
                    break
                except Exception:
                    continue
        artifact = payload.get("artifact")
        if not artifact:
            raise RuntimeError("WAN2_COMMAND did not return an artifact path")
        return {"artifact": str(artifact), "simulated": bool(payload.get("simulated", True))}

    # No external hook: try in-process generation.
    try:
        import diffusers  # noqa: F401
        artifact = await _generate_in_process(script, duration, output_dir)
        return {"artifact": artifact, "simulated": True}
    except ImportError as exc:
        raise RuntimeError(
            "WAN2_COMMAND is not set and diffusers is not installed in this environment"
        ) from exc
