"""Compose the edition from the research: tools/edition.json and tools/photos.json.

python -I tools/edition.py

research/news.json holds the sourced stories, research/photos.json the Commons photos found for
them (each with the story ids it honestly shows, in "for"). Posting times are this edition's own:
spread through each day, newest last, and for today up to NOW. tools/live.json (hand-written,
sourced) holds the live page's timed updates when there is a live story.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
DATE = '2026-10-27'
NOW = '2026-10-27T12:40:00+02:00'
ORDER = ['palestine', 'region', 'world', 'culture', 'sport', 'tech']
LEAD = 'ramallah-entrances-sealed-new-checkpoints'   # pinned; None = the newest Palestine story with a photo


def times(n, first, last):
    """n posting times between first and last (minutes since midnight), as HH:MM, earliest first."""
    if n == 1:
        return [f'{last // 60:02d}:{last % 60:02d}']
    step = (last - first) / (n - 1)
    out = []
    for i in range(n):
        m = int(round((first + i * step) / 5) * 5) + (2 if i % 2 else 0)   # not all on the fives
        out.append(f'{m // 60:02d}:{m % 60:02d}')
    return out


def main():
    news = json.load(open(R('research', 'news.json'), encoding='utf-8'))
    found = json.load(open(R('research', 'photos.json'), encoding='utf-8'))
    items = [i for i in news['items'] if i.get('section') in ORDER]

    # photos: each story takes the first photo that names it; extras stay for the book
    use, taken = {}, {}
    for slug, p in found.items():
        for sid in p.get('for', []):
            taken.setdefault(sid, slug)
    for slug, p in found.items():
        if p.get('for') and any(taken.get(s) == slug for s in p['for']) or slug.startswith('_extra'):
            page = 'https://commons.wikimedia.org/wiki/' + p['file'].replace(' ', '_')
            use[slug.lstrip('_')] = {k: p[k] for k in ('file', 'alt', 'caption', 'author', 'license') if k in p} | (
                {'focus': p['focus']} if p.get('focus') else {}) | {'page_url': page}

    # posting times, per day
    days = {}
    for i in items:
        days.setdefault(i['date'], []).append(i)
    stories = []
    now_m = int(NOW[11:13]) * 60 + int(NOW[14:16])
    for d, its in sorted(days.items()):
        its.sort(key=lambda i: (ORDER.index(i['section']), i['id']))
        last = now_m - 6 if d == DATE else 21 * 60 + 10
        ts = times(len(its), 7 * 60 + 5, last)
        # spread sections through the day rather than in blocks
        order = sorted(range(len(its)), key=lambda k: (k % 3, k))
        for t, k in zip(ts, order):
            i = its[k]
            s = {k2: i.get(k2) for k2 in ('id', 'section', 'date', 'place', 'headline', 'standfirst', 'body', 'quote', 'sources', 'kind', 'live')}
            s['time'] = t
            slug = taken.get(i['id'])
            s['photo'] = slug.lstrip('_') if slug else None
            stories.append(s)
    stories.sort(key=lambda s: (s['date'], s['time']))

    lead = LEAD or next(s['id'] for s in reversed(stories) if s['section'] == 'palestine' and s['photo'] and not s.get('live'))
    ed = {'date': DATE, 'now': NOW, 'lead': lead, 'stories': stories}
    if news.get('weather'):
        ed['weather'] = news['weather']
    if news.get('rates'):
        r = news['rates']
        vals = {k: float(r[k]) for k in ('USD', 'EUR', 'JOD') if r.get(k)}
        if vals:
            ed['rates'] = {'values': vals, 'source': r.get('source', '')}
    if os.path.exists(R('tools', 'live.json')):
        ed['live'] = json.load(open(R('tools', 'live.json'), encoding='utf-8'))
    json.dump(ed, open(R('tools', 'edition.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(use, open(R('tools', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = sum(1 for s in stories if s['photo'])
    print(len(stories), 'stories,', n, 'with photos,', len(use), 'photos; lead', lead)


if __name__ == '__main__':
    main()
