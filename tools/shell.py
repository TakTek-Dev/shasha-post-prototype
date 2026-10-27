"""The page shell every built page shares: head, status bar, masthead, footer, loader, marks.

Imported by build.py (home) and pages.py (everything else). C.R is the path back to the site
root: '' at the root, '../' inside story/, the absolute site path on the 404 page.
"""
import datetime as dt
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '6'                                       # bump on any asset change (Chrome caches hard)
SITE = 'Shasha Post'
BASE_URL = 'https://taktek-dev.github.io/shasha-post-prototype/'
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))
PH = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8'))
DIM_P = os.path.join(ROOT, 'tools', 'out', 'photos.json')
DIM = json.load(open(DIM_P, encoding='utf-8')) if os.path.exists(DIM_P) else {}
esc = html.escape
D = dt.date.fromisoformat
TODAY = D(E['date'])
NOW = E['now']                                 # the edition's "now", ISO with offset
S = E['stories']
BY = {s['id']: s for s in S}


class Ctx:
    R = ''


C = Ctx()

SECTIONS = [  # slug, nav label, page title, standfirst
    ('palestine', 'Palestine', 'Palestine', 'The West Bank, Gaza and Jerusalem: what happened today, who said it, and where it leaves people.'),
    ('region', 'Region', 'The region', 'Israel, Jordan, Lebanon, Syria, Egypt and the Gulf, read from Palestine.'),
    ('world', 'World', 'World', 'The rest of the world’s news, and the parts of it that reach home.'),
    ('culture', 'Culture', 'Culture', 'Film, music, books and art by Palestinians, and where to see and hear them.'),
    ('sport', 'Sport', 'Sport', 'The national teams, the clubs, the athletes, and the games everyone is watching.'),
    ('tech', 'Tech', 'Tech', 'Startups, networks and platforms: who builds what, who gets cut off, who gets moderated.'),
]
SEC = {s[0]: s for s in SECTIONS}


def day(d, year=False, wd=False):
    d = D(d) if isinstance(d, str) else d
    s = f"{d.day} {d.strftime('%b')}" + (f" {d.year}" if year else '')
    return (d.strftime('%a') + ' ' + s) if wd else s


def long_day(d):
    d = D(d) if isinstance(d, str) else d
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B')} {d.year}"


def stamp(s):
    """ISO date-time of a story's posting on this edition (Jerusalem time)."""
    return f"{s['date']}T{s.get('time', '08:00')}:00+02:00"


def when(s, rel=False):
    """A story's time as printed: today's show the clock (and count up in JS), older ones the day."""
    if s['date'] == E['date']:
        r = ' data-rel' if rel else ''
        return f'<time datetime="{stamp(s)}"{r}>{s.get("time", "")}</time>'
    return f'<time datetime="{stamp(s)}">{day(s["date"])}</time>'


# ---------------------------------------------------------------- icons and marks
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="i-right" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-search" viewBox="0 0 16 16"><path d="M7 2.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zM10.4 10.4 14 14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-out" viewBox="0 0 16 16"><path d="M6 3.5H3.5v9h9V10M9 3h4v4M13 3 7.5 8.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-menu" viewBox="0 0 16 16"><path d="M2.5 5h11M2.5 11h11" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-moon" viewBox="0 0 16 16"><path d="M13.2 10.1A5.6 5.6 0 0 1 5.9 2.8a5.6 5.6 0 1 0 7.3 7.3z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></symbol>
<symbol id="i-sun" viewBox="0 0 16 16"><circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 1.5v1.6M8 12.9v1.6M1.5 8h1.6M12.9 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></symbol>
<symbol id="i-link" viewBox="0 0 16 16"><path d="M6.8 9.2a2.8 2.8 0 0 0 4 0l2-2a2.8 2.8 0 0 0-4-4l-.7.7M9.2 6.8a2.8 2.8 0 0 0-4 0l-2 2a2.8 2.8 0 0 0 4 4l.7-.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></symbol>
</defs></svg>'''


def icon(name, cls='ic'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


def dots(typing=False, read=False):
    c = 'dots' + (' typing' if typing else '') + (' read' if read else '')
    return f'<span class="{c}" aria-hidden="true"><i></i><i></i><i></i></span>'


def f2(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def glyph_svg(tile='var(--tile)', teeth='#fff', dot='var(--signal)', cls='mk', label=None):
    m = MARKS
    a = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true"'
    ds = ''.join(f'<circle cx="{x}" cy="{y}" r="{m["dotR"]}"/>' for x, y in m['dots'])
    t = f'<path d="{m["tile"]}" fill="{tile}"/>' if tile else ''
    return (f'<svg class="{cls}" viewBox="0 0 100 100" {a}>{t}<path d="{m["comb"]}" fill="none" stroke="{teeth}" '
            f'stroke-width="{m["combW"]}" stroke-linecap="round" stroke-linejoin="round"/><g fill="{dot}">{ds}</g></svg>')


def wordmark(label=SITE):
    w, m = MARKS['wordmark'], MARKS
    x, y, s = w['tile']
    k = s / 100
    ds = ''.join(f'<circle cx="{x + cx * k:.2f}" cy="{y + cy * k:.2f}" r="{m["dotR"] * k:.2f}"/>' for cx, cy in m['dots'])
    return (f'<svg viewBox="0 0 {w["w"]} {w["h"]}" role="img" aria-label="{esc(label)}">'
            f'<g class="w-tile" transform="translate({x} {y}) scale({k:.4f})"><path d="{m["tile"]}" fill="var(--tile)"/>'
            f'<path d="{m["comb"]}" fill="none" stroke="#fff" stroke-width="{m["combW"]}" stroke-linecap="round" stroke-linejoin="round"/></g>'
            f'<g fill="var(--signal)">{ds}</g>'
            f'<path class="t-shasha" d="{w["shasha"]}"/><path class="t-post" d="{w["post"]}"/></svg>')


# ---------------------------------------------------------------- photographs
def photo(slug, sizes='100vw', cls='ph r1610', eager=False, on=True):
    if not slug or slug not in PH:
        return ''
    p = PH[slug]
    dm = DIM.get(slug, {'w': 1200, 'h': 800})
    pos = f' style="object-position:{p["focus"]}"' if p.get('focus') else ''
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = cls + (' on' if on and not eager else '') + ' sq'
    return (f'<div class="{c}"><img src="{C.R}assets/img/photo/{slug}.webp?v={V}" width="{dm["w"]}" height="{dm["h"]}" '
            f'alt="{esc(p["alt"])}" sizes="{sizes}" {load}{pos}></div>')


def plate(cls='ph r1610'):
    return f'<div class="{cls} plate sq">{glyph_svg(tile=None, teeth="#3A4260", dot="var(--signal)")}</div>'


def caption(slug):
    p = PH[slug]
    return f'<figcaption>{esc(p["caption"])} Photo: {esc(p["author"])}, {esc(p["license"])}, via Wikimedia Commons.</figcaption>'


def fig(slug, cls='ph r169', **kw):
    img = photo(slug, cls=cls, **kw)
    return f'<figure>{img}{caption(slug)}</figure>' if img else ''


def link(sid):
    return f'{C.R}story/{sid}.html'


def kick(s):
    sl, label = s['section'], SEC[s['section']][1]
    return f'<a class="kick" href="{C.R}{sl}.html">{esc(label)}</a>'


def card(s, kind='', img=True, sf=True, sizes='(min-width:1000px) 30vw, 100vw', ratio='r1610'):
    """One story. kind: '' (photo on top), 'big', 'row' (thumbnail at the side)."""
    ph = ''
    if img:
        if kind == 'row':
            ph = photo(s.get('photo'), sizes='150px', cls='ph r11')
        else:
            ph = photo(s.get('photo'), sizes=sizes, cls=f'ph {ratio}') or plate(f'ph {ratio}')
    live = f'<span class="new" style="display:inline-flex;gap:7px;align-items:center;font-weight:700">{dots(True)}Live</span>' if s.get('live') else ''
    meta = f'<p class="meta">{kick(s)}{live}<span>{when(s)}</span><span>{esc(s["place"])}</span></p>'
    st = f'<p class="sf">{esc(s["standfirst"])}</p>' if sf else ''
    cls = 'card' + (f' {kind}' if kind else '') + ' rise'
    if kind == 'row':
        return f'<article class="{cls}">{meta}<h3><a href="{link(s["id"])}">{esc(s["headline"])}</a></h3>{st}{ph}</article>'
    return f'<article class="{cls}">{ph}{meta}<h3><a href="{link(s["id"])}">{esc(s["headline"])}</a></h3>{st}</article>'


# ---------------------------------------------------------------- the shell
def head(title, desc, og=None, cls=''):
    t = esc(title if title == SITE else f'{title} · {SITE}')
    return f'''<!doctype html>
<html lang="en" data-now="{NOW}" data-root="{C.R}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0B0E1C">
<script>try{{var t=localStorage.getItem('sp-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}document.documentElement.classList.add('js')</script>
<link rel="icon" href="{C.R}favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="{C.R}assets/fonts/familjen.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{C.R}assets/fonts/faustina.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{C.R}assets/css/sp.css?v={V}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE_URL}{og or 'assets/og.png'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="noindex">
</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to the news</a>
{SPRITE}'''


def status():
    live = sorted((s for s in S if s.get('live')), key=lambda s: s['id'] != E.get('live', {}).get('story'))
    lv = (f'<a class="live" href="{C.R}live.html">{dots(True)}<span class="t">Live: {esc(E.get("live", {}).get("short") or live[0]["headline"])}</span></a>'
          if live else '')
    wx = ''
    if E.get('weather'):
        w = E['weather'][0]
        wx = f'<span class="wx">{esc(w["sky"])} <b>{round(w["hi"])}°</b> / {round(w["lo"])}°</span>'
    fx = ''
    if E.get('rates'):
        r = E['rates']
        fx = '<span class="fx">' + ' · '.join(f'{k} <b>₪{v:.2f}</b>' for k, v in r['values'].items()) + '</span>'
    return (f'<div class="status"><div class="wrap"><span><b>{long_day(TODAY)}</b></span>'
            f'<span class="clock">Jerusalem <b data-clock>{NOW[11:16]}</b></span>{wx}{fx}<span class="sp"></span>{lv}</div></div>')


def mast(current='', reading=False):
    lis = ''.join(f'<li><a href="{C.R}{s}.html"{" aria-current=\"page\"" if s == current else ""}>{esc(l)}</a></li>'
                  for s, l, *_ in SECTIONS)
    lis += f'<li><a href="{C.R}latest.html"{" aria-current=\"page\"" if current == "latest" else ""}>Latest</a></li>'
    lis += f'<li class="m-only"><a href="{C.R}newsletter.html">The Daily Post</a></li><li class="m-only"><a href="{C.R}live.html">Live</a></li>'
    rd = f'<span class="reading">{dots(read=True)}<span>Reading</span></span>' if reading else ''
    return f'''<header class="mast">
<div class="wrap">
<a class="brand" href="{C.R}home.html" aria-label="{SITE}, front page">{wordmark()}</a>
<nav class="nav" id="nav" aria-label="Sections"><ul>{lis}</ul></nav>
<div class="tools">{rd}<a class="btn icon" href="{C.R}search.html" aria-label="Search">{icon("i-search")}</a><button class="btn icon lights" type="button" aria-label="Switch to dark screen">{icon("i-moon", "ic moon")}{icon("i-sun", "ic sun")}</button><a class="btn solid sub-b" href="{C.R}newsletter.html">The Daily Post</a><button class="btn icon menu-b" type="button" aria-expanded="false" aria-controls="nav" aria-label="Sections">{icon("i-menu")}</button></div>
</div>
</header>'''


def loader():
    m = MARKS
    ds = ''.join(f'<circle class="l-dot" cx="{x}" cy="{y}" r="{m["dotR"]}" fill="var(--signal)"/>' for x, y in m['dots'])
    n = NOW[11:16]
    return (f'<div class="ldr" aria-hidden="true" data-typing=\'{json.dumps(m["typing"])}\' data-posted=\'{json.dumps(m["dots"])}\'>'
            f'<div class="scan"></div><div class="tile"><svg viewBox="0 0 100 100">'
            f'<path class="l-tile" d="{m["tile"]}" fill="var(--tile)"/>'
            f'<path class="l-comb" d="{m["comb"]}" fill="none" stroke="#fff" stroke-width="{m["combW"]}" stroke-linecap="round" stroke-linejoin="round"/>{ds}'
            f'</svg></div><p>Posted <b>{day(TODAY, year=True)}, {n}</b> · Jerusalem</p></div>')


def daily(compact=False):
    return f'''<div class="daily sq">
<div><h2>The Daily Post</h2><p>One email at 7 in the morning, Jerusalem time: the day’s stories from Palestine, in the order they matter.</p></div>
<form class="sub" action="#" method="post" data-proto novalidate><label for="em-{'c' if compact else 'm'}">Email address</label><input id="em-{'c' if compact else 'm'}" name="email" type="email" placeholder="you@example.com" autocomplete="email" required><button type="submit">Subscribe</button><p class="msg" role="status"></p><p class="fine">Prototype form: nothing is stored or sent.</p></form>
</div>'''


def foot():
    secs = ''.join(f'<li><a href="{C.R}{s}.html">{esc(l)}</a></li>' for s, l, *_ in SECTIONS)
    return f'''<footer class="foot">
<div class="wrap cols">
<div><a class="brand" href="{C.R}home.html" aria-label="{SITE}, front page">{wordmark()}</a>
<p class="tag">The English edition of <span lang="ar">شاشة</span>, Shasha: news from Palestine for readers everywhere, each story with its source.</p></div>
<div><p class="lbl">Sections</p><ul>{secs}</ul></div>
<div><p class="lbl">Shasha Post</p><ul><li><a href="{C.R}latest.html">Latest, by day</a></li><li><a href="{C.R}live.html">Live</a></li><li><a href="{C.R}search.html">Search</a></li><li><a href="{C.R}newsletter.html">The Daily Post</a></li></ul></div>
<div><p class="lbl">About</p><ul><li><a href="{C.R}about.html">About Shasha Post</a></li><li><a href="{C.R}about.html#standards">Sources and corrections</a></li><li><a href="{C.R}credits.html">Photo credits</a></li><li><a href="{C.R}index.html">Identity</a></li></ul></div>
</div>
<div class="bottom"><div class="wrap"><span>Design prototype by TakTek for Shasha. Stories are summaries of the linked reporting; no newsroom, readership or partners are implied.</span><span>Type: Familjen Grotesk and Faustina (OFL). Photos: Wikimedia Commons, <a href="{C.R}credits.html">credited</a>.</span></div></div>
</footer>'''


def page(title, desc, body, current='', with_loader=False, og=None, reading=False):
    return (head(title, desc, og=og, cls='story-page' if reading else '') + (loader() if with_loader else '') +
            ('<div class="readbar" aria-hidden="true"></div>' if reading else '') + status() + mast(current, reading) +
            f'<main id="main">{body}</main>' + foot() +
            f'<script src="{C.R}assets/js/sp.js?v={V}" defer></script>\n</body>\n</html>\n')


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
