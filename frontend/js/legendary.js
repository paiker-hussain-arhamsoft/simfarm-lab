/* Legendary Detection Module — Frontend */

let legendaryTTPs = [];
let legendaryScenarios = [];
let activeScenario = null;
let scenarioAnswers = {};

// ── Navigation ─────────────────────────────────────────────────────

function showLegendary() {
    document.querySelectorAll('main > section').forEach(s => s.classList.add('hidden'));
    document.getElementById('view-legendary').classList.remove('hidden');
    document.querySelectorAll('.header-nav button').forEach(b => b.classList.remove('active'));
    document.getElementById('nav-legendary').classList.add('active');
    loadLegendaryTTPs();
    loadLegendaryScenarios();
}

function switchLegendaryTab(btn) {
    const tabId = btn.dataset.tab;
    document.querySelectorAll('#legendary-tabs button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.leg-tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    if (tabId === 'leg-tab-killchain') renderKillChain();
}

// ── TTP Library ────────────────────────────────────────────────────

async function loadLegendaryTTPs() {
    if (legendaryTTPs.length > 0) return;
    try {
        const resp = await fetch('/api/legendary/ttps');
        const data = await resp.json();
        legendaryTTPs = data.ttps;
        renderTTPFilterBar();
        renderTTPList(legendaryTTPs);
    } catch (e) {
        console.error('Failed to load TTPs:', e);
    }
}

function renderTTPFilterBar() {
    const categories = [...new Set(legendaryTTPs.map(t => t.category))];
    const catLabels = {
        infrastructure: 'Infrastructure',
        acquisition: 'SIM Acquisition',
        identity: 'Identity & Personas',
        evasion: 'Detection Evasion',
        automation: 'Automation & C2',
        amplification: 'Amplification',
        persistence: 'Persistence',
        exfiltration: 'Exfiltration',
    };
    const bar = document.getElementById('ttp-filter-bar');
    bar.innerHTML = `
        <button class="ttp-filter-btn active" onclick="filterTTPs('all')">All (${legendaryTTPs.length})</button>
        ${categories.map(c => `
            <button class="ttp-filter-btn" onclick="filterTTPs('${c}')">${catLabels[c] || c} (${legendaryTTPs.filter(t => t.category === c).length})</button>
        `).join('')}
    `;
}

function filterTTPs(category) {
    document.querySelectorAll('.ttp-filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    if (category === 'all') {
        renderTTPList(legendaryTTPs);
    } else {
        renderTTPList(legendaryTTPs.filter(t => t.category === category));
    }
    // Hide detail view
    document.getElementById('ttp-detail-container').classList.add('hidden');
    document.getElementById('ttp-list').classList.remove('hidden');
}

function renderTTPList(ttps) {
    const container = document.getElementById('ttp-list');
    const threatColors = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444', critical: '#dc2626' };
    const difficultyColors = {
        trivial: '#22c55e', easy: '#86efac', moderate: '#f59e0b',
        hard: '#f97316', very_hard: '#ef4444', near_impossible: '#dc2626'
    };

    container.innerHTML = ttps.map(ttp => `
        <div class="ttp-card" onclick="showTTPDetail('${ttp.id}')">
            <div class="ttp-card-header">
                <span class="ttp-id">${ttp.id}</span>
                <span class="ttp-threat" style="color: ${threatColors[ttp.threat_level]}">${ttp.threat_level.toUpperCase()}</span>
            </div>
            <h4 class="ttp-card-title">${ttp.name}</h4>
            <p class="ttp-card-summary">${ttp.summary}</p>
            <div class="ttp-card-footer">
                <span class="ttp-category-badge">${ttp.category}</span>
                <span class="ttp-difficulty" style="color: ${difficultyColors[ttp.detection_difficulty]}">Detection: ${ttp.detection_difficulty.replace('_', ' ')}</span>
            </div>
        </div>
    `).join('');
}

async function showTTPDetail(ttpId) {
    const ttp = legendaryTTPs.find(t => t.id === ttpId);
    if (!ttp) return;

    document.getElementById('ttp-list').classList.add('hidden');
    const container = document.getElementById('ttp-detail-container');
    container.classList.remove('hidden');

    const threatColors = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444', critical: '#dc2626' };

    container.innerHTML = `
        <button class="back-btn" onclick="closeTTPDetail()" style="margin-bottom: 1rem">&larr; Back to TTP List</button>

        <div class="ttp-detail">
            <div class="ttp-detail-header">
                <div>
                    <span class="ttp-id-large">${ttp.id}</span>
                    <h2>${ttp.name}</h2>
                    <div class="ttp-meta-row">
                        <span class="ttp-threat-badge" style="background: ${threatColors[ttp.threat_level]}20; color: ${threatColors[ttp.threat_level]}">Threat: ${ttp.threat_level.toUpperCase()}</span>
                        <span class="ttp-meta-item">Kill Chain: ${ttp.kill_chain_phase}</span>
                        <span class="ttp-meta-item">Category: ${ttp.category}</span>
                    </div>
                </div>
            </div>

            <div class="ttp-section">
                <h3>Technical Definition</h3>
                <p>${ttp.technical_definition}</p>
            </div>

            <div class="ttp-section">
                <h3>How It Works</h3>
                <p>${ttp.how_it_works}</p>
            </div>

            <div class="ttp-section">
                <h3>Threat Description</h3>
                <p>${ttp.threat_description}</p>
            </div>

            <div class="ttp-section">
                <h3>Indicators of Compromise (${ttp.indicators.length})</h3>
                <div class="ioc-grid">
                    ${ttp.indicators.map(ioc => `
                        <div class="ioc-card">
                            <div class="ioc-header">
                                <span class="ioc-type">${ioc.type}</span>
                                <span class="ioc-confidence ${ioc.confidence}">Confidence: ${ioc.confidence}</span>
                            </div>
                            <p class="ioc-desc">${ioc.description}</p>
                            <span class="ioc-source">Data Source: ${ioc.data_source}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="ttp-section">
                <h3>Detection Methods (${ttp.detection_methods.length})</h3>
                ${ttp.detection_methods.map(dm => `
                    <div class="detection-method-card">
                        <h4>${dm.name}</h4>
                        <p>${dm.description}</p>
                        <div class="dm-meta">
                            <span>Effectiveness: <strong>${dm.effectiveness}</strong></span>
                            <span>False Positive Rate: <strong>${dm.false_positive_rate}</strong></span>
                            <span>Skill Required: <strong>${dm.skill_level}</strong></span>
                        </div>
                        <div class="dm-tools">Tools: ${dm.tools.join(', ')}</div>
                    </div>
                `).join('')}
            </div>

            <div class="ttp-section">
                <h3>Countermeasures (${ttp.countermeasures.length})</h3>
                <div class="countermeasure-grid">
                    ${ttp.countermeasures.map(cm => `
                        <div class="cm-card">
                            <h4>${cm.name}</h4>
                            <p>${cm.description}</p>
                            <div class="cm-meta">
                                <span>Level: ${cm.level}</span>
                                <span>Effectiveness: ${cm.effectiveness}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            ${ttp.ethical_cover ? `
            <div class="ttp-section ethical-cover-section">
                <h3>Ethical Cover Analysis</h3>
                <div class="ethical-cover">
                    <div class="ec-block">
                        <h4>Claimed Purpose</h4>
                        <p class="ec-claimed">"${ttp.ethical_cover.claimed_purpose}"</p>
                    </div>
                    <div class="ec-block">
                        <h4>Legitimate Equivalent</h4>
                        <p>${ttp.ethical_cover.legitimate_equivalent}</p>
                    </div>
                    <div class="ec-block">
                        <h4>Red Flags That Expose the Cover</h4>
                        <ul class="ec-red-flags">
                            ${ttp.ethical_cover.red_flags.map(rf => `<li>${rf}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="ec-block">
                        <h4>Investigative Questions</h4>
                        <ol class="ec-questions">
                            ${ttp.ethical_cover.investigative_questions.map(q => `<li>${q}</li>`).join('')}
                        </ol>
                    </div>
                </div>
            </div>
            ` : ''}

            ${ttp.related_ttps.length > 0 ? `
            <div class="ttp-section">
                <h3>Related TTPs</h3>
                <div class="related-ttps">
                    ${ttp.related_ttps.map(id => {
                        const related = legendaryTTPs.find(t => t.id === id);
                        return related ? `<button class="related-ttp-btn" onclick="showTTPDetail('${id}')">${id}: ${related.name}</button>` : `<span class="ttp-id">${id}</span>`;
                    }).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

function closeTTPDetail() {
    document.getElementById('ttp-detail-container').classList.add('hidden');
    document.getElementById('ttp-list').classList.remove('hidden');
}

// ── Investigation Scenarios ────────────────────────────────────────

async function loadLegendaryScenarios() {
    if (legendaryScenarios.length > 0) return;
    try {
        const resp = await fetch('/api/legendary/scenarios');
        const data = await resp.json();
        legendaryScenarios = data.scenarios;
        renderScenarioGrid();
    } catch (e) {
        console.error('Failed to load scenarios:', e);
    }
}

function renderScenarioGrid() {
    const container = document.getElementById('scenario-grid');
    const diffColors = { intermediate: '#f59e0b', advanced: '#ef4444', expert: '#dc2626' };

    container.innerHTML = legendaryScenarios.map(s => `
        <div class="scenario-card" onclick="openScenario('${s.id}')">
            <div class="scenario-card-header">
                <span class="scenario-difficulty" style="color: ${diffColors[s.difficulty]}">${s.difficulty.toUpperCase()}</span>
                <span class="scenario-points">${s.total_points} pts</span>
            </div>
            <h3>${s.title}</h3>
            <p class="scenario-briefing-preview">${s.briefing.substring(0, 150)}...</p>
            <div class="scenario-card-footer">
                <span>${s.question_count} questions</span>
                <span>${s.time_estimate_minutes} min</span>
                <span>${s.evidence_count} evidence items</span>
            </div>
            <div class="scenario-skills">
                ${s.skills_tested.map(sk => `<span class="skill-tag">${sk}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

async function openScenario(scenarioId) {
    try {
        const resp = await fetch(`/api/legendary/scenarios/${scenarioId}`);
        activeScenario = await resp.json();
        scenarioAnswers = {};
        renderActiveScenario();
    } catch (e) {
        console.error('Failed to load scenario:', e);
    }
}

function renderActiveScenario() {
    const s = activeScenario;
    document.getElementById('scenario-grid').classList.add('hidden');
    const container = document.getElementById('scenario-active');
    container.classList.remove('hidden');

    container.innerHTML = `
        <button class="back-btn" onclick="closeScenario()" style="margin-bottom: 1rem">&larr; Back to Scenarios</button>

        <div class="scenario-header">
            <h2>${s.title}</h2>
            <div class="scenario-meta">
                <span class="scenario-difficulty-badge">${s.difficulty}</span>
                <span>${s.total_points} total points</span>
                <span>${s.time_estimate_minutes} min estimated</span>
            </div>
        </div>

        <div class="scenario-briefing-full">
            <h3>Briefing</h3>
            <p>${s.briefing}</p>
        </div>

        <div class="scenario-context">
            <h3>Your Role</h3>
            <p>${s.context}</p>
        </div>

        <div class="scenario-evidence-section">
            <h3>Evidence (${s.evidence.length} items)</h3>
            ${s.evidence.map((ev, idx) => `
                <div class="evidence-card">
                    <div class="evidence-header" onclick="toggleEvidence(${idx})">
                        <span class="evidence-type-badge">${ev.type}</span>
                        <h4>${ev.title}</h4>
                        <span class="evidence-toggle">+</span>
                    </div>
                    <div class="evidence-body hidden" id="evidence-body-${idx}">
                        <p class="evidence-desc">${ev.description}</p>
                        <pre class="evidence-data">${JSON.stringify(ev.data, null, 2)}</pre>
                    </div>
                </div>
            `).join('')}
        </div>

        <div class="scenario-questions-section">
            <h3>Questions</h3>
            ${s.questions.map((q, idx) => `
                <div class="question-card" id="question-${q.id}">
                    <div class="question-header">
                        <span class="question-number">Q${idx + 1}</span>
                        <span class="question-points">${q.points} pts</span>
                    </div>
                    <p class="question-text">${q.question}</p>
                    ${q.hint ? `<p class="question-hint">Hint: ${q.hint}</p>` : ''}
                    <div class="question-input">
                        ${q.type === 'multiple_choice' ? `
                            <div class="mc-options">
                                ${q.options.map((opt, oi) => `
                                    <label class="mc-option">
                                        <input type="radio" name="q-${q.id}" value="${opt}" onchange="setAnswer('${q.id}', this.value)">
                                        <span>${opt}</span>
                                    </label>
                                `).join('')}
                            </div>
                        ` : `
                            <textarea class="ft-answer" placeholder="Type your answer..." onchange="setAnswer('${q.id}', this.value)" rows="4"></textarea>
                        `}
                    </div>
                    <button class="submit-answer-btn" onclick="submitAnswer('${s.id}', '${q.id}')">Check Answer</button>
                    <div class="answer-result hidden" id="result-${q.id}"></div>
                </div>
            `).join('')}
        </div>
    `;
}

function toggleEvidence(idx) {
    const body = document.getElementById(`evidence-body-${idx}`);
    body.classList.toggle('hidden');
    const toggle = body.previousElementSibling.querySelector('.evidence-toggle');
    toggle.textContent = body.classList.contains('hidden') ? '+' : '-';
}

function setAnswer(questionId, value) {
    scenarioAnswers[questionId] = value;
}

async function submitAnswer(scenarioId, questionId) {
    const answer = scenarioAnswers[questionId];
    if (!answer) {
        alert('Please provide an answer first.');
        return;
    }

    try {
        const resp = await fetch('/api/legendary/scenarios/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: scenarioId, question_id: questionId, answer }),
        });
        const result = await resp.json();
        const resultDiv = document.getElementById(`result-${questionId}`);
        resultDiv.classList.remove('hidden');

        if (result.correct) {
            resultDiv.innerHTML = `
                <div class="answer-correct">
                    <strong>Correct! +${result.points_earned} points</strong>
                    <p>${result.explanation}</p>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="answer-incorrect">
                    <strong>Incorrect (0/${result.max_points} points)</strong>
                    <p><strong>Correct answer:</strong> ${result.correct_answer}</p>
                    <p>${result.explanation}</p>
                </div>
            `;
        }
    } catch (e) {
        console.error('Failed to check answer:', e);
    }
}

function closeScenario() {
    document.getElementById('scenario-active').classList.add('hidden');
    document.getElementById('scenario-grid').classList.remove('hidden');
    activeScenario = null;
}

// ── Kill Chain Map ─────────────────────────────────────────────────

function renderKillChain() {
    const container = document.getElementById('killchain-container');
    const phases = [
        { name: 'Resource Development', ttps: legendaryTTPs.filter(t => t.kill_chain_phase === 'Resource Development') },
        { name: 'Defense Evasion', ttps: legendaryTTPs.filter(t => t.kill_chain_phase === 'Defense Evasion') },
        { name: 'Command and Control', ttps: legendaryTTPs.filter(t => t.kill_chain_phase === 'Command and Control') },
        { name: 'Collection', ttps: legendaryTTPs.filter(t => t.kill_chain_phase === 'Collection') },
        { name: 'Impact', ttps: legendaryTTPs.filter(t => t.kill_chain_phase === 'Impact') },
        { name: 'Persistence', ttps: legendaryTTPs.filter(t => t.kill_chain_phase === 'Persistence') },
    ];

    const threatColors = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444', critical: '#dc2626' };

    container.innerHTML = `
        <div class="killchain-header">
            <h3>SIM Farm Kill Chain — MITRE ATT&CK Mapping</h3>
            <p class="text-muted">Each phase maps techniques to the adversary's operational lifecycle. Click a technique to view its full TTP entry.</p>
        </div>
        <div class="killchain-grid">
            ${phases.filter(p => p.ttps.length > 0).map(phase => `
                <div class="killchain-phase">
                    <div class="kc-phase-header">${phase.name}</div>
                    <div class="kc-phase-ttps">
                        ${phase.ttps.map(ttp => `
                            <div class="kc-ttp-item" onclick="switchLegendaryTab(document.querySelector('[data-tab=leg-tab-ttps]')); showTTPDetail('${ttp.id}')">
                                <span class="kc-ttp-id">${ttp.id}</span>
                                <span class="kc-ttp-name">${ttp.name}</span>
                                <span class="kc-ttp-threat" style="color: ${threatColors[ttp.threat_level]}">&#9679;</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}
