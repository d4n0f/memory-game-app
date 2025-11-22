(function(){
    // Read players from sessionStorage and render into #result-players-list
    function safeParse(s){ try { return JSON.parse(s); } catch(e){ return null; } }
    const data = safeParse(sessionStorage.getItem('color_hunter_last_players')) || [];
    const container = document.getElementById('result-players-list');
    if (!container) return;

    container.innerHTML = '';
    if (!data || !data.length){
        container.textContent = 'Nincsenek játékos adatok.';
        return;
    }

    data.forEach(p => {
        const el = document.createElement('div');
        el.className = 'player';
        const name = document.createElement('div');
        name.className = 'name';
        name.textContent = (p.name || 'Ismeretlen');
        const score = document.createElement('div');
        score.className = 'score';
        score.textContent = (p.score != null) ? (p.score + ' pont') : '';
        el.appendChild(name);
        el.appendChild(score);
        container.appendChild(el);
    });
})();
