"""Every page but the front: stories, sections, latest, live, search, the Daily Post, about, credits, 404.

python -I tools/pages.py
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir

import re

import shell as sh
from shell import C, E, S, BY, SEC, SECTIONS, PH, esc, card, photo, plate, fig, link, kick, when, dots, icon, day, long_day
from build import newest, of

SITE = sh.SITE


def words(s):
    return sum(len(p.split()) for p in s['body'])


def crumbs(*parts):
    out = [f'<a href="{C.R}home.html">Front page</a>']
    for label, url in parts:
        out.append('<span aria-hidden="true">/</span>' + (f'<a href="{url}">{esc(label)}</a>' if url else f'<span>{esc(label)}</span>'))
    return f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(out)}</nav>'


def chips(current):
    a = ''.join(f'<a href="{C.R}{s}.html"{" aria-current=\"page\"" if s == current else ""}>{esc(l)}</a>' for s, l, *_ in SECTIONS)
    return f'<nav class="chips" aria-label="Sections">{a}</nav>'


# ---------------------------------------------------------------- stories
def story(s):
    C.R = '../'
    sec = s['section']
    paras = [f'<p>{esc(p)}</p>' for p in s['body']]
    q = s.get('quote')
    if q and q.get('text'):
        bq = f'<blockquote><p>“{esc(q["text"].strip("“”\""))}”</p><cite>{esc(q.get("who", ""))}</cite></blockquote>'
        paras.insert(min(2, len(paras)), bq)
    paras[-1] = paras[-1].replace('</p>', f'<span class="end" title="End of post">{dots()}</span></p>')
    srcs = ''.join(f'<li><a href="{esc(x["url"])}" rel="noopener" target="_blank">{esc(x["name"])}</a>'
                   f'<span class="d">{day(x["date"]) if x.get("date") else ""}</span></li>' for x in s['sources'])
    mins = max(1, round(words(s) / 230))
    live = f'<span class="new" style="display:inline-flex;gap:7px;align-items:center;font:700 13.5px var(--sans)">{dots(True)}Live</span>' if s.get('live') else ''
    posted = f'Posted {day(s["date"], year=True)}' + (f', {s["time"]}' if s.get('time') else '')
    leadfig = f'<div class="lead-fig">{fig(s["photo"], cls="ph r169", eager=True, sizes="(min-width:1320px) 1260px, 100vw")}</div>' if s.get('photo') in PH else ''
    more = [x for x in of(sec) if x['id'] != s['id']][:4]
    just = [x for x in newest(S) if x['id'] != s['id'] and x['section'] != sec][:4]
    body = f'''<article class="story">
<div class="wrap">
<header class="story-h">
<p class="meta">{kick(s)}{live}<span>{esc(s["place"])}</span></p>
<h1>{esc(s["headline"])}</h1>
<p class="sf">{esc(s["standfirst"])}</p>
<p class="meta"><span>{posted}</span><span class="dot"></span><span>{mins} min read</span><span class="dot"></span><span>{len(s["sources"])} source{"s" if len(s["sources"]) != 1 else ""}</span></p>
</header>
{leadfig}
<div class="story-body">
<div>
<div class="prose">{"".join(paras)}</div>
<section class="srcs" aria-labelledby="src-h"><h2 id="src-h">Reported from</h2><ul>{srcs}</ul></section>
<div class="share"><button class="btn" type="button" data-copy>{icon("i-link")}<span> Copy link</span></button><a class="btn" href="{C.R}{sec}.html">More {esc(SEC[sec][1])} {icon("i-right")}</a></div>
</div>
<aside class="aside" aria-label="More stories">
<h2>{dots()}More from {esc(SEC[sec][2])}</h2>
<div class="stack">{"".join(card(x, "row", sf=False) for x in more)}</div>
<h2 style="margin-top:12px">{dots()}Just posted</h2>
<div class="stack">{"".join(card(x, "row", sf=False) for x in just)}</div>
</aside>
</div>
</div>
</article>
<section class="sec" style="border:0"><div class="wrap">{sh.daily(compact=True)}</div></section>'''
    og = f'assets/img/photo/{s["photo"]}.webp' if s.get('photo') in PH else None
    sh.write(f'story/{s["id"]}.html', sh.page(s['headline'], s['standfirst'], body, current=sec, reading=True, og=og))


# ---------------------------------------------------------------- sections
def by_day(stories):
    days = {}
    for s in stories:
        days.setdefault(s['date'], []).append(s)
    out = ''
    for d in sorted(days, reverse=True):
        n = len(days[d])
        label = 'Today' if d == E['date'] else long_day(d)
        out += (f'<section class="daygroup"><h2>{esc(label)}<span>{day(d, year=True) if d == E["date"] else ""} · {n} '
                f'{"story" if n == 1 else "stories"}</span></h2><div class="rows">{"".join(card(s, "row") for s in days[d])}</div></section>')
    return out


def section(slug):
    C.R = ''
    _, label, title, sf = SEC[slug]
    ss = of(slug)
    top = [s for s in ss if s.get('photo')][:1] or ss[:1]
    rest = [s for s in ss if s not in top]
    grid = rest[:3]
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs((title, None))}<h1>{esc(title)}</h1><p>{esc(sf)}</p>{chips(slug)}</header>
<div class="pal">{card(top[0], "big", sizes="(min-width:900px) 56vw, 100vw")}<div class="side">{"".join(card(s, "row") for s in grid)}</div></div>
<div style="margin-top:clamp(40px,5vw,64px)">{by_day(rest[3:]) if rest[3:] else ""}</div>
</div>'''
    sh.write(f'{slug}.html', sh.page(title, sf, body, current=slug))


def latest():
    C.R = ''
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Latest", None))}<h1>Latest</h1><p>Every story in this edition, newest first, {len(S)} in all from {day(min(s["date"] for s in S))} to {day(E["date"], year=True)}.</p>{chips("")}</header>
{by_day(newest(S))}
</div>'''
    sh.write('latest.html', sh.page('Latest', 'Every story in this edition of Shasha Post, newest first.', body, current='latest'))


def live():
    C.R = ''
    lv = [s for s in S if s.get('live')]
    L = E.get('live', {})
    ups = L.get('updates', [])
    lis = ''.join(f'<li><time>{esc(u["time"])}</time><div><p>{esc(u["text"])}</p>'
                  f'<p class="src">{esc(u.get("source", ""))}</p></div></li>' for u in ups)
    stories = ''.join(card(s, 'row') for s in lv)
    tl = f'<ol class="timeline">{lis}</ol>' if lis else '<p class="lbl">Updates will appear here as they are posted.</p>'
    h = esc(L.get('title') or (lv[0]['headline'] if lv else 'Live'))
    sf = esc(L.get('standfirst') or (lv[0]['standfirst'] if lv else 'Nothing is being followed live right now.'))
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Live", None))}<p class="kick new" style="color:var(--signal-ink)">{dots(True)} Live · {long_day(E["date"])}</p><h1 style="margin-top:12px;font-size:clamp(34px,5vw,64px)">{h}</h1><p>{sf}</p></header>
<div class="story-body" style="margin-top:0">
<div>{tl}</div>
<aside class="aside"><h2>{dots()}The stories</h2><div class="stack">{stories}</div></aside>
</div>
</div>'''
    sh.write('live.html', sh.page('Live', 'Followed live on Shasha Post today.', body, current='live'))


def search():
    C.R = ''
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Search", None))}<h1>Search</h1><p>Search every story in this edition by place, name or subject.</p>
<form class="searchbox" role="search" action="search.html"><label class="vh" for="q">Search Shasha Post</label><input id="q" name="q" type="search" placeholder="Try Jenin, olive harvest, Knesset" autocomplete="off"><button class="btn solid" type="submit" style="height:56px;padding:0 22px">Search</button></form></header>
<section class="results" aria-live="polite"><p class="count"></p><div class="rows list"></div></section>
</div>'''
    sh.write('search.html', sh.page('Search', 'Search Shasha Post.', body, current='search'))


def newsletter():
    C.R = ''
    sample = newest([s for s in S if s['date'] == E['date']])[:5] or newest(S)[:5]
    lis = ''.join(f'<li><a href="{link(s["id"])}">{esc(s["headline"])}</a></li>' for s in sample)
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("The Daily Post", None))}<h1>The Daily Post</h1><p>One email, every morning at 7, Jerusalem time. The day’s stories from Palestine in the order they matter, each with the link to who reported it first.</p></header>
{sh.daily()}
<div class="doc"><h2>What this morning’s would have carried</h2><ul>{lis}</ul>
<h2>What it is not</h2><p>No ads between the stories, no tracking pixels, no “breaking” in the subject line unless something has broken. One email; you can leave with one click.</p></div>
</div>'''
    sh.write('newsletter.html', sh.page('The Daily Post', 'The Daily Post: Shasha Post’s morning email.', body, current='newsletter'))


def about():
    C.R = ''
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("About", None))}<h1>About</h1><p>Shasha Post is the English edition of <span lang="ar">شاشة</span>, Shasha, a Palestinian news site. Shasha is Arabic for a screen.</p></header>
<div class="doc">
<h2>The screen and the three dots</h2>
<p>The mark is the first letter of <span lang="ar">شاشة</span>, <span lang="ar">ش</span>, the sound “sh”: three rounded teeth and the three dots that sit over them, drawn inside a screen. Three dots are also what a screen shows while someone is writing to you, and the site uses them that way. Dots in a row, moving, mean a story is still being written; settled into the letter, a story is posted.</p>
<p>The <a href="{C.R}index.html">identity book</a> sets out the mark, the type, the colours and the rules.</p>
<h2 id="standards">Sources and corrections</h2>
<ul><li>Every story names who reported it and links there. A story summarises that reporting in our own words; claims are attributed to the people and bodies that made them.</li>
<li>Photographs show the place, the person or the thing the story is about, and are captioned with what they are, where and when. Where no honest photograph exists, the story runs without one.</li>
<li>No photographs of the dead or the wounded.</li>
<li>Times on this prototype are the posting times of this edition, in Jerusalem time.</li>
<li>A correction is made in the story and said at the foot of it.</li></ul>
<h2>This prototype</h2>
<p>This is a design prototype by TakTek. It is built from real, linked reporting from {day(min(s["date"] for s in S))} to {day(E["date"], year=True)}, but it is not a live newsroom: no staff, readership, partners or subscribers are implied, and the forms send nothing.</p>
</div>
</div>'''
    sh.write('about.html', sh.page('About', 'About Shasha Post, the English edition of Shasha.', body, current='about'))


def credits():
    C.R = ''
    used = {}
    for s in S:
        if s.get('photo') in PH:
            used.setdefault(s['photo'], []).append(s)
    rows = ''
    for slug, p in PH.items():
        file = p['file'].replace('File:', '')
        url = 'https://commons.wikimedia.org/wiki/File:' + file.replace(' ', '_')
        ss = used.get(slug, [])
        st = ', '.join(f'<a href="{link(s["id"])}">{esc(s["headline"])}</a>' for s in ss) or 'Not used on a story'
        rows += (f'<tr><td><img src="assets/img/photo/{slug}.webp?v={sh.V}" alt="" loading="lazy" width="84" height="56"></td>'
                 f'<td><a href="{url}" rel="noopener" target="_blank">{esc(p["caption"])}</a></td><td>{esc(p["author"])}</td>'
                 f'<td>{esc(p["license"])}</td><td class="hide-s">{st}</td></tr>')
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Photo credits", None))}<h1>Photo credits</h1><p>Every photograph on Shasha Post is freely licensed on Wikimedia Commons and shown in its own colour. Each one links to its file page.</p></header>
<div style="overflow-x:auto"><table class="credits-t"><thead><tr><th><span class="vh">Photo</span></th><th>Subject</th><th>Author</th><th>Licence</th><th class="hide-s">Used on</th></tr></thead><tbody>{rows}</tbody></table></div>
</div>'''
    sh.write('credits.html', sh.page('Photo credits', 'Credits for the photographs on Shasha Post.', body, current='credits'))


def lost():
    C.R = '/shasha-post-prototype/'
    m = sh.MARKS
    ds = ''.join(f'<circle cx="{x}" cy="{y}" r="{m["dotR"]}"/>' for x, y in m['typing'])
    scr = (f'<svg class="scr" viewBox="0 0 100 100" aria-hidden="true"><path d="{m["tile"]}" fill="var(--screen)"/>'
           f'<g fill="var(--signal)">{ds}</g></svg>')
    body = f'''<div class="wrap lost">{scr}<h1>This screen is blank.</h1><p>The page you asked for isn’t here: the link may be old, or the address mistyped.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn solid" href="{C.R}home.html">Front page</a><a class="btn" href="{C.R}search.html">Search</a><a class="btn" href="{C.R}latest.html">Latest</a></div></div>'''
    sh.write('404.html', sh.page('Not found', 'Page not found.', body))


def main():
    for s in S:
        story(s)
    for slug, *_ in SECTIONS:
        section(slug)
    latest()
    live()
    search()
    newsletter()
    about()
    credits()
    lost()
    print(len(S), 'stories,', len(SECTIONS), 'sections, 8 more pages')


if __name__ == '__main__':
    main()
