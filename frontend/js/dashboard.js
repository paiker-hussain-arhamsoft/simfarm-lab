/* Dashboard — level selection grid */

async function loadDashboard() {
    const grid = document.getElementById('level-grid');
    try {
        const data = await API.getLevels();
        grid.innerHTML = data.levels.map(lv => `
            <div class="level-card ${lv.id}" onclick="startLevel('${lv.id}')">
                <span class="badge">${lv.icon} ${lv.difficulty}</span>
                <h3>${lv.name}</h3>
                <p>${lv.description}</p>
                <div class="card-footer">
                    <span>Click to enter</span>
                    <span>&rarr;</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        grid.innerHTML = `<p class="text-red">Failed to load levels: ${err.message}</p>`;
    }
}

function showDashboard() {
    showView('view-dashboard', 'nav-dashboard');
}

function showLab() {
    showView('view-lab', 'nav-lab');
}
