"""tools/out/og.html: the 1200x630 sharing card (the lead on a screen, the mark beside it).

python -I tools/og.py
node --experimental-websocket tools/shot.mjs http://localhost:8211/tools/out/og.html assets/og.png 1200 630 view
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir

import shell as sh
from shell import C, E, BY, esc, day

lead = BY[E['lead']]
C.R = '../../'
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>og</title>
<link rel="stylesheet" href="../../assets/css/sp.css?v={sh.V}">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#0B0E1C}}
.og{{display:grid;grid-template-columns:520px 680px;height:630px}}
.l{{padding:52px 48px 46px 56px;display:flex;flex-direction:column;color:#fff}}
.l .brand svg{{height:46px;width:auto}}
.l .brand .t-shasha{{fill:#fff}}.l .brand .t-post{{fill:#AFC0FF}}
.l h1{{margin-top:auto;font:700 44px/1.04 var(--sans);letter-spacing:-.03em}}
.l p{{margin-top:18px;font:600 17px var(--sans);color:#A9B0C6;display:flex;gap:10px;align-items:center}}
.r{{padding:28px 28px 28px 0}}
.r img{{width:100%;height:100%;object-fit:cover;border-radius:34px}}
</style></head><body><div class="og"><div class="l"><div class="brand">{sh.wordmark()}</div>
<h1>{esc(lead["headline"])}</h1><p>{sh.dots()} {esc(lead["place"])} · {day(lead["date"], year=True)}</p></div>
<div class="r"><img src="../../assets/img/photo/{lead["photo"]}.webp" alt=""></div></div></body></html>'''
sh.write('tools/out/og.html', html)
print('tools/out/og.html')
