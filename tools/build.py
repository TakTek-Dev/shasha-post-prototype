"""The front page.

python -I tools/build.py   (reads tools/edition.json, writes home.html and assets/data/search.json)
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir

import json
import os

import shell as sh
from shell import C, E, S, BY, SEC, esc, card, photo, plate, link, kick, when, dots, icon, day

ROOT = sh.ROOT


def newest(stories):
    return sorted(stories, key=sh.stamp, reverse=True)


def of(sec, n=None, skip=()):
    out = [s for s in newest(S) if s['section'] == sec and s['id'] not in skip]
    return out[:n] if n else out


def head_of(sec, more=True, tag=''):
    _, label, title, sf = SEC[sec]
    m = f'<a class="more" href="{C.R}{sec}.html">All {esc(label.lower() if sec != "tech" else "tech")} {sh.icon("i-right")}</a>' if more else ''
    return f'<div class="sec-h"><h2>{dots()}{esc(title)}</h2><p>{esc(sf)}</p>{m}</div>'


def front():
    lead = BY[E['lead']]
    stream = [s for s in newest(S) if s['id'] != lead['id']][:9]
    lis = ''
    for i, s in enumerate(stream):
        fresh = ' class="fresh"' if s['date'] == E['date'] and i < 3 else ''
        lis += (f'<li{fresh}>{when(s, rel=True)}<a href="{link(s["id"])}">{esc(s["headline"])}</a>'
                f'<span class="s">{esc(SEC[s["section"]][1])} · {esc(s["place"])}</span></li>')
    ph = photo(lead.get('photo'), sizes='(min-width:1000px) 66vw, 100vw', cls='ph r169', eager=True) or plate('ph r169')
    return f'''<section class="front" aria-label="Top story">
<div class="wrap">
<article class="lead">
{ph}
<div class="cap">{kick(lead)}<span class="meta">{when(lead)}<span class="dot"></span>{esc(lead["place"])}</span></div>
<h1><a href="{link(lead["id"])}">{esc(lead["headline"])}</a></h1>
<p class="sf">{esc(lead["standfirst"])}</p>
</article>
<aside class="stream" aria-labelledby="jp"><h2 id="jp">{dots()}Just posted</h2><ol>{lis}</ol>
<a class="all" href="{C.R}latest.html">Everything, by day</a></aside>
</div>
</section>'''


def liveband():
    lv = [s for s in S if s.get('live')]
    if not lv:
        return ''
    s = BY.get(E.get('live', {}).get('story')) or lv[0]
    ups = E.get('live', {}).get('updates', [])[:4]
    ol = ''.join(f'<li><time>{esc(u["time"])}</time><p>{esc(u["text"])}</p></li>' for u in ups)
    right = f'<ol aria-label="Latest updates">{ol}</ol>' if ol else ''
    return f'''<section class="wrap" style="padding-bottom:clamp(40px,5vw,64px)" aria-label="Live">
<div class="liveband sq">
<div><span class="tag">{dots(True)}Live · {esc(s["place"])}</span>
<h2>{esc(s["headline"])}</h2><p>{esc(s["standfirst"])}</p>
<a class="btn go" href="{C.R}live.html">Follow it live {icon("i-right")}</a></div>
{right}
</div>
</section>'''


def palestine(skip):
    ps = of('palestine', skip=skip)
    with_ph = [s for s in ps if s.get('photo')]
    big = with_ph[0] if with_ph else ps[0]
    rest = [s for s in ps if s is not big]
    side = rest[:3]
    more = rest[3:7]
    return f'''<section class="sec" aria-labelledby="h-pal"><div class="wrap">
{head_of('palestine').replace('<h2>', '<h2 id="h-pal">', 1)}
<div class="pal">{card(big, 'big', sizes='(min-width:900px) 56vw, 100vw')}
<div class="side">{''.join(card(s, 'row') for s in side)}</div></div>
<div class="grid g4 pal-more">{''.join(card(s, sf=False, sizes='(min-width:1000px) 23vw, 100vw') for s in more)}</div>
</div></section>'''


def culture():
    cs = sorted(of('culture')[:4], key=lambda s: not s.get('photo'))
    if not cs:
        return ''
    return f'''<section class="screenband" aria-labelledby="h-cul"><div class="wrap">
{head_of('culture').replace('<h2>', '<h2 id="h-cul">', 1)}
<div class="reel">{''.join(card(s, sizes='(min-width:1100px) 23vw, 78vw', ratio='r45') for s in cs)}</div>
</div></section>'''


def photo_first(ss):
    """The top of a column is the newest story with a photo; the rest keep their order."""
    top = next((s for s in ss if s.get('photo')), ss[0])
    return [top] + [s for s in ss if s is not top]


def split(a, b, skip=()):
    def col(sec):
        ss = photo_first(of(sec, skip=skip))
        return (head_of(sec) + f'<div class="stack">{card(ss[0], sizes="(min-width:960px) 45vw, 100vw")}'
                + ''.join(card(s, 'row') for s in ss[1:4]) + '</div>')
    return f'<section class="sec"><div class="wrap split"><div>{col(a)}</div><div>{col(b)}</div></div></section>'


def main():
    lead = E['lead']
    skip = {lead}
    body = front() + liveband() + palestine(skip) + split('region', 'world', skip={E.get('live', {}).get('story')}) + culture() + split('sport', 'tech')
    body += f'<section class="sec" style="border:0"><div class="wrap">{sh.daily()}</div></section>'
    sh.write('home.html', sh.page(sh.SITE, 'News from Palestine, in English: the West Bank, Gaza and Jerusalem, the region, culture, sport and tech, each story with its source.',
                                  body, current='home', with_loader=True))

    idx = []
    for s in newest(S):
        p = s.get('photo')
        idx.append({'id': s['id'], 'sec': s['section'], 'k': SEC[s['section']][1], 'h': s['headline'], 's': s['standfirst'],
                    'p': s['place'], 'd': day(s['date']), 'img': f'assets/img/photo/{p}.webp' if p in sh.PH else ''})
    os.makedirs(os.path.join(ROOT, 'assets', 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'assets', 'data', 'search.json'), 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, separators=(',', ':'))
    print('home.html,', len(S), 'stories')


if __name__ == '__main__':
    main()
