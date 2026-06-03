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
    document.getElementById('view-dashboard').classList.remove('hidden');
    document.getElementById('view-lab').classList.add('hidden');
    document.getElementById('view-playground').classList.add('hidden');
    document.querySelectorAll('.header-nav button').forEach(b => b.classList.remove('active'));
    document.getElementById('nav-dashboard').classList.add('active');
}

function showLab() {
    document.getElementById('view-dashboard').classList.add('hidden');
    document.getElementById('view-lab').classList.remove('hidden');
    document.getElementById('view-playground').classList.add('hidden');
    document.querySelectorAll('.header-nav button').forEach(b => b.classList.remove('active'));
    document.getElementById('nav-lab').classList.add('active');
}
