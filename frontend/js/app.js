/**
 * TIER 1 — Strategic Brain — Main Application Controller.
 */

/* ── State ──────────────────────────────────────────── */

let sessionId = localStorage.getItem('brain_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('brain_session_id', sessionId);
}

let agents = [];
let scenarios = [];
let runState = 'idle'; // idle | running | done | error
let turns = [];
let activeAgent = null;
let doneAgents = new Set();
let currentRunId = null;
let abortController = null;
let isDemo = false;

// Framework / backend selection
let selectedFramework = localStorage.getItem('brain_framework') || '';
let selectedBackend = localStorage.getItem('brain_backend') || '';
let platformConfig = null;

const EXAMPLE_TASKS = [
    "Analyze the SIM farming threat in Pakistan and design a detection framework",
    "Design a framework for detecting AI-generated deepfakes in political campaigns",
    "Evaluate the security of a CI/CD pipeline against supply chain attacks",
    "Propose a Zero Trust migration plan for a financial services firm",
];

/* ── Navigation ─────────────────────────────────────── */

function showDashboard() {
    setView('dashboard');
    loadDashboard();
}

function showPipeline() {
    setView('pipeline');
    setupPipelineView();
}

function showScenarios() {
    setView('scenarios');
    loadScenariosPage();
}

function setView(name) {
    document.querySelectorAll('main > section').forEach(s => s.classList.add('hidden'));
    document.getElementById(`view-${name}`).classList.remove('hidden');
    document.querySelectorAll('.header-nav button').forEach(b => b.classList.remove('active'));
    const navBtn = document.getElementById(`nav-${name}`);
    if (navBtn) navBtn.classList.add('active');
}

/* ── Dashboard ──────────────────────────────────────── */

async function loadDashboard() {
    try {
        const [agentData, scenarioData, healthData] = await Promise.all([
            API.getAgents(),
            API.getScenarios(),
            API.health(),
        ]);
        agents = agentData.agents;
        scenarios = scenarioData.scenarios;

        renderStatusBanner(healthData);
        renderAgentGrid();
        renderScenarioGrid();
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

function renderStatusBanner(healthData) {
    const slot = document.getElementById('demo-banner-slot');
    const backends = healthData.backends || [];
    const ollamaBackend = backends.find(b => b.id === 'ollama');
    const openaiBackend = backends.find(b => b.id === 'openai');

    if (!healthData.llm_configured) {
        const ollamaStatus = ollamaBackend ? ollamaBackend.status : 'unavailable';
        if (ollamaStatus === 'pulling') {
            slot.innerHTML = '<div class="demo-banner" style="border-color: rgba(96,165,250,0.2); background: rgba(96,165,250,0.08); color: var(--accent-blue)">⏳ Ollama model is downloading... Pipeline will use <strong>demo mode</strong> until ready. Refresh to check status.</div>';
        } else {
            slot.innerHTML = '<div class="demo-banner">⚠ No LLM configured — running in <strong>demo mode</strong> with pre-recorded responses. Ollama model will auto-download on first start.</div>';
        }
        isDemo = true;
    } else {
        const parts = [];
        if (ollamaBackend && ollamaBackend.status === 'ready') {
            parts.push(`<span class="backend-pill ollama">🟢 Ollama: ${ollamaBackend.model}</span>`);
        }
        if (openaiBackend) {
            parts.push(`<span class="backend-pill openai">🟢 OpenAI: ${openaiBackend.model}</span>`);
        }
        slot.innerHTML = `<div class="llm-status">${parts.join(' ')}</div>`;
        isDemo = false;
    }
}

function renderAgentGrid() {
    const grid = document.getElementById('agent-grid');
    grid.innerHTML = agents.map(a => `
        <div class="agent-card">
            <div class="card-header">
                <div class="card-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                <div class="card-role" style="color: ${a.color}">${a.role}</div>
            </div>
            <div class="card-desc">${a.description}</div>
            <div class="card-tools">
                ${a.tools.map(t => `<span class="tool-badge">${t}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function renderScenarioGrid() {
    const grid = document.getElementById('scenario-grid');
    grid.innerHTML = scenarios.map(s => `
        <div class="scenario-card" onclick="loadScenarioInPipeline('${s.id}')">
            <div class="sc-header">
                <span class="sc-icon">${s.icon}</span>
                <span class="sc-name">${s.name}</span>
                <span class="sc-difficulty" style="background: ${s.color}15; color: ${s.color}; border: 1px solid ${s.color}30">${s.difficulty}</span>
            </div>
            <div class="sc-desc">${s.description}</div>
        </div>
    `).join('');
}

/* ── Scenarios Page ─────────────────────────────────── */

async function loadScenariosPage() {
    try {
        const data = await API.getScenarios();
        const list = document.getElementById('scenario-list');
        list.innerHTML = data.scenarios.map(s => `
            <div class="scenario-card" onclick="loadScenarioInPipeline('${s.id}')">
                <div class="sc-header">
                    <span class="sc-icon">${s.icon}</span>
                    <span class="sc-name">${s.name}</span>
                    <span class="sc-difficulty" style="background: ${s.color}15; color: ${s.color}; border: 1px solid ${s.color}30">${s.difficulty}</span>
                </div>
                <div class="sc-desc">${s.description}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Scenarios load error:', err);
    }
}

async function loadScenarioInPipeline(scenarioId) {
    try {
        const s = await API.getScenario(scenarioId);
        showPipeline();
        const textarea = document.getElementById('task-input');
        textarea.value = s.task;
        updateCharCount();
        updateRunButton();
    } catch (err) {
        console.error('Scenario load error:', err);
    }
}

/* ── Pipeline View ──────────────────────────────────── */

async function setupPipelineView() {
    if (!platformConfig) {
        try {
            platformConfig = await API.getConfig();
            if (!selectedFramework) {
                selectedFramework = platformConfig.default_framework || 'autogen';
            }
        } catch (err) {
            console.error('Config load error:', err);
        }
    }

    renderPipelineAgents();
    renderFrameworkSelector();
    document.getElementById('session-id-display').textContent = sessionId.slice(0, 16) + '…';
    renderExampleChips();
    renderOutputArea();
    updateRunButton();

    const textarea = document.getElementById('task-input');
    textarea.addEventListener('input', () => {
        updateCharCount();
        updateRunButton();
    });
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runPipeline();
    });
}

function renderFrameworkSelector() {
    const container = document.getElementById('framework-selector');
    if (!container || !platformConfig) return;

    const frameworks = platformConfig.frameworks || [];
    const backends = platformConfig.backends || [];
    const readyBackends = backends.filter(b => b.status === 'ready');

    let html = '<div class="fw-group">';
    html += '<label class="fw-label">Framework</label>';
    html += '<div class="fw-pills">';
    for (const fw of frameworks) {
        const active = selectedFramework === fw.id ? 'active' : '';
        html += `<button class="fw-pill ${active}" onclick="selectFramework('${fw.id}')" title="${fw.description}">${fw.name}</button>`;
    }
    html += '</div></div>';

    if (readyBackends.length > 1) {
        html += '<div class="fw-group">';
        html += '<label class="fw-label">LLM Backend</label>';
        html += '<div class="fw-pills">';
        const autoActive = !selectedBackend ? 'active' : '';
        html += `<button class="fw-pill ${autoActive}" onclick="selectBackend('')">Auto</button>`;
        for (const be of readyBackends) {
            const active = selectedBackend === be.id ? 'active' : '';
            const label = be.id === 'ollama' ? `Ollama (${be.model})` : `OpenAI (${be.model})`;
            html += `<button class="fw-pill ${active}" onclick="selectBackend('${be.id}')">${label}</button>`;
        }
        html += '</div></div>';
    }

    container.innerHTML = html;
}

function selectFramework(fw) {
    selectedFramework = fw;
    localStorage.setItem('brain_framework', fw);
    renderFrameworkSelector();
}

function selectBackend(be) {
    selectedBackend = be;
    localStorage.setItem('brain_backend', be);
    renderFrameworkSelector();
}

function renderPipelineAgents() {
    const list = document.getElementById('pipeline-agent-list');
    list.innerHTML = agents.map((a, i) => {
        const isActive = activeAgent === a.id;
        const isDone = doneAgents.has(a.id);
        let statusHtml = '';
        if (isActive) {
            statusHtml = `<span class="pa-status" style="color: ${a.color}"><span class="spinner" style="border-top-color: ${a.color}"></span> Running</span>`;
        } else if (isDone) {
            statusHtml = '<span class="pa-status" style="color: var(--accent-green)">✓</span>';
        }

        let bgStyle = '';
        let borderStyle = `border-color: var(--border)`;
        if (isActive) {
            bgStyle = `background: ${a.color}08`;
            borderStyle = `border-color: ${a.color}30`;
        } else if (isDone) {
            bgStyle = 'background: var(--bg-card); opacity: 0.7';
        }

        const arrow = i < agents.length - 1 ? '<div class="pa-arrow">▼</div>' : '';

        return `
            <div class="pa-agent ${isActive ? 'active' : ''}" style="${bgStyle}; ${borderStyle}">
                <div class="pa-row">
                    <div class="pa-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                    <span class="pa-role">${a.role}</span>
                    ${statusHtml}
                </div>
                <div class="pa-desc">${a.description}</div>
            </div>
            ${arrow}
        `;
    }).join('');
}

function renderExampleChips() {
    const area = document.getElementById('example-tasks-area');
    const chips = document.getElementById('example-chips');
    if (runState !== 'idle' || turns.length > 0) {
        area.classList.add('hidden');
        return;
    }
    area.classList.remove('hidden');
    chips.innerHTML = EXAMPLE_TASKS.map(t => {
        const display = t.length > 60 ? t.slice(0, 60) + '…' : t;
        return `<button class="example-chip" onclick="setTask('${t.replace(/'/g, "\\'")}')">${display}</button>`;
    }).join('');
}

function setTask(text) {
    const textarea = document.getElementById('task-input');
    textarea.value = text;
    updateCharCount();
    updateRunButton();
}

function updateCharCount() {
    const textarea = document.getElementById('task-input');
    document.getElementById('char-count').textContent = `${textarea.value.length}/4000 · Ctrl+Enter to run`;
}

function updateRunButton() {
    const textarea = document.getElementById('task-input');
    const btnRun = document.getElementById('btn-run');
    const btnStop = document.getElementById('btn-stop');
    const btnReset = document.getElementById('btn-reset');

    btnRun.disabled = !textarea.value.trim() || runState === 'running' || runState === 'done';

    if (runState === 'running') {
        btnRun.classList.add('hidden');
        btnStop.classList.remove('hidden');
        btnReset.classList.add('hidden');
    } else if (runState === 'done' || runState === 'error') {
        btnRun.classList.add('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.remove('hidden');
    } else {
        btnRun.classList.remove('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.add('hidden');
    }

    textarea.disabled = runState === 'running';
}

/* ── Pipeline Execution ─────────────────────────────── */

async function runPipeline() {
    const textarea = document.getElementById('task-input');
    const task = textarea.value.trim();
    if (!task || runState === 'running') return;

    runState = 'running';
    turns = [];
    activeAgent = null;
    doneAgents = new Set();
    currentRunId = null;
    updateRunButton();
    renderPipelineAgents();
    renderExampleChips();
    renderOutputArea();

    abortController = new AbortController();

    try {
        const reader = await API.runPipeline(
            task, sessionId, abortController.signal,
            selectedFramework, selectedBackend
        );
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const raw = line.slice(6).trim();
                if (!raw) continue;

                let event;
                try { event = JSON.parse(raw); } catch { continue; }
                handleSSE(event);
            }
        }

        if (runState === 'running') {
            runState = 'done';
        }
    } catch (err) {
        if (err.name !== 'AbortError') {
            runState = 'error';
            renderOutputArea(`Pipeline interrupted: ${err.message}`);
        } else {
            runState = 'idle';
        }
    }

    updateRunButton();
    renderPipelineAgents();
}

function handleSSE(event) {
    switch (event.type) {
        case 'pipeline_start':
            currentRunId = event.run_id;
            break;

        case 'agent_start': {
            const a = agents.find(ag => ag.id === event.agent);
            activeAgent = event.agent;
            turns.push({
                agentId: event.agent,
                role: event.role,
                color: event.color,
                icon: event.icon || (a ? a.icon : '🤖'),
                content: '',
                done: false,
            });
            renderPipelineAgents();
            renderOutputArea();
            break;
        }

        case 'token': {
            const turn = turns.find(t => t.agentId === event.agent && !t.done);
            if (turn) {
                turn.content += event.content;
                updateLastMessage(turn);
            }
            break;
        }

        case 'agent_done': {
            const turn = turns.find(t => t.agentId === event.agent);
            if (turn) turn.done = true;
            doneAgents.add(event.agent);
            activeAgent = null;
            renderPipelineAgents();
            renderOutputArea();
            break;
        }

        case 'agent_error':
            renderOutputArea(null, `${event.agent} error: ${event.error}`);
            break;

        case 'done':
            runState = 'done';
            updateRunButton();
            renderPipelineAgents();
            renderOutputArea();
            break;

        case 'error':
            runState = 'error';
            updateRunButton();
            renderOutputArea(event.message);
            break;

        case 'cancelled':
            runState = 'idle';
            updateRunButton();
            break;
    }
}

function stopPipeline() {
    if (abortController) abortController.abort();
    runState = 'idle';
    activeAgent = null;
    updateRunButton();
    renderPipelineAgents();
}

function resetPipeline() {
    turns = [];
    activeAgent = null;
    doneAgents = new Set();
    currentRunId = null;
    runState = 'idle';
    updateRunButton();
    renderPipelineAgents();
    renderExampleChips();
    renderOutputArea();
}

/* ── Output Rendering ───────────────────────────────── */

function renderOutputArea(errorMsg, warningMsg) {
    const area = document.getElementById('output-area');

    if (turns.length === 0 && !errorMsg) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🧠</div>
                <h3>Ready to orchestrate</h3>
                <p>Enter a task above and the four-agent pipeline will collaborate — Director, Researcher, Critic, and Synthesizer — to produce a high-quality result.</p>
                <div class="agent-dots">
                    ${agents.map(a => `<span class="dot"><span class="dot-circle" style="background: ${a.color}"></span> ${a.role}</span>`).join('')}
                </div>
            </div>
        `;
        return;
    }

    let html = '';
    if (errorMsg) {
        html += `<div class="error-banner">${errorMsg}</div>`;
    }
    if (warningMsg) {
        html += `<div class="error-banner" style="border-color: rgba(245,158,11,0.2); background: rgba(245,158,11,0.08); color: var(--accent-amber)">${warningMsg}</div>`;
    }

    html += '<div class="output-log" id="output-log">';
    for (const turn of turns) {
        const cursorHtml = !turn.done
            ? `<span class="am-cursor" style="background: ${turn.color}"></span>`
            : '';
        html += `
            <div class="agent-message" id="msg-${turn.agentId}">
                <div class="am-header">
                    <div class="am-icon" style="background: ${turn.color}15; border: 1px solid ${turn.color}30">${turn.icon}</div>
                    <span class="am-role" style="color: ${turn.color}">${turn.role}</span>
                    ${!turn.done ? '<span class="spinner" style="width:10px;height:10px"></span>' : ''}
                    ${turn.done ? `<button class="am-copy" onclick="copyContent('${turn.agentId}')">📋</button>` : ''}
                </div>
                <div class="am-content" id="content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }

    if (runState === 'done') {
        html += '<div class="pipeline-complete">Pipeline complete — all 4 agents contributed</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollOutputToBottom();
}

function updateLastMessage(turn) {
    const el = document.getElementById(`content-${turn.agentId}`);
    if (el) {
        el.innerHTML = escapeHtml(turn.content) + `<span class="am-cursor" style="background: ${turn.color}"></span>`;
        scrollOutputToBottom();
    }
}

function scrollOutputToBottom() {
    const log = document.getElementById('output-log');
    if (log) log.scrollTop = log.scrollHeight;
}

function copyContent(agentId) {
    const turn = turns.find(t => t.agentId === agentId);
    if (turn) {
        navigator.clipboard.writeText(turn.content);
    }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ── Init ───────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
