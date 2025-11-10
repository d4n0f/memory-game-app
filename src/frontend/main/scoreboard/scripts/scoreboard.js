document.addEventListener('DOMContentLoaded', () => {
    const tabMe = document.getElementById('tab-me');
    const tabGlobal = document.getElementById('tab-global');
    const scoresList = document.getElementById('scores-list');

    async function loadScores(scope = 'me'){
        scoresList.innerHTML = '';
        const q = scope === 'me' ? '/api/scores?scope=me&limit=50' : '/api/scores?scope=global&limit=50';
        try{
            const res = await api.getJSON(q);
            if(!res.ok || !res.json){
                showEmpty('Nem sikerült betölteni az eredményeket.');
                return;
            }
            const data = res.json;
            const rows = data.scores || [];
            if(rows.length === 0){
                showEmpty('Nincs elérhető eredmény.');
                return;
            }
            rows.forEach(r => {
                const li = document.createElement('li');
                li.className = 'score-item';

                const left = document.createElement('div');
                left.className = 'score-left';
                left.textContent = r.display_name || r.name || 'Ismeretlen';

                // Meta information: date and game mode/difficulty
                const dateNode = document.createElement('div');
                dateNode.className = 'score-meta';
                if(r.date_val) dateNode.textContent = r.date_val.split('T')[0];
                if(!dateNode.textContent && r.last_played) dateNode.textContent = (r.last_played || '').split('T')[0] || '';

                const mode = r.game_mode || r.game || r.mode || '';
                const difficulty = r.difficulty || '';
                const modeNode = document.createElement('div');
                modeNode.className = 'score-mode';
                if(mode || difficulty){
                    // nicer display: replace underscores and capitalize
                    const niceMode = mode ? (String(mode).replace(/_/g, ' ')) : '';
                    const diff = difficulty ? String(difficulty) : '';
                    modeNode.textContent = diff ? `${niceMode} • ${diff}` : niceMode;
                }

                const lwrap = document.createElement('div');
                lwrap.appendChild(left);
                if(dateNode.textContent) lwrap.appendChild(dateNode);
                if(modeNode.textContent) lwrap.appendChild(modeNode);

                const right = document.createElement('div');
                right.className = 'score-right';
                const scoreVal = r.score_val || r.score || r.best_score || 0;
                right.textContent = `${scoreVal} pont`;

                li.appendChild(lwrap);
                li.appendChild(right);
                scoresList.appendChild(li);
            });
        }catch(err){
            console.error('Load scores error', err);
            showEmpty('Hálózati hiba történt.');
        }
    }

    function showEmpty(msg){
        scoresList.innerHTML = '';
        const li = document.createElement('li');
        li.className = 'score-item';
        li.style.justifyContent = 'center';
        li.textContent = msg;
        scoresList.appendChild(li);
    }

    tabMe.addEventListener('click', () => { tabMe.classList.add('active'); tabGlobal.classList.remove('active'); loadScores('me'); });
    tabGlobal.addEventListener('click', () => { tabGlobal.classList.add('active'); tabMe.classList.remove('active'); loadScores('global'); });

    // initial load: global (matches picture?) show global by default or me if logged in
    loadScores('global');
});
