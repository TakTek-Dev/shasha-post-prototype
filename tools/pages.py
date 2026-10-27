"""Every page but the front: stories, sections, topics, places, latest, today, live, search, the Daily Post,
about, standards, contact, privacy, credits, site map, 404.

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
KIND = {'analysis': 'Analysis', 'feature': 'Feature', 'brief': 'In brief'}


def share(s):
    from urllib.parse import quote
    u = quote(sh.BASE_URL + f'story/{s["id"]}.html', safe='')
    t = quote(s['headline'], safe='')
    out = [f'<button class="btn" type="button" data-copy>{icon("i-link")}<span> Copy link</span></button>',
           f'<a class="btn" href="https://x.com/intent/post?text={t}&amp;url={u}" target="_blank" rel="noopener">X</a>',
           f'<a class="btn" href="https://wa.me/?text={t}%20{u}" target="_blank" rel="noopener">WhatsApp</a>',
           f'<a class="btn" href="https://t.me/share/url?url={u}&amp;text={t}" target="_blank" rel="noopener">Telegram</a>',
           f'<a class="btn" href="mailto:?subject={t}&amp;body={u}">{icon("i-mail")}<span> Email</span></a>']
    return f'<div class="share" role="group" aria-label="Share this story">{"".join(out)}</div>'


def ld(s):
    """NewsArticle structured data; isBasedOn carries the reporting the story summarises."""
    import json
    d = {'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': s['headline'], 'description': s['standfirst'],
         'datePublished': sh.stamp(s), 'dateModified': sh.stamp(s), 'inLanguage': 'en',
         'articleSection': SEC[s['section']][2], 'contentLocation': {'@type': 'Place', 'name': s['place']},
         'mainEntityOfPage': sh.BASE_URL + f'story/{s["id"]}.html',
         'publisher': {'@type': 'NewsMediaOrganization', 'name': SITE,
                       'logo': {'@type': 'ImageObject', 'url': sh.BASE_URL + 'assets/brand/mark.svg'}},
         'isBasedOn': [x['url'] for x in s['sources']]}
    if s.get('photo') in PH:
        d['image'] = sh.BASE_URL + f'assets/img/photo/{s["photo"]}.webp'
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def follow_box(s):
    """Each topic the story belongs to, with the rest of that topic's stories, newest first."""
    out = ''
    for t in sh.topics_of(s['id']):
        rest = sorted((BY[i] for i in t['ids'] if i != s['id']), key=sh.stamp, reverse=True)[:4]
        lis = ''.join(f'<li><time datetime="{sh.stamp(x)}">{day(x["date"])}</time><a href="{link(x["id"])}">{esc(x["headline"])}</a></li>'
                      for x in rest)
        out += (f'<section class="followbox sq" aria-label="Following: {esc(t["title"])}"><p class="lbl">{dots(True)}Following</p>'
                f'<h2><a href="{C.R}topic/{t["slug"]}.html">{esc(t["title"])}</a></h2><ol>{lis}</ol>'
                f'<a class="more" href="{C.R}topic/{t["slug"]}.html">All {len(t["ids"])} stories {icon("i-right")}</a></section>')
    return out


def neighbours(s):
    """The older and newer story in the same section."""
    ss = sorted(of(s['section']), key=sh.stamp)
    k = ss.index(s)
    older = ss[k - 1] if k > 0 else None
    newer = ss[k + 1] if k + 1 < len(ss) else None
    label = SEC[s['section']][1]

    def a(x, text, cls, ic):
        if not x:
            return '<span></span>'
        return f'<a class="nb {cls}" href="{link(x["id"])}"><span class="lbl">{ic}{text}</span><b>{esc(x["headline"])}</b></a>'
    return (f'<nav class="nbs" aria-label="More in {esc(SEC[s["section"]][2])}">'
            f'{a(older, "Older in " + label, "o", icon("i-left"))}{a(newer, "Newer in " + label, "n", "")}</nav>')


def story(s):
    C.R = '../'
    sec = s['section']
    paras = [f'<p>{esc(p)}</p>' for p in s['body']]
    q = s.get('quote')
    if q and q.get('text'):
        bq = f'<blockquote><p>“{esc(q["text"].strip(chr(8220) + chr(8221) + chr(34)))}”</p><cite>{esc(q.get("who", ""))}</cite></blockquote>'
        paras.insert(min(2, len(paras)), bq)
    paras[-1] = paras[-1].replace('</p>', f'<span class="end" title="End of post">{dots()}</span></p>')
    srcs = ''.join(f'<li><a href="{esc(x["url"])}" rel="noopener" target="_blank">{esc(x["name"])}{icon("i-out")}</a>'
                   f'<span class="d">{day(x["date"]) if x.get("date") else ""}</span></li>' for x in s['sources'])
    mins = max(1, round(words(s) / 230))
    live = (f'<span class="new" style="display:inline-flex;gap:7px;align-items:center;font:700 13.5px var(--sans)">{dots(True)}Live</span>'
            if s.get('live') else '')
    kind = f'<span class="kind">{KIND[s["kind"]]}</span>' if s.get('kind') in KIND else ''
    posted = f'Posted {day(s["date"], year=True)}' + (f', {s["time"]}' if s.get('time') else '')
    leadfig = (f'<div class="lead-fig">{fig(s["photo"], cls="ph r169", eager=True, sizes="(min-width:1320px) 1260px, 100vw")}</div>'
               if s.get('photo') in PH else '')
    pl = sh.place_of(s['id'])
    where = (f'<a class="pl" href="{C.R}place/{pl["slug"]}.html">{icon("i-pin")}{esc(s["place"])}</a>' if pl
             else f'<span class="pl">{icon("i-pin")}{esc(s["place"])}</span>')
    tags = [f'<a href="{C.R}{sec}.html">{esc(SEC[sec][2])}</a>']
    tags += [f'<a href="{C.R}topic/{t["slug"]}.html">{esc(t["title"])}</a>' for t in sh.topics_of(s['id'])]
    if pl:
        tags.append(f'<a href="{C.R}place/{pl["slug"]}.html">{esc(pl["title"])}</a>')
    tagrow = f'<nav class="tags" aria-label="Filed under"><span class="lbl">Filed under</span>{"".join(tags)}</nav>'
    related = {i for t in sh.topics_of(s['id']) for i in t['ids']}
    more = [x for x in of(sec) if x['id'] != s['id'] and x['id'] not in related][:4]
    just = [x for x in newest(S) if x['id'] != s['id'] and x['section'] != sec and x['id'] not in related][:4]
    nsrc = len(s['sources'])
    body = f'''<article class="story">
<div class="wrap">
<header class="story-h">
{crumbs((SEC[sec][2], f"{C.R}{sec}.html"))}
<p class="meta">{kick(s)}{kind}{live}{where}</p>
<h1>{esc(s["headline"])}</h1>
<p class="sf">{esc(s["standfirst"])}</p>
<p class="meta"><span>{posted}</span><span class="dot"></span><span>{mins} min read</span><span class="dot"></span><a href="#src-h">{nsrc} source{"s" if nsrc != 1 else ""}</a></p>
</header>
{leadfig}
<div class="story-body">
<div>
<div class="prose">{"".join(paras)}</div>
<section class="srcs" aria-labelledby="src-h"><h2 id="src-h">Reported from</h2><ul>{srcs}</ul>
<p class="note">This story summarises the reporting above in Shasha Post’s own words. Spotted an error? <a href="{C.R}contact.html">Tell us</a>: corrections are made in the story and noted at its foot.</p></section>
{tagrow}
{share(s)}
{neighbours(s)}
</div>
<aside class="aside" aria-label="More stories">
{follow_box(s)}
<h2>{dots()}More from {esc(SEC[sec][2])}</h2>
<div class="stack">{"".join(card(x, "row", sf=False) for x in more)}</div>
<h2 style="margin-top:12px">{dots()}Just posted</h2>
<div class="stack">{"".join(card(x, "row", sf=False) for x in just)}</div>
</aside>
</div>
</div>
</article>
{ld(s)}
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
<h2 class="vh">Top stories in {esc(title)}</h2><div class="pal">{card(top[0], "big", sizes="(min-width:900px) 56vw, 100vw")}<div class="side">{"".join(card(s, "row") for s in grid)}</div></div>
<div style="margin-top:clamp(40px,5vw,64px)">{by_day(rest[3:]) if rest[3:] else ""}</div>
</div>'''
    sh.write(f'{slug}.html', sh.page(title, sf, sh.following() + body, current=slug))


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
<div class="sugg"><span class="lbl">Try</span>{"".join(f'<button type="button">{w}</button>' for w in ("Hebron", "olive harvest", "Knesset", "Gaza", "Ramallah", "Asian Cup", "UN"))}</div>
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
<p>Every story names and links the reporting it is built on; photographs show what the story is about; corrections are made in the story and noted. The full rules are on the <a href="{C.R}standards.html">standards page</a>.</p>
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


# ---------------------------------------------------------------- topics and places
def group_hero(g, kind_label, crumb):
    n = len(g['ids'])
    ss = sorted((BY[i] for i in g['ids']), key=sh.stamp)
    span = f'{day(ss[0]["date"])} – {day(ss[-1]["date"], year=True)}' if len(ss) > 1 else day(ss[0]['date'], year=True)
    ph = photo(g['photo'], cls='ph r21', sizes='(min-width:1320px) 1260px, 100vw', eager=True)
    cap = (f'<p class="gh-cap">{esc(PH[g["photo"]]["caption"])} Photo: {esc(PH[g["photo"]]["author"])}, '
           f'{esc(PH[g["photo"]]["license"])}.</p>') if g['photo'] in PH else ''
    return f'''<header class="gh">
<div class="wrap">{crumbs(*crumb)}</div>
<div class="wrap gh-in">
<div class="gh-t"><p class="kick">{dots(True) if kind_label == "Following" else icon("i-pin")}{kind_label}</p>
<h1>{esc(g["title"])}</h1><p class="sf">{esc(g["standfirst"])}</p>
<p class="meta"><span>{n} {"story" if n == 1 else "stories"}</span><span class="dot"></span><span>{span}</span></p></div>
<div class="gh-p">{ph}{cap}</div>
</div>
</header>'''


def thread(ids):
    """A topic's stories as a thread, newest first, each stamped with its day."""
    ss = sorted((BY[i] for i in ids), key=sh.stamp, reverse=True)
    lis = ''
    for s in ss:
        ph = photo(s.get('photo'), cls='ph r1610', sizes='(min-width:900px) 260px, 100vw')
        lis += (f'<li class="rise"><div class="th-d"><time datetime="{sh.stamp(s)}">{day(s["date"], wd=True)}</time>'
                f'<span>{esc(s.get("time", ""))}</span></div><article class="card th-c">'
                f'<p class="meta">{kick(s)}{sh.place_link(s)}</p><h3><a href="{link(s["id"])}">{esc(s["headline"])}</a></h3>'
                f'<p class="sf">{esc(s["standfirst"])}</p></article>{ph}</li>')
    return f'<h2 class="vh">Every story, newest first</h2><ol class="thread">{lis}</ol>'


def topic(t):
    C.R = '../'
    others = [x for x in sh.TOPICS if x is not t]
    side = ''.join(f'<li><a href="{C.R}topic/{x["slug"]}.html">{esc(x["title"])}<span>{len(x["ids"])}</span></a></li>' for x in others)
    body = (group_hero(t, 'Following', (('Topics', f'{C.R}topics.html'), (t['title'], None))) +
            f'''<div class="wrap g-body"><div>{thread(t["ids"])}</div>
<aside class="aside"><h2>{dots(True)}Also following</h2><ul class="toplist">{side}</ul></aside></div>''')
    sh.write(f'topic/{t["slug"]}.html', sh.page(t['title'], t['standfirst'], body, current='topics',
                                                 og=f'assets/img/photo/{t["photo"]}.webp' if t['photo'] in PH else None))


def topics():
    C.R = ''
    cards = ''
    for t in sh.TOPICS:
        ss = sorted((BY[i] for i in t['ids']), key=sh.stamp, reverse=True)
        latest = ss[0]
        cards += (f'<article class="card tcard rise">{photo(t["photo"], cls="ph r1610", sizes="(min-width:1000px) 30vw, 100vw")}'
                  f'<p class="meta"><span class="new" style="display:inline-flex;gap:7px;align-items:center;font-weight:700">{dots(True)}Following</span>'
                  f'<span>{len(t["ids"])} stories</span><span>Latest {day(latest["date"])}</span></p>'
                  f'<h3><a href="topic/{t["slug"]}.html">{esc(t["title"])}</a></h3><p class="sf">{esc(t["standfirst"])}</p>'
                  f'<p class="latest">Latest: {esc(latest["headline"])}</p></article>')
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Topics", None))}<h1>Topics</h1><p>The stories we are following across sections. Each topic gathers every post on it in one thread, newest first.</p></header>
<h2 class="vh">Topics</h2><div class="grid g3">{cards}</div></div>'''
    sh.write('topics.html', sh.page('Topics', 'The stories Shasha Post is following.', body, current='topics'))


def place(p):
    C.R = '../'
    others = ''.join(f'<li><a href="{C.R}place/{x["slug"]}.html">{esc(x["title"])}<span>{len(x["ids"])}</span></a></li>'
                     for x in sh.PLACES if x is not p)
    body = (group_hero(p, 'Place', (('Places', f'{C.R}places.html'), (p['title'], None))) +
            f'''<div class="wrap g-body"><div>{thread(p["ids"])}</div>
<aside class="aside"><h2>{icon("i-pin")}Other places</h2><ul class="toplist">{others}</ul></aside></div>''')
    sh.write(f'place/{p["slug"]}.html', sh.page(p['title'], p['standfirst'], body, current='places',
                                                 og=f'assets/img/photo/{p["photo"]}.webp' if p['photo'] in PH else None))


def places():
    C.R = ''
    tiles = ''
    for p in sh.PLACES:
        n = len(p['ids'])
        tiles += (f'<a class="ptile rise" href="place/{p["slug"]}.html">{photo(p["photo"], cls="ph r43", sizes="(min-width:1000px) 30vw, 100vw")}'
                  f'<span class="pt-t"><b>{esc(p["title"])}</b><span>{n} {"story" if n == 1 else "stories"}</span></span></a>')
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Places", None))}<h1>Places</h1><p>The news by where it happened in Palestine. Stories from the region and the world stay in their sections.</p></header>
<div class="ptiles">{tiles}</div></div>'''
    sh.write('places.html', sh.page('Places', 'Shasha Post by place in Palestine.', body, current='places'))


# ---------------------------------------------------------------- today
def today():
    C.R = ''
    w = E.get('weather', [])
    rows = ''.join(f'<tr><th scope="row">{esc(x["city"])}</th><td>{esc(x["sky"])}</td><td class="n">{round(x["hi"])}°</td><td class="n">{round(x["lo"])}°</td></tr>' for x in w)
    wx = (f'''<section class="tbox sq" aria-labelledby="wx-h"><h2 id="wx-h">Weather</h2>
<table class="tt"><thead><tr><th scope="col">City</th><th scope="col">Sky</th><th scope="col" class="n">High</th><th scope="col" class="n">Low</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note">Forecast for {day(E["date"], year=True)} from Open-Meteo (model data). The Palestinian Meteorological Department expected showers and thunderstorms, with temperatures slightly below average.</p></section>''' if w else '')
    r = E.get('rates')
    fx = ''
    if r:
        rr = ''.join(f'<tr><th scope="row">{k}</th><td class="n">₪{v:.2f}</td></tr>' for k, v in r['values'].items())
        src = r.get('source') or {}
        fx = (f'''<section class="tbox sq" aria-labelledby="fx-h"><h2 id="fx-h">The shekel</h2>
<table class="tt"><thead><tr><th scope="col">Currency</th><th scope="col" class="n">In shekels</th></tr></thead><tbody>{rr}</tbody></table>
<p class="note">Rates for one unit on {day(E["date"], year=True)}, as published by <a href="{esc(src.get("url", "#"))}" rel="noopener" target="_blank">Shasha</a>.</p></section>''')
    L = E.get('live', {})
    poll = (f'''<section class="tbox sq" aria-labelledby="pl-h"><h2 id="pl-h">{dots(True)} {esc(L.get("title", ""))}</h2><p>{esc(L.get("standfirst", ""))}</p>
<a class="btn solid" href="live.html">Follow it live {icon("i-right")}</a></section>''' if L else '')
    td = sorted((s for s in S if s['date'] == E['date']), key=sh.stamp, reverse=True)
    lis = ''.join(f'<li>{when(s, rel=True)}<a href="{link(s["id"])}">{esc(s["headline"])}</a><span class="s">{esc(SEC[s["section"]][1])} · {esc(s["place"])}</span></li>' for s in td)
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Today", None))}<h1>Today</h1><p>{long_day(E["date"])}: the weather, the shekel, what is being followed live, and everything posted so far today.</p></header>
<div class="today">
<div class="tcol">{poll}{wx}{fx}</div>
<section class="stream sq" aria-labelledby="td-h"><h2 id="td-h">{dots()}Posted today · {len(td)}</h2><ol>{lis}</ol><a class="all" href="latest.html">Everything, by day</a></section>
</div></div>'''
    sh.write('today.html', sh.page('Today', f'{long_day(E["date"])} on Shasha Post.', body, current='today'))


# ---------------------------------------------------------------- contact, privacy, standards, site map
def contact():
    C.R = ''
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Contact", None))}<h1>Contact and tips</h1><p>Tell us about a story, send a correction, or ask a question.</p></header>
<div class="cgrid">
<form class="cform sq" action="#" method="post" data-proto-form novalidate>
<div class="f"><label for="c-k">What is it about?</label><select id="c-k" name="kind"><option>A story tip</option><option>A correction</option><option>A question</option><option>Something else</option></select></div>
<div class="f"><label for="c-n">Your name <span>(optional)</span></label><input id="c-n" name="name" autocomplete="name"></div>
<div class="f"><label for="c-e">Email address</label><input id="c-e" name="email" type="email" autocomplete="email" required aria-describedby="c-e-h"><p class="h" id="c-e-h">Only so we can reply.</p></div>
<div class="f"><label for="c-u">A link to the story <span>(optional)</span></label><input id="c-u" name="url" type="url" inputmode="url" placeholder="https://"></div>
<div class="f"><label for="c-m">Your message</label><textarea id="c-m" name="message" rows="6" required></textarea></div>
<div class="f-end"><button class="btn solid" type="submit">Send</button><p class="msg" role="status"></p></div>
<p class="fine">Prototype form: nothing is stored or sent.</p>
</form>
<div class="doc cside">
<h2 style="margin-top:0">Corrections</h2><p>Name the story and what is wrong, with a source if you have one. We correct the story itself and say so at its foot.</p>
<h2>Tips</h2><p>Say what you saw, where and when. If it is sensitive, do not send names or photos of people through a web form.</p>
<h2>Shasha in Arabic</h2><p>The Arabic site is at <a href="https://shasha.ps/" rel="noopener" target="_blank">shasha.ps</a>.</p>
</div></div></div>'''
    sh.write('contact.html', sh.page('Contact and tips', 'Contact Shasha Post, send a tip or a correction.', body, current='contact'))


def privacy():
    C.R = ''
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Privacy", None))}<h1>Privacy</h1><p>What this site keeps on your device, and what it does not.</p></header>
<div class="doc">
<h2 style="margin-top:0">Nothing leaves your browser</h2>
<p>Shasha Post sets no cookies, runs no analytics or advertising, and loads nothing from other servers: the type, the photographs and the scripts are all served from this site.</p>
<h2>What it remembers</h2>
<ul><li><b>Lights</b>: if you switch the screen to dark or light, that choice is kept in your browser’s local storage (<code>sp-theme</code>) so the next page opens the same way.</li>
<li><b>The opening screen</b>: once you have seen it, your browser remembers for this visit (<code>sp-on</code>, session storage) so it does not play on every page.</li>
<li><b>Between pages</b>: while a link is opening, a flag (<code>sp-nav</code>, session storage) tells the next page to open from the line. It is cleared as soon as that page loads.</li></ul>
<p>Session storage is emptied when you close the tab. You can clear local storage from your browser’s settings at any time.</p>
<h2>Forms</h2>
<p>The Daily Post and contact forms on this prototype send nothing anywhere. On the live site each form would say, next to it, what is kept and for how long.</p>
<h2>Links out</h2>
<p>Every story links to the reporting it is built on, and the share buttons open X, WhatsApp, Telegram or your email. Those sites have their own policies.</p>
</div></div>'''
    sh.write('privacy.html', sh.page('Privacy', 'What Shasha Post keeps on your device.', body, current='privacy'))


def standards():
    C.R = ''
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Standards", None))}<h1>Standards and corrections</h1><p>How a story gets onto this screen, and how it is put right.</p></header>
<div class="doc">
<h2 style="margin-top:0">Every story has a source</h2>
<ul><li>Each post names who reported it first and links there, under “Reported from”. A post summarises that reporting in our own words; it does not copy it.</li>
<li>Claims are attributed to whoever made them: a ministry, the army, a UN agency, a witness. Where accounts differ, as with the number of people displaced in Hebron, each figure is given with its source.</li>
<li>Quotes are short, word for word, and named.</li></ul>
<h2>Photographs</h2>
<ul><li>A photograph shows the place, the person or the thing a story is about, and its caption says what it is, where and when it was taken. A photo of a town is captioned as the town, never as the event.</li>
<li>No photographs of the dead or the wounded.</li>
<li>Where no honest photograph exists, the story runs with the dark screen and its dots instead.</li></ul>
<h2>What the dots mean</h2>
<ul><li>Three dots in a row, moving: the story is still being written, and is followed live.</li>
<li>Three dots settled over the letter: the story is posted.</li>
<li>On a story page, the dots in the header light one by one as you read.</li></ul>
<h2>Live coverage</h2>
<p>Live updates carry the time they were reported and the outlet that reported them. When a live story ends, its page says so and keeps the updates in order.</p>
<h2>Corrections</h2>
<p>A mistake is corrected in the story itself, and a note at its foot says what was changed and when. Send corrections through the <a href="contact.html">contact page</a>.</p>
<h2>Times</h2>
<p>All times are Jerusalem time. On this prototype they are the posting times of this edition.</p>
</div></div>'''
    sh.write('standards.html', sh.page('Standards and corrections', 'How Shasha Post sources, illustrates and corrects its stories.', body, current='standards'))


def sitemap():
    C.R = ''
    col = lambda title, items: f'<section><h2>{esc(title)}</h2><ul>{"".join(f"<li><a href={chr(34)}{u}{chr(34)}>{esc(t)}</a></li>" for t, u in items)}</ul></section>'
    main = [('Front page', 'home.html'), ('Today', 'today.html'), ('Latest, by day', 'latest.html'), ('Live', 'live.html'),
            ('Search', 'search.html'), ('The Daily Post', 'newsletter.html')]
    secs = [(t, f'{sl}.html') for sl, _, t, _ in SECTIONS]
    tops = [('All topics', 'topics.html')] + [(t['title'], f'topic/{t["slug"]}.html') for t in sh.TOPICS]
    pls = [('All places', 'places.html')] + [(p['title'], f'place/{p["slug"]}.html') for p in sh.PLACES]
    about = [('About', 'about.html'), ('Standards and corrections', 'standards.html'), ('Contact and tips', 'contact.html'),
             ('Privacy', 'privacy.html'), ('Photo credits', 'credits.html'), ('Identity', 'index.html')]
    stories = ''
    for sl, _, t, _ in SECTIONS:
        stories += col(t, [(s['headline'], link(s['id'])) for s in of(sl)])
    body = f'''<div class="wrap">
<header class="pagehead">{crumbs(("Site map", None))}<h1>Site map</h1><p>Every page on Shasha Post.</p></header>
<div class="smap">{col("Shasha Post", main)}{col("Sections", secs)}{col("Topics", tops)}{col("Places", pls)}{col("About", about)}</div>
<h2 class="smap-h">All {len(S)} stories</h2>
<div class="smap stories">{stories}</div></div>'''
    sh.write('sitemap.html', sh.page('Site map', 'Every page on Shasha Post.', body, current='sitemap'))


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
    for t in sh.TOPICS:
        topic(t)
    topics()
    for p in sh.PLACES:
        place(p)
    places()
    today()
    contact()
    privacy()
    standards()
    sitemap()
    lost()
    print(len(S), 'stories,', len(SECTIONS), 'sections,', len(sh.TOPICS), 'topics,', len(sh.PLACES), 'places, 15 more pages')


if __name__ == '__main__':
    main()
