#!/usr/bin/env python3
"""Out-of-process Wan2.1 text-to-video generator.

Runs in a separate virtualenv so its diffusers/torch/transformers versions do
not conflict with the main application's voice stack (Chatterbox/Coqui).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid

WAN2_MODEL_NAME = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
WAN2_NEGATIVE_PROMPT = (
    "Bright tones, overexposed, static, blurred details, subtitles, style, works, "
    "paintings, images, static, overall gray, worst quality, low quality, JPEG "
    "compression residue, ugly, incomplete, extra fingers, poorly drawn hands, "
    "poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, "
    "still picture, messy background, three legs, many people in the background, "
    "walking backwards"
)


def _torch_dtype():
    import torch
    if torch.cuda.is_available():
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return torch.float32


def _parse_duration(duration: str) -> int:
    """Parse a duration string like '60s' or '5' into seconds (default 5)."""
    digits = "".join(ch for ch in (duration or "5s") if ch.isdigit())
    return max(1, int(digits or 5))


async def _load_pipeline():
    """Load and cache the Wan2.1 1.3B T2V pipeline in a worker thread."""
    import torch
    from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanPipeline

    dtype = _torch_dtype()
    vae_dtype = torch.float32
    vae = await asyncio.to_thread(
        AutoencoderKLWan.from_pretrained,
        WAN2_MODEL_NAME,
        subfolder="vae",
        torch_dtype=vae_dtype,
    )
    pipe = await asyncio.to_thread(
        WanPipeline.from_pretrained,
        WAN2_MODEL_NAME,
        vae=vae,
        torch_dtype=dtype,
    )

    # Wan2.1 needs the UniPCMultistepScheduler with the correct flow_shift for the
    # target resolution. 3.0 is the recommended value for 480P; without it the
    # output is colored noise / unidentifiable frames.
    pipe.scheduler = UniPCMultistepScheduler.from_config(
        pipe.scheduler.config,
        prediction_type="flow_prediction",
        use_flow_sigmas=True,
        num_train_timesteps=1000,
        flow_shift=3.0,
    )

    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to("cpu")
    return pipe


async def generate_video(script: str, duration: str, output_dir: str) -> str:
    import torch
    from diffusers.utils import export_to_video

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{uuid.uuid4()}.mp4")

    pipe = await _load_pipeline()
    seconds = _parse_duration(duration)
    # Wan2.1 default training resolution is 480P; keep frame count modest.
    num_frames = min(max(5, seconds * 15), 81)
    num_frames = max(5, (num_frames // 4) * 4 + 1)

    frames = await asyncio.to_thread(
        pipe,
        prompt=script,
        negative_prompt=WAN2_NEGATIVE_PROMPT,
        height=480,
        width=832,
        num_frames=num_frames,
        guidance_scale=6.0,
        num_inference_steps=40,
    )
    await asyncio.to_thread(
        export_to_video,
        frames.frames[0],
        out_path,
        fps=15,
    )
    return out_path


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Wan2.1 video")
    parser.add_argument("--script", required=True, help="text prompt")
    parser.add_argument("--duration", default="5s", help="e.g. 60s or 5")
    parser.add_argument("--output-dir", default="/artifacts/media", help="output folder")
    args = parser.parse_args()

    try:
        artifact = await generate_video(args.script, args.duration, args.output_dir)
        result = {"artifact": artifact, "simulated": True}
    except Exception as exc:
        result = {"error": str(exc), "simulated": True}
        print(json.dumps(result), file=sys.stderr)
        raise

    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
