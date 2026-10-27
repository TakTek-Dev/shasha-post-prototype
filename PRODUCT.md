# Product

## Platform

web

## Stack

Static HTML/CSS/JS, no framework. Python helper scripts generate the marks, fonts, photos and pages (the TakTek prototype pattern: Canary Palestine, The Inside). Published on GitHub Pages under TakTek-Dev only when the user says «ارفع». Commits only on request.

Build order: `python -I tools/fonts.py` → `brand.py` → `edition.py` → `photos.py` → `build.py` → `pages.py` → `book.py` → `links.py` → `og.py` (+ `node --experimental-websocket tools/shot.mjs http://localhost:8211/tools/out/og.html assets/og.png 1200 630 view`). Bump `V` in tools/shell.py on any asset change. Never hand-edit the built HTML.

## Users

English-speaking readers who follow Palestine: diaspora Palestinians, journalists, researchers, solidarity audiences. They want the day's news from the West Bank, Gaza and Jerusalem, the region around it, and Palestinian culture, sport and tech, each story with its source.

## Product Purpose

Shasha Post: the English edition of شاشة (shasha.ps), a Palestinian news site (News, Art, Sports, Technology). No logo existed; identity from zero.

## Brand Commitments

- شاشة = screen. The mark is ش written in a screen: three teeth, three dots. Cobalt is the screen; signal orange is only the dots.
- The dots carry state: in a row and hopping = still being written (live); settled = posted; lighting one by one = reading progress; dark screen with dots = no photo.
- Every story names and links its source; every photo is a real Commons photo of the place/person/thing, captioned; no photos of the dead or wounded; no invented staff, readership, partners or numbers.
- Faces used by other TakTek prototypes are off-limits; IBM Plex banned. No cream or beige grounds. Soft radii (superellipse tile, corner-shape: squircle where supported).
