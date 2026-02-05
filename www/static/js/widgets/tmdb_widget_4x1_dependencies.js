/**
 * TMDB Module - Dependencies Widget (4x1)
 * Zeigt TMDB spezifische Tools (Python-Module)
 * Version: 1.0.0
 */

function loadTmdbDependencies() {
    fetch('/api/system')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.software) {
                updateTmdbDependencies(data.software);
            }
        })
        .catch(error => {
            console.error('Fehler beim Laden der TMDB-Dependencies:', error);
            showTmdbDependenciesError();
        });
}

function updateTmdbDependencies(softwareList) {
    const tbody = document.getElementById('tmdb-dependencies-tbody');
    if (!tbody) return;
    
    // TMDB-spezifische Tools (aus libtmdb.ini [dependencies])
    const tmdbTools = [
        { name: 'curl', display_name: 'curl' },
        { name: 'jq', display_name: 'jq' }
    ];
    
    let html = '';
    
    tmdbTools.forEach(tool => {
        const software = softwareList.find(s => s.name === tool.name);
        if (software) {
            html += renderSoftwareRow(tool.display_name, software);
        }
    });
    
    if (html === '') {
        html = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #999;">Keine Informationen verfügbar</td></tr>';
    }
    
    tbody.innerHTML = html;
}

function showTmdbDependenciesError() {
    const tbody = document.getElementById('tmdb-dependencies-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #e53e3e;">Fehler beim Laden</td></tr>';
}

// Auto-Load
if (document.getElementById('tmdb-dependencies-widget')) {
    loadTmdbDependencies();
}
