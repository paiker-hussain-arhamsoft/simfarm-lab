/* API client for SimFarm backend */

const API_BASE = '';  // same origin

async function apiFetch(path, options = {}) {
    const url = API_BASE + path;
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `API error ${res.status}`);
    }
    return res.json();
}

const API = {
    // Levels
    getLevels: () => apiFetch('/api/levels'),

    // Scenarios
    generateScenario: (level) => apiFetch(`/api/scenario/${level}`, { method: 'POST' }),
    getSims: (level, page = 1) => apiFetch(`/api/scenario/${level}/sims?page=${page}&per_page=50`),
    getCDRs: (level, page = 1) => apiFetch(`/api/scenario/${level}/cdrs?page=${page}&per_page=100`),
    getNetworkLogs: (level, page = 1) => apiFetch(`/api/scenario/${level}/network-logs?page=${page}&per_page=100`),

    // Analysis
    getAnalysisTools: () => apiFetch('/api/analysis-tools'),
    runAnalysis: (level, tool) =>
        apiFetch(`/api/analyze/${level}`, {
            method: 'POST',
            body: JSON.stringify({ tool }),
        }),

    // Exercises
    getExercises: (level) => apiFetch(`/api/exercises/${level}`),
    submitFlag: (exerciseId, flag) =>
        apiFetch('/api/exercises/submit', {
            method: 'POST',
            body: JSON.stringify({ exercise_id: exerciseId, flag }),
        }),

    // Phishing game
    newPhishingGame: () => apiFetch('/api/phishing/new-game', { method: 'POST' }),
    getDirectory: () => apiFetch('/api/phishing/directory'),
    sendPhish: (data) =>
        apiFetch('/api/phishing/send', { method: 'POST', body: JSON.stringify(data) }),
    getPhishingStatus: (sessionId) => apiFetch(`/api/phishing/status/${sessionId}`),
    submitReport: (sessionId, reportText) =>
        apiFetch('/api/phishing/submit-report', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId, report_text: reportText }),
        }),

    // Playground
    getPlaygroundOptions: () => apiFetch('/api/playground/options'),
    buildFarm: (config) =>
        apiFetch('/api/playground/build', {
            method: 'POST',
            body: JSON.stringify(config),
        }),

    // UK Demo
    getUkDemoScenarios: () => apiFetch('/api/uk-demo/scenarios'),
    runUkDemo: (scenarioId) => apiFetch(`/api/uk-demo/run/${scenarioId}`),
    getUkDemoOptions: () => apiFetch('/api/uk-demo/options'),
    buildUkFarm: (config) =>
        apiFetch('/api/uk-demo/build', { method: 'POST', body: JSON.stringify(config) }),
    simulateUkDemo: (scenarioId) => apiFetch(`/api/uk-demo/simulate/${scenarioId}`),
};
