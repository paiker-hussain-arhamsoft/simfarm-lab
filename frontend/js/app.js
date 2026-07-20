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
let pendingToolActivity = {}; // worker id -> [activity items] (buffered before agent_start)
let spawnedWorkers = [];

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
    pendingToolActivity = {};
    spawnedWorkers = [];
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

        case 'worker_spawn':
            spawnedWorkers = event.workers || [];
            renderOutputArea();
            break;

        case 'tool_call':
        case 'tool_result':
        case 'self_heal': {
            const w = event.worker || 'unknown';
            if (!pendingToolActivity[w]) pendingToolActivity[w] = [];
            pendingToolActivity[w].push(event);
            // If the worker's turn already exists, attach live.
            const existing = turns.find(t => t.agentId === w);
            if (existing) {
                existing.toolActivity = pendingToolActivity[w];
                renderOutputArea();
            }
            break;
        }

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
                toolActivity: pendingToolActivity[event.agent] || [],
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

    if (spawnedWorkers.length > 0) {
        html += `<div class="worker-spawn-banner">
            <span class="wsb-label">⚙ Spawned workers:</span>
            ${spawnedWorkers.map(w => `<span class="wsb-pill" style="color: ${w.color}; border-color: ${w.color}40; background: ${w.color}10">${w.icon} ${w.role}</span>`).join('')}
        </div>`;
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
                ${renderToolActivity(turn.toolActivity)}
                <div class="am-content" id="content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }

    if (runState === 'done') {
        html += '<div class="pipeline-complete">Pipeline complete</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollOutputToBottom();
}

function renderToolActivity(activity) {
    if (!activity || activity.length === 0) return '';
    let rows = '';
    for (const ev of activity) {
        if (ev.type === 'tool_call') {
            const attempt = ev.attempt > 1 ? ` <span class="ta-retry">retry #${ev.attempt}</span>` : '';
            rows += `<div class="ta-row ta-call">
                <span class="ta-icon">🔧</span>
                <span class="ta-tool">${ev.tool}</span>
                <span class="ta-provider">${ev.provider || ''}</span>${attempt}
            </div>`;
        } else if (ev.type === 'tool_result') {
            if (ev.ok) {
                rows += `<div class="ta-row ta-ok"><span class="ta-icon">✓</span> <span class="ta-tool">${ev.tool}</span> <span class="ta-note">returned ${escapeHtml(summarizeResult(ev.result))}</span></div>`;
            } else {
                rows += `<div class="ta-row ta-fail"><span class="ta-icon">✕</span> <span class="ta-tool">${ev.tool}</span> <span class="ta-note">${escapeHtml(ev.error || 'failed')}</span></div>`;
            }
        } else if (ev.type === 'self_heal') {
            rows += `<div class="ta-row ta-heal"><span class="ta-icon">♻</span> <span class="ta-note">Self-heal: ${escapeHtml(ev.note || ev.action)}</span></div>`;
        }
    }
    return `<div class="tool-activity">${rows}</div>`;
}

function summarizeResult(result) {
    if (!result || typeof result !== 'object') return String(result);
    if (result.provider) return `${result.provider}${result.simulated ? ' (simulated)' : ''}`;
    return 'ok';
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

/* ── TIER 2 · Intelligence Crew ─────────────────────── */

let tier2Config = null;
let tier2State = 'idle'; // idle | running | done | error
let tier2Turns = [];
let tier2Active = null;
let tier2Done = new Set();
let tier2RunId = null;
let tier2Abort = null;
let tier2Pending = {}; // agent id -> [tool activity]

const TIER2_EXAMPLES = [
    "Analyze voter sentiment and turnout likelihood among swing voter segments",
    "Profile rural vs urban voting behavior and economic grievances",
    "Assess party loyalty shifts driven by inflation and load-shedding",
    "Forecast youth turnout and identify persuadable demographic clusters",
];

async function showTier2() {
    setView('tier2');
    await setupTier2View();
}

async function setupTier2View() {
    if (!tier2Config) {
        try {
            tier2Config = await API.getIntelligenceConfig();
        } catch (err) {
            console.error('Tier2 config load error:', err);
            return;
        }
    }

    renderTier2Agents();
    renderTier2Backend();
    renderTier2Selectors();
    renderTier2Examples();
    document.getElementById('tier2-session-display').textContent = sessionId.slice(0, 16) + '…';
    renderTier2Output();
    updateTier2Button();

    const textarea = document.getElementById('tier2-query');
    if (!textarea.dataset.bound) {
        textarea.dataset.bound = '1';
        textarea.addEventListener('input', () => {
            updateTier2CharCount();
            updateTier2Button();
        });
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runTier2();
        });
    }
}

function renderTier2Selectors() {
    const regionSel = document.getElementById('tier2-region');
    const langSel = document.getElementById('tier2-language');
    regionSel.innerHTML = (tier2Config.regions || [])
        .map(r => `<option value="${r}">${r}</option>`).join('');
    langSel.innerHTML = (tier2Config.languages || [])
        .map(l => `<option value="${l.code}">${l.label} · ${l.native}</option>`).join('');
}

function renderTier2Agents() {
    const list = document.getElementById('tier2-agent-list');
    const crew = tier2Config.agents || [];
    list.innerHTML = crew.map((a, i) => {
        const isActive = tier2Active === a.id;
        const isDone = tier2Done.has(a.id);
        let statusHtml = '';
        if (isActive) {
            statusHtml = `<span class="pa-status" style="color: ${a.color}"><span class="spinner" style="border-top-color: ${a.color}"></span> Running</span>`;
        } else if (isDone) {
            statusHtml = '<span class="pa-status" style="color: var(--accent-green)">✓</span>';
        }
        let bgStyle = '';
        let borderStyle = 'border-color: var(--border)';
        if (isActive) {
            bgStyle = `background: ${a.color}08`;
            borderStyle = `border-color: ${a.color}30`;
        } else if (isDone) {
            bgStyle = 'background: var(--bg-card); opacity: 0.7';
        }
        const arrow = i < crew.length - 1 ? '<div class="pa-arrow">▼</div>' : '';
        return `
            <div class="pa-agent ${isActive ? 'active' : ''}" style="${bgStyle}; ${borderStyle}">
                <div class="pa-row">
                    <div class="pa-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                    <span class="pa-role">${a.role}</span>
                    ${statusHtml}
                </div>
                <div class="pa-desc">${a.description}</div>
                <div class="pa-fw" style="color: ${a.color}">${a.framework}</div>
            </div>
            ${arrow}
        `;
    }).join('');
}

function renderTier2Backend() {
    const container = document.getElementById('tier2-backend');
    const cfg = tier2Config.config || {};
    const backends = cfg.backends || [];
    const readyBackends = backends.filter(b => b.status === 'ready');
    if (readyBackends.length === 0) {
        container.innerHTML = '<div class="fw-group"><label class="fw-label">Backend</label><div class="fw-pills"><span class="backend-pill">Demo mode</span></div></div>';
        return;
    }
    let html = '<div class="fw-group"><label class="fw-label">LLM Backend</label><div class="fw-pills">';
    const autoActive = !selectedBackend ? 'active' : '';
    html += `<button class="fw-pill ${autoActive}" onclick="selectBackend('')">Auto</button>`;
    for (const be of readyBackends) {
        const active = selectedBackend === be.id ? 'active' : '';
        const label = be.id === 'ollama' ? `Ollama (${be.model})` : `OpenAI (${be.model})`;
        html += `<button class="fw-pill ${active}" onclick="selectTier2Backend('${be.id}')">${label}</button>`;
    }
    html += '</div></div>';
    container.innerHTML = html;
}

function selectTier2Backend(be) {
    selectedBackend = be;
    localStorage.setItem('brain_backend', be);
    renderTier2Backend();
}

function renderTier2Examples() {
    const area = document.getElementById('tier2-examples-area');
    const chips = document.getElementById('tier2-example-chips');
    if (tier2State !== 'idle' || tier2Turns.length > 0) {
        area.classList.add('hidden');
        return;
    }
    area.classList.remove('hidden');
    chips.innerHTML = TIER2_EXAMPLES.map(t => {
        const display = t.length > 60 ? t.slice(0, 60) + '…' : t;
        return `<button class="example-chip" onclick="setTier2Query('${t.replace(/'/g, "\\'")}')">${display}</button>`;
    }).join('');
}

function setTier2Query(text) {
    const textarea = document.getElementById('tier2-query');
    textarea.value = text;
    updateTier2CharCount();
    updateTier2Button();
}

function updateTier2CharCount() {
    const textarea = document.getElementById('tier2-query');
    document.getElementById('tier2-char-count').textContent = `${textarea.value.length}/4000 · Ctrl+Enter to run`;
}

function updateTier2Button() {
    const textarea = document.getElementById('tier2-query');
    const btnRun = document.getElementById('tier2-btn-run');
    const btnStop = document.getElementById('tier2-btn-stop');
    const btnReset = document.getElementById('tier2-btn-reset');

    btnRun.disabled = !textarea.value.trim() || tier2State === 'running' || tier2State === 'done';

    if (tier2State === 'running') {
        btnRun.classList.add('hidden');
        btnStop.classList.remove('hidden');
        btnReset.classList.add('hidden');
    } else if (tier2State === 'done' || tier2State === 'error') {
        btnRun.classList.add('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.remove('hidden');
    } else {
        btnRun.classList.remove('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.add('hidden');
    }
    textarea.disabled = tier2State === 'running';
}

async function runTier2() {
    const textarea = document.getElementById('tier2-query');
    const query = textarea.value.trim();
    if (!query || tier2State === 'running') return;

    const region = document.getElementById('tier2-region').value;
    const language = document.getElementById('tier2-language').value;

    tier2State = 'running';
    tier2Turns = [];
    tier2Active = null;
    tier2Done = new Set();
    tier2RunId = null;
    tier2Pending = {};
    updateTier2Button();
    renderTier2Agents();
    renderTier2Examples();
    renderTier2Output();

    tier2Abort = new AbortController();

    try {
        const reader = await API.runIntelligencePlan(
            { query, region, language, sessionId, backend: selectedBackend },
            tier2Abort.signal
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
                handleTier2SSE(event);
            }
        }
        if (tier2State === 'running') tier2State = 'done';
    } catch (err) {
        if (err.name !== 'AbortError') {
            tier2State = 'error';
            renderTier2Output(`Intelligence Crew interrupted: ${err.message}`);
        } else {
            tier2State = 'idle';
        }
    }

    updateTier2Button();
    renderTier2Agents();
}

function handleTier2SSE(event) {
    switch (event.type) {
        case 'pipeline_start':
            tier2RunId = event.run_id;
            break;

        case 'tool_call':
        case 'tool_result':
        case 'self_heal': {
            const w = event.worker || 'unknown';
            if (!tier2Pending[w]) tier2Pending[w] = [];
            tier2Pending[w].push(event);
            const existing = tier2Turns.find(t => t.agentId === w);
            if (existing) {
                existing.toolActivity = tier2Pending[w];
                renderTier2Output();
            }
            break;
        }

        case 'agent_start': {
            tier2Active = event.agent;
            tier2Turns.push({
                agentId: event.agent,
                role: event.role,
                color: event.color,
                icon: event.icon || '🤖',
                content: '',
                done: false,
                toolActivity: tier2Pending[event.agent] || [],
            });
            renderTier2Agents();
            renderTier2Output();
            break;
        }

        case 'token': {
            const turn = tier2Turns.find(t => t.agentId === event.agent && !t.done);
            if (turn) {
                turn.content += event.content;
                const el = document.getElementById(`t2-content-${turn.agentId}`);
                if (el) {
                    el.innerHTML = escapeHtml(turn.content) + `<span class="am-cursor" style="background: ${turn.color}"></span>`;
                    scrollTier2ToBottom();
                }
            }
            break;
        }

        case 'agent_done': {
            const turn = tier2Turns.find(t => t.agentId === event.agent);
            if (turn) turn.done = true;
            tier2Done.add(event.agent);
            tier2Active = null;
            renderTier2Agents();
            renderTier2Output();
            break;
        }

        case 'done':
            tier2State = 'done';
            updateTier2Button();
            renderTier2Agents();
            renderTier2Output();
            break;

        case 'error':
            tier2State = 'error';
            updateTier2Button();
            renderTier2Output(event.message);
            break;

        case 'cancelled':
            tier2State = 'idle';
            updateTier2Button();
            break;
    }
}

function stopTier2() {
    if (tier2Abort) tier2Abort.abort();
    tier2State = 'idle';
    tier2Active = null;
    updateTier2Button();
    renderTier2Agents();
}

function resetTier2() {
    tier2Turns = [];
    tier2Active = null;
    tier2Done = new Set();
    tier2RunId = null;
    tier2State = 'idle';
    updateTier2Button();
    renderTier2Agents();
    renderTier2Examples();
    renderTier2Output();
}

function renderTier2Output(errorMsg) {
    const area = document.getElementById('tier2-output-area');
    const crew = tier2Config ? (tier2Config.agents || []) : [];

    if (tier2Turns.length === 0 && !errorMsg) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🛰️</div>
                <h3>Ready for intelligence analysis</h3>
                <p>Pick a region and language, enter an analysis query, and the Intelligence Crew will fuse open-source research, behavior forecasting, and social strategy into a cross-channel brief.</p>
                <div class="agent-dots">
                    ${crew.map(a => `<span class="dot"><span class="dot-circle" style="background: ${a.color}"></span> ${a.role}</span>`).join('')}
                </div>
            </div>
        `;
        return;
    }

    let html = '';
    if (errorMsg) {
        html += `<div class="error-banner">${errorMsg}</div>`;
    }

    html += '<div class="output-log" id="tier2-output-log">';
    for (const turn of tier2Turns) {
        const cursorHtml = !turn.done
            ? `<span class="am-cursor" style="background: ${turn.color}"></span>`
            : '';
        html += `
            <div class="agent-message" id="t2-msg-${turn.agentId}">
                <div class="am-header">
                    <div class="am-icon" style="background: ${turn.color}15; border: 1px solid ${turn.color}30">${turn.icon}</div>
                    <span class="am-role" style="color: ${turn.color}">${turn.role}</span>
                    ${!turn.done ? '<span class="spinner" style="width:10px;height:10px"></span>' : ''}
                    ${turn.done ? `<button class="am-copy" onclick="copyTier2Content('${turn.agentId}')">📋</button>` : ''}
                </div>
                ${renderToolActivity(turn.toolActivity)}
                <div class="am-content" id="t2-content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }
    if (tier2State === 'done') {
        html += '<div class="pipeline-complete">Intelligence brief complete</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollTier2ToBottom();
}

function scrollTier2ToBottom() {
    const log = document.getElementById('tier2-output-log');
    if (log) log.scrollTop = log.scrollHeight;
}

function copyTier2Content(agentId) {
    const turn = tier2Turns.find(t => t.agentId === agentId);
    if (turn) navigator.clipboard.writeText(turn.content);
}

/* ── TIER 2 · Media Crew (Duix-Avatar Pipeline) ─────── */

let mediaConfig = null;
let mediaState = 'idle';
let mediaTurns = [];
let mediaActive = null;
let mediaDone = new Set();
let mediaRunId = null;
let mediaAbort = null;
let mediaPending = {};
let mediaVoiceTool = 'chatterbox';
let mediaVideoTool = 'wan2';
let mediaAvatarTool = 'duix';

const MEDIA_EXAMPLES = [
    "A public-service explainer on protecting your CNIC from SIM fraud",
    "A 60-second training clip on spotting phishing messages",
    "An awareness reel on OTP-sharing scams for rural audiences",
    "A short authoritative brief on new PTA SIM registration rules",
];

async function showMedia() {
    setView('media');
    await setupMediaView();
}

async function setupMediaView() {
    if (!mediaConfig) {
        try {
            mediaConfig = await API.getMediaConfig();
        } catch (err) {
            console.error('Media config load error:', err);
            return;
        }
    }

    renderMediaAgents();
    renderMediaBackend();
    renderMediaSelectors();
    renderMediaToolPickers();
    renderMediaExamples();
    document.getElementById('media-session-display').textContent = sessionId.slice(0, 16) + '…';
    renderMediaOutput();
    updateMediaButton();

    const textarea = document.getElementById('media-topic');
    if (!textarea.dataset.bound) {
        textarea.dataset.bound = '1';
        textarea.addEventListener('input', () => {
            updateMediaCharCount();
            updateMediaButton();
        });
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runMedia();
        });
    }
}

function renderMediaSelectors() {
    document.getElementById('media-tone').innerHTML =
        (mediaConfig.tones || []).map(t => `<option value="${t}">${t}</option>`).join('');
    document.getElementById('media-language').innerHTML =
        (mediaConfig.languages || []).map(l => `<option value="${l.code}" data-label="${l.label}">${l.label} · ${l.native}</option>`).join('');
    document.getElementById('media-duration').innerHTML =
        (mediaConfig.durations || []).map(d => `<option value="${d}">${d}</option>`).join('');
}

function renderMediaToolPickers() {
    renderMediaPills('media-voice-tools', mediaConfig.voice_tools || [], mediaVoiceTool, 'selectMediaVoice');
    renderMediaPills('media-video-tools', mediaConfig.video_tools || [], mediaVideoTool, 'selectMediaVideo');
    renderMediaPills('media-avatar-tools', mediaConfig.avatar_tools || [], mediaAvatarTool, 'selectMediaAvatar');
}

function renderMediaPills(containerId, tools, selected, handler) {
    const container = document.getElementById(containerId);
    container.innerHTML = tools.map(t => {
        const active = selected === t.id ? 'active' : '';
        const online = t.online ? '<span class="media-online-tag">online</span>' : '';
        return `<button class="fw-pill ${active}" title="${t.note}" onclick="${handler}('${t.id}')">${t.label} ${online}</button>`;
    }).join('');
}

function selectMediaVoice(id) { mediaVoiceTool = id; renderMediaToolPickers(); }
function selectMediaVideo(id) { mediaVideoTool = id; renderMediaToolPickers(); }
function selectMediaAvatar(id) { mediaAvatarTool = id; renderMediaToolPickers(); }

function renderMediaAgents() {
    const list = document.getElementById('media-agent-list');
    const crew = mediaConfig.agents || [];
    list.innerHTML = crew.map((a, i) => {
        const isActive = mediaActive === a.id;
        const isDone = mediaDone.has(a.id);
        let statusHtml = '';
        if (isActive) {
            statusHtml = `<span class="pa-status" style="color: ${a.color}"><span class="spinner" style="border-top-color: ${a.color}"></span> Running</span>`;
        } else if (isDone) {
            statusHtml = '<span class="pa-status" style="color: var(--accent-green)">✓</span>';
        }
        let bgStyle = '';
        let borderStyle = 'border-color: var(--border)';
        if (isActive) {
            bgStyle = `background: ${a.color}08`;
            borderStyle = `border-color: ${a.color}30`;
        } else if (isDone) {
            bgStyle = 'background: var(--bg-card); opacity: 0.7';
        }
        const arrow = i < crew.length - 1 ? '<div class="pa-arrow">▼</div>' : '';
        return `
            <div class="pa-agent ${isActive ? 'active' : ''}" style="${bgStyle}; ${borderStyle}">
                <div class="pa-row">
                    <div class="pa-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                    <span class="pa-role">${a.role}</span>
                    ${statusHtml}
                </div>
                <div class="pa-desc">${a.description}</div>
                <div class="pa-fw" style="color: ${a.color}">${a.framework}</div>
            </div>
            ${arrow}
        `;
    }).join('');
}

function renderMediaBackend() {
    const container = document.getElementById('media-backend');
    const cfg = mediaConfig.config || {};
    const backends = cfg.backends || [];
    const readyBackends = backends.filter(b => b.status === 'ready');
    if (readyBackends.length === 0) {
        container.innerHTML = '<div class="fw-group"><label class="fw-label">Backend</label><div class="fw-pills"><span class="backend-pill">Demo mode</span></div></div>';
        return;
    }
    let html = '<div class="fw-group"><label class="fw-label">LLM Backend</label><div class="fw-pills">';
    const autoActive = !selectedBackend ? 'active' : '';
    html += `<button class="fw-pill ${autoActive}" onclick="selectMediaBackend('')">Auto</button>`;
    for (const be of readyBackends) {
        const active = selectedBackend === be.id ? 'active' : '';
        const label = be.id === 'ollama' ? `Ollama (${be.model})` : `OpenAI (${be.model})`;
        html += `<button class="fw-pill ${active}" onclick="selectMediaBackend('${be.id}')">${label}</button>`;
    }
    html += '</div></div>';
    container.innerHTML = html;
}

function selectMediaBackend(be) {
    selectedBackend = be;
    localStorage.setItem('brain_backend', be);
    renderMediaBackend();
}

function renderMediaExamples() {
    const area = document.getElementById('media-examples-area');
    const chips = document.getElementById('media-example-chips');
    if (mediaState !== 'idle' || mediaTurns.length > 0) {
        area.classList.add('hidden');
        return;
    }
    area.classList.remove('hidden');
    chips.innerHTML = MEDIA_EXAMPLES.map(t => {
        const display = t.length > 60 ? t.slice(0, 60) + '…' : t;
        return `<button class="example-chip" onclick="setMediaTopic('${t.replace(/'/g, "\\'")}')">${display}</button>`;
    }).join('');
}

function setMediaTopic(text) {
    const textarea = document.getElementById('media-topic');
    textarea.value = text;
    updateMediaCharCount();
    updateMediaButton();
}

function updateMediaCharCount() {
    const textarea = document.getElementById('media-topic');
    document.getElementById('media-char-count').textContent = `${textarea.value.length}/2000 · Ctrl+Enter to run`;
}

function updateMediaButton() {
    const textarea = document.getElementById('media-topic');
    const btnRun = document.getElementById('media-btn-run');
    const btnStop = document.getElementById('media-btn-stop');
    const btnReset = document.getElementById('media-btn-reset');

    btnRun.disabled = !textarea.value.trim() || mediaState === 'running' || mediaState === 'done';

    if (mediaState === 'running') {
        btnRun.classList.add('hidden');
        btnStop.classList.remove('hidden');
        btnReset.classList.add('hidden');
    } else if (mediaState === 'done' || mediaState === 'error') {
        btnRun.classList.add('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.remove('hidden');
    } else {
        btnRun.classList.remove('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.add('hidden');
    }
    textarea.disabled = mediaState === 'running';
}

async function runMedia() {
    const textarea = document.getElementById('media-topic');
    const topic = textarea.value.trim();
    if (!topic || mediaState === 'running') return;

    const tone = document.getElementById('media-tone').value;
    const langSel = document.getElementById('media-language');
    const languageCode = langSel.value;
    const language = langSel.selectedOptions[0].dataset.label || 'English';
    const duration = document.getElementById('media-duration').value;

    mediaState = 'running';
    mediaTurns = [];
    mediaActive = null;
    mediaDone = new Set();
    mediaRunId = null;
    mediaPending = {};
    updateMediaButton();
    renderMediaAgents();
    renderMediaExamples();
    renderMediaOutput();

    mediaAbort = new AbortController();

    try {
        const reader = await API.runMediaProduce({
            topic, tone, language, languageCode, duration,
            voiceTool: mediaVoiceTool, videoTool: mediaVideoTool, avatarTool: mediaAvatarTool,
            sessionId, backend: selectedBackend,
        }, mediaAbort.signal);
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
                handleMediaSSE(event);
            }
        }
        if (mediaState === 'running') mediaState = 'done';
    } catch (err) {
        if (err.name !== 'AbortError') {
            mediaState = 'error';
            renderMediaOutput(`Media Crew interrupted: ${err.message}`);
        } else {
            mediaState = 'idle';
        }
    }

    updateMediaButton();
    renderMediaAgents();
}

function handleMediaSSE(event) {
    switch (event.type) {
        case 'pipeline_start':
            mediaRunId = event.run_id;
            break;

        case 'tool_call':
        case 'tool_result':
        case 'self_heal': {
            const w = event.worker || 'unknown';
            if (!mediaPending[w]) mediaPending[w] = [];
            mediaPending[w].push(event);
            const existing = mediaTurns.find(t => t.agentId === w);
            if (existing) {
                existing.toolActivity = mediaPending[w];
                renderMediaOutput();
            }
            break;
        }

        case 'agent_start': {
            mediaActive = event.agent;
            mediaTurns.push({
                agentId: event.agent,
                role: event.role,
                color: event.color,
                icon: event.icon || '🎬',
                content: '',
                done: false,
                toolActivity: mediaPending[event.agent] || [],
            });
            renderMediaAgents();
            renderMediaOutput();
            break;
        }

        case 'token': {
            const turn = mediaTurns.find(t => t.agentId === event.agent && !t.done);
            if (turn) {
                turn.content += event.content;
                const el = document.getElementById(`media-content-${turn.agentId}`);
                if (el) {
                    el.innerHTML = escapeHtml(turn.content) + `<span class="am-cursor" style="background: ${turn.color}"></span>`;
                    scrollMediaToBottom();
                }
            }
            break;
        }

        case 'agent_done': {
            const turn = mediaTurns.find(t => t.agentId === event.agent);
            if (turn) turn.done = true;
            mediaDone.add(event.agent);
            mediaActive = null;
            renderMediaAgents();
            renderMediaOutput();
            break;
        }

        case 'done':
            mediaState = 'done';
            updateMediaButton();
            renderMediaAgents();
            renderMediaOutput();
            break;

        case 'error':
            mediaState = 'error';
            updateMediaButton();
            renderMediaOutput(event.message);
            break;

        case 'cancelled':
            mediaState = 'idle';
            updateMediaButton();
            break;
    }
}

function stopMedia() {
    if (mediaAbort) mediaAbort.abort();
    mediaState = 'idle';
    mediaActive = null;
    updateMediaButton();
    renderMediaAgents();
}

function resetMedia() {
    mediaTurns = [];
    mediaActive = null;
    mediaDone = new Set();
    mediaRunId = null;
    mediaState = 'idle';
    updateMediaButton();
    renderMediaAgents();
    renderMediaExamples();
    renderMediaOutput();
}

function renderMediaOutput(errorMsg) {
    const area = document.getElementById('media-output-area');
    const crew = mediaConfig ? (mediaConfig.agents || []) : [];

    if (mediaTurns.length === 0 && !errorMsg) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎬</div>
                <h3>Ready to produce</h3>
                <p>Pick tone, language, duration and your offline-first tool chain, enter a topic, and the Media Crew will produce a full digital-human production plan.</p>
                <div class="agent-dots">
                    ${crew.map(a => `<span class="dot"><span class="dot-circle" style="background: ${a.color}"></span> ${a.role}</span>`).join('')}
                </div>
            </div>
        `;
        return;
    }

    let html = '';
    if (errorMsg) {
        html += `<div class="error-banner">${errorMsg}</div>`;
    }

    html += '<div class="output-log" id="media-output-log">';
    for (const turn of mediaTurns) {
        const cursorHtml = !turn.done
            ? `<span class="am-cursor" style="background: ${turn.color}"></span>`
            : '';
        html += `
            <div class="agent-message" id="media-msg-${turn.agentId}">
                <div class="am-header">
                    <div class="am-icon" style="background: ${turn.color}15; border: 1px solid ${turn.color}30">${turn.icon}</div>
                    <span class="am-role" style="color: ${turn.color}">${turn.role}</span>
                    ${!turn.done ? '<span class="spinner" style="width:10px;height:10px"></span>' : ''}
                    ${turn.done ? `<button class="am-copy" onclick="copyMediaContent('${turn.agentId}')">📋</button>` : ''}
                </div>
                ${renderToolActivity(turn.toolActivity)}
                <div class="am-content" id="media-content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }
    if (mediaState === 'done') {
        html += '<div class="pipeline-complete">Production plan complete</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollMediaToBottom();
}

function scrollMediaToBottom() {
    const log = document.getElementById('media-output-log');
    if (log) log.scrollTop = log.scrollHeight;
}

function copyMediaContent(agentId) {
    const turn = mediaTurns.find(t => t.agentId === agentId);
    if (turn) navigator.clipboard.writeText(turn.content);
}

/* ── TIER 2 · Video Stack (face-swap / lip-sync) ────── */

let videoConfig = null;
let videoState = 'idle';
let videoTurns = [];
let videoActive = null;
let videoDone = new Set();
let videoRunId = null;
let videoAbort = null;
let videoPending = {};
let videoSwapTool = 'deepfacelab';
let videoLipsyncTool = 'wav2lip';
let videoCompliance = null;

const VIDEO_EXAMPLES = [
    "A consented training video with a spokesperson explaining SIM-registration rules",
    "An internal onboarding clip using a licensed avatar presenter",
    "A public-awareness anchor segment on OTP scams (synthetic, watermarked)",
    "A dubbed explainer re-voiced into Saraiki with lip-sync",
];

async function showVideo() {
    setView('video');
    await setupVideoView();
}

async function setupVideoView() {
    if (!videoConfig) {
        try {
            videoConfig = await API.getVideoConfig();
        } catch (err) {
            console.error('Video config load error:', err);
            return;
        }
    }

    renderVideoAgents();
    renderVideoBackend();
    renderVideoSelectors();
    renderVideoToolPickers();
    renderVideoExamples();
    const lpBox = document.getElementById('video-legal-proxy');
    if (lpBox) lpBox.classList.toggle('hidden', !videoConfig.legal_proxy_enabled);
    if (videoConfig.legal_proxy_enabled) refreshLedgerStatus();
    document.getElementById('video-session-display').textContent = sessionId.slice(0, 16) + '…';
    renderVideoOutput();
    updateVideoButton();
    refreshAuditStats();

    const textarea = document.getElementById('video-topic');
    if (!textarea.dataset.bound) {
        textarea.dataset.bound = '1';
        textarea.addEventListener('input', () => {
            updateVideoCharCount();
            updateVideoButton();
        });
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runVideo();
        });
    }
}

function renderVideoSelectors() {
    document.getElementById('video-style').innerHTML =
        (videoConfig.styles || []).map(s => `<option value="${s}">${s}</option>`).join('');
    document.getElementById('video-duration').innerHTML =
        (videoConfig.durations || []).map(d => `<option value="${d}">${d}</option>`).join('');
}

function renderVideoToolPickers() {
    renderMediaPills('video-swap-tools', videoConfig.swap_tools || [], videoSwapTool, 'selectVideoSwap');
    renderMediaPills('video-lipsync-tools', videoConfig.lipsync_tools || [], videoLipsyncTool, 'selectVideoLipsync');
}

function selectVideoSwap(id) { videoSwapTool = id; renderVideoToolPickers(); }
function selectVideoLipsync(id) { videoLipsyncTool = id; renderVideoToolPickers(); }

function renderVideoAgents() {
    const list = document.getElementById('video-agent-list');
    const crew = videoConfig.agents || [];
    list.innerHTML = crew.map((a, i) => {
        const isActive = videoActive === a.id;
        const isDone = videoDone.has(a.id);
        let statusHtml = '';
        if (isActive) {
            statusHtml = `<span class="pa-status" style="color: ${a.color}"><span class="spinner" style="border-top-color: ${a.color}"></span> Running</span>`;
        } else if (isDone) {
            statusHtml = '<span class="pa-status" style="color: var(--accent-green)">✓</span>';
        }
        let bgStyle = '';
        let borderStyle = 'border-color: var(--border)';
        if (isActive) {
            bgStyle = `background: ${a.color}08`;
            borderStyle = `border-color: ${a.color}30`;
        } else if (isDone) {
            bgStyle = 'background: var(--bg-card); opacity: 0.7';
        }
        const arrow = i < crew.length - 1 ? '<div class="pa-arrow">▼</div>' : '';
        return `
            <div class="pa-agent ${isActive ? 'active' : ''}" style="${bgStyle}; ${borderStyle}">
                <div class="pa-row">
                    <div class="pa-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                    <span class="pa-role">${a.role}</span>
                    ${statusHtml}
                </div>
                <div class="pa-desc">${a.description}</div>
                <div class="pa-fw" style="color: ${a.color}">${a.framework}</div>
            </div>
            ${arrow}
        `;
    }).join('');
}

function renderVideoBackend() {
    const container = document.getElementById('video-backend');
    const cfg = videoConfig.config || {};
    const backends = cfg.backends || [];
    const readyBackends = backends.filter(b => b.status === 'ready');
    if (readyBackends.length === 0) {
        container.innerHTML = '<div class="fw-group"><label class="fw-label">Backend</label><div class="fw-pills"><span class="backend-pill">Demo mode</span></div></div>';
        return;
    }
    let html = '<div class="fw-group"><label class="fw-label">LLM Backend</label><div class="fw-pills">';
    const autoActive = !selectedBackend ? 'active' : '';
    html += `<button class="fw-pill ${autoActive}" onclick="selectVideoBackend('')">Auto</button>`;
    for (const be of readyBackends) {
        const active = selectedBackend === be.id ? 'active' : '';
        const label = be.id === 'ollama' ? `Ollama (${be.model})` : `OpenAI (${be.model})`;
        html += `<button class="fw-pill ${active}" onclick="selectVideoBackend('${be.id}')">${label}</button>`;
    }
    html += '</div></div>';
    container.innerHTML = html;
}

function selectVideoBackend(be) {
    selectedBackend = be;
    localStorage.setItem('brain_backend', be);
    renderVideoBackend();
}

function renderVideoExamples() {
    const area = document.getElementById('video-examples-area');
    const chips = document.getElementById('video-example-chips');
    if (videoState !== 'idle' || videoTurns.length > 0) {
        area.classList.add('hidden');
        return;
    }
    area.classList.remove('hidden');
    chips.innerHTML = VIDEO_EXAMPLES.map(t => {
        const display = t.length > 60 ? t.slice(0, 60) + '…' : t;
        return `<button class="example-chip" onclick="setVideoTopic('${t.replace(/'/g, "\\'")}')">${display}</button>`;
    }).join('');
}

function setVideoTopic(text) {
    const textarea = document.getElementById('video-topic');
    textarea.value = text;
    updateVideoCharCount();
    updateVideoButton();
}

function updateVideoCharCount() {
    const textarea = document.getElementById('video-topic');
    document.getElementById('video-char-count').textContent = `${textarea.value.length}/2000 · Ctrl+Enter to run`;
}

function updateVideoButton() {
    const textarea = document.getElementById('video-topic');
    const btnRun = document.getElementById('video-btn-run');
    const btnStop = document.getElementById('video-btn-stop');
    const btnReset = document.getElementById('video-btn-reset');

    btnRun.disabled = !textarea.value.trim() || videoState === 'running' || videoState === 'done';

    if (videoState === 'running') {
        btnRun.classList.add('hidden');
        btnStop.classList.remove('hidden');
        btnReset.classList.add('hidden');
    } else if (videoState === 'done' || videoState === 'error') {
        btnRun.classList.add('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.remove('hidden');
    } else {
        btnRun.classList.remove('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.add('hidden');
    }
    textarea.disabled = videoState === 'running';
}

async function runVideo() {
    const textarea = document.getElementById('video-topic');
    const topic = textarea.value.trim();
    if (!topic || videoState === 'running') return;

    const style = document.getElementById('video-style').value;
    const duration = document.getElementById('video-duration').value;
    const consent = document.getElementById('video-consent').checked;
    const approverEl = document.getElementById('video-approver');
    const authRefEl = document.getElementById('video-auth-ref');
    const approver = approverEl ? approverEl.value.trim() : '';
    const authorizationRef = authRefEl ? authRefEl.value.trim() : '';

    videoState = 'running';
    videoTurns = [];
    videoActive = null;
    videoDone = new Set();
    videoRunId = null;
    videoPending = {};
    videoCompliance = null;
    updateVideoButton();
    renderVideoAgents();
    renderVideoExamples();
    renderVideoOutput();

    videoAbort = new AbortController();

    try {
        const reader = await API.runVideoPlan({
            topic, style, duration,
            swapTool: videoSwapTool, lipsyncTool: videoLipsyncTool, consent,
            approver, authorizationRef,
            sessionId, backend: selectedBackend,
        }, videoAbort.signal);
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
                handleVideoSSE(event);
            }
        }
        if (videoState === 'running') videoState = 'done';
    } catch (err) {
        if (err.name !== 'AbortError') {
            videoState = 'error';
            renderVideoOutput(`Video Stack interrupted: ${err.message}`);
        } else {
            videoState = 'idle';
        }
    }

    updateVideoButton();
    renderVideoAgents();
    refreshAuditStats();
}

function handleVideoSSE(event) {
    switch (event.type) {
        case 'pipeline_start':
            videoRunId = event.run_id;
            break;

        case 'compliance':
            videoCompliance = event;
            renderVideoOutput();
            break;

        case 'compliance_block':
            videoCompliance = Object.assign({}, videoCompliance, { blocked: true, message: event.message });
            videoState = 'error';
            renderVideoOutput();
            break;

        case 'tool_call':
        case 'tool_result':
        case 'self_heal': {
            const w = event.worker || 'unknown';
            if (!videoPending[w]) videoPending[w] = [];
            videoPending[w].push(event);
            const existing = videoTurns.find(t => t.agentId === w);
            if (existing) {
                existing.toolActivity = videoPending[w];
                renderVideoOutput();
            }
            break;
        }

        case 'agent_start': {
            videoActive = event.agent;
            videoTurns.push({
                agentId: event.agent,
                role: event.role,
                color: event.color,
                icon: event.icon || '🎬',
                content: '',
                done: false,
                toolActivity: videoPending[event.agent] || [],
            });
            renderVideoAgents();
            renderVideoOutput();
            break;
        }

        case 'token': {
            const turn = videoTurns.find(t => t.agentId === event.agent && !t.done);
            if (turn) {
                turn.content += event.content;
                const el = document.getElementById(`video-content-${turn.agentId}`);
                if (el) {
                    el.innerHTML = escapeHtml(turn.content) + `<span class="am-cursor" style="background: ${turn.color}"></span>`;
                    scrollVideoToBottom();
                }
            }
            break;
        }

        case 'agent_done': {
            const turn = videoTurns.find(t => t.agentId === event.agent);
            if (turn) turn.done = true;
            videoDone.add(event.agent);
            videoActive = null;
            renderVideoAgents();
            renderVideoOutput();
            break;
        }

        case 'done':
            videoState = event.blocked ? 'error' : 'done';
            updateVideoButton();
            renderVideoAgents();
            renderVideoOutput();
            break;

        case 'error':
            videoState = 'error';
            updateVideoButton();
            renderVideoOutput(event.message);
            break;

        case 'cancelled':
            videoState = 'idle';
            updateVideoButton();
            break;
    }
}

function stopVideo() {
    if (videoAbort) videoAbort.abort();
    videoState = 'idle';
    videoActive = null;
    updateVideoButton();
    renderVideoAgents();
}

function resetVideo() {
    videoTurns = [];
    videoActive = null;
    videoDone = new Set();
    videoRunId = null;
    videoState = 'idle';
    videoCompliance = null;
    updateVideoButton();
    renderVideoAgents();
    renderVideoExamples();
    renderVideoOutput();
}

function renderComplianceBanner() {
    if (!videoCompliance) return '';
    if (videoCompliance.override) {
        return `<div class="compliance-banner sensitive">
            <strong>🔴 PRE-CLEARED LEGAL PROXY — SENSITIVE.</strong> Flagged content was cleared under an elevated override and logged in red for legal review. ${escapeHtml((videoCompliance.reasons || []).join('; '))}
            <div class="cb-audit">Audit ID: ${videoCompliance.audit_id}</div>
        </div>`;
    }
    if (videoCompliance.blocked) {
        return `<div class="compliance-banner flagged">
            <strong>⛔ Flagged — access limited.</strong> ${escapeHtml(videoCompliance.message || '')}
            <div class="cb-audit">Audit ID: ${videoCompliance.audit_id}</div>
        </div>`;
    }
    if (videoCompliance.flagged) {
        return `<div class="compliance-banner flagged">
            <strong>⚠ Flagged for review.</strong> ${escapeHtml((videoCompliance.reasons || []).join('; '))}
            <div class="cb-audit">Audit ID: ${videoCompliance.audit_id}</div>
        </div>`;
    }
    return `<div class="compliance-banner ok">
        <strong>✓ Cleared &amp; logged.</strong> Recorded for legal review — audit ID ${videoCompliance.audit_id}.
    </div>`;
}

function renderVideoOutput(errorMsg) {
    const area = document.getElementById('video-output-area');
    const crew = videoConfig ? (videoConfig.agents || []) : [];
    const banner = renderComplianceBanner();

    if (videoTurns.length === 0 && !errorMsg && !banner) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎬</div>
                <h3>Ready to plan a production</h3>
                <p>Pick a style, duration and offline tool chain, describe your (consented) project, and the Video Stack produces a full, audit-logged face-swap + lip-sync production plan.</p>
                <div class="agent-dots">
                    ${crew.map(a => `<span class="dot"><span class="dot-circle" style="background: ${a.color}"></span> ${a.role}</span>`).join('')}
                </div>
            </div>
        `;
        return;
    }

    let html = banner;
    if (errorMsg) {
        html += `<div class="error-banner">${errorMsg}</div>`;
    }

    html += '<div class="output-log" id="video-output-log">';
    for (const turn of videoTurns) {
        const cursorHtml = !turn.done
            ? `<span class="am-cursor" style="background: ${turn.color}"></span>`
            : '';
        html += `
            <div class="agent-message" id="video-msg-${turn.agentId}">
                <div class="am-header">
                    <div class="am-icon" style="background: ${turn.color}15; border: 1px solid ${turn.color}30">${turn.icon}</div>
                    <span class="am-role" style="color: ${turn.color}">${turn.role}</span>
                    ${!turn.done ? '<span class="spinner" style="width:10px;height:10px"></span>' : ''}
                    ${turn.done ? `<button class="am-copy" onclick="copyVideoContent('${turn.agentId}')">📋</button>` : ''}
                </div>
                ${renderToolActivity(turn.toolActivity)}
                <div class="am-content" id="video-content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }
    if (videoState === 'done') {
        html += '<div class="pipeline-complete">Production plan complete</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollVideoToBottom();
}

function scrollVideoToBottom() {
    const log = document.getElementById('video-output-log');
    if (log) log.scrollTop = log.scrollHeight;
}

function copyVideoContent(agentId) {
    const turn = videoTurns.find(t => t.agentId === agentId);
    if (turn) navigator.clipboard.writeText(turn.content);
}

async function refreshAuditStats() {
    try {
        const data = await API.getComplianceAudit(sessionId);
        const el = document.getElementById('video-audit-stats');
        if (el && data.stats) {
            el.textContent = `${data.stats.total_events} events logged · ${data.stats.flagged_events} flagged`;
        }
    } catch (err) {
        console.error('Audit stats error:', err);
    }
}

async function loadAuditLog() {
    const container = document.getElementById('video-audit-log');
    try {
        const data = await API.getComplianceAudit(sessionId);
        const events = data.events || [];
        if (events.length === 0) {
            container.innerHTML = '<div class="audit-empty">No recorded activity yet.</div>';
            return;
        }
        container.innerHTML = events.map(e => {
            const when = new Date(e.created_at * 1000).toLocaleTimeString();
            let cls = 'ok';
            if (e.sensitivity === 'red' || e.verdict === 'pre_cleared_legal_proxy') cls = 'sensitive';
            else if (e.verdict === 'flagged') cls = 'flagged';
            const reasons = e.reasons && e.reasons.length ? ` — ${escapeHtml(e.reasons.join('; '))}` : '';
            const approver = e.approver ? ` [approver: ${escapeHtml(e.approver)}]` : '';
            return `<div class="audit-row ${cls}">
                <span class="audit-when">${when}</span>
                <span class="audit-action">${escapeHtml(e.action)}</span>
                <span class="audit-verdict">${e.verdict}${approver}${reasons}</span>
            </div>`;
        }).join('');
    } catch (err) {
        container.innerHTML = `<div class="audit-empty">Failed to load audit log: ${err.message}</div>`;
    }
}

/* ── Legal-authorization ledger (shared across views) ── */

// The ledger is a single server-side resource; the Video and Cyber views each
// render a status element (class `ledger-status`). Update them all at once and
// read the approver from whichever legal-proxy panel is currently visible.
function setLedgerStatus(text, cls) {
    document.querySelectorAll('.ledger-status').forEach(el => {
        el.textContent = text;
        el.className = cls || 'ledger-status';
    });
}

function activeApprover() {
    const personaView = document.getElementById('view-persona');
    if (personaView && !personaView.classList.contains('hidden')) {
        return (document.getElementById('persona-approver') || {}).value || '';
    }
    const cyberView = document.getElementById('view-cyber');
    if (cyberView && !cyberView.classList.contains('hidden')) {
        return (document.getElementById('cyber-approver') || {}).value || '';
    }
    return (document.getElementById('video-approver') || {}).value || '';
}

async function refreshLedgerStatus() {
    if (!document.querySelector('.ledger-status')) return;
    try {
        const s = await API.getLedgerStatus();
        if (!s.loaded) {
            setLedgerStatus('Ledger not loaded.', 'ledger-status');
            return;
        }
        const when = new Date(s.fetched_at * 1000).toLocaleString();
        const sig = s.verified ? ' · ✓ signed' : (s.config && s.config.signature_required ? ' · UNVERIFIED' : '');
        const text = `${s.count} authorizations · via ${s.source} · ${when}${sig}` + (s.stale ? ' · STALE' : '');
        const cls = 'ledger-status' + ((s.stale || (s.config && s.config.signature_required && !s.verified)) ? ' stale' : ' ok');
        setLedgerStatus(text, cls);
    } catch (err) {
        setLedgerStatus(`Ledger status unavailable: ${err.message}`, 'ledger-status stale');
    }
}

async function fetchLedger(source) {
    const approver = activeApprover();
    setLedgerStatus(`Fetching via ${source}…`, 'ledger-status');
    try {
        await API.fetchLedger({ source, sessionId, approver });
        await refreshLedgerStatus();
        refreshAuditStats();
    } catch (err) {
        setLedgerStatus(`Fetch failed: ${err.message}`, 'ledger-status stale');
    }
}

async function fetchLedgerSSH() {
    const approver = activeApprover();
    const username = prompt('SSH username (used once, never stored):');
    if (username === null) return;
    const password = prompt('SSH password (used once, never stored):');
    if (password === null) return;
    setLedgerStatus('Fetching via SSH…', 'ledger-status');
    try {
        await API.fetchLedger({ source: 'ssh', sessionId, approver, username, password });
        await refreshLedgerStatus();
        refreshAuditStats();
    } catch (err) {
        setLedgerStatus(`SSH fetch failed: ${err.message}`, 'ledger-status stale');
    }
}

async function uploadLedger(event) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;
    const approver = activeApprover();
    const csvFile = files.find(f => f.name.toLowerCase().endsWith('.csv'));
    const sigFile = files.find(f => f.name.toLowerCase().endsWith('.sig'));
    if (!csvFile) {
        setLedgerStatus('Select the .csv file (and its .sig when signing is required).', 'ledger-status stale');
        event.target.value = '';
        return;
    }
    try {
        const csv = await csvFile.text();
        let signatureB64 = '';
        if (sigFile) {
            const buf = new Uint8Array(await sigFile.arrayBuffer());
            let binary = '';
            buf.forEach(b => { binary += String.fromCharCode(b); });
            signatureB64 = btoa(binary);
        }
        setLedgerStatus('Uploading…', 'ledger-status');
        await API.fetchLedger({ source: 'upload', sessionId, approver, csv, signatureB64 });
        await refreshLedgerStatus();
        refreshAuditStats();
    } catch (err) {
        setLedgerStatus(`Upload failed: ${err.message}`, 'ledger-status stale');
    } finally {
        event.target.value = '';
    }
}

/* ── TIER 2 · Cyber Crew ────────────────────────────── */

let cyberConfig = null;
let cyberState = 'idle';
let cyberTurns = [];
let cyberActive = null;
let cyberDone = new Set();
let cyberRunId = null;
let cyberAbort = null;
let cyberPending = {};
let cyberScanTool = 'nmap';
let cyberCompliance = null;

const CYBER_EXAMPLES = [
    "Assess the authorized staging web app at app.example-lab.internal",
    "External network pentest of the in-scope /24 lab range",
    "Purple-team exercise: validate detection of anomalous JA3 fingerprints",
    "Cloud config review of an owned, authorized test account",
];

async function showCyber() {
    setView('cyber');
    await setupCyberView();
}

async function setupCyberView() {
    if (!cyberConfig) {
        try {
            cyberConfig = await API.getCyberConfig();
        } catch (err) {
            console.error('Cyber config load error:', err);
            return;
        }
    }

    renderCyberAgents();
    renderCyberBackend();
    renderCyberSelectors();
    renderCyberExamples();
    document.getElementById('cyber-session-display').textContent = sessionId.slice(0, 16) + '…';
    renderCyberOutput();
    updateCyberButton();
    refreshCyberAuditStats();

    const lpBox = document.getElementById('cyber-legal-proxy');
    if (lpBox) lpBox.classList.toggle('hidden', !cyberConfig.legal_proxy_enabled);
    if (cyberConfig.legal_proxy_enabled) refreshLedgerStatus();

    const textarea = document.getElementById('cyber-target');
    if (!textarea.dataset.bound) {
        textarea.dataset.bound = '1';
        textarea.addEventListener('input', () => {
            updateCyberCharCount();
            updateCyberButton();
        });
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runCyber();
        });
    }
}

function renderCyberSelectors() {
    document.getElementById('cyber-engagement').innerHTML =
        (cyberConfig.engagements || []).map(s => `<option value="${s}">${s}</option>`).join('');
    const scanSel = document.getElementById('cyber-scan');
    scanSel.innerHTML =
        (cyberConfig.scan_tools || []).map(t => `<option value="${t.id}">${t.label}</option>`).join('');
    scanSel.value = cyberScanTool;
    if (!scanSel.dataset.bound) {
        scanSel.dataset.bound = '1';
        scanSel.addEventListener('change', () => { cyberScanTool = scanSel.value; });
    }
}

function renderCyberAgents() {
    const list = document.getElementById('cyber-agent-list');
    const crew = cyberConfig.agents || [];
    list.innerHTML = crew.map((a, i) => {
        const isActive = cyberActive === a.id;
        const isDone = cyberDone.has(a.id);
        let statusHtml = '';
        if (isActive) {
            statusHtml = `<span class="pa-status" style="color: ${a.color}"><span class="spinner" style="border-top-color: ${a.color}"></span> Running</span>`;
        } else if (isDone) {
            statusHtml = '<span class="pa-status" style="color: var(--accent-green)">✓</span>';
        }
        let bgStyle = '';
        let borderStyle = 'border-color: var(--border)';
        if (isActive) {
            bgStyle = `background: ${a.color}08`;
            borderStyle = `border-color: ${a.color}30`;
        } else if (isDone) {
            bgStyle = 'background: var(--bg-card); opacity: 0.7';
        }
        const arrow = i < crew.length - 1 ? '<div class="pa-arrow">▼</div>' : '';
        return `
            <div class="pa-agent ${isActive ? 'active' : ''}" style="${bgStyle}; ${borderStyle}">
                <div class="pa-row">
                    <div class="pa-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                    <span class="pa-role">${a.role}</span>
                    ${statusHtml}
                </div>
                <div class="pa-desc">${a.description}</div>
                <div class="pa-fw" style="color: ${a.color}">${a.framework}</div>
            </div>
            ${arrow}
        `;
    }).join('');
}

function renderCyberBackend() {
    const container = document.getElementById('cyber-backend');
    const cfg = cyberConfig.config || {};
    const backends = cfg.backends || [];
    const readyBackends = backends.filter(b => b.status === 'ready');
    if (readyBackends.length === 0) {
        container.innerHTML = '<div class="fw-group"><label class="fw-label">Backend</label><div class="fw-pills"><span class="backend-pill">Demo mode</span></div></div>';
        return;
    }
    let html = '<div class="fw-group"><label class="fw-label">LLM Backend</label><div class="fw-pills">';
    const autoActive = !selectedBackend ? 'active' : '';
    html += `<button class="fw-pill ${autoActive}" onclick="selectCyberBackend('')">Auto</button>`;
    for (const be of readyBackends) {
        const active = selectedBackend === be.id ? 'active' : '';
        const label = be.id === 'ollama' ? `Ollama (${be.model})` : `OpenAI (${be.model})`;
        html += `<button class="fw-pill ${active}" onclick="selectCyberBackend('${be.id}')">${label}</button>`;
    }
    html += '</div></div>';
    container.innerHTML = html;
}

function selectCyberBackend(be) {
    selectedBackend = be;
    localStorage.setItem('brain_backend', be);
    renderCyberBackend();
}

function renderCyberExamples() {
    const area = document.getElementById('cyber-examples-area');
    const chips = document.getElementById('cyber-example-chips');
    if (cyberState !== 'idle' || cyberTurns.length > 0) {
        area.classList.add('hidden');
        return;
    }
    area.classList.remove('hidden');
    chips.innerHTML = CYBER_EXAMPLES.map(t => {
        const display = t.length > 60 ? t.slice(0, 60) + '…' : t;
        return `<button class="example-chip" onclick="setCyberTarget('${t.replace(/'/g, "\\'")}')">${display}</button>`;
    }).join('');
}

function setCyberTarget(text) {
    const textarea = document.getElementById('cyber-target');
    textarea.value = text;
    updateCyberCharCount();
    updateCyberButton();
}

function updateCyberCharCount() {
    const textarea = document.getElementById('cyber-target');
    document.getElementById('cyber-char-count').textContent = `${textarea.value.length}/2000 · Ctrl+Enter to run`;
}

function updateCyberButton() {
    const textarea = document.getElementById('cyber-target');
    const btnRun = document.getElementById('cyber-btn-run');
    const btnStop = document.getElementById('cyber-btn-stop');
    const btnReset = document.getElementById('cyber-btn-reset');

    btnRun.disabled = !textarea.value.trim() || cyberState === 'running' || cyberState === 'done';

    if (cyberState === 'running') {
        btnRun.classList.add('hidden');
        btnStop.classList.remove('hidden');
        btnReset.classList.add('hidden');
    } else if (cyberState === 'done' || cyberState === 'error') {
        btnRun.classList.add('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.remove('hidden');
    } else {
        btnRun.classList.remove('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.add('hidden');
    }
    textarea.disabled = cyberState === 'running';
}

async function runCyber() {
    const textarea = document.getElementById('cyber-target');
    const target = textarea.value.trim();
    if (!target || cyberState === 'running') return;

    const engagement = document.getElementById('cyber-engagement').value;
    const authorized = document.getElementById('cyber-authorized').checked;
    const approverEl = document.getElementById('cyber-approver');
    const authRefEl = document.getElementById('cyber-auth-ref');
    const approver = approverEl ? approverEl.value.trim() : '';
    const authorizationRef = authRefEl ? authRefEl.value.trim() : '';

    cyberState = 'running';
    cyberTurns = [];
    cyberActive = null;
    cyberDone = new Set();
    cyberRunId = null;
    cyberPending = {};
    cyberCompliance = null;
    updateCyberButton();
    renderCyberAgents();
    renderCyberExamples();
    renderCyberOutput();

    cyberAbort = new AbortController();

    try {
        const reader = await API.runCyberPlan({
            target, engagement, scanTool: cyberScanTool, authorized,
            approver, authorizationRef,
            sessionId, backend: selectedBackend,
        }, cyberAbort.signal);
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
                handleCyberSSE(event);
            }
        }
        if (cyberState === 'running') cyberState = 'done';
    } catch (err) {
        if (err.name !== 'AbortError') {
            cyberState = 'error';
            renderCyberOutput(`Cyber Crew interrupted: ${err.message}`);
        } else {
            cyberState = 'idle';
        }
    }

    updateCyberButton();
    renderCyberAgents();
    refreshCyberAuditStats();
}

function handleCyberSSE(event) {
    switch (event.type) {
        case 'pipeline_start':
            cyberRunId = event.run_id;
            break;

        case 'compliance':
            cyberCompliance = event;
            renderCyberOutput();
            break;

        case 'compliance_block':
            cyberCompliance = Object.assign({}, cyberCompliance, { blocked: true, message: event.message });
            cyberState = 'error';
            renderCyberOutput();
            break;

        case 'tool_call':
        case 'tool_result':
        case 'self_heal': {
            const w = event.worker || 'unknown';
            if (!cyberPending[w]) cyberPending[w] = [];
            cyberPending[w].push(event);
            const existing = cyberTurns.find(t => t.agentId === w);
            if (existing) {
                existing.toolActivity = cyberPending[w];
                renderCyberOutput();
            }
            break;
        }

        case 'agent_start': {
            cyberActive = event.agent;
            cyberTurns.push({
                agentId: event.agent,
                role: event.role,
                color: event.color,
                icon: event.icon || '🛡️',
                content: '',
                done: false,
                toolActivity: cyberPending[event.agent] || [],
            });
            renderCyberAgents();
            renderCyberOutput();
            break;
        }

        case 'token': {
            const turn = cyberTurns.find(t => t.agentId === event.agent && !t.done);
            if (turn) {
                turn.content += event.content;
                const el = document.getElementById(`cyber-content-${turn.agentId}`);
                if (el) {
                    el.innerHTML = escapeHtml(turn.content) + `<span class="am-cursor" style="background: ${turn.color}"></span>`;
                    scrollCyberToBottom();
                }
            }
            break;
        }

        case 'agent_done': {
            const turn = cyberTurns.find(t => t.agentId === event.agent);
            if (turn) turn.done = true;
            cyberDone.add(event.agent);
            cyberActive = null;
            renderCyberAgents();
            renderCyberOutput();
            break;
        }

        case 'done':
            cyberState = event.blocked ? 'error' : 'done';
            updateCyberButton();
            renderCyberAgents();
            renderCyberOutput();
            break;

        case 'error':
            cyberState = 'error';
            updateCyberButton();
            renderCyberOutput(event.message);
            break;

        case 'cancelled':
            cyberState = 'idle';
            updateCyberButton();
            break;
    }
}

function stopCyber() {
    if (cyberAbort) cyberAbort.abort();
    cyberState = 'idle';
    cyberActive = null;
    updateCyberButton();
    renderCyberAgents();
}

function resetCyber() {
    cyberTurns = [];
    cyberActive = null;
    cyberDone = new Set();
    cyberRunId = null;
    cyberState = 'idle';
    cyberCompliance = null;
    updateCyberButton();
    renderCyberAgents();
    renderCyberExamples();
    renderCyberOutput();
}

function renderCyberComplianceBanner() {
    if (!cyberCompliance) return '';
    if (cyberCompliance.blocked) {
        return `<div class="compliance-banner flagged">
            <strong>⛔ Flagged — access limited.</strong> ${escapeHtml(cyberCompliance.message || '')}
            <div class="cb-audit">Audit ID: ${cyberCompliance.audit_id}</div>
        </div>`;
    }
    if (cyberCompliance.flagged) {
        return `<div class="compliance-banner flagged">
            <strong>⚠ Flagged for review.</strong> ${escapeHtml((cyberCompliance.reasons || []).join('; '))}
            <div class="cb-audit">Audit ID: ${cyberCompliance.audit_id}</div>
        </div>`;
    }
    return `<div class="compliance-banner ok">
        <strong>✓ Cleared &amp; logged.</strong> Recorded for legal review — audit ID ${cyberCompliance.audit_id}.
    </div>`;
}

function renderCyberOutput(errorMsg) {
    const area = document.getElementById('cyber-output-area');
    const crew = cyberConfig ? (cyberConfig.agents || []) : [];
    const banner = renderCyberComplianceBanner();

    if (cyberTurns.length === 0 && !errorMsg && !banner) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🛡️</div>
                <h3>Ready to plan an assessment</h3>
                <p>Pick an engagement type and scanner, describe the authorized in-scope target, and the Cyber Crew produces a full, audit-logged defensive assessment plan.</p>
                <div class="agent-dots">
                    ${crew.map(a => `<span class="dot"><span class="dot-circle" style="background: ${a.color}"></span> ${a.role}</span>`).join('')}
                </div>
            </div>
        `;
        return;
    }

    let html = banner;
    if (errorMsg) {
        html += `<div class="error-banner">${errorMsg}</div>`;
    }

    html += '<div class="output-log" id="cyber-output-log">';
    for (const turn of cyberTurns) {
        const cursorHtml = !turn.done
            ? `<span class="am-cursor" style="background: ${turn.color}"></span>`
            : '';
        html += `
            <div class="agent-message" id="cyber-msg-${turn.agentId}">
                <div class="am-header">
                    <div class="am-icon" style="background: ${turn.color}15; border: 1px solid ${turn.color}30">${turn.icon}</div>
                    <span class="am-role" style="color: ${turn.color}">${turn.role}</span>
                    ${!turn.done ? '<span class="spinner" style="width:10px;height:10px"></span>' : ''}
                    ${turn.done ? `<button class="am-copy" onclick="copyCyberContent('${turn.agentId}')">📋</button>` : ''}
                </div>
                ${renderToolActivity(turn.toolActivity)}
                <div class="am-content" id="cyber-content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }
    if (cyberState === 'done') {
        html += '<div class="pipeline-complete">Assessment plan complete</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollCyberToBottom();
}

function scrollCyberToBottom() {
    const log = document.getElementById('cyber-output-log');
    if (log) log.scrollTop = log.scrollHeight;
}

function copyCyberContent(agentId) {
    const turn = cyberTurns.find(t => t.agentId === agentId);
    if (turn) navigator.clipboard.writeText(turn.content);
}

async function refreshCyberAuditStats() {
    try {
        const data = await API.getComplianceAudit(sessionId);
        const el = document.getElementById('cyber-audit-stats');
        if (el && data.stats) {
            el.textContent = `${data.stats.total_events} events logged · ${data.stats.flagged_events} flagged`;
        }
    } catch (err) {
        console.error('Audit stats error:', err);
    }
}

async function loadCyberAuditLog() {
    const container = document.getElementById('cyber-audit-log');
    try {
        const data = await API.getComplianceAudit(sessionId);
        const events = data.events || [];
        if (events.length === 0) {
            container.innerHTML = '<div class="audit-empty">No recorded activity yet.</div>';
            return;
        }
        container.innerHTML = events.map(e => {
            const when = new Date(e.created_at * 1000).toLocaleTimeString();
            let cls = 'ok';
            if (e.sensitivity === 'red' || e.verdict === 'pre_cleared_legal_proxy') cls = 'sensitive';
            else if (e.verdict === 'flagged') cls = 'flagged';
            const reasons = e.reasons && e.reasons.length ? ` — ${escapeHtml(e.reasons.join('; '))}` : '';
            const approver = e.approver ? ` [approver: ${escapeHtml(e.approver)}]` : '';
            return `<div class="audit-row ${cls}">
                <span class="audit-when">${when}</span>
                <span class="audit-action">${escapeHtml(e.action)}</span>
                <span class="audit-verdict">${e.verdict}${approver}${reasons}</span>
            </div>`;
        }).join('');
    } catch (err) {
        container.innerHTML = `<div class="audit-empty">Failed to load audit log: ${err.message}</div>`;
    }
}

/* ── TIER 3 · Persona Orchestration ─────────────────── */

let personaConfig = null;
let personaState = 'idle';
let personaTurns = [];
let personaActive = null;
let personaDone = new Set();
let personaRunId = null;
let personaAbort = null;
let personaPending = {};
let personaCompliance = null;

const PERSONA_EXAMPLES = [
    "Model a synthetic-persona fleet to build detection signatures for coordinated inauthentic behavior",
    "Blue-team tabletop: map how a bot fleet would coordinate so we can detect it",
    "Design lab personas with regional dialects to test our authenticity classifier",
    "Study platform-integrity signals for a simulated multi-account campaign",
];

async function showPersona() {
    setView('persona');
    await setupPersonaView();
}

async function setupPersonaView() {
    if (!personaConfig) {
        try {
            personaConfig = await API.getPersonaConfig();
        } catch (err) {
            console.error('Persona config load error:', err);
            return;
        }
    }

    renderPersonaAgents();
    renderPersonaBackend();
    renderPersonaSelectors();
    renderPersonaExamples();
    document.getElementById('persona-session-display').textContent = sessionId.slice(0, 16) + '…';
    renderPersonaOutput();
    updatePersonaButton();
    refreshPersonaAuditStats();

    const lpBox = document.getElementById('persona-legal-proxy');
    if (lpBox) lpBox.classList.toggle('hidden', !personaConfig.legal_proxy_enabled);
    if (personaConfig.legal_proxy_enabled) refreshLedgerStatus();

    const textarea = document.getElementById('persona-objective');
    if (!textarea.dataset.bound) {
        textarea.dataset.bound = '1';
        textarea.addEventListener('input', () => {
            updatePersonaCharCount();
            updatePersonaButton();
        });
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) runPersona();
        });
    }
}

function renderPersonaSelectors() {
    document.getElementById('persona-scenario').innerHTML =
        (personaConfig.scenarios || []).map(s => `<option value="${s}">${s}</option>`).join('');
    document.getElementById('persona-platform').innerHTML =
        (personaConfig.platforms || []).map(p => `<option value="${p.id}">${p.label}</option>`).join('');
    document.getElementById('persona-region').innerHTML =
        (personaConfig.regions || []).map(r => `<option value="${r.id}">${r.label}</option>`).join('');
}

function renderPersonaAgents() {
    const list = document.getElementById('persona-agent-list');
    const crew = personaConfig.agents || [];
    list.innerHTML = crew.map((a, i) => {
        const isActive = personaActive === a.id;
        const isDone = personaDone.has(a.id);
        let statusHtml = '';
        if (isActive) {
            statusHtml = `<span class="pa-status" style="color: ${a.color}"><span class="spinner" style="border-top-color: ${a.color}"></span> Running</span>`;
        } else if (isDone) {
            statusHtml = '<span class="pa-status" style="color: var(--accent-green)">✓</span>';
        }
        let bgStyle = '';
        let borderStyle = 'border-color: var(--border)';
        if (isActive) {
            bgStyle = `background: ${a.color}08`;
            borderStyle = `border-color: ${a.color}30`;
        } else if (isDone) {
            bgStyle = 'background: var(--bg-card); opacity: 0.7';
        }
        const arrow = i < crew.length - 1 ? '<div class="pa-arrow">▼</div>' : '';
        return `
            <div class="pa-agent ${isActive ? 'active' : ''}" style="${bgStyle}; ${borderStyle}">
                <div class="pa-row">
                    <div class="pa-icon" style="background: ${a.color}15; border: 1px solid ${a.color}30">${a.icon}</div>
                    <span class="pa-role">${a.role}</span>
                    ${statusHtml}
                </div>
                <div class="pa-desc">${a.description}</div>
                <div class="pa-fw" style="color: ${a.color}">${a.framework}</div>
            </div>
            ${arrow}
        `;
    }).join('');
}

function renderPersonaBackend() {
    const container = document.getElementById('persona-backend');
    const cfg = personaConfig.config || {};
    const backends = cfg.backends || [];
    const readyBackends = backends.filter(b => b.status === 'ready');
    if (readyBackends.length === 0) {
        container.innerHTML = '<div class="fw-group"><label class="fw-label">Backend</label><div class="fw-pills"><span class="backend-pill">Demo mode</span></div></div>';
        return;
    }
    let html = '<div class="fw-group"><label class="fw-label">LLM Backend</label><div class="fw-pills">';
    const autoActive = !selectedBackend ? 'active' : '';
    html += `<button class="fw-pill ${autoActive}" onclick="selectPersonaBackend('')">Auto</button>`;
    for (const be of readyBackends) {
        const active = selectedBackend === be.id ? 'active' : '';
        const label = be.id === 'ollama' ? `Ollama (${be.model})` : `OpenAI (${be.model})`;
        html += `<button class="fw-pill ${active}" onclick="selectPersonaBackend('${be.id}')">${label}</button>`;
    }
    html += '</div></div>';
    container.innerHTML = html;
}

function selectPersonaBackend(be) {
    selectedBackend = be;
    localStorage.setItem('brain_backend', be);
    renderPersonaBackend();
}

function renderPersonaExamples() {
    const area = document.getElementById('persona-examples-area');
    const chips = document.getElementById('persona-example-chips');
    if (personaState !== 'idle' || personaTurns.length > 0) {
        area.classList.add('hidden');
        return;
    }
    area.classList.remove('hidden');
    chips.innerHTML = PERSONA_EXAMPLES.map(t => {
        const display = t.length > 60 ? t.slice(0, 60) + '…' : t;
        return `<button class="example-chip" onclick="setPersonaObjective('${t.replace(/'/g, "\\'")}')">${display}</button>`;
    }).join('');
}

function setPersonaObjective(text) {
    const textarea = document.getElementById('persona-objective');
    textarea.value = text;
    updatePersonaCharCount();
    updatePersonaButton();
}

function updatePersonaCharCount() {
    const textarea = document.getElementById('persona-objective');
    document.getElementById('persona-char-count').textContent = `${textarea.value.length}/2000 · Ctrl+Enter to run`;
}

function updatePersonaButton() {
    const textarea = document.getElementById('persona-objective');
    const btnRun = document.getElementById('persona-btn-run');
    const btnStop = document.getElementById('persona-btn-stop');
    const btnReset = document.getElementById('persona-btn-reset');

    btnRun.disabled = !textarea.value.trim() || personaState === 'running' || personaState === 'done';

    if (personaState === 'running') {
        btnRun.classList.add('hidden');
        btnStop.classList.remove('hidden');
        btnReset.classList.add('hidden');
    } else if (personaState === 'done' || personaState === 'error') {
        btnRun.classList.add('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.remove('hidden');
    } else {
        btnRun.classList.remove('hidden');
        btnStop.classList.add('hidden');
        btnReset.classList.add('hidden');
    }
    textarea.disabled = personaState === 'running';
}

async function runPersona() {
    const textarea = document.getElementById('persona-objective');
    const objective = textarea.value.trim();
    if (!objective || personaState === 'running') return;

    const scenario = document.getElementById('persona-scenario').value;
    const platform = document.getElementById('persona-platform').value;
    const region = document.getElementById('persona-region').value;
    const authorized = document.getElementById('persona-authorized').checked;
    const approverEl = document.getElementById('persona-approver');
    const authRefEl = document.getElementById('persona-auth-ref');
    const approver = approverEl ? approverEl.value.trim() : '';
    const authorizationRef = authRefEl ? authRefEl.value.trim() : '';

    personaState = 'running';
    personaTurns = [];
    personaActive = null;
    personaDone = new Set();
    personaRunId = null;
    personaPending = {};
    personaCompliance = null;
    updatePersonaButton();
    renderPersonaAgents();
    renderPersonaExamples();
    renderPersonaOutput();

    personaAbort = new AbortController();

    try {
        const reader = await API.runPersonaPlan({
            objective, scenario, platform, region, authorized,
            approver, authorizationRef,
            sessionId, backend: selectedBackend,
        }, personaAbort.signal);
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
                handlePersonaSSE(event);
            }
        }
        if (personaState === 'running') personaState = 'done';
    } catch (err) {
        if (err.name !== 'AbortError') {
            personaState = 'error';
            renderPersonaOutput(`Persona Orchestration interrupted: ${err.message}`);
        } else {
            personaState = 'idle';
        }
    }

    updatePersonaButton();
    renderPersonaAgents();
    refreshPersonaAuditStats();
}

function handlePersonaSSE(event) {
    switch (event.type) {
        case 'pipeline_start':
            personaRunId = event.run_id;
            break;

        case 'compliance':
            personaCompliance = event;
            renderPersonaOutput();
            break;

        case 'compliance_block':
            personaCompliance = Object.assign({}, personaCompliance, { blocked: true, message: event.message });
            personaState = 'error';
            renderPersonaOutput();
            break;

        case 'tool_call':
        case 'tool_result':
        case 'self_heal': {
            const w = event.worker || 'unknown';
            if (!personaPending[w]) personaPending[w] = [];
            personaPending[w].push(event);
            const existing = personaTurns.find(t => t.agentId === w);
            if (existing) {
                existing.toolActivity = personaPending[w];
                renderPersonaOutput();
            }
            break;
        }

        case 'agent_start': {
            personaActive = event.agent;
            personaTurns.push({
                agentId: event.agent,
                role: event.role,
                color: event.color,
                icon: event.icon || '🪪',
                content: '',
                done: false,
                toolActivity: personaPending[event.agent] || [],
            });
            renderPersonaAgents();
            renderPersonaOutput();
            break;
        }

        case 'token': {
            const turn = personaTurns.find(t => t.agentId === event.agent && !t.done);
            if (turn) {
                turn.content += event.content;
                const el = document.getElementById(`persona-content-${turn.agentId}`);
                if (el) {
                    el.innerHTML = escapeHtml(turn.content) + `<span class="am-cursor" style="background: ${turn.color}"></span>`;
                    scrollPersonaToBottom();
                }
            }
            break;
        }

        case 'agent_done': {
            const turn = personaTurns.find(t => t.agentId === event.agent);
            if (turn) turn.done = true;
            personaDone.add(event.agent);
            personaActive = null;
            renderPersonaAgents();
            renderPersonaOutput();
            break;
        }

        case 'done':
            personaState = event.blocked ? 'error' : 'done';
            updatePersonaButton();
            renderPersonaAgents();
            renderPersonaOutput();
            break;

        case 'error':
            personaState = 'error';
            updatePersonaButton();
            renderPersonaOutput(event.message);
            break;

        case 'cancelled':
            personaState = 'idle';
            updatePersonaButton();
            break;
    }
}

function stopPersona() {
    if (personaAbort) personaAbort.abort();
    personaState = 'idle';
    personaActive = null;
    updatePersonaButton();
    renderPersonaAgents();
}

function resetPersona() {
    personaTurns = [];
    personaActive = null;
    personaDone = new Set();
    personaRunId = null;
    personaState = 'idle';
    personaCompliance = null;
    updatePersonaButton();
    renderPersonaAgents();
    renderPersonaExamples();
    renderPersonaOutput();
}

function renderPersonaComplianceBanner() {
    if (!personaCompliance) return '';
    if (personaCompliance.blocked) {
        return `<div class="compliance-banner flagged">
            <strong>⛔ Flagged — access limited.</strong> ${escapeHtml(personaCompliance.message || '')}
            <div class="cb-audit">Audit ID: ${personaCompliance.audit_id}</div>
        </div>`;
    }
    if (personaCompliance.flagged) {
        return `<div class="compliance-banner flagged">
            <strong>⚠ Flagged for review.</strong> ${escapeHtml((personaCompliance.reasons || []).join('; '))}
            <div class="cb-audit">Audit ID: ${personaCompliance.audit_id}</div>
        </div>`;
    }
    return `<div class="compliance-banner ok">
        <strong>✓ Cleared &amp; logged.</strong> Recorded for legal review — audit ID ${personaCompliance.audit_id}.
    </div>`;
}

function renderPersonaOutput(errorMsg) {
    const area = document.getElementById('persona-output-area');
    const crew = personaConfig ? (personaConfig.agents || []) : [];
    const banner = renderPersonaComplianceBanner();

    if (personaTurns.length === 0 && !errorMsg && !banner) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🪪</div>
                <h3>Ready to plan an orchestration</h3>
                <p>Pick a scenario, sandbox platform and region, describe the authorized lab-only objective, and the Persona Crew produces a full, audit-logged synthetic-persona design &amp; detection plan.</p>
                <div class="agent-dots">
                    ${crew.map(a => `<span class="dot"><span class="dot-circle" style="background: ${a.color}"></span> ${a.role}</span>`).join('')}
                </div>
            </div>
        `;
        return;
    }

    let html = banner;
    if (errorMsg) {
        html += `<div class="error-banner">${errorMsg}</div>`;
    }

    html += '<div class="output-log" id="persona-output-log">';
    for (const turn of personaTurns) {
        const cursorHtml = !turn.done
            ? `<span class="am-cursor" style="background: ${turn.color}"></span>`
            : '';
        html += `
            <div class="agent-message" id="persona-msg-${turn.agentId}">
                <div class="am-header">
                    <div class="am-icon" style="background: ${turn.color}15; border: 1px solid ${turn.color}30">${turn.icon}</div>
                    <span class="am-role" style="color: ${turn.color}">${turn.role}</span>
                    ${!turn.done ? '<span class="spinner" style="width:10px;height:10px"></span>' : ''}
                    ${turn.done ? `<button class="am-copy" onclick="copyPersonaContent('${turn.agentId}')">📋</button>` : ''}
                </div>
                ${renderToolActivity(turn.toolActivity)}
                <div class="am-content" id="persona-content-${turn.agentId}" style="background: ${turn.color}06; border-color: ${turn.color}18">${escapeHtml(turn.content)}${cursorHtml}</div>
            </div>
        `;
    }
    if (personaState === 'done') {
        html += '<div class="pipeline-complete">Orchestration plan complete</div>';
    }
    html += '</div>';

    area.innerHTML = html;
    scrollPersonaToBottom();
}

function scrollPersonaToBottom() {
    const log = document.getElementById('persona-output-log');
    if (log) log.scrollTop = log.scrollHeight;
}

function copyPersonaContent(agentId) {
    const turn = personaTurns.find(t => t.agentId === agentId);
    if (turn) navigator.clipboard.writeText(turn.content);
}

async function refreshPersonaAuditStats() {
    try {
        const data = await API.getComplianceAudit(sessionId);
        const el = document.getElementById('persona-audit-stats');
        if (el && data.stats) {
            el.textContent = `${data.stats.total_events} events logged · ${data.stats.flagged_events} flagged`;
        }
    } catch (err) {
        console.error('Audit stats error:', err);
    }
}

async function loadPersonaAuditLog() {
    const container = document.getElementById('persona-audit-log');
    try {
        const data = await API.getComplianceAudit(sessionId);
        const events = data.events || [];
        if (events.length === 0) {
            container.innerHTML = '<div class="audit-empty">No recorded activity yet.</div>';
            return;
        }
        container.innerHTML = events.map(e => {
            const when = new Date(e.created_at * 1000).toLocaleTimeString();
            let cls = 'ok';
            if (e.sensitivity === 'red' || e.verdict === 'pre_cleared_legal_proxy') cls = 'sensitive';
            else if (e.verdict === 'flagged') cls = 'flagged';
            const reasons = e.reasons && e.reasons.length ? ` — ${escapeHtml(e.reasons.join('; '))}` : '';
            const approver = e.approver ? ` [approver: ${escapeHtml(e.approver)}]` : '';
            return `<div class="audit-row ${cls}">
                <span class="audit-when">${when}</span>
                <span class="audit-action">${escapeHtml(e.action)}</span>
                <span class="audit-verdict">${e.verdict}${approver}${reasons}</span>
            </div>`;
        }).join('');
    } catch (err) {
        container.innerHTML = `<div class="audit-empty">Failed to load audit log: ${err.message}</div>`;
    }
}

/* ── Init ───────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
