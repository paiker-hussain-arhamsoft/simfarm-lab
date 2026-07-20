/**
 * API client for TIER 1 Strategic Brain backend.
 */

const API = {
    async health() {
        const res = await fetch('/api/health');
        return res.json();
    },

    async getConfig() {
        const res = await fetch('/api/config');
        return res.json();
    },

    async getAgents() {
        const res = await fetch('/api/agents');
        return res.json();
    },

    async getAgent(agentId) {
        const res = await fetch(`/api/agents/${agentId}`);
        return res.json();
    },

    async getTools() {
        const res = await fetch('/api/tools');
        return res.json();
    },

    async getScenarios(difficulty) {
        const url = difficulty ? `/api/scenarios?difficulty=${difficulty}` : '/api/scenarios';
        const res = await fetch(url);
        return res.json();
    },

    async getScenario(scenarioId) {
        const res = await fetch(`/api/scenarios/${scenarioId}`);
        return res.json();
    },

    async getHistory(sessionId) {
        const res = await fetch(`/api/history/${sessionId}`);
        return res.json();
    },

    /**
     * Run the pipeline and return an SSE reader.
     * @param {string} task
     * @param {string} sessionId
     * @param {AbortSignal} signal
     * @param {string} framework - autogen | langgraph | direct
     * @param {string} backend - ollama | openai (auto if empty)
     * @returns {ReadableStreamDefaultReader}
     */
    async runPipeline(task, sessionId, signal, framework = '', backend = '') {
        const res = await fetch('/api/pipeline/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                task,
                session_id: sessionId,
                framework,
                backend,
            }),
            signal,
        });
        if (!res.ok || !res.body) {
            throw new Error(`API error: ${res.status}`);
        }
        return res.body.getReader();
    },

    async getIntelligenceConfig() {
        const res = await fetch('/api/intelligence/config');
        return res.json();
    },

    /**
     * Run the TIER 2 Intelligence Crew and return an SSE reader.
     * @param {{query: string, region: string, language: string, sessionId: string, backend?: string}} opts
     * @param {AbortSignal} signal
     * @returns {ReadableStreamDefaultReader}
     */
    async runIntelligencePlan(opts, signal) {
        const res = await fetch('/api/intelligence/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: opts.query,
                region: opts.region,
                language: opts.language,
                session_id: opts.sessionId,
                backend: opts.backend || '',
            }),
            signal,
        });
        if (!res.ok || !res.body) {
            throw new Error(`API error: ${res.status}`);
        }
        return res.body.getReader();
    },

    async getMediaConfig() {
        const res = await fetch('/api/media/config');
        return res.json();
    },

    /**
     * Run the TIER 2 Media Crew (Duix-Avatar Pipeline) and return an SSE reader.
     * @param {object} opts - topic, tone, language, languageCode, duration, audience, voiceTool, videoTool, avatarTool, sessionId, backend
     * @param {AbortSignal} signal
     * @returns {ReadableStreamDefaultReader}
     */
    async runMediaProduce(opts, signal) {
        const res = await fetch('/api/media/produce', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: opts.topic,
                tone: opts.tone,
                language: opts.language,
                language_code: opts.languageCode,
                duration: opts.duration,
                audience: opts.audience || 'General public',
                voice_tool: opts.voiceTool,
                video_tool: opts.videoTool,
                avatar_tool: opts.avatarTool,
                session_id: opts.sessionId,
                backend: opts.backend || '',
            }),
            signal,
        });
        if (!res.ok || !res.body) {
            throw new Error(`API error: ${res.status}`);
        }
        return res.body.getReader();
    },

    async getVideoConfig() {
        const res = await fetch('/api/video/config');
        return res.json();
    },

    /**
     * Run the TIER 2 Video Stack and return an SSE reader.
     * @param {object} opts - topic, style, duration, swapTool, lipsyncTool, consent, sessionId, backend
     * @param {AbortSignal} signal
     * @returns {ReadableStreamDefaultReader}
     */
    async runVideoPlan(opts, signal) {
        const res = await fetch('/api/video/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: opts.topic,
                style: opts.style,
                duration: opts.duration,
                swap_tool: opts.swapTool,
                lipsync_tool: opts.lipsyncTool,
                consent: !!opts.consent,
                authorization_ref: opts.authorizationRef || '',
                approver: opts.approver || '',
                session_id: opts.sessionId,
                backend: opts.backend || '',
            }),
            signal,
        });
        if (!res.ok || !res.body) {
            throw new Error(`API error: ${res.status}`);
        }
        return res.body.getReader();
    },

    async getComplianceAudit(sessionId) {
        const q = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
        const res = await fetch(`/api/compliance/audit${q}`);
        return res.json();
    },

    async getLedgerStatus() {
        const res = await fetch('/api/compliance/ledger/status');
        if (!res.ok) throw new Error(`Ledger status ${res.status}`);
        return res.json();
    },

    /**
     * Fetch/refresh the legal-authorization ledger.
     * @param {object} opts - source ('https'|'ssh'|'upload'), sessionId, approver,
     *                        and for ssh: username/password (transient), for upload: csv
     */
    async fetchLedger(opts) {
        const res = await fetch('/api/compliance/ledger/fetch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: opts.source,
                session_id: opts.sessionId || 'system',
                approver: opts.approver || '',
                username: opts.username || '',
                password: opts.password || '',
                csv: opts.csv || '',
            }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || `Ledger fetch ${res.status}`);
        return data;
    },

    async cancelPipeline(runId) {
        const res = await fetch('/api/pipeline/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ run_id: runId }),
        });
        return res.json();
    },
};
