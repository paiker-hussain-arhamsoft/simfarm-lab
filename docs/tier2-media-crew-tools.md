# TIER 2 · Media Crew — Tool References & Stub Status

This document records which tools were referenced from the user's Media Crew
("Duix-Avatar" Pipeline) request and which have **stub implementations** in place.

Guiding rule (from the user): *"prioritize offline tools first but keep support
for the online tools too"* — and keep **HeyGen, ElevenLabs, Roop, Wav2Lip**.

> **All Media Crew tools are currently simulated stubs.** Every stub returns a
> structured result containing `"simulated": true`, a placeholder artifact path
> (e.g. `/artifacts/media/clip_stub.mp4`) that is **not actually written to
> disk**, and a `note` describing the real integration it stands in for. No real
> voice cloning, video generation, avatar lip-sync, or face-swap is performed.
> Swapping a stub for a real integration requires no change to the orchestrators
> — only the tool's `run` function.

Registry source: `backend/tools/registry.py`
Agents: `backend/agents/media_crew.py` · Pipeline: `backend/pipeline/media_crew.py`

---

## Requested tools → stub status

### Voice cloning / TTS
Registry tool: `clone_voice` (`category=media`) → `_clone_voice`
(`registry.py:229`), providers map `_VOICE_PROVIDERS` (`registry.py:208`).

| Requested tool | Offline/Online | Stub in place | Provider key | License | Notes |
|---|---|---|---|---|---|
| **Chatterbox** (Resemble AI) | Offline (default) | ✅ | `chatterbox` | MIT | Default voice provider; 23 languages |
| **Coqui XTTS-v2** | Offline | ✅ | `coqui` | MPL-2.0 | Multilingual / cross-lingual |
| **Bark** (Suno AI) | Offline | ✅ | `bark` | MIT | Expressive TTS |
| **ElevenLabs** | **Online (optional)** | ✅ | `elevenlabs` | commercial | Gated by `ALLOW_ONLINE_TOOLS`; self-heals to Chatterbox when offline |

### Text-to-video
Registry tool: `generate_video` (`category=media`) → `_generate_video`
(`registry.py:246`), providers map `_VIDEO_PROVIDERS` (`registry.py:215`).

| Requested tool | Offline/Online | Stub in place | Provider key | License | Notes |
|---|---|---|---|---|---|
| **Wan2.1** (Alibaba) | Offline (default) | ✅ | `wan2` | Apache-2.0 | Default video provider; "14B" |
| **CogVideoX** (Tsinghua) | Offline | ✅ | `cogvideo` | open | "5B" |
| **Open-Sora 2.0** | Offline | ✅ | `opensora` | open | "11B" |
| **HeyGen** | **Online (optional)** | ✅ | `heygen` | commercial | Gated by `ALLOW_ONLINE_TOOLS`; self-heals to Wan2.1 when offline |

### Digital human / avatar lip-sync
Registry tool: `render_avatar` (`category=media`) → `_render_avatar`
(`registry.py:264`), providers map `_AVATAR_PROVIDERS` (`registry.py:222`).

| Requested tool | Offline/Online | Stub in place | Provider key | License | Notes |
|---|---|---|---|---|---|
| **Duix-Avatar** [user provided] | Offline (default) | ✅ | `duix` | open | Photo + text-script digital human |
| **Wav2Lip** | Offline | ✅ | `wav2lip` | open | Audio-driven lip-sync (also used in Video Stack) |
| **Roop** | Offline | ✅ | `roop` | open | Single-image face pipeline |

---

## Offline-first enforcement

- `ToolSpec.requires_internet` (`registry.py:38`) marks online tools.
- `_online_available()` (`registry.py:278`) returns true only when
  `ALLOW_ONLINE_TOOLS` ∈ {`1`,`true`,`yes`} — **default is OFF (offline-first)**.
- When an online provider (ElevenLabs / HeyGen) is selected while online tools
  are disabled, the stub raises `ToolError`, and the self-refining loop **falls
  back to the offline default** (ElevenLabs→Chatterbox, HeyGen→Wan2.1).
- All offline providers set `requires_internet: false` and run locally.

---

## Related Video Stack tools (added in the next TIER 2 part)

These are referenced here because Wav2Lip is shared with the Media Crew request.
All are simulated stubs, offline, and consent-gated / audit-logged.

| Tool | Registry id | Provider key | Function |
|---|---|---|---|
| DeepFaceLab | `face_swap` | `deepfacelab` | `_face_swap` (`registry.py:297`) |
| FaceSwap | `face_swap` | `faceswap` | `_face_swap` |
| Deep-Live-Cam | `face_swap` | `deeplivecam` | `_face_swap` |
| Wav2Lip | `lip_sync` | `wav2lip` | `_lip_sync` (`registry.py:312`) |
| VideoRetalking | `lip_sync` | `videoretalking` | `_lip_sync` |
| GFPGAN | `gfpgan_upscale` | — | `_gfpgan_upscale` (`registry.py:325`) |
| FFmpeg | `ffmpeg_pipeline` | — | `_ffmpeg_pipeline` (`registry.py:336`) |

---

## Reference commit `4b2fc5e24c799accfea7df57370d0d1afba40828`

`Add a media production pipeline for digital human avatars` — the historical
React/Express Media Crew from the "other version". It was used as a **concept
reference only**; its TypeScript was not copied. Files it touched:

- `artifacts/api-server/src/routes/media.ts` (209 lines) — `POST /media/produce` (SSE)
- `artifacts/compliance-gateway/src/pages/MediaCrew.tsx` (709 lines) — 4-agent UI
- `artifacts/api-server/src/routes/index.ts` — route registration
- `artifacts/compliance-gateway/src/App.tsx` — route wiring
- `artifacts/compliance-gateway/src/pages/IntelligenceCrew.tsx` — minor edit

Historical agent structure (adapted, not copied): Script Writer → Voice
Architect → Video Director → Production Lead. Our implementation reimplements
the concept on FastAPI + vanilla JS with the offline-first registry above,
SSE streaming, Ollama-default LLM, and demo fallback.

---

## Summary

Every tool in the Media Crew request has a stub in place:
**Duix-Avatar, Wan2.1, CogVideoX, Open-Sora 2.0, Chatterbox, Coqui XTTS-v2,
Bark** (offline), plus **HeyGen, ElevenLabs** (online, optional) and **Roop,
Wav2Lip** (offline). None execute real generation yet; all are clearly-labeled
simulations behind stable interfaces ready for real integration per-tier.
