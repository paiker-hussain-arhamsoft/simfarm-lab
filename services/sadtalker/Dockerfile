# SadTalker container for simfarm-lab.
#
# Extends the community wawa9000/sadtalker image (which already contains the
# OpenTalker/SadTalker code and pretrained checkpoints) with CPU fallbacks and
# a small wrapper so the main app can call it with --output instead of
# SadTalker's --result_dir. The container stays alive so strategic-brain can
# docker exec into it.
#
# On a host with an NVIDIA GPU and the NVIDIA Container Toolkit, override
# SADTALKER_COMMAND in strategic-brain to remove --cpu for GPU inference.
FROM wawa9000/sadtalker:latest

# Make the image usable on CPU-only machines by monkeypatching torch.load,
# face_alignment defaults, torch.cuda no-ops, and pydub AudioSegment.from_mp3.
RUN cat > /usr/local/lib/python3.8/site-packages/sitecustomize.py <<'PY'
import warnings

import torch

_orig_torch_load = torch.load

def _cpu_torch_load(*args, **kwargs):
    kwargs.setdefault("map_location", torch.device("cpu"))
    return _orig_torch_load(*args, **kwargs)

torch.load = _cpu_torch_load

if hasattr(torch.cuda, "empty_cache"):
    _orig_empty_cache = torch.cuda.empty_cache
    def _safe_empty_cache():
        if torch.cuda.is_available():
            _orig_empty_cache()
    torch.cuda.empty_cache = _safe_empty_cache

if hasattr(torch.cuda, "synchronize"):
    _orig_synchronize = torch.cuda.synchronize
    def _safe_synchronize():
        if torch.cuda.is_available():
            _orig_synchronize()
    torch.cuda.synchronize = _safe_synchronize

try:
    import face_alignment
    _orig_fa_init = face_alignment.FaceAlignment.__init__
    def _new_fa_init(self, landmarks_type, *args, **kwargs):
        kwargs.setdefault("device", "cpu")
        return _orig_fa_init(self, landmarks_type, *args, **kwargs)
    face_alignment.FaceAlignment.__init__ = _new_fa_init
except Exception:
    pass

try:
    import pydub
    def _from_mp3(cls, file, *args, **kwargs):
        return cls.from_file(file, *args, **kwargs)
    pydub.AudioSegment.from_mp3 = classmethod(_from_mp3)
except Exception:
    pass
PY

COPY run_sadtalker.sh /app/SadTalker/run_sadtalker.sh
RUN chmod +x /app/SadTalker/run_sadtalker.sh

# Keep the container alive so strategic-brain can docker exec into it.
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["tail -f /dev/null"]
