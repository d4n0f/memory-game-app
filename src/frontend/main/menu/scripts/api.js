// Lightweight API helper for JSON requests
(function (global) {
    async function postJSON(url, data) {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(data)
        });
        const text = await resp.text();
        let json = null;
        try { json = JSON.parse(text); } catch (e) { /* not JSON */ }
        return { ok: resp.ok, status: resp.status, json, text };
    }

    async function getJSON(url) {
        const resp = await fetch(url, { credentials: 'same-origin' });
        const text = await resp.text();
        let json = null;
        try { json = JSON.parse(text); } catch (e) { /* not JSON */ }
        return { ok: resp.ok, status: resp.status, json, text };
    }

    global.api = { postJSON, getJSON };
})(window);
