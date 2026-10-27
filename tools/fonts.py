"""Self-hosted WOFF2 subsets of the two brand faces.

python -I tools/fonts.py   (from the project root; sources in research/font-src, gitignored)

Familjen Grotesk (Familjen STHLM, OFL) is the screen's voice: headlines, labels, times, the
wordmark. Its single-storey a is drawn like a rounded screen tile, so "Shasha" sets as two
small screens side by side. Faustina (Omnibus-Type, OFL) was drawn for long reading on
screens; it carries the stories. Both keep every layout feature (tnum, frac, case, zero).
"""
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Basic Latin, Latin-1, Latin Extended-A, the transliteration letters names use
# (ḥ ṣ ḍ ṭ ẓ ʿ ʾ), typographic punctuation, arrows, the shekel and maths signs for figures.
UNICODES = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
    [0x1E0C, 0x1E0D, 0x1E24, 0x1E25, 0x1E62, 0x1E63, 0x1E6C, 0x1E6D, 0x1E92, 0x1E93, 0x02BE, 0x02BF, 0x02BC,
     0x2009, 0x200A, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
     0x2032, 0x2033, 0x2039, 0x203A, 0x2044, 0x20AC, 0x20AA, 0x2116, 0x2190, 0x2191, 0x2192, 0x2193,
     0x2197, 0x2198, 0x2212, 0x2248, 0x2264, 0x2265, 0x00D7, 0x00B0, 0x00B7, 0x00B2, 0x2153, 0x00BD, 0x00BC]
)

JOBS = [
    ('FamiljenGrotesk[wght].ttf', 'familjen.woff2', None),
    ('FamiljenGrotesk-Italic[wght].ttf', 'familjen-italic.woff2', None),
    ('Faustina[wght].ttf', 'faustina.woff2', None),
    ('Faustina-Italic[wght].ttf', 'faustina-italic.woff2', None),
]


def options():
    o = subset.Options()
    o.flavor = 'woff2'
    o.layout_features = ['*']
    o.name_IDs = ['*']
    o.name_languages = ['*']
    o.notdef_outline = True
    o.glyph_names = False
    o.hinting = False
    o.desubroutinize = True
    return o


for src, out, limits in JOBS:
    font = TTFont(os.path.join(SRC, src))
    if limits:
        font = instancer.instantiateVariableFont(font, limits)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    font = TTFont(buf)
    sub = subset.Subsetter(options())
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    path = os.path.join(OUT, out)
    subset.save_font(font, path, options())
    print(out, os.path.getsize(path) // 1024, 'KB')

# The few Arabic words the site prints (the name, the letter): Noto Kufi Arabic, only those letters.
ARABIC = 'شاشة ش'
font = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, 'NotoKufiArabic[wght].ttf')), {'wght': (400, 700)})
buf = io.BytesIO()
font.save(buf)
buf.seek(0)
font = TTFont(buf)
sub = subset.Subsetter(options())
sub.populate(text=ARABIC)
sub.subset(font)
subset.save_font(font, os.path.join(OUT, 'kufi.woff2'), options())
print('kufi.woff2', os.path.getsize(os.path.join(OUT, 'kufi.woff2')) // 1024, 'KB')

for src, lic in (('familjengrotesk-OFL.txt', 'OFL-FamiljenGrotesk.txt'), ('faustina-OFL.txt', 'OFL-Faustina.txt'), ('notokufi-OFL.txt', 'OFL-NotoKufiArabic.txt')):
    with open(os.path.join(SRC, src), encoding='utf-8') as f, open(os.path.join(OUT, lic), 'w', encoding='utf-8') as g:
        g.write(f.read())
