// VEXORA data sync: bookmarks + history, Supabase when logged in, localStorage fallback
(function () {
  const BM_KEY = 'vexora_bookmarks';
  const HIST_KEY = 'vexora_history';

  async function getAuth() {
    try {
      let r = await fetch('/api/auth/me', { credentials: 'include' });
      let j = await r.json();
      return j.logged_in ? (j.user || true) : null;
    } catch (e) { return null; }
  }
  function lsGet(k) { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch (e) { return []; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  async function svGet(path) { let r = await fetch(path); let j = await r.json(); return j.data || []; }
  async function svPost(path, body) {
    await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  }
  async function svDel(path, body) {
    await fetch(path, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
  }

  async function getBookmarks() {
    let user = await getAuth();
    if (user) { try { return await svGet('/api/bookmarks'); } catch (e) {} }
    return lsGet(BM_KEY);
  }
  async function getHistory() {
    let user = await getAuth();
    if (user) { try { return await svGet('/api/history'); } catch (e) {} }
    return lsGet(HIST_KEY);
  }

  async function toggleBookmark(item) {
    let user = await getAuth();
    let list = await getBookmarks();
    let exists = list.some(b => b.url === item.url);
    if (user) {
      try {
        if (exists) await svDel('/api/bookmarks', { url: item.url });
        else await svPost('/api/bookmarks', item);
      } catch (e) {}
    }
    let ls = lsGet(BM_KEY).filter(b => b.url !== item.url);
    if (!exists) ls.unshift(item);
    lsSet(BM_KEY, ls);
    return !exists; // true => now bookmarked
  }
  async function removeBookmark(url) {
    let user = await getAuth();
    if (user) { try { await svDel('/api/bookmarks', { url }); } catch (e) {} }
    lsSet(BM_KEY, lsGet(BM_KEY).filter(b => b.url !== url));
  }
  async function addHistory(item) {
    let user = await getAuth();
    let ls = lsGet(HIST_KEY).filter(h => h.url !== item.url);
    ls.unshift(item);
    if (ls.length > 100) ls = ls.slice(0, 100);
    lsSet(HIST_KEY, ls);
    if (user) { try { await svPost('/api/history', item); } catch (e) {} }
  }
  async function clearHistory() {
    let user = await getAuth();
    if (user) { try { await svDel('/api/history', {}); } catch (e) {} }
    lsSet(HIST_KEY, []);
  }

  window.VX = { getAuth, getBookmarks, getHistory, toggleBookmark, removeBookmark, addHistory, clearHistory };
  window.dispatchEvent(new Event('vx-ready'));
})();
