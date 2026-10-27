"""index.html: the Shasha Post identity book, plus assets/shasha-post-identity.zip.

python -I tools/book.py
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir

import os
import zipfile

import shell as sh
from shell import C, E, S, BY, esc, dots, glyph_svg, wordmark, photo, card, icon

ROOT = sh.ROOT
M = sh.MARKS
COL = M['colours']


def construction():
    """The mark on its grid: tile, the three teeth, the bowls, the dot centres."""
    g = ''.join(f'<path d="M{v} 0V100M0 {v}H100" />' for v in range(10, 100, 10))
    teeth = (23, 50, 77)
    guides = ''.join(f'<path d="M{x} 6V94" class="gd"/>' for x in teeth)
    guides += '<path d="M6 54H94M6 62H94" class="gd"/>'
    cs = ''.join(f'<circle cx="{x}" cy="{y}" r="{M["dotR"]}" class="dc"/><circle cx="{x}" cy="{y}" r="1" class="cc"/>' for x, y in M['dots'])
    tri = 'M{0} {1}L{2} {3}L{4} {5}Z'.format(*[v for p in M['dots'] for v in p])
    return f'''<svg class="cons" viewBox="-8 -8 116 116" role="img" aria-label="Construction of the mark on a 100 unit grid">
<g class="grid-l">{g}</g>
<path d="{M["tile"]}" class="tl"/>
<path d="{M["comb"]}" class="cb" stroke-width="{M["combW"]}"/>
<path d="{M["comb"]}" class="cl"/>
{guides}<path d="{tri}" class="tri"/>{cs}
<text x="23" y="100" class="t">23</text><text x="50" y="100" class="t">50</text><text x="77" y="100" class="t">77</text>
<text x="97" y="55" class="t" text-anchor="end">54</text><text x="97" y="66" class="t" text-anchor="end">62</text>
</svg>'''


def swatch(name, hexv, note, dark=False):
    return (f'<div class="sw"><div class="chip sq" style="background:{hexv}{";box-shadow:inset 0 0 0 1px var(--rule)" if hexv.upper() in ("#FFFFFF", "#F1F3F8") else ""}"></div>'
            f'<p><b>{esc(name)}</b><span>{hexv}</span></p><p class="n">{esc(note)}</p></div>')


def states():
    return f'''<div class="states">
<div class="st"><div class="demo"><span class="dots typing big">{"<i></i>" * 3}</span></div><h3>Writing</h3><p>Three dots in a row, hopping. A story still being written: live pages, live labels, the status bar.</p></div>
<div class="st"><div class="demo"><span class="dots big">{"<i></i>" * 3}</span></div><h3>Posted</h3><p>The dots settled into the letter, one over two. Section heads, “Just posted”, the end of every story.</p></div>
<div class="st"><div class="demo"><span class="dots read big"><i class="read"></i><i class="read"></i><i></i></span></div><h3>Reading</h3><p>On a story page the masthead’s dots light one by one as you read: a third, two thirds, the end.</p></div>
<div class="st"><div class="demo">{glyph_svg(tile="var(--screen)", teeth="var(--screen)", dot="var(--signal)", cls="off")}</div><h3>Off</h3><p>A dark screen with its dots and no letter stands in for a photo that does not exist. It never pretends to be one.</p></div>
</div>'''


def main():
    C.R = ''
    lead = BY[E['lead']]
    wm = wordmark()
    body = f'''<div class="book">
<header class="b-hero"><div class="wrap">
<p class="lbl">Identity · Shasha Post · {sh.day(E["date"], year=True)}</p>
<div class="b-mark">{glyph_svg(label="The Shasha Post mark")}</div>
<h1>A screen, and the three dots of someone writing.</h1>
<p class="sf"><span lang="ar">شاشة</span>, shasha, is Arabic for a screen. The mark is the word’s first letter, <span lang="ar">ش</span>, written inside one: three teeth for the sound “sh”, and over them three dots, the dots every screen shows while someone is writing to you.</p>
<div class="b-cta"><a class="btn solid" href="home.html">Open the site {icon("i-right")}</a><a class="btn" href="assets/shasha-post-identity.zip" download>Download the marks</a></div>
</div></header>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">01</p><h2>The name</h2></div>
<div class="b-txt"><p>Shasha is the Arabic news site’s own name, and the English edition keeps it whole: “Post” says what it is, a place where news is posted, and the Arabic says where it is seen.</p>
<p><span lang="ar">ش</span> is the letter for “sh”. A reader of Arabic sees the first letter of the name; a reader of English sees three dots over a soft “w”, which is how the brand introduces itself: the dots first.</p></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">02</p><h2>The mark</h2></div>
<div class="b-txt"><div class="b-pair">{construction()}<div class="b-row">{glyph_svg()}{glyph_svg(tile=COL["ink"])}{glyph_svg(tile="#fff", teeth=COL["cobalt"], cls="mk w")}</div></div>
<p>Drawn on a 100 unit grid. The tile is a superellipse (exponent 5): its corners run into the sides instead of meeting them, like the glass of a phone. The three teeth stand 27 apart and join in two half circles of radius 13.5; the stroke is 10, with round ends. The dots are 6.2 in radius, one over two, the triangle a written <span lang="ar">ش</span> makes.</p>
<p>Under 24 px a small cut takes over (favicon, tab): heavier teeth at 13, dots at 8.2, so the letter survives at 16 px.</p></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">03</p><h2>The dots</h2></div>
<div class="b-txt"><p>The dots are the brand’s grammar. They carry state, and they are the only thing on the site in signal orange.</p>{states()}</div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">04</p><h2>Wordmark</h2></div>
<div class="b-txt"><div class="b-wm">{wm}</div><div class="b-wm dark">{wm}</div>
<p>Familjen Grotesk at 700, shaped with its own kerning and tightened 2.8%, then drawn as outlines. The tile is 1.42 cap heights tall and centred on the capitals; the gap is three tenths of the tile. “Post” takes the screen’s cobalt. Keep clear space of one tile height around it; do not set it under 96 px wide.</p></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">05</p><h2>Colour</h2></div>
<div class="b-txt"><div class="sws">
{swatch("Cobalt", COL["cobalt"], "The screen, switched on. Tile, links, the reading bar, the live band.")}
{swatch("Signal", COL["signal"], "Only the dots: what is new, what is live, how far you have read.")}
{swatch("Ink", COL["ink"], "Text, the status bar, the dark screen of the culture band and footer.")}
{swatch("White", "#FFFFFF", "The page. Never cream, never paper.")}
{swatch("Mist", COL["mist"], "A cool grey for panels: “Just posted”, sources, the Daily Post.")}
</div>
<p>Cobalt on white is 9.0:1; ink 19.2:1; secondary ink (#394057) 10.3:1; meta (#5E6680) 5.7:1, and 5.1:1 on mist. Signal orange is never text on white; where it must speak it darkens to #C2361A (5.5:1). With the lights off the page is ink, links lift to #9DACFF, and the tile stays cobalt.</p></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">06</p><h2>Type</h2></div>
<div class="b-txt">
<div class="spec"><p class="s1">Familjen Grotesk</p><p class="s2">Settlers set up an outpost north of Ramallah</p><p class="s3">Headlines · labels · times 14:32 · 27 Oct · ₪3.74</p></div>
<div class="spec"><p class="s4">Faustina</p><p class="s5">Faustina was drawn for long reading on screens. It carries every story, at 19.5 px with a line of 1.65, and its italic sets the quotes.</p></div>
<p>Familjen Grotesk (Familjen STHLM) for everything that speaks: its single-storey ɑ is a small rounded screen, so “Shasha” sets as two of them. Faustina (Omnibus-Type) for everything you read. Both are open source, self-hosted as WOFF2 subsets (20 and 29 KB).</p></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">07</p><h2>Photographs</h2></div>
<div class="b-txt"><div class="b-photo">{photo(lead.get("photo"), cls="ph r169", sizes="(min-width:1000px) 60vw, 100vw")}</div>
<p>Photographs are screens: the same continuous corners, in their own colour, never tinted. As a photo enters the view it switches on, a line of light opening into the picture. Every photo shows the place, the person or the thing the story is about, with a caption saying what, where and when. Where no honest photo exists, the dark screen with its dots stands in.</p></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">08</p><h2>Motion</h2></div>
<div class="b-txt"><ul class="b-list">
<li><b>The loader</b>, once a visit: a line of light opens into the screen, three dots type, then settle over the teeth as the letter is written, and the tile flies to its place in the masthead. <a href="home.html?loader">See it</a>.</li>
<li><b>Switching on</b>: photos open from a line, 0.75 s, ease out.</li>
<li><b>Writing</b>: dots hop 3.5 px, 1.1 s, staggered 140 ms.</li>
<li><b>Reading</b>: a cobalt bar and the masthead’s three dots.</li>
<li>Pages cross-fade with view transitions. With reduced motion everything is still and immediate.</li></ul></div>
</div></section>

<section class="b-sec"><div class="wrap b-two">
<div><p class="b-n">09</p><h2>Don’t</h2></div>
<div class="b-txt"><ul class="b-list">
<li>Don’t use signal orange for anything but the dots.</li>
<li>Don’t redraw <span lang="ar">ش</span> with real calligraphy or add its tail: the mark is the letter as a screen writes it.</li>
<li>Don’t put the mark in a circle or a sharp square, or outline it.</li>
<li>Don’t tint photographs blue, or put text on them.</li>
<li>Don’t invent staff, readers, partners or numbers.</li></ul></div>
</div></section>
</div>'''
    sh.write('index.html', sh.page('Identity', 'The Shasha Post identity: a screen, and the three dots of someone writing.', body, current='identity'))

    z = os.path.join(ROOT, 'assets', 'shasha-post-identity.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for n in sorted(os.listdir(os.path.join(ROOT, 'assets', 'brand'))):
            zf.write(os.path.join(ROOT, 'assets', 'brand', n), f'shasha-post/{n}')
        for n in ('OFL-FamiljenGrotesk.txt', 'OFL-Faustina.txt'):
            zf.write(os.path.join(ROOT, 'assets', 'fonts', n), f'shasha-post/fonts/{n}')
    print('index.html + zip')


if __name__ == '__main__':
    main()
