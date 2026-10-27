/* Shasha Post: the screen switching on, the dots, the clock, and the small behaviours. */
(() => {
  const doc = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
    sget(k) { try { return sessionStorage.getItem(k); } catch { return null; } },
    sset(k, v) { try { sessionStorage.setItem(k, v); } catch {} },
  };

  // ---------------------------------------------------------------- lights (theme)
  const lights = $('.lights');
  if (lights) {
    const dark = () => doc.dataset.theme ? doc.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    const label = () => lights.setAttribute('aria-label', dark() ? 'Switch to light screen' : 'Switch to dark screen');
    label();
    lights.addEventListener('click', () => {
      doc.dataset.theme = dark() ? 'light' : 'dark';
      store.set('sp-theme', doc.dataset.theme);
      label();
    });
  }

  // ---------------------------------------------------------------- masthead: menu and the tight state
  const mast = $('.mast');
  const nav = $('#nav');
  const menu = $('.menu-b');
  if (menu && nav) {
    const close = () => { nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); };
    menu.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
    });
    addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) { close(); menu.focus(); } });
    let w = innerWidth;   // phones fire resize while scrolling (the address bar); only a width change closes it
    addEventListener('resize', () => { if (innerWidth !== w) { w = innerWidth; close(); } }, { passive: true });
    nav.addEventListener('click', e => { if (e.target.closest('a')) close(); });
  }
  if (mast) {
    let tight = false;
    const onScroll = () => {
      const t = scrollY > 90;
      if (t !== tight) { tight = t; mast.classList.toggle('tight', t); }
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---------------------------------------------------------------- the clock in the status bar (Jerusalem)
  const clock = $('[data-clock]');
  if (clock) {
    const fmt = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Jerusalem' });
    const tick = () => { clock.textContent = fmt.format(new Date()); };
    tick();
    setInterval(tick, 15000);
  }

  // ---------------------------------------------------------------- times: "12 min ago" on the day of the edition
  // Counted from the reader's clock; once a story is a day old (or the edition is ahead) it keeps its time.
  const now = Date.now();
  $$('time[data-rel]').forEach(t => {
    const d = Date.parse(t.getAttribute('datetime'));
    if (!d) return;
    const m = Math.round((now - d) / 60000);
    if (m < 0 || m > 60 * 20) return;
    t.textContent = m < 1 ? 'Now' : m < 60 ? `${m} min` : `${Math.round(m / 60)} h`;
    t.title = new Date(d).toLocaleString('en-GB', { timeZone: 'Asia/Jerusalem', dateStyle: 'medium', timeStyle: 'short' });
  });

  // ---------------------------------------------------------------- screens switch on as they arrive
  // A screen still clipped to its line has almost no area, so its parent is what gets watched.
  const io = 'IntersectionObserver' in window && !reduce ? new IntersectionObserver(es => {
    es.forEach(e => {
      if (!e.isIntersecting) return;
      const t = e.target;
      if (t.classList.contains('rise')) t.classList.add('in');
      $$(':scope > .on', t).forEach(el => el.classList.add('lit'));
      io.unobserve(t);
    });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0 }) : null;
  const watch = () => {
    if (!io) { $$('.on, .rise').forEach(el => el.classList.add('lit', 'in')); return; }
    new Set([...$$('.rise:not(.in)'), ...$$('.on:not(.lit)').map(el => el.parentElement)]).forEach(el => io.observe(el));
  };

  // ---------------------------------------------------------------- reading: the bar and the three dots fill
  const prose = $('.prose');
  if (prose) {
    const bar = $('.readbar');
    const dots = $$('.dots.read i');
    let raf = 0;
    const read = () => {
      raf = 0;
      const r = prose.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (innerHeight * 0.55 - r.top) / r.height));
      if (bar) bar.style.setProperty('--p', p.toFixed(4));
      dots.forEach((d, i) => d.classList.toggle('read', p >= (i + 1) / 3 - 0.001));
    };
    addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(read); }, { passive: true });
    read();
  }

  // ---------------------------------------------------------------- copy link
  $$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); b.lastChild.textContent = ' Link copied'; }
    catch { b.lastChild.textContent = ' Copy failed'; }
    setTimeout(() => { b.lastChild.textContent = ' Copy link'; }, 2200);
  }));

  // ---------------------------------------------------------------- the daily post (prototype: nothing is sent)
  $$('form[data-proto]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault();
    const em = f.querySelector('input[type=email]');
    const msg = f.querySelector('.msg');
    if (!em.checkValidity()) { msg.textContent = 'That address doesn’t look complete.'; em.focus(); return; }
    msg.innerHTML = '<span class="dots"><i></i><i></i><i></i></span> Noted. This is a prototype, so no email will be sent.';
    f.querySelector('button').disabled = true;
  }));

  // ---------------------------------------------------------------- contact (prototype): check the required fields, say so in words
  $$('form[data-proto-form]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault();
    const msg = f.querySelector('.msg');
    const bad = [...f.querySelectorAll('input,textarea,select')].filter(el => {
      const ok = el.checkValidity();
      el.setAttribute('aria-invalid', String(!ok));
      return !ok;
    });
    if (bad.length) {
      const name = (bad[0].labels && bad[0].labels[0] ? bad[0].labels[0].firstChild.textContent.trim() : 'that field');
      msg.textContent = 'Check ' + name.toLowerCase() + ' and try again.';
      bad[0].focus();
      return;
    }
    msg.innerHTML = '<span class="dots"><i></i><i></i><i></i></span> Thank you. This is a prototype, so nothing was sent.';
    f.querySelector('button[type=submit]').disabled = true;
  }));

  // ---------------------------------------------------------------- search (the whole edition is small enough to ship)
  const sb = $('#q');
  if (sb) {
    const out = $('.results .list');
    const count = $('.results .count');
    const R = doc.dataset.root || '';
    let idx = [];
    const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const hi = (s, ws) => ws.reduce((a, w) => a.replace(new RegExp(`(${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'), '<mark>$1</mark>'), esc(s));
    const run = () => {
      const q = sb.value.trim().toLowerCase();
      const ws = q.split(/\s+/).filter(w => w.length > 1);
      history.replaceState(null, '', q ? `?q=${encodeURIComponent(q)}` : location.pathname);
      if (!ws.length) { out.innerHTML = ''; count.textContent = `${idx.length} stories in this edition.`; return; }
      const hits = idx.map(s => {
        const hay = (s.h + ' ' + s.s + ' ' + s.p + ' ' + s.k).toLowerCase();
        const score = ws.reduce((n, w) => n + (hay.includes(w) ? 1 + (s.h.toLowerCase().includes(w) ? 2 : 0) : -99), 0);
        return [score, s];
      }).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]);
      count.textContent = hits.length ? `${hits.length} ${hits.length === 1 ? 'story' : 'stories'}` : 'Nothing in this edition matches. Try a place or a name.';
      out.innerHTML = hits.map(([, s]) => `<article class="card row">
        <p class="meta"><a class="kick" href="${R}${s.sec}.html">${esc(s.k)}</a><span>${esc(s.d)}</span><span>${esc(s.p)}</span></p>
        <h3><a href="${R}story/${s.id}.html">${hi(s.h, ws)}</a></h3>
        <p class="sf">${hi(s.s, ws)}</p>
        ${s.img ? `<div class="ph r11"><img src="${R}${s.img}" alt="" loading="lazy" width="150" height="150"></div>` : ''}</article>`).join('');
    };
    fetch(R + 'assets/data/search.json').then(r => r.json()).then(j => {
      idx = j;
      const q = new URLSearchParams(location.search).get('q');
      if (q) sb.value = q;
      run();
    });
    sb.addEventListener('input', run);
    $$('.sugg button').forEach(b => b.addEventListener('click', () => { sb.value = b.textContent; run(); sb.focus(); }));
    $('.searchbox')?.addEventListener('submit', e => { e.preventDefault(); run(); });
  }

  // ---------------------------------------------------------------- page to page: the screen closes to a line, the next one opens from it
  const pt = $('.pt');
  if (pt && !reduce) {
    document.addEventListener('click', e => {
      const a = e.target.closest('a[href]');
      if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if ((a.target && a.target !== '_self') || a.hasAttribute('download')) return;
      const u = new URL(a.href, location.href);
      if (u.origin !== location.origin || !/(\.html|\/)$/.test(u.pathname)) return;   // other sites, files
      if (u.pathname === location.pathname && u.search === location.search) return;      // same page, an anchor
      e.preventDefault();
      store.sset('sp-nav', '1');
      doc.classList.add('leaving');
      setTimeout(() => { location.href = u.href; }, 280);
    });
    // back and forward restore the page as it was left: open the screen again
    addEventListener('pageshow', e => { if (e.persisted) doc.classList.remove('leaving', 'arriving', 'open'); });
    if (doc.classList.contains('arriving')) {
      const open = () => {
        doc.classList.add('open');
        setTimeout(() => doc.classList.remove('arriving', 'open'), 700);
      };
      Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 450))]).then(() => requestAnimationFrame(open));
    }
  }

  // ---------------------------------------------------------------- the loader: the screen switches on, the first post arrives
  const ldr = $('.ldr');
  const force = new URLSearchParams(location.search).has('loader');
  const done = () => { ldr && ldr.classList.add('gone'); doc.classList.remove('loading'); watch(); };
  if (!ldr) { watch(); return; }
  if ((store.sget('sp-on') && !force) || reduce || !ldr.animate) { done(); return; }
  store.sset('sp-on', '1');
  setTimeout(done, 6000);   // never hold the page behind the screen (a background tab pauses animations)

  const tile = $('.l-tile', ldr), comb = $('.l-comb', ldr), dts = $$('.l-dot', ldr);
  const scan = $('.scan', ldr), cap = $('p', ldr), box = $('.tile', ldr);
  const typing = JSON.parse(ldr.dataset.typing), posted = JSON.parse(ldr.dataset.posted);
  const len = comb.getTotalLength();
  comb.style.strokeDasharray = len;
  comb.style.strokeDashoffset = len;
  tile.style.transformOrigin = '50px 50px';
  tile.style.transform = 'scale(0.02, 0.02)';
  dts.forEach((d, i) => { d.setAttribute('cx', typing[i][0]); d.setAttribute('cy', typing[i][1]); d.style.opacity = 0; });

  const E = 'cubic-bezier(.2,.7,.2,1)';
  const at = (ms) => new Promise(r => setTimeout(r, ms));
  (async () => {
    // a line of light across the dark
    await scan.animate([{ transform: 'scaleX(0)', opacity: 1 }, { transform: 'scaleX(1)', opacity: 1 }], { duration: 300, easing: E, fill: 'forwards' }).finished;
    // the line opens into the screen
    scan.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 260, fill: 'forwards' });
    await tile.animate([{ transform: 'scale(1.6, 0.02)' }, { transform: 'scale(1, 1)' }], { duration: 420, easing: 'cubic-bezier(.3,1.25,.5,1)', fill: 'forwards' }).finished;
    // three dots: someone is writing
    dts.forEach((d, i) => d.animate([{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], { duration: 200, delay: i * 70, fill: 'forwards', easing: E }));
    await at(300);
    for (let k = 0; k < 2; k++) {
      dts.forEach((d, i) => d.animate([{ transform: 'none' }, { transform: 'translateY(-5px)' }, { transform: 'none' }], { duration: 320, delay: i * 90, easing: E }));
      await at(470);
    }
    // posted: the dots settle over the teeth, and the teeth are written
    comb.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { duration: 460, easing: 'cubic-bezier(.6,0,.3,1)', fill: 'forwards' });
    dts.forEach((d, i) => {
      const dx = posted[i][0] - typing[i][0], dy = posted[i][1] - typing[i][1];
      d.animate([{ transform: 'none' }, { transform: `translate(${dx}px, ${dy}px)` }], { duration: 480, delay: 60 + i * 50, easing: 'cubic-bezier(.34,1.5,.64,1)', fill: 'forwards' });
    });
    cap.animate([{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], { duration: 360, delay: 200, fill: 'forwards', easing: E });
    await at(820);
    // the screen takes its place in the masthead
    const target = $('.mast .brand .w-tile');
    const from = box.getBoundingClientRect();
    if (target) {
      const to = target.getBoundingClientRect();
      const s = to.width / from.width;
      const x = to.left + to.width / 2 - (from.left + from.width / 2);
      const y = to.top + to.height / 2 - (from.top + from.height / 2);
      cap.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 160, fill: 'forwards' });
      box.animate([{ transform: 'none' }, { transform: `translate(${x}px, ${y}px) scale(${s})` }], { duration: 560, easing: 'cubic-bezier(.7,0,.2,1)', fill: 'forwards' });
      ldr.animate([{ backgroundColor: getComputedStyle(ldr).backgroundColor }, { backgroundColor: 'rgba(0,0,0,0)' }], { duration: 420, delay: 160, fill: 'forwards' });
      await at(560);
    } else {
      await ldr.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 300, fill: 'forwards' }).finished;
    }
    done();
  })();
})();
