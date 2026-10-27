"""Check the published site: every built page and every local asset it references returns 200.

python -I tools/live.py   -> prints counts and any failures; exit 1 if any
"""
import glob
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urldefrag, urljoin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://taktek-dev.github.io/shasha-post-prototype/'
pages = sorted(os.path.relpath(p, ROOT).replace('\\', '/') for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
               if not os.path.relpath(p, ROOT).startswith(('tools', 'research', 'node_modules')))
urls = {BASE + p for p in pages}
for p in pages:
    h = open(os.path.join(ROOT, p), encoding='utf-8').read()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', h):
        if ref.startswith(('http', 'mailto:', 'data:', '#')) or "'" in ref:
            continue
        urls.add(urldefrag(urljoin(BASE + p, ref))[0])
urls.add(BASE + 'assets/data/search.json')
urls.add(BASE + 'assets/og.png')


def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'ti-live-check'}), timeout=30)
        return u, r.status
    except urllib.error.HTTPError as e:
        return u, e.code
    except Exception as e:
        return u, str(e)


with ThreadPoolExecutor(12) as ex:
    res = list(ex.map(get, sorted(urls)))
bad = [(u, s) for u, s in res if s != 200]
missing = get(BASE + 'no-such-page.html')
print(len(pages), 'pages,', len(urls) - len(pages), 'assets/links checked,', len(bad), 'failed; unknown path ->', missing[1])
for u, s in bad[:40]:
    print('  ', s, u)
sys.exit(1 if bad or missing[1] != 404 else 0)
