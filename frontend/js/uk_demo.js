/* UK Demo — Political Campaign SIM Farm Scenarios + Live Simulation */

let ukDemoData = null;
let ukSimRunning = false;
let ukSimTimer = null;
let ukSimSpeed = 1;

async function showUkDemo() {
    document.querySelectorAll('main > section').forEach(s => s.classList.add('hidden'));
    document.getElementById('view-uk-demo').classList.remove('hidden');
    document.querySelectorAll('.header-nav button').forEach(b => b.classList.remove('active'));
    document.getElementById('nav-uk-demo').classList.add('active');

    if (!ukDemoData) await loadUkDemoData();
}

async function loadUkDemoData() {
    const container = document.getElementById('uk-scenarios');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading UK scenarios...</div>';
    try {
        ukDemoData = await API.getUkDemoScenarios();
        renderUkScenarioCards(ukDemoData);
    } catch (err) {
        container.innerHTML = `<p class="text-red">Failed to load UK demo: ${err.message}</p>`;
    }
}

function renderUkScenarioCards(data) {
    const container = document.getElementById('uk-scenarios');
    container.innerHTML = data.scenarios.map(s => `
        <div class="uk-scenario-card" style="border-left: 4px solid ${s.party_color};" onclick="runUkScenario('${s.id}')">
            <div class="uk-scenario-header">
                <div class="uk-party-badge" style="background:${s.party_color};">${s.party}</div>
                <span class="uk-election-type">${s.election_type}</span>
            </div>
            <h3>${s.title}</h3>
            <p class="uk-subtitle">${s.subtitle}</p>
            <p class="uk-objective">${s.objective}</p>
            <div class="uk-card-footer">
                <span>Click to analyze &amp; simulate</span>
                <span>&rarr;</span>
            </div>
        </div>
    `).join('');

    const ctx = data.regulatory_context;
    document.getElementById('uk-reg-context').innerHTML = `
        <div class="uk-reg-box">
            <h4>UK Regulatory Context</h4>
            <p class="uk-reg-highlight">${ctx.sim_registration}</p>
            <p><strong>Regulator:</strong> ${ctx.regulator}</p>
            <div class="uk-laws">
                <strong>Key Laws:</strong>
                ${ctx.key_laws.map(l => `<span class="uk-law-badge">${l}</span>`).join('')}
            </div>
        </div>
    `;
}

function fmtNum(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (n >= 1_000) return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + 'K';
    return n.toLocaleString();
}

// ── Scenario Analysis + Simulation Launch ──────────────────────────

async function runUkScenario(scenarioId) {
    const resultDiv = document.getElementById('uk-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Running scenario analysis...</div>';
    resultDiv.scrollIntoView({ behavior: 'smooth' });

    try {
        const [analysis, simData] = await Promise.all([
            API.runUkDemo(scenarioId),
            API.simulateUkDemo(scenarioId),
        ]);
        renderUkAnalysisAndSim(analysis, simData.events);
    } catch (err) {
        resultDiv.innerHTML = `<p class="text-red">Error: ${err.message}</p>`;
    }
}

function renderUkAnalysisAndSim(r, events) {
    const gradeColors = { S: '#a855f7', A: '#22c55e', B: '#f59e0b', C: '#f97316', F: '#ef4444' };
    const gradeColor = gradeColors[r.stealth_grade] || '#6b7280';

    document.getElementById('uk-result').innerHTML = `
        <!-- Analysis Card -->
        <div class="pg-result-card" style="border-top: 3px solid ${r.party_color};">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
                <div>
                    <h3 style="margin:0;">${r.title}</h3>
                    <p class="text-muted" style="margin:4px 0 0;">${r.subtitle}</p>
                    <div style="margin-top:8px;">
                        <span class="uk-party-badge" style="background:${r.party_color};">${r.party}</span>
                        <span class="uk-election-type" style="margin-left:8px;">${r.election_date}</span>
                    </div>
                </div>
                <div class="pg-grade" style="background:${gradeColor};">
                    <span style="font-size:2.5rem;font-weight:800;">${r.stealth_grade}</span>
                    <span style="font-size:.7rem;">${r.stealth_label}</span>
                </div>
            </div>
            <div class="uk-objective-box"><strong>OBJECTIVE:</strong> ${r.objective}</div>

            <!-- Key Metrics -->
            <div class="pg-metrics-grid">
                <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.total_sims)}</span><span class="pg-metric-label">Active SIMs</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.total_accounts)}</span><span class="pg-metric-label">Fake Accounts</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.network_detection_percent}</span><span class="pg-metric-label">Network Detection</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.platform_detection_percent}</span><span class="pg-metric-label">Platform Detection</span></div>
                <div class="pg-metric"><span class="pg-metric-value">GBP ${fmtNum(r.total_campaign_cost_gbp)}</span><span class="pg-metric-label">Total Cost</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.estimated_detection_timeline}</span><span class="pg-metric-label">Detection Timeline</span></div>
            </div>

            <!-- Infrastructure -->
            <div class="uk-section">
                <h4 class="uk-section-title">Infrastructure Selected</h4>
                <div class="uk-info-grid">
                    <div class="uk-info-item"><strong>Platforms:</strong> ${r.platforms.join(', ')}</div>
                    <div class="uk-info-item"><strong>Carriers:</strong> ${r.carriers.join(', ')}</div>
                    <div class="uk-info-item"><strong>Cities:</strong> ${r.cities.join(', ')}</div>
                    <div class="uk-info-item"><strong>Duration:</strong> ${r.campaign_duration_weeks} weeks</div>
                </div>
            </div>

            <!-- Cost Breakdown -->
            <div class="uk-section">
                <h4 class="pg-cost-title">Cost Breakdown (GBP)</h4>
                <div class="pg-cost-breakdown">
                    <div class="pg-cost-row"><span>Hardware</span><span>${r.hardware_cost_gbp.toLocaleString()}</span></div>
                    <div class="pg-cost-row"><span>SIM Cards</span><span>${r.sim_cost_gbp.toLocaleString()}</span></div>
                    <div class="pg-cost-row"><span>OPSEC Tools</span><span>${r.opsec_cost_gbp.toLocaleString()}</span></div>
                    <div class="pg-cost-row"><span>Monthly Ops (x${Math.round(r.campaign_duration_weeks / 4)})</span><span>${(r.monthly_operating_cost_gbp * Math.round(r.campaign_duration_weeks / 4)).toLocaleString()}</span></div>
                    <div class="pg-cost-total"><span>Total Campaign</span><span>GBP ${r.total_campaign_cost_gbp.toLocaleString()}</span></div>
                </div>
            </div>

            ${r.warnings.length ? `<div class="pg-warnings">${r.warnings.map(w => `<div class="pg-warning">${w}</div>`).join('')}</div>` : ''}
        </div>

        <!-- SIMULATION DASHBOARD -->
        <div class="sim-dashboard" id="sim-dashboard">
            <div class="sim-header">
                <h3>Live Simulation: Farm in Operation</h3>
                <p class="text-muted">Watch the SIM farm go from manual setup to full automation</p>
            </div>

            <!-- Controls -->
            <div class="sim-controls">
                <button class="sim-btn sim-btn-start" id="sim-start-btn" onclick="startSimulation()">
                    Start Simulation
                </button>
                <button class="sim-btn sim-btn-pause hidden" id="sim-pause-btn" onclick="pauseSimulation()">
                    Pause
                </button>
                <div class="sim-speed-controls">
                    <span>Speed:</span>
                    <button class="sim-speed-btn ${ukSimSpeed===1?'active':''}" onclick="setSimSpeed(1)">1x</button>
                    <button class="sim-speed-btn ${ukSimSpeed===3?'active':''}" onclick="setSimSpeed(3)">3x</button>
                    <button class="sim-speed-btn ${ukSimSpeed===10?'active':''}" onclick="setSimSpeed(10)">10x</button>
                    <button class="sim-speed-btn" onclick="setSimSpeed(50)">50x</button>
                </div>
            </div>

            <!-- Phase indicator -->
            <div class="sim-phase-bar">
                <div class="sim-phase-item" id="sim-phase-manual">
                    <div class="sim-phase-dot"></div>
                    <span>Manual Setup</span>
                </div>
                <div class="sim-phase-arrow">&rarr;</div>
                <div class="sim-phase-item" id="sim-phase-initial">
                    <div class="sim-phase-dot"></div>
                    <span>Automation Starting</span>
                </div>
                <div class="sim-phase-arrow">&rarr;</div>
                <div class="sim-phase-item" id="sim-phase-full">
                    <div class="sim-phase-dot"></div>
                    <span>Full Automation</span>
                </div>
            </div>

            <!-- Live counters -->
            <div class="sim-counters" id="sim-counters">
                <div class="sim-counter">
                    <div class="sim-counter-icon">&#128241;</div>
                    <div class="sim-counter-value" id="sim-cnt-sims">0</div>
                    <div class="sim-counter-label">SIMs Active</div>
                </div>
                <div class="sim-counter">
                    <div class="sim-counter-icon">&#128100;</div>
                    <div class="sim-counter-value" id="sim-cnt-accounts">0</div>
                    <div class="sim-counter-label">Accounts Created</div>
                </div>
                <div class="sim-counter">
                    <div class="sim-counter-icon">&#128172;</div>
                    <div class="sim-counter-value" id="sim-cnt-posts">0</div>
                    <div class="sim-counter-label">Posts Made</div>
                </div>
                <div class="sim-counter">
                    <div class="sim-counter-icon">&#10084;</div>
                    <div class="sim-counter-value" id="sim-cnt-engagements">0</div>
                    <div class="sim-counter-label">Engagements</div>
                </div>
                <div class="sim-counter">
                    <div class="sim-counter-icon">&#128065;</div>
                    <div class="sim-counter-value" id="sim-cnt-impressions">0</div>
                    <div class="sim-counter-label">Impressions</div>
                </div>
                <div class="sim-counter">
                    <div class="sim-counter-icon">&#128101;</div>
                    <div class="sim-counter-value" id="sim-cnt-groups">0</div>
                    <div class="sim-counter-label">Groups Joined</div>
                </div>
            </div>

            <!-- Detection gauge -->
            <div class="sim-detection-gauge">
                <div class="sim-gauge-label">Detection Risk</div>
                <div class="sim-gauge-bar">
                    <div class="sim-gauge-fill" id="sim-gauge-fill" style="width:0%;"></div>
                </div>
                <div class="sim-gauge-status" id="sim-gauge-status">UNDETECTED</div>
            </div>

            <!-- Progress bar -->
            <div class="sim-progress">
                <div class="sim-progress-label">
                    <span>Progress</span>
                    <span id="sim-progress-text">0 / 200 events</span>
                </div>
                <div class="sim-progress-bar">
                    <div class="sim-progress-fill" id="sim-progress-fill" style="width:0%;"></div>
                </div>
            </div>

            <!-- Live event feed -->
            <div class="sim-feed-container">
                <h4>Live Activity Feed</h4>
                <div class="sim-feed" id="sim-feed"></div>
            </div>

            <!-- Key Campaign Messages -->
            <div class="uk-section">
                <h4 class="uk-section-title">Key Campaign Messages</h4>
                <div class="uk-messages-grid">
                    ${r.key_messages.map(m => `<div class="uk-message-card" style="border-left:3px solid ${r.party_color};">${m}</div>`).join('')}
                </div>
            </div>

            <!-- Target Constituencies -->
            <div class="uk-section">
                <h4 class="uk-section-title">Target Constituencies (${r.target_constituencies.length})</h4>
                <div class="uk-constituency-grid">
                    ${r.target_constituencies.map(c => `<span class="uk-constituency-badge">${c}</span>`).join('')}
                </div>
            </div>

            <!-- Campaign Timeline -->
            <div class="uk-section">
                <h4 class="uk-section-title">Operation Timeline</h4>
                <div class="uk-timeline">
                    ${r.timeline.map(t => `
                        <div class="uk-timeline-item">
                            <div class="uk-timeline-week">${t.week}</div>
                            <div class="uk-timeline-body">
                                <strong>${t.phase}</strong>
                                <p>${t.details}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Legal Notes -->
            <div class="uk-section">
                <h4 class="pg-notes-title">Legal &amp; Educational Notes</h4>
                <div class="pg-notes">
                    ${r.legal_notes.map(n => `<div class="pg-note">${n}</div>`).join('')}
                </div>
            </div>
        </div>
    `;

    // Store events for simulation
    window._ukSimEvents = events;
    window._ukSimIndex = 0;
    window._ukSimMetrics = { sims: 0, accounts: 0, posts: 0, engagements: 0, impressions: 0, groups_joined: 0 };
}

// ── Simulation Engine ──────────────────────────────────────────────

const SIM_ICONS = {
    sim: '&#128241;', account: '&#128100;', shield: '&#128737;', group: '&#128101;',
    post: '&#128172;', megaphone: '&#128227;', heart: '&#10084;', reply: '&#128488;',
    radar: '&#128225;',
};

function startSimulation() {
    if (ukSimRunning) return;
    ukSimRunning = true;
    document.getElementById('sim-start-btn').classList.add('hidden');
    document.getElementById('sim-pause-btn').classList.remove('hidden');
    runNextEvent();
}

function pauseSimulation() {
    ukSimRunning = false;
    clearTimeout(ukSimTimer);
    document.getElementById('sim-start-btn').classList.remove('hidden');
    document.getElementById('sim-start-btn').textContent = 'Resume';
    document.getElementById('sim-pause-btn').classList.add('hidden');
}

function setSimSpeed(s) {
    ukSimSpeed = s;
    document.querySelectorAll('.sim-speed-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

function runNextEvent() {
    if (!ukSimRunning) return;
    const events = window._ukSimEvents;
    const idx = window._ukSimIndex;
    if (idx >= events.length) {
        finishSimulation();
        return;
    }

    const ev = events[idx];
    window._ukSimIndex++;

    // Update metrics
    const m = window._ukSimMetrics;
    const d = ev.metric_deltas || {};
    if (d.sims) m.sims += d.sims;
    if (d.accounts) m.accounts += d.accounts;
    if (d.posts) m.posts += d.posts;
    if (d.engagements) m.engagements += d.engagements;
    if (d.impressions) m.impressions += d.impressions;
    if (d.groups_joined) m.groups_joined += d.groups_joined;

    // Update counter displays
    document.getElementById('sim-cnt-sims').textContent = m.sims.toLocaleString();
    document.getElementById('sim-cnt-accounts').textContent = m.accounts.toLocaleString();
    document.getElementById('sim-cnt-posts').textContent = m.posts.toLocaleString();
    document.getElementById('sim-cnt-engagements').textContent = m.engagements.toLocaleString();
    document.getElementById('sim-cnt-impressions').textContent = fmtNum(m.impressions);
    document.getElementById('sim-cnt-groups').textContent = m.groups_joined.toLocaleString();

    // Update phase indicator
    updatePhaseIndicator(ev.phase);

    // Update detection gauge
    updateDetectionGauge(idx, events.length, ev);

    // Update progress
    const pct = ((idx + 1) / events.length * 100).toFixed(0);
    document.getElementById('sim-progress-fill').style.width = pct + '%';
    document.getElementById('sim-progress-text').textContent = `${idx + 1} / ${events.length} events`;

    // Add to feed
    addFeedEvent(ev);

    // Schedule next event
    const baseDelay = ev.phase === 'manual_setup' ? 800 : (ev.phase === 'initial_automation' ? 500 : 300);
    const delay = Math.max(30, baseDelay / ukSimSpeed);
    ukSimTimer = setTimeout(runNextEvent, delay);
}

function updatePhaseIndicator(phase) {
    const phases = ['manual_setup', 'initial_automation', 'full_automation'];
    const ids = ['sim-phase-manual', 'sim-phase-initial', 'sim-phase-full'];
    const current = phases.indexOf(phase);

    ids.forEach((id, i) => {
        const el = document.getElementById(id);
        if (i < current) {
            el.className = 'sim-phase-item completed';
        } else if (i === current) {
            el.className = 'sim-phase-item active';
        } else {
            el.className = 'sim-phase-item';
        }
    });
}

function updateDetectionGauge(idx, total, ev) {
    let riskPct;
    if (idx < 30) riskPct = Math.min(5, idx * 0.15);
    else if (idx < 60) riskPct = 5 + (idx - 30) * 0.1;
    else riskPct = 8 + (idx - 60) * 0.05;

    if (ev.type === 'detection_check' && ev.detail.includes('LOW_ALERT')) {
        riskPct += 3;
    }
    riskPct = Math.min(riskPct, 15);

    const fill = document.getElementById('sim-gauge-fill');
    const status = document.getElementById('sim-gauge-status');
    fill.style.width = riskPct + '%';

    if (riskPct < 5) {
        fill.style.background = '#22c55e';
        status.textContent = 'UNDETECTED';
        status.style.color = '#22c55e';
    } else if (riskPct < 10) {
        fill.style.background = '#f59e0b';
        status.textContent = 'LOW RISK';
        status.style.color = '#f59e0b';
    } else {
        fill.style.background = '#f97316';
        status.textContent = 'MODERATE — STILL UNDETECTED';
        status.style.color = '#f97316';
    }
}

function addFeedEvent(ev) {
    const feed = document.getElementById('sim-feed');
    const icon = SIM_ICONS[ev.icon] || '&#9679;';
    const phaseClass = ev.phase.replace('_', '-');

    const div = document.createElement('div');
    div.className = `sim-feed-item sim-feed-${phaseClass}`;
    div.innerHTML = `
        <span class="sim-feed-icon">${icon}</span>
        <div class="sim-feed-body">
            <div class="sim-feed-title">${ev.title}</div>
            <div class="sim-feed-detail">${ev.detail}</div>
        </div>
        <span class="sim-feed-phase">${ev.phase_label}</span>
    `;

    feed.insertBefore(div, feed.firstChild);
    // Keep feed to 50 items max
    while (feed.children.length > 50) feed.removeChild(feed.lastChild);
}

function finishSimulation() {
    ukSimRunning = false;
    document.getElementById('sim-start-btn').classList.remove('hidden');
    document.getElementById('sim-start-btn').textContent = 'Simulation Complete';
    document.getElementById('sim-start-btn').disabled = true;
    document.getElementById('sim-pause-btn').classList.add('hidden');

    const m = window._ukSimMetrics;
    const summary = document.createElement('div');
    summary.className = 'sim-complete-banner';
    summary.innerHTML = `
        <h4>Simulation Complete</h4>
        <p>The SIM farm ran 200 automated operations: ${m.sims} SIMs activated, ${m.accounts} fake accounts created,
        ${m.posts} posts published, ${m.engagements.toLocaleString()} engagements generated,
        ${fmtNum(m.impressions)} impressions — all while remaining <strong>undetected</strong>.</p>
        <p class="text-muted">This demonstrates how a SIM farm can go from manual setup to full autonomous operation
        with minimal human intervention, and why these operations are a real threat to election integrity.</p>
    `;
    const dashboard = document.getElementById('sim-dashboard');
    const controls = dashboard.querySelector('.sim-controls');
    controls.parentNode.insertBefore(summary, controls.nextSibling);
}
