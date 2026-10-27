"""Shasha Post marks.

python -I tools/brand.py   -> assets/brand/*.svg + favicon.svg + tools/out/marks.json

شاشة (shasha) is Arabic for a screen. The mark is the word's first letter, ش (shin, the
sound "sh"), drawn inside a screen: three rounded teeth and the three dots that sit over
them. The tile is the screen, cobalt as a screen switched on; the dots are signal orange.

Three dots are also what a screen shows while somebody is writing to you. The site uses
that: three dots in a row, hopping, is a story still being written (live); the dots
settled into the triangle over the teeth is a story posted. The loader is the screen
switching on and the first post arriving.
"""
import json
import math
import os

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'brand')
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)

COBALT, SIGNAL, INK, WHITE, MIST = '#1E2BD2', '#FF5A36', '#0B0E1C', '#FFFFFF', '#F1F3F8'

# ---- the mark on a 100 grid
COMB_W = 10.0                       # stroke of the teeth
TEETH = (23.0, 50.0, 77.0)          # three teeth, 27 apart
TOOTH_TOP, BOWL_Y = 54.0, 62.0      # straight part ends at BOWL_Y, then a half circle
BOWL_R = (TEETH[1] - TEETH[0]) / 2
DOT_R = 6.2
DOTS = ((50.0, 26.0), (41.0, 39.0), (59.0, 39.0))      # one over two, as over a written ش
TYPING = ((34.0, 39.0), (50.0, 39.0), (66.0, 39.0))    # the same dots in a row: "writing…"
SQUIRCLE_N = 5.0                    # superellipse exponent for the tile (continuous corners)


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def squircle(x=0.0, y=0.0, s=100.0, n=SQUIRCLE_N, steps=96):
    """A superellipse tile: the corner curvature runs into the sides instead of meeting them."""
    a = s / 2
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, d = math.cos(t), math.sin(t)
        px = a * math.copysign(abs(c) ** (2 / n), c)
        py = a * math.copysign(abs(d) ** (2 / n), d)
        pts.append((x + a + px, y + a + py))
    return 'M' + 'L'.join(f'{f(p[0])} {f(p[1])}' for p in pts) + 'Z'


# the small cut, for 24 px and under (favicon, tab): heavier teeth, bigger dots, less air
SMALL = {'w': 13.0, 'teeth': (21.0, 50.0, 79.0), 'top': 55.0, 'bowl': 63.0, 'r': 8.2,
         'dots': ((50.0, 24.0), (39.0, 41.0), (61.0, 41.0))}


def comb(k=1.0, x=0.0, y=0.0, teeth=TEETH, top=TOOTH_TOP, bowl=BOWL_Y):
    t = lambda v, o: f(o + v * k)
    a, b, c = teeth
    r = f((b - a) / 2 * k)
    return (f'M{t(a, x)} {t(top, y)}V{t(bowl, y)}A{r} {r} 0 0 0 {t(b, x)} {t(bowl, y)}'
            f'V{t(top, y)}V{t(bowl, y)}A{r} {r} 0 0 0 {t(c, x)} {t(bowl, y)}V{t(top, y)}')


def mark(tile=COBALT, teeth=WHITE, dots=SIGNAL, k=1.0, x=0.0, y=0.0, with_tile=True, small=False):
    c = SMALL if small else {'w': COMB_W, 'teeth': TEETH, 'top': TOOTH_TOP, 'bowl': BOWL_Y, 'r': DOT_R, 'dots': DOTS}
    out = f'<path d="{squircle(x, y, 100 * k)}" fill="{tile}"/>' if with_tile else ''
    out += (f'<path d="{comb(k, x, y, c["teeth"], c["top"], c["bowl"])}" fill="none" stroke="{teeth}" '
            f'stroke-width="{f(c["w"] * k)}" stroke-linecap="round" stroke-linejoin="round"/>')
    out += f'<g fill="{dots}">' + ''.join(
        f'<circle cx="{f(x + cx * k)}" cy="{f(y + cy * k)}" r="{f(c["r"] * k)}"/>' for cx, cy in c['dots']) + '</g>'
    return out


# ---- the name, shaped by HarfBuzz from Familjen Grotesk at 700 (kerning and all)
def shaped(text, wght=700, path='FamiljenGrotesk[wght].ttf', track=-0.028):
    fp = os.path.join(SRC, path)
    blob = hb.Blob.from_file_path(fp)
    face = hb.Face(blob)
    font = hb.Font(face)
    font.set_variations({'wght': wght})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True, 'liga': True})
    tt = TTFont(fp)
    from fontTools.varLib.instancer import instantiateVariableFont
    tt = instantiateVariableFont(tt, {'wght': wght})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    upem = tt['head'].unitsPerEm
    x, glyphs = 0.0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append((order[info.codepoint], x + pos.x_offset))
        x += pos.x_advance + track * upem
    return gs, glyphs, x - track * upem, upem, tt


def outline(gs, glyphs, scale, ox, base):
    pen = SVGPathPen(gs)
    for name, gx in glyphs:
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, ox + gx * scale, base)))
    return pen.getCommands()


def wordmark():
    """Tile + 'Shasha Post'. The tile is 1.42 cap heights tall, centred on the capitals."""
    gs, glyphs, adv, upem, tt = shaped('Shasha Post')
    cap = tt['OS/2'].sCapHeight
    s = 100 / upem                       # 100 units of the lockup = one em
    cap_px = cap * s
    tile = cap_px * 1.42
    gap = tile * 0.30
    pad = 2.0
    h = tile + 2 * pad
    base = pad + tile / 2 + cap_px / 2
    ox = pad + tile + gap
    space = next(i for i, (n, _) in enumerate(glyphs) if n == 'space')
    shasha = outline(gs, glyphs[:space], s, ox, base)
    post = outline(gs, glyphs[space + 1:], s, ox, base)
    w = ox + adv * s + pad
    return {'w': round(w, 2), 'h': round(h, 2), 'tile': [pad, pad, round(tile, 3)],
            'shasha': shasha, 'post': post, 'cap': round(cap_px, 3), 'base': round(base, 3)}


def svg(w, h, body, label='Shasha Post'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" role="img" '
            f'aria-label="{label}">{body}</svg>\n')


def write(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def main():
    wm = wordmark()
    tx, ty, ts = wm['tile']
    k = ts / 100
    lock = lambda ink, post, tile, teeth, dots: svg(wm['w'], wm['h'],
        mark(tile, teeth, dots, k, tx, ty) + f'<path d="{wm["shasha"]}" fill="{ink}"/><path d="{wm["post"]}" fill="{post}"/>')

    write('mark.svg', svg(100, 100, mark()))
    write('mark-ink.svg', svg(100, 100, mark(INK, WHITE, SIGNAL)))
    write('mark-white.svg', svg(100, 100, mark(WHITE, COBALT, SIGNAL)))
    write('mark-mono.svg', svg(100, 100, mark(INK, WHITE, WHITE)))
    write('glyph.svg', svg(100, 100, mark(None, INK, SIGNAL, with_tile=False)))
    write('wordmark.svg', lock(INK, COBALT, COBALT, WHITE, SIGNAL))
    write('wordmark-reverse.svg', lock(WHITE, '#AFC0FF', COBALT, WHITE, SIGNAL))
    write('wordmark-mono.svg', lock(INK, INK, INK, WHITE, WHITE))
    with open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(svg(100, 100, mark(small=True)))
    write('mark-small.svg', svg(100, 100, mark(small=True)))

    marks = {'tile': squircle(), 'comb': comb(), 'combW': COMB_W, 'dotR': DOT_R,
             'dots': DOTS, 'typing': TYPING, 'wordmark': wm,
             'colours': {'cobalt': COBALT, 'signal': SIGNAL, 'ink': INK, 'mist': MIST}}
    with open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), 'w', encoding='utf-8') as fh:
        json.dump(marks, fh)
    print('wordmark', wm['w'], 'x', wm['h'])


if __name__ == '__main__':
    main()
