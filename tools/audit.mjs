// A measured audit of built pages: overflow, clipped text, tap targets, headings, names, alt, contrast.
// node --experimental-websocket tools/audit.mjs <base-url> <width> <page> [page...]
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [base, w, ...pages] = process.argv.slice(2);
const port = 9100 + Math.floor(Math.random() * 300);
const proc = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'sp-audit-'))}`, '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map(); let errs = [];
const send = (m, p = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method: m, params: p })); });

// runs in the page
const PROBE = () => {
  const out = { overflow: document.documentElement.scrollWidth - innerWidth, issues: [] };
  const add = (k, el, x = '') => out.issues.push(k + ' ' + (el ? (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '') + ' “' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 40) + '”') : '') + (x ? ' ' + x : ''));
  const vis = (el) => { const s = getComputedStyle(el); const r = el.getBoundingClientRect(); return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0 && !el.closest('[aria-hidden="true"],.pt,.ldr,.vh'); };
  // headings
  const hs = [...document.querySelectorAll('h1,h2,h3,h4')].filter((h) => h.classList.contains('vh') ? !h.closest('[aria-hidden="true"]') : vis(h));   // a .vh heading is read by screen readers
  const h1 = hs.filter((h) => h.tagName === 'H1').length;
  if (h1 !== 1) out.issues.push('h1 count ' + h1);
  let prev = 1;
  for (const h of hs) { const l = +h.tagName[1]; if (l > prev + 1) add('heading skip h' + prev + '→h' + l, h); prev = l; }
  // names
  document.querySelectorAll('a,button,input,select,textarea').forEach((el) => {
    if (!vis(el)) return;
    const name = (el.getAttribute('aria-label') || el.textContent || el.value || el.getAttribute('title') || '').trim() || (el.labels && el.labels.length ? 'L' : '') || el.querySelector('img[alt]:not([alt=""])')?.alt;
    if (!name && el.type !== 'hidden') add('no accessible name', el);
    const r0 = el.getBoundingClientRect();
    const ps = getComputedStyle(el, '::after');
    const pad = ps.content !== 'none' && ps.position === 'absolute' ? -2 * parseFloat(ps.top || 0) : 0;   // a hit area drawn by ::after
    const r = { width: r0.width + (ps.content !== 'none' && ps.position === 'absolute' ? -2 * parseFloat(ps.left || 0) : 0), height: r0.height + pad };
    const inline = el.tagName === 'A' && getComputedStyle(el).display === 'inline' && el.closest('p,li,figcaption,td');
    if (!inline && (r.height < 24 || r.width < 24)) add('small target ' + Math.round(r.width) + 'x' + Math.round(r.height), el);
  });
  document.querySelectorAll('img').forEach((im) => { if (!im.hasAttribute('alt')) add('img no alt', im, im.src.split('/').pop()); if (im.complete && im.naturalWidth === 0) add('img broken', im, im.src.split('/').pop()); });
  // clipped text: text boxes whose content is wider than the box without an intended ellipsis/scroller
  document.querySelectorAll('h1,h2,h3,p,a,span,b,li,td,th,label,button').forEach((el) => {
    if (!vis(el)) return;
    const s = getComputedStyle(el);
    if (el.scrollWidth > el.clientWidth + 2 && s.overflow !== 'visible' && s.textOverflow !== 'ellipsis' && !el.closest('.rail,.reel,.status,[style*="overflow"]')) add('clipped text', el);
    const r = el.getBoundingClientRect();
    if (r.right > innerWidth + 1 && !el.closest('.rail,.reel,.follow')) add('past viewport', el);
  });
  // contrast of text on its nearest solid background
  const rgb = (c) => (c.match(/[\d.]+/g) || []).map(Number);
  const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const bgOf = (el) => { for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e); const c = rgb(s.backgroundColor); if (s.backgroundImage !== 'none' && !e.matches('.card h3 a')) return null; if (c.length >= 3 && (c[3] === undefined || c[3] > 0.9)) return c; } return [255, 255, 255]; };
  const seen = new Set();
  document.querySelectorAll('p,span,a,li,time,h1,h2,h3,td,th,label,figcaption,b').forEach((el) => {
    if (!vis(el) || !el.childNodes.length || ![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) return;
    if (el.closest('.ph,.ptile .ph')) return;
    const s = getComputedStyle(el); const bg = bgOf(el); if (!bg) return;
    const fg = rgb(s.color); if (fg[3] !== undefined && fg[3] < 1) return;
    const L1 = lum(fg), L2 = lum(bg); const cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const big = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && +s.fontWeight >= 700);
    if (cr < (big ? 3 : 4.5)) { const k = s.color + '/' + bg.join(','); if (!seen.has(k)) { seen.add(k); add('contrast ' + cr.toFixed(2), el, s.color + ' on rgb(' + bg.join(',') + ')'); } }
  });
  const ids = {}; document.querySelectorAll('[id]').forEach((e) => { ids[e.id] = (ids[e.id] || 0) + 1; });
  Object.entries(ids).filter(([, n]) => n > 1).forEach(([k]) => out.issues.push('duplicate id ' + k));
  return JSON.stringify(out);
};

try {
  let t; for (let k = 0; k < 50 && !t; k++) { try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    if (m.method === 'Runtime.exceptionThrown') errs.push('EXC ' + m.params.exceptionDetails.exception?.description?.split('\n')[0]);
    if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value).join(' '));
    if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url); });
  await send('Runtime.enable'); await send('Network.enable'); await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: 860, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('sp-on','1')}catch(e){}" });
  for (const p of pages) {
    errs = [];
    await send('Page.navigate', { url: base + p }); await sleep(1600);
    const H = (await send('Runtime.evaluate', { expression: 'document.documentElement.scrollHeight', returnByValue: true })).result.value;
    for (let y = 0; y < H; y += 700) { await send('Runtime.evaluate', { expression: `scrollTo(0,${y})` }); await sleep(50); }
    await sleep(900);
    const r = JSON.parse((await send('Runtime.evaluate', { expression: `(${PROBE})()`, returnByValue: true })).result.value);
    const iss = [...new Set(r.issues)];
    console.log(`# ${p} @${w}: overflow ${r.overflow}, ${iss.length} issues${errs.length ? ', ' + errs.length + ' console' : ''}`);
    iss.slice(0, 14).forEach((x) => console.log('  - ' + x));
    errs.forEach((x) => console.log('  ! ' + x));
  }
} finally { try { ws.close(); } catch {} proc.kill(); }
