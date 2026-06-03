/* UK Demo — Political Campaign SIM Farm Scenarios */

let ukDemoData = null;

async function showUkDemo() {
    document.getElementById('view-dashboard').classList.add('hidden');
    document.getElementById('view-lab').classList.add('hidden');
    document.getElementById('view-playground').classList.add('hidden');
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
                <span>Click to run scenario</span>
                <span>&rarr;</span>
            </div>
        </div>
    `).join('');

    // Also render regulatory context
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

async function runUkScenario(scenarioId) {
    const resultDiv = document.getElementById('uk-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Running scenario analysis...</div>';
    resultDiv.scrollIntoView({ behavior: 'smooth' });

    try {
        const r = await API.runUkDemo(scenarioId);
        renderUkResult(r);
    } catch (err) {
        resultDiv.innerHTML = `<p class="text-red">Error: ${err.message}</p>`;
    }
}

function fmtNum(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (n >= 1_000) return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + 'K';
    return n.toLocaleString();
}

function renderUkResult(r) {
    const gradeColors = { S: '#a855f7', A: '#22c55e', B: '#f59e0b', C: '#f97316', F: '#ef4444' };
    const gradeColor = gradeColors[r.stealth_grade] || '#6b7280';

    document.getElementById('uk-result').innerHTML = `
        <div class="pg-result-card" style="border-top: 3px solid ${r.party_color};">
            <!-- Header -->
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

            <!-- Objective -->
            <div class="uk-objective-box">
                <strong>OBJECTIVE:</strong> ${r.objective}
            </div>

            <!-- Key Metrics -->
            <div class="pg-metrics-grid">
                <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.total_sims)}</span><span class="pg-metric-label">Active SIMs</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.total_accounts)}</span><span class="pg-metric-label">Fake Accounts</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.network_detection_percent}</span><span class="pg-metric-label">Network Detection</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.platform_detection_percent}</span><span class="pg-metric-label">Platform Detection</span></div>
                <div class="pg-metric"><span class="pg-metric-value">GBP ${fmtNum(r.total_campaign_cost_gbp)}</span><span class="pg-metric-label">Total Campaign Cost</span></div>
                <div class="pg-metric"><span class="pg-metric-value">GBP ${fmtNum(r.monthly_operating_cost_gbp)}</span><span class="pg-metric-label">Monthly OpCost</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.estimated_detection_timeline}</span><span class="pg-metric-label">Detection Timeline</span></div>
                <div class="pg-metric"><span class="pg-metric-value">${r.electoral_commission_percent}</span><span class="pg-metric-label">Electoral Commission Risk</span></div>
            </div>

            <!-- Campaign Reach -->
            <div class="uk-section">
                <h4 class="uk-section-title">Campaign Reach</h4>
                <div class="pg-metrics-grid">
                    <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.daily_posts)}</span><span class="pg-metric-label">Daily Posts</span></div>
                    <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.daily_impressions)}</span><span class="pg-metric-label">Daily Impressions</span></div>
                    <div class="pg-metric"><span class="pg-metric-value">${fmtNum(r.total_campaign_impressions)}</span><span class="pg-metric-label">Total Impressions</span></div>
                    <div class="pg-metric"><span class="pg-metric-value">${r.accounts_per_constituency}</span><span class="pg-metric-label">Accounts/Constituency</span></div>
                </div>
            </div>

            <!-- Infrastructure -->
            <div class="uk-section">
                <h4 class="uk-section-title">Infrastructure</h4>
                <div class="uk-info-grid">
                    <div class="uk-info-item"><strong>Platforms:</strong> ${r.platforms.join(', ')}</div>
                    <div class="uk-info-item"><strong>Carriers:</strong> ${r.carriers.join(', ')}</div>
                    <div class="uk-info-item"><strong>Cities:</strong> ${r.cities.join(', ')}</div>
                    <div class="uk-info-item"><strong>Duration:</strong> ${r.campaign_duration_weeks} weeks</div>
                </div>
            </div>

            <!-- Key Messages -->
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

            <!-- Cost Breakdown -->
            <div class="uk-section">
                <h4 class="pg-cost-title">Cost Breakdown (GBP)</h4>
                <div class="pg-cost-breakdown">
                    <div class="pg-cost-row"><span>Hardware</span><span>${r.hardware_cost_gbp.toLocaleString()}</span></div>
                    <div class="pg-cost-row"><span>SIM Cards</span><span>${r.sim_cost_gbp.toLocaleString()}</span></div>
                    <div class="pg-cost-row"><span>OPSEC Tools</span><span>${r.opsec_cost_gbp.toLocaleString()}</span></div>
                    <div class="pg-cost-row"><span>Monthly Operations (x${r.campaign_duration_weeks / 4})</span><span>${(r.monthly_operating_cost_gbp * r.campaign_duration_weeks / 4).toLocaleString()}</span></div>
                    <div class="pg-cost-total"><span>Total Campaign</span><span>GBP ${r.total_campaign_cost_gbp.toLocaleString()}</span></div>
                </div>
            </div>

            <!-- Warnings -->
            ${r.warnings.length ? `
                <div class="pg-warnings">
                    ${r.warnings.map(w => `<div class="pg-warning">${w}</div>`).join('')}
                </div>
            ` : ''}

            <!-- Legal / Educational Notes -->
            <div class="uk-section">
                <h4 class="pg-notes-title">Legal & Educational Notes</h4>
                <div class="pg-notes">
                    ${r.legal_notes.map(n => `<div class="pg-note">${n}</div>`).join('')}
                </div>
            </div>
        </div>
    `;
}
