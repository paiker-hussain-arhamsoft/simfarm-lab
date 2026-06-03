/* Phishing Game — Legendary level detection mode */

let phishingSession = null;
let selectedTarget = null;

async function initPhishingGame() {
    const container = document.getElementById('phishing-container');
    container.innerHTML = '<div class="loading"><div class="spinner"></div> Initializing phishing game...</div>';

    try {
        const data = await API.newPhishingGame();
        phishingSession = data.session_id;

        container.innerHTML = `
            <div class="game-stats" id="phishing-stats">
                <div class="stat-box">
                    <div class="stat-value" id="ps-attempts">${data.max_attempts}</div>
                    <div class="stat-label">Attempts Left</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="ps-evidence">0</div>
                    <div class="stat-label">Evidence</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="ps-score">0</div>
                    <div class="stat-label">Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="ps-status" style="color: var(--accent-green);">ACTIVE</div>
                    <div class="stat-label">Status</div>
                </div>
            </div>

            <div class="phishing-game">
                <!-- Left: Company Directory -->
                <div class="company-directory">
                    <h3>NovaCom Digital Solutions</h3>
                    <p class="text-muted" style="font-size:0.8rem; margin-bottom:12px;">
                        "Cloud Communications SaaS Provider"<br>Employee Directory
                    </p>
                    <div id="employee-list">
                        ${data.company_directory.map(emp => `
                            <div class="employee-card" onclick="selectTarget('${emp.email}', this)">
                                <div class="emp-name">${emp.name}</div>
                                <div class="emp-role">${emp.role}</div>
                                <div class="emp-hint">${emp.social_media_hint}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Right: Workspace -->
                <div class="phishing-workspace">
                    <!-- Email Composer -->
                    <div class="email-composer">
                        <h3>Compose Phishing Email</h3>
                        <div class="email-field">
                            <label>To</label>
                            <input type="text" id="phish-to" readonly placeholder="Select a target from the directory">
                        </div>
                        <div class="email-field">
                            <label>Your Alias (From)</label>
                            <input type="text" id="phish-from" placeholder="e.g., John Smith, IT Security Team">
                        </div>
                        <div class="email-field">
                            <label>Subject</label>
                            <input type="text" id="phish-subject" placeholder="e.g., Urgent: Security Audit Required">
                        </div>
                        <div class="email-field">
                            <label>Pretext Category</label>
                            <select id="phish-pretext">
                                <option value="">-- Select pretext --</option>
                                <option value="tech_support">Tech Support / IT Issue</option>
                                <option value="security_audit">Security Audit / Compliance</option>
                                <option value="job_offer">Job Offer / Recruitment</option>
                                <option value="bonus">Bonus / Salary Review</option>
                                <option value="partnership">Business Partnership</option>
                                <option value="tech_conference">Tech Conference Invitation</option>
                                <option value="api_documentation">API Documentation Request</option>
                                <option value="compliance_review">Compliance Review</option>
                                <option value="whistleblower_protection">Whistleblower Protection</option>
                                <option value="competitor_intel">Competitor Intelligence</option>
                                <option value="investment_opportunity">Investment Opportunity</option>
                                <option value="side_gig">Side Gig / Freelance Work</option>
                                <option value="quick_money">Quick Money Opportunity</option>
                                <option value="buyer_for_data">Buyer Looking for Data</option>
                                <option value="competitor_wants_clients">Competitor Wants Client List</option>
                                <option value="mentorship">Mentorship Offer</option>
                                <option value="job_referral">Job Referral</option>
                                <option value="hackathon">Hackathon Invitation</option>
                                <option value="github_notification">GitHub Notification</option>
                                <option value="code_review">Code Review Request</option>
                            </select>
                        </div>
                        <div class="email-field">
                            <label>Email Body</label>
                            <textarea id="phish-body" placeholder="Write your phishing email here. Be creative and convincing..."></textarea>
                        </div>
                        <button class="send-btn" id="send-phish-btn" onclick="sendPhish()">
                            Send Phishing Email
                        </button>
                    </div>

                    <!-- Response log -->
                    <div class="response-log">
                        <h3>Response Log</h3>
                        <div id="response-log-entries">
                            <p class="text-muted" style="font-size:0.85rem;">
                                No emails sent yet. Select a target and craft your message.
                            </p>
                        </div>
                    </div>

                    <!-- Evidence panel -->
                    <div class="evidence-panel">
                        <h3>Evidence Collected</h3>
                        <div id="evidence-items">
                            <p class="text-muted" style="font-size:0.85rem;">
                                No evidence collected yet. Successfully phish an insider to obtain documents.
                            </p>
                        </div>
                    </div>

                    <!-- Report submission -->
                    <div class="report-form" id="report-section">
                        <h3>Submit Investigation Report</h3>
                        <p class="text-muted" style="font-size:0.85rem; margin-bottom:12px;">
                            Compile your evidence into a formal report for law enforcement.
                            Include: company name, operation type, scale, location, clients, and technical details.
                        </p>
                        <textarea id="report-text" placeholder="INVESTIGATION REPORT&#10;&#10;Subject: SIM Farm Operation&#10;Company: ...&#10;Operation: ...&#10;Location: ...&#10;Evidence: ..."></textarea>
                        <button class="submit-report-btn" id="submit-report-btn" onclick="submitReport()">
                            Submit Report to Authorities
                        </button>
                    </div>

                    <!-- Report result (shown after submission) -->
                    <div id="report-result-container"></div>
                </div>
            </div>
        `;
    } catch (err) {
        container.innerHTML = `<p class="text-red">Failed to initialize: ${err.message}</p>`;
    }
}

function selectTarget(email, el) {
    selectedTarget = email;
    document.getElementById('phish-to').value = email;
    document.querySelectorAll('.employee-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
}

async function sendPhish() {
    if (!phishingSession) return;
    if (!selectedTarget) {
        alert('Select a target from the company directory.');
        return;
    }

    const subject = document.getElementById('phish-subject').value.trim();
    const body = document.getElementById('phish-body').value.trim();
    const senderAlias = document.getElementById('phish-from').value.trim() || 'Anonymous';
    const pretext = document.getElementById('phish-pretext').value;

    if (!subject || !body) {
        alert('Fill in the subject and body of your email.');
        return;
    }

    const btn = document.getElementById('send-phish-btn');
    btn.disabled = true;
    btn.textContent = 'Sending...';

    try {
        const result = await API.sendPhish({
            session_id: phishingSession,
            target_email: selectedTarget,
            subject,
            body,
            sender_alias: senderAlias,
            pretext,
        });

        // Add to response log
        const logEntries = document.getElementById('response-log-entries');
        if (logEntries.querySelector('.text-muted')) {
            logEntries.innerHTML = '';
        }

        let entryClass = 'neutral';
        if (result.success) entryClass = 'success';
        else if (result.alert) entryClass = 'warning';
        else if (result.tip) entryClass = 'failure';

        const entry = document.createElement('div');
        entry.className = `response-entry ${entryClass}`;
        entry.innerHTML = `
            <div class="re-header">
                <span><strong>${result.npc_name || selectedTarget}</strong></span>
                <span>Quality: ${(result.email_quality_score * 100).toFixed(0)}%</span>
            </div>
            <div class="re-body">${result.response}</div>
            ${result.alert ? `<div class="text-red mt-1" style="font-size:0.82rem;">${result.alert}</div>` : ''}
            ${result.tip ? `<div class="text-yellow mt-1" style="font-size:0.82rem;">${result.tip}</div>` : ''}
            ${result.evidence_obtained && result.evidence_obtained.length ?
                `<div class="text-green mt-1" style="font-size:0.82rem;">Evidence obtained: ${result.evidence_obtained.join(', ')}</div>` : ''}
        `;
        logEntries.prepend(entry);

        // Update game status
        if (result.game_status) {
            updatePhishingStatus(result.game_status);
        }

        // Clear form
        document.getElementById('phish-subject').value = '';
        document.getElementById('phish-body').value = '';
        document.getElementById('phish-pretext').selectedIndex = 0;

    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Send Phishing Email';
    }
}

function updatePhishingStatus(status) {
    document.getElementById('ps-attempts').textContent = status.attempts_remaining;
    document.getElementById('ps-evidence').textContent = status.total_evidence;
    document.getElementById('ps-score').textContent = status.score;

    const statusEl = document.getElementById('ps-status');
    if (status.game_over) {
        statusEl.textContent = 'GAME OVER';
        statusEl.style.color = 'var(--accent-red)';
        document.getElementById('send-phish-btn').disabled = true;
    } else if (status.detected) {
        statusEl.textContent = 'DETECTED';
        statusEl.style.color = 'var(--accent-yellow)';
    }

    // Update evidence panel
    if (status.evidence_collected && status.evidence_collected.length > 0) {
        const evidenceDiv = document.getElementById('evidence-items');
        evidenceDiv.innerHTML = status.evidence_collected.map(ev => `
            <div class="evidence-item">
                <span class="ev-name">${ev.name}</span>
                <span class="ev-type ${ev.type}">${ev.type}</span>
                <div class="ev-desc">${ev.description}</div>
                <div class="ev-preview">${ev.content_preview}</div>
            </div>
        `).join('');
    }

    // Enable/disable report submission
    const reportBtn = document.getElementById('submit-report-btn');
    if (reportBtn) {
        reportBtn.disabled = !status.can_submit_report;
    }
}

async function submitReport() {
    if (!phishingSession) return;

    const reportText = document.getElementById('report-text').value.trim();
    if (reportText.length < 50) {
        alert('Your report is too short. Include detailed findings.');
        return;
    }

    const btn = document.getElementById('submit-report-btn');
    btn.disabled = true;
    btn.textContent = 'Submitting...';

    try {
        const result = await API.submitReport(phishingSession, reportText);
        const container = document.getElementById('report-result-container');

        if (result.accepted) {
            container.innerHTML = `
                <div class="report-result">
                    <div class="grade ${result.grade}">${result.grade}</div>
                    <div class="verdict">${result.verdict}</div>
                    <div class="score-breakdown">
                        <div class="score-item">
                            <div class="score-num">${result.evidence_score}</div>
                            <div class="score-lbl">Evidence</div>
                        </div>
                        <div class="score-item">
                            <div class="score-num">${result.report_score}</div>
                            <div class="score-lbl">Report</div>
                        </div>
                        <div class="score-item">
                            <div class="score-num">${result.total_score}</div>
                            <div class="score-lbl">Total</div>
                        </div>
                    </div>
                    <div class="mt-2" style="text-align:left;">
                        <h4 style="margin-bottom:8px;">Findings identified:</h4>
                        <ul style="padding-left:20px; color: var(--text-secondary); font-size: 0.9rem;">
                            ${result.findings_identified.map(f => `<li>${f}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="mt-2" style="text-align:left;">
                        <h4 style="margin-bottom:8px;">Evidence collected:</h4>
                        <ul style="padding-left:20px; color: var(--accent-green); font-size: 0.9rem;">
                            ${result.evidence_summary.map(e => `<li>${e}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;

            // Disable further actions
            document.getElementById('send-phish-btn').disabled = true;
            btn.textContent = 'Report Submitted';
        } else {
            alert(result.message);
            btn.disabled = false;
            btn.textContent = 'Submit Report to Authorities';
        }
    } catch (err) {
        alert('Error: ' + err.message);
        btn.disabled = false;
        btn.textContent = 'Submit Report to Authorities';
    }
}
