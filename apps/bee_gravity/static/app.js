const promptEl = document.getElementById('prompt');
const scriptEl = document.getElementById('script');
const styleEl = document.getElementById('style');
const durationEl = document.getElementById('duration');
const generateBtn = document.getElementById('generateBtn');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const ollamaBadge = document.getElementById('ollamaBadge');
const wan2Badge = document.getElementById('wan2Badge');

async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        const cfg = await res.json();
        ollamaBadge.textContent = cfg.ollama_ready ? `Ollama: ${cfg.ollama_model}` : 'Ollama: not ready';
        ollamaBadge.style.background = cfg.ollama_ready ? '#238636' : '#da3633';
        wan2Badge.textContent = cfg.wan2_available ? 'Wan2.1: ready' : 'Wan2.1: not ready';
        wan2Badge.style.background = cfg.wan2_available ? '#238636' : '#da3633';

        styleEl.innerHTML = '';
        cfg.styles.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            styleEl.appendChild(opt);
        });
    } catch (err) {
        statusEl.textContent = 'Failed to load config: ' + err;
    }
}

generateBtn.addEventListener('click', async () => {
    resultEl.innerHTML = '';
    statusEl.textContent = 'Generating… this may take a few minutes for Wan2.1.';
    generateBtn.disabled = true;

    const body = {
        prompt: promptEl.value,
        script: scriptEl.value,
        style: styleEl.value,
        duration: durationEl.value,
    };

    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || `HTTP ${res.status}`);
        }

        const scriptBox = document.createElement('div');
        scriptBox.id = 'scriptBox';
        scriptBox.textContent = data.script;

        const video = document.createElement('video');
        video.src = data.video_url;
        video.controls = true;
        video.autoplay = true;
        video.muted = true;
        video.loop = true;

        resultEl.appendChild(document.createTextNode('Video prompt used:'));
        resultEl.appendChild(scriptBox);
        resultEl.appendChild(video);

        statusEl.textContent = 'Done.';
    } catch (err) {
        statusEl.textContent = 'Error: ' + err;
    } finally {
        generateBtn.disabled = false;
    }
});

loadConfig();
