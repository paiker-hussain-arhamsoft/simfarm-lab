/* Lab view — data explorer, analysis tools, exercises */

let currentLevel = null;
let currentScenario = null;

// ── Tab switching ──────────────────────────────────────────────────

function switchTab(btn) {
    const tabBar = btn.closest('.tab-bar');
    tabBar.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const tabId = btn.dataset.tab;
    const parent = tabBar.parentElement;
    parent.querySelectorAll(':scope > .tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}

function switchSubTab(btn) {
    const tabBar = btn.closest('.tab-bar');
    tabBar.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const tabId = btn.dataset.tab;
    const container = tabBar.parentElement;
    container.querySelectorAll(':scope > .tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}

// ── Level loading ──────────────────────────────────────────────────

async function startLevel(level) {
    currentLevel = level;
    showLab();

    document.getElementById('lab-title').textContent = 'Loading scenario...';
    document.getElementById('lab-briefing').innerHTML = '<div class="loading"><div class="spinner"></div> Generating scenario data...</div>';

    // Show/hide phishing tab
    const phishBtn = document.getElementById('phishing-tab-btn');
    if (level === 'legendary') {
        phishBtn.classList.remove('hidden');
    } else {
        phishBtn.classList.add('hidden');
    }

    // Reset tabs to first
    document.querySelectorAll('#lab-tabs button').forEach(b => b.classList.remove('active'));
    document.querySelector('#lab-tabs button[data-tab="tab-data"]').classList.add('active');
    document.querySelectorAll('#view-lab > .tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById('tab-data').classList.add('active');

    try {
        const scenario = await API.generateScenario(level);
        currentScenario = scenario;

        document.getElementById('lab-title').textContent = scenario.name;
        document.getElementById('lab-briefing').innerHTML =
            `<strong>BRIEFING:</strong> ${scenario.briefing}`;

        document.getElementById('lab-stats').innerHTML = `
            <div class="stat-box">
                <div class="stat-value">${scenario.sim_count}</div>
                <div class="stat-label">SIM Cards</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${scenario.cdr_count}</div>
                <div class="stat-label">CDRs</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${scenario.cell_towers.length}</div>
                <div class="stat-label">Cell Towers</div>
            </div>
        `;

        // Load data tabs
        loadSims(level, 1);
        loadCDRs(level, 1);
        loadNetworkLogs(level, 1);
        loadAnalysisTools();
        loadExercises(level);

        if (level === 'legendary') {
            initPhishingGame();
        }
    } catch (err) {
        document.getElementById('lab-briefing').innerHTML =
            `<span class="text-red">Error: ${err.message}</span>`;
    }
}

// ── Data tables ────────────────────────────────────────────────────

function buildTable(headers, rows, container) {
    if (!rows.length) {
        container.innerHTML = '<p class="text-muted">No data available.</p>';
        return;
    }
    const ths = headers.map(h => `<th>${h}</th>`).join('');
    const trs = rows.map(row => {
        const tds = headers.map(h => {
            const key = h.toLowerCase().replace(/ /g, '_');
            let val = row[key] ?? '';
            if (typeof val === 'object') val = JSON.stringify(val);
            if (typeof val === 'string' && val.length > 40) val = val.slice(0, 37) + '...';
            return `<td>${val}</td>`;
        }).join('');
        return `<tr>${tds}</tr>`;
    }).join('');
    container.innerHTML = `
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead><tr>${ths}</tr></thead>
                <tbody>${trs}</tbody>
            </table>
        </div>`;
}

function buildPagination(container, currentPage, total, perPage, loadFn) {
    const totalPages = Math.ceil(total / perPage);
    const pag = document.createElement('div');
    pag.className = 'pagination';
    pag.innerHTML = `
        <button ${currentPage <= 1 ? 'disabled' : ''} onclick="${loadFn}(currentLevel, ${currentPage - 1})">&laquo; Prev</button>
        <span>Page ${currentPage} of ${totalPages} (${total} total)</span>
        <button ${currentPage >= totalPages ? 'disabled' : ''} onclick="${loadFn}(currentLevel, ${currentPage + 1})">Next &raquo;</button>
    `;
    container.appendChild(pag);
}

async function loadSims(level, page) {
    const container = document.getElementById('sims-table-container');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';
    try {
        const data = await API.getSims(level, page);
        const headers = ['ICCID', 'MSISDN', 'IMSI', 'IMEI', 'Activation_Date', 'Cell_Tower_ID', 'IP_Address', 'Device_Model'];
        buildTable(headers, data.sims, container);
        buildPagination(container, data.page, data.total, data.per_page, 'loadSims');
    } catch (err) {
        container.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

async function loadCDRs(level, page) {
    const container = document.getElementById('cdrs-table-container');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';
    try {
        const data = await API.getCDRs(level, page);
        const headers = ['Timestamp', 'Source_MSISDN', 'Destination_MSISDN', 'Traffic_Type', 'Duration_Seconds', 'Cell_Tower_ID', 'IMEI', 'IP_Address'];
        buildTable(headers, data.cdrs, container);
        buildPagination(container, data.page, data.total, data.per_page, 'loadCDRs');
    } catch (err) {
        container.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

async function loadNetworkLogs(level, page) {
    const container = document.getElementById('netlogs-table-container');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';
    try {
        const data = await API.getNetworkLogs(level, page);
        const headers = ['Timestamp', 'Source_IP', 'Dest_IP', 'Protocol', 'Port', 'Payload_Size', 'Flags'];
        buildTable(headers, data.logs, container);
        buildPagination(container, data.page, data.total, data.per_page, 'loadNetworkLogs');
    } catch (err) {
        container.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

// ── Analysis tools ─────────────────────────────────────────────────

async function loadAnalysisTools() {
    const grid = document.getElementById('analysis-grid');
    try {
        const data = await API.getAnalysisTools();
        grid.innerHTML = data.tools.map(t => `
            <div class="analysis-card" onclick="runAnalysis('${t.id}')">
                <h4>${t.name}</h4>
                <p>${t.description}</p>
            </div>
        `).join('');
    } catch (err) {
        grid.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

async function runAnalysis(toolId) {
    const container = document.getElementById('analysis-result-container');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Running analysis...</div>';
    try {
        const data = await API.runAnalysis(currentLevel, toolId);
        container.innerHTML = `
            <div class="analysis-result">
                <h4 class="text-cyan" style="color: var(--accent-cyan); margin-bottom: 12px;">
                    Analysis Result: ${data.tool}
                </h4>
                <pre>${JSON.stringify(data.result, null, 2)}</pre>
            </div>`;
    } catch (err) {
        container.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

// ── Exercises ──────────────────────────────────────────────────────

async function loadExercises(level) {
    const list = document.getElementById('exercise-list');
    try {
        const data = await API.getExercises(level);
        list.innerHTML = data.exercises.map(ex => `
            <div class="exercise-card" id="ex-${ex.exercise_id}">
                <h4>${ex.title}</h4>
                <p>${ex.description}</p>
                <div class="objective">Objective: ${ex.objective}</div>
                <details class="hints">
                    <summary>Show hints (${ex.hints.length})</summary>
                    <ul>${ex.hints.map(h => `<li>${h}</li>`).join('')}</ul>
                </details>
                <div class="flag-input">
                    <input type="text" id="flag-${ex.exercise_id}" placeholder="Enter your answer...">
                    <button onclick="submitFlag('${ex.exercise_id}')">Submit</button>
                </div>
                <div id="result-${ex.exercise_id}"></div>
                <div class="text-muted mt-1" style="font-size:0.8rem;">${ex.points} points</div>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

async function submitFlag(exerciseId) {
    const input = document.getElementById(`flag-${exerciseId}`);
    const resultDiv = document.getElementById(`result-${exerciseId}`);
    const flag = input.value.trim();
    if (!flag) return;

    try {
        const data = await API.submitFlag(exerciseId, flag);
        resultDiv.innerHTML = `
            <div class="flag-result ${data.valid ? 'success' : 'failure'}">
                ${data.message}${data.points ? ` (+${data.points} pts)` : ''}
            </div>`;
    } catch (err) {
        resultDiv.innerHTML = `<div class="flag-result failure">${err.message}</div>`;
    }
}
