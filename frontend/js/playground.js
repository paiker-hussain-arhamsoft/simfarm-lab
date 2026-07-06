/* Playground — Build a SIM farm from scratch (Pakistani ecosystem) */

let pgOptions = null;
let pgResult = null;

async function showPlayground() {
    showView('view-playground', 'nav-playground');

    if (!pgOptions) {
        await loadPlaygroundOptions();
    }
}

async function loadPlaygroundOptions() {
    const container = document.getElementById('pg-wizard');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading Pakistani telecom data...</div>';

    try {
        pgOptions = await API.getPlaygroundOptions();
        renderPlaygroundWizard();
    } catch (err) {
        container.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

function renderPlaygroundWizard() {
    const c = document.getElementById('pg-wizard');

    // ── Step 1: City & Carriers ──
    const cityOpts = Object.entries(pgOptions.cities).map(([k, v]) =>
        `<option value="${k}">${v.name} (${v.province}) — ${v.towers} towers — Risk: ${v.risk_level}</option>`
    ).join('');

    const carrierCards = Object.entries(pgOptions.carriers).map(([k, v]) => `
        <label class="pg-checkbox-card">
            <input type="checkbox" name="pg-carrier" value="${k}" ${k === 'jazz' ? 'checked' : ''}>
            <div class="pg-card-body">
                <strong>${v.name}</strong>
                <div class="text-muted" style="font-size:0.78rem;">${v.description}</div>
                <div class="pg-card-stats">
                    <span>SIM: PKR ${v.sim_cost_pkr}</span>
                    <span>SMS: PKR ${v.sms_rate_pkr}</span>
                    <span>Share: ${v.market_share}</span>
                    <span>Biometric: ${v.biometric_strictness}</span>
                </div>
            </div>
        </label>
    `).join('');

    // ── Step 2: SIM Acquisition ──
    const acqOpts = Object.entries(pgOptions.acquisition_methods).map(([k, v]) => `
        <label class="pg-radio-card">
            <input type="radio" name="pg-acq" value="${k}" ${k === 'legitimate_cnic' ? 'checked' : ''}>
            <div class="pg-card-body">
                <strong>${v.name}</strong>
                <span class="badge-sm ${v.risk_level}">${v.risk_level}</span>
                <div class="text-muted" style="font-size:0.78rem;">${v.description}</div>
                <div class="pg-card-stats">
                    <span>SIMs/CNIC: ${v.sims_per_cnic}</span>
                    <span>Cost: ${v.cost_multiplier}</span>
                    <span>Detection: ${v.detection_risk}</span>
                </div>
                <div class="text-muted" style="font-size:0.75rem; margin-top:4px;">${v.notes}</div>
            </div>
        </label>
    `).join('');

    // ── Step 3: Hardware ──
    const hwCards = Object.entries(pgOptions.hardware).map(([k, v]) => `
        <div class="pg-hw-card">
            <div class="pg-hw-header">
                <strong>${v.name}</strong>
                <span class="badge-sm type-${v.type}">${v.type}</span>
            </div>
            <div class="text-muted" style="font-size:0.78rem;">${v.description}</div>
            <div class="pg-card-stats">
                <span>Slots: ${v.sim_capacity}</span>
                <span>PKR ${v.cost_pkr.toLocaleString()}</span>
                <span>${v.throughput_sms_per_hour} SMS/hr</span>
                <span>Detect: ${v.detectability}</span>
            </div>
            <div class="pg-hw-qty">
                <label>Qty:</label>
                <input type="number" min="0" max="20" value="0" data-hw="${k}" class="pg-hw-input">
            </div>
        </div>
    `).join('');

    // ── Step 4: Automation ──
    const autoOpts = Object.entries(pgOptions.automation_tools).map(([k, v]) => `
        <label class="pg-radio-card">
            <input type="radio" name="pg-auto" value="${k}" ${k === 'gammu' ? 'checked' : ''}>
            <div class="pg-card-body">
                <strong>${v.name}</strong>
                <div class="text-muted" style="font-size:0.78rem;">${v.description}</div>
                <div class="pg-card-stats">
                    <span>Throughput: ${v.throughput}</span>
                    <span>Complexity: ${v.complexity}</span>
                    <span>PKR ${v.cost_pkr.toLocaleString()}</span>
                </div>
            </div>
        </label>
    `).join('');

    // ── Step 5: OPSEC ──
    const opsecCards = Object.entries(pgOptions.opsec_measures).map(([k, v]) => `
        <label class="pg-checkbox-card">
            <input type="checkbox" name="pg-opsec" value="${k}">
            <div class="pg-card-body">
                <strong>${v.name}</strong>
                <span class="badge-sm complexity-${v.complexity}">${v.complexity}</span>
                <div class="text-muted" style="font-size:0.78rem;">${v.description}</div>
                <div class="pg-card-stats">
                    <span>Effect: ${v.effectiveness}</span>
                    <span>PKR ${v.cost_pkr.toLocaleString()}</span>
                </div>
                <div class="text-muted" style="font-size:0.75rem; margin-top:4px;">${v.notes}</div>
            </div>
        </label>
    `).join('');

    // ── Step 6: Purpose ──
    const purposeOpts = pgOptions.purposes.map(p => `
        <option value="${p.id}">${p.name}</option>
    `).join('');

    c.innerHTML = `
        <div class="pg-step">
            <h3>Step 1: Choose Location & Carriers</h3>
            <div class="pg-field">
                <label>City</label>
                <select id="pg-city">${cityOpts}</select>
            </div>
            <div class="pg-field">
                <label>Carriers (select one or more)</label>
                <div class="pg-card-grid">${carrierCards}</div>
            </div>
        </div>

        <div class="pg-step">
            <h3>Step 2: SIM Acquisition Method</h3>
            <div class="pg-card-grid cols-1">${acqOpts}</div>
            <div class="pg-field" style="margin-top:12px;">
                <label>Number of CNICs Available</label>
                <input type="number" id="pg-cnics" min="1" max="500" value="5">
            </div>
            <div class="pg-field">
                <label>Target Number of SIMs</label>
                <input type="number" id="pg-target-sims" min="1" max="10000" value="50">
            </div>
        </div>

        <div class="pg-step">
            <h3>Step 3: Select Hardware</h3>
            <div class="pg-card-grid cols-2">${hwCards}</div>
        </div>

        <div class="pg-step">
            <h3>Step 4: Automation Software</h3>
            <div class="pg-card-grid cols-1">${autoOpts}</div>
        </div>

        <div class="pg-step">
            <h3>Step 5: Operational Security (OPSEC)</h3>
            <div class="pg-card-grid cols-1">${opsecCards}</div>
        </div>

        <div class="pg-step">
            <h3>Step 6: Farm Purpose & Config</h3>
            <div class="pg-field">
                <label>Purpose</label>
                <select id="pg-purpose">${purposeOpts}</select>
            </div>
            <div class="pg-field">
                <label>Farm Name</label>
                <input type="text" id="pg-name" value="Operation Karachi" placeholder="Give your operation a name">
            </div>
        </div>

        <button class="pg-build-btn" onclick="buildFarm()">Deploy SIM Farm</button>
    `;
}

async function buildFarm() {
    const carriers = [...document.querySelectorAll('input[name="pg-carrier"]:checked')].map(i => i.value);
    const acq = document.querySelector('input[name="pg-acq"]:checked')?.value || 'legitimate_cnic';
    const auto = document.querySelector('input[name="pg-auto"]:checked')?.value || 'gammu';
    const opsec = [...document.querySelectorAll('input[name="pg-opsec"]:checked')].map(i => i.value);

    const hardware = [];
    document.querySelectorAll('.pg-hw-input').forEach(input => {
        const qty = parseInt(input.value) || 0;
        if (qty > 0) hardware.push({ id: input.dataset.hw, quantity: qty });
    });

    if (carriers.length === 0) { alert('Select at least one carrier.'); return; }
    if (hardware.length === 0) { alert('Select at least one hardware device.'); return; }

    const config = {
        name: document.getElementById('pg-name').value || 'My Farm',
        city: document.getElementById('pg-city').value,
        carriers,
        acquisition_method: acq,
        num_cnics: parseInt(document.getElementById('pg-cnics').value) || 1,
        hardware,
        automation_tool: auto,
        opsec_measures: opsec,
        target_sims: parseInt(document.getElementById('pg-target-sims').value) || 10,
        purpose: document.getElementById('pg-purpose').value,
    };

    const resultDiv = document.getElementById('pg-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Deploying farm and calculating metrics...</div>';
    resultDiv.scrollIntoView({ behavior: 'smooth' });

    try {
        pgResult = await API.buildFarm(config);
        renderFarmResult(pgResult);
    } catch (err) {
        resultDiv.innerHTML = `<p class="text-red">${err.message}</p>`;
    }
}

function renderFarmResult(r) {
    const gradeColor = stealthGradeColor(r.stealth_grade);

    const warningsHtml = r.warnings.length
        ? `<div class="pg-warnings">${r.warnings.map(w => `<div class="pg-warning">${w}</div>`).join('')}</div>`
        : '';

    const notesHtml = r.educational_notes.length
        ? `<div class="pg-notes"><h4>Educational Notes</h4>${r.educational_notes.map(n => `<div class="pg-note">${n}</div>`).join('')}</div>`
        : '';

    document.getElementById('pg-result').innerHTML = `
        <div class="pg-result-card">
            <div class="pg-result-header">
                <div>
                    <h3>${r.farm_name}</h3>
                    <div class="text-muted">${r.city}, ${r.province} — ${r.carriers.join(', ')}</div>
                </div>
                <div class="pg-grade" style="background: ${gradeColor};">
                    <div class="pg-grade-letter">${r.stealth_grade}</div>
                    <div class="pg-grade-label">${r.stealth_label}</div>
                </div>
            </div>

            <div class="pg-metrics-grid">
                <div class="pg-metric">
                    <div class="pg-metric-value">${r.actual_sims}</div>
                    <div class="pg-metric-label">Active SIMs</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">${r.throughput_sms_per_hour.toLocaleString()}</div>
                    <div class="pg-metric-label">SMS/Hour</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">${r.detection_risk_percent}</div>
                    <div class="pg-metric-label">Detection Risk</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">${r.pta_flag_percent}</div>
                    <div class="pg-metric-label">PTA Flag Risk</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">PKR ${r.setup_cost_pkr.toLocaleString()}</div>
                    <div class="pg-metric-label">Setup Cost</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">PKR ${r.monthly_operating_cost_pkr.toLocaleString()}</div>
                    <div class="pg-metric-label">Monthly Cost</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">${r.estimated_detection_timeline}</div>
                    <div class="pg-metric-label">Time to Detection</div>
                </div>
                <div class="pg-metric">
                    <div class="pg-metric-value">${r.total_sim_slots}</div>
                    <div class="pg-metric-label">Hardware Slots</div>
                </div>
            </div>

            ${warningsHtml}

            <div class="pg-cost-breakdown">
                <h4>Cost Breakdown (PKR)</h4>
                <div class="pg-cost-row"><span>Hardware</span><span>${r.hardware_cost_pkr.toLocaleString()}</span></div>
                <div class="pg-cost-row"><span>SIM Cards</span><span>${r.sim_cost_pkr.toLocaleString()}</span></div>
                <div class="pg-cost-row"><span>OPSEC Measures</span><span>${r.opsec_cost_pkr.toLocaleString()}</span></div>
                <div class="pg-cost-row total"><span>Total Setup</span><span>PKR ${r.setup_cost_pkr.toLocaleString()}</span></div>
            </div>

            ${notesHtml}
        </div>
    `;
}
