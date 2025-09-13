// app.js
const API_BASE = 'http://localhost:8000';

const $ = (id) => document.getElementById(id);
const setHTML = (el, html) => (el.innerHTML = html);
const setText = (el, txt) => (el.textContent = txt);
const setLoading = (btn, on) => (btn.disabled = !!on);

$('apiBase').textContent = API_BASE;

async function pingHealth() {
  try {
    const r = await fetch(`${API_BASE}/health`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const j = await r.json();
    setHTML($('health'), `<span class="ok">OK</span> · ${j.app || 'api'}`);
  } catch (e) {
    setHTML($('health'), `<span class="err">DOWN</span> · ${e.message}`);
  }
}

async function ask() {
  const btn = $('askBtn');
  const q = $('q').value.trim();
  const debug = $('debug').checked;
  if (!q) return;

  setLoading(btn, true);
  setText($('answer'), 'Pensando…');
  setText($('citations'), '');
  setHTML($('debugBox'), '');

  try {
    const r = await fetch(`${API_BASE}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q, debug })
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);

    setText($('answer'), j.answer || '—');

    // citas
    if (Array.isArray(j.citations) && j.citations.length) {
      const pages = j.citations.map(c => c.page).join(', ');
      setHTML($('citations'), `Citas · páginas: <strong>${pages}</strong>`);
    } else {
      setText($('citations'), 'Sin citas.');
    }

    // debug opcional
    if (j.debug) {
      const { pages = [], contexts = [] } = j.debug;
      const items = contexts.map((c, i) => {
        const p = pages[i] ?? '?';
        return `<details><summary>p.${p}</summary><pre>${escapeHTML(c)}</pre></details>`;
      }).join('\n');
      setHTML($('debugBox'), `<h4>Debug</h4>${items || '<div class="muted">—</div>'}`);
    }
  } catch (e) {
    setHTML($('answer'), `<span class="err">${e.message}</span>`);
  } finally {
    setLoading(btn, false);
  }
}

async function suggestTerms() {
  const btn = $('termsBtn');
  const q = $('q').value.trim();
  if (!q) return;
  setLoading(btn, true);
  setText($('suggestions'), 'Buscando…');

  try {
    const r = await fetch(`${API_BASE}/suggest-terms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);

    const kws = Array.isArray(j.keywords) ? j.keywords : [];
    if (!kws.length) {
      setText($('suggestions'), '—');
      return;
    }
    setHTML($('suggestions'), kws.map(k => `<span class="pill">${escapeHTML(k)}</span>`).join(''));
  } catch (e) {
    setHTML($('suggestions'), `<span class="err">${e.message}</span>`);
  } finally {
    setLoading(btn, false);
  }
}

function escapeHTML(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

// UX rápido
$('askBtn').addEventListener('click', ask);
$('termsBtn').addEventListener('click', suggestTerms);
$('healthBtn').addEventListener('click', pingHealth);
$('q').addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'enter') ask();
});

pingHealth();
