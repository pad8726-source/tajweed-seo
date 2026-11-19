#!/usr/bin/env python3
"""Construit le blog statique (dossier docs/) à partir de content/*.md.

Stdlib uniquement. Usage : python3 tools/build.py
Variables facultatives :
  SITE_URL       défaut : https://blog.tajweedtutorai.com
  CUSTOM_DOMAIN  écrit docs/CNAME (nécessaire pour GitHub Pages avec un domaine perso)

Copie aussi assets/ (logo) et social/visuals/ (visuels Instagram) dans docs/,
pour qu'ils soient servis publiquement par GitHub Pages.
"""
import html
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
SITE_URL = os.environ.get("SITE_URL", "https://blog.tajweedtutorai.com").rstrip("/")
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN", "").strip()
APP_URL = "https://tajweedtutorai.com"
REQUIRED = ("title", "description", "lang", "slug", "date")
LANGS = {"fr": "Français", "en": "English"}
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COPY_DIRS = ("assets", "social/visuals")

CSS = """
:root{--bg:#1a1a2e;--bg2:#0f0f22;--card:#23233f;--gold:#f0b94b;--teal:#26c6b4;--text:#f2f0ea;--muted:#b9b8cc;--line:rgba(240,185,75,.28)}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.75;color:var(--text);
background:radial-gradient(900px 500px at 85% -10%,rgba(240,185,75,.18),transparent 60%),radial-gradient(700px 500px at -10% 30%,rgba(38,198,180,.14),transparent 60%),linear-gradient(180deg,var(--bg),var(--bg2) 70%);
min-height:100vh}
a{color:var(--gold);text-decoration:none}
a:hover{text-decoration:underline}
header{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem 1.25rem;max-width:1100px;margin:0 auto}
.brand{display:flex;align-items:center;gap:.7rem;color:var(--text);font-weight:800;letter-spacing:.02em}
.brand:hover{text-decoration:none}
.brand img{width:46px;height:46px;border-radius:50%;box-shadow:0 0 0 2px var(--gold)}
.pill{display:inline-block;background:var(--gold);color:#1a1a2e;font-weight:800;padding:.6rem 1.1rem;border-radius:999px;box-shadow:0 8px 24px rgba(240,185,75,.25);transition:transform .2s}
.pill:hover{transform:translateY(-2px);text-decoration:none}
.ghost{display:inline-block;border:2px solid var(--gold);color:var(--gold);font-weight:800;padding:.55rem 1.05rem;border-radius:999px}
.ghost:hover{text-decoration:none;background:rgba(240,185,75,.1)}
main{max-width:1100px;margin:0 auto;padding:0 1.25rem}
.hero{text-align:center;padding:3.5rem 0 2.5rem}
.hero .kicker{display:inline-block;color:#1a1a2e;background:linear-gradient(90deg,var(--gold),#ffd98a);font-weight:800;font-size:.85rem;letter-spacing:.12em;text-transform:uppercase;padding:.35rem .9rem;border-radius:999px}
.hero h1{font-size:clamp(2.1rem,6vw,3.6rem);line-height:1.1;margin:1.2rem 0 1rem;font-weight:900}
.hero h1 span{background:linear-gradient(90deg,var(--gold),var(--teal));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p.lead{font-size:1.15rem;color:var(--muted);max-width:640px;margin:0 auto 1.8rem}
.hero .actions{display:flex;flex-wrap:wrap;gap:.8rem;justify-content:center}
h2.section{font-size:1.6rem;margin:3rem 0 1.2rem;display:flex;align-items:center;gap:.7rem}
h2.section::before{content:"";width:6px;height:1.6rem;border-radius:3px;background:linear-gradient(var(--gold),var(--teal))}
.benefits{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem}
.benefit{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.4rem}
.benefit b{display:block;font-size:1.6rem;color:var(--gold);font-weight:900}
.benefit h3{margin:.3rem 0 .4rem;font-size:1.1rem}
.benefit p{margin:0;color:var(--muted);font-size:.97rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.2rem}
.card{position:relative;background:var(--card);border:1px solid var(--line);border-radius:20px;padding:1.5rem;overflow:hidden;transition:transform .25s,border-color .25s,box-shadow .25s;display:flex;flex-direction:column;color:var(--text)}
.card::before{content:"";position:absolute;inset:0 0 auto 0;height:5px;background:linear-gradient(90deg,var(--gold),var(--teal))}
.card:hover{transform:translateY(-5px);border-color:var(--gold);box-shadow:0 18px 40px rgba(0,0,0,.35);text-decoration:none}
.card .num{font-size:.8rem;font-weight:800;letter-spacing:.14em;color:var(--teal);text-transform:uppercase}
.card h3{font-size:1.25rem;line-height:1.3;margin:.6rem 0 .5rem}
.card p{color:var(--muted);margin:0 0 1rem;font-size:.97rem;flex:1}
.card .more{color:var(--gold);font-weight:800}
.lang-title{margin-top:2.5rem}
.banner{margin:3.5rem 0 1rem;text-align:center;border-radius:24px;padding:2.4rem 1.4rem;background:linear-gradient(135deg,rgba(240,185,75,.22),rgba(38,198,180,.18));border:1px solid var(--line)}
.banner h2{margin:0 0 .6rem;font-size:1.7rem}
.banner p{color:var(--muted);margin:0 auto 1.4rem;max-width:560px}
article{max-width:760px;margin:2rem auto 0}
article .eyebrow{color:var(--teal);font-weight:800;font-size:.85rem;letter-spacing:.12em;text-transform:uppercase}
article h1{font-size:clamp(1.9rem,5vw,2.8rem);line-height:1.15;margin:.5rem 0 .8rem;font-weight:900}
article .desc{font-size:1.15rem;color:var(--gold);font-style:italic;border-left:4px solid var(--gold);padding-left:1rem;margin:0 0 2rem}
article h2{font-size:1.5rem;margin:2.4rem 0 .7rem;color:var(--gold)}
article h3{font-size:1.2rem;margin:1.8rem 0 .5rem}
article p,article li{font-size:1.06rem;color:#e6e4ee}
article ul{padding-left:1.2rem}
article li{margin:.35rem 0}
.cta{margin:3rem 0 1rem;border-radius:22px;padding:1.8rem;text-align:center;background:linear-gradient(135deg,var(--gold),#ffd98a);color:#1a1a2e;box-shadow:0 20px 40px rgba(240,185,75,.22)}
.cta p{margin:0 0 1rem;font-weight:800;font-size:1.2rem;color:#1a1a2e}
.cta a{display:inline-block;background:#1a1a2e;color:var(--gold);padding:.8rem 1.4rem;border-radius:999px;font-weight:900}
.cta a:hover{text-decoration:none;transform:translateY(-2px)}
.back{display:inline-block;margin-top:2rem;color:var(--muted)}
footer{max-width:1100px;margin:4rem auto 0;padding:2rem 1.25rem;border-top:1px solid var(--line);color:var(--muted);display:flex;flex-wrap:wrap;justify-content:space-between;gap:1rem;font-size:.95rem}
footer a{color:var(--gold)}
@media (max-width:600px){.hero{padding-top:2.2rem}header .ghost{display:none}}
"""


def parse(path):
    """Lit le front matter (entre deux lignes ---) et le corps Markdown."""
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"')
        body = match.group(2)
    return meta, body


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', text)
    return text


def markdown_to_html(body):
    """Conversion volontairement minimale : titres, paragraphes, listes."""
    out, in_list = [], False
    for raw in body.strip().splitlines():
        line = raw.rstrip()
        if not line:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        for level in (3, 2, 1):
            if line.startswith("#" * level + " "):
                out.append(f"<h{level}>{inline(line[level + 1:])}</h{level}>")
                break
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def cta(lang, slug):
    url = f"{APP_URL}/?utm_source=blog&utm_medium=seo&utm_campaign={slug}"
    if lang == "fr":
        text, button = "Ta récitation mérite un vrai retour. Récite un verset et reçois une analyse mot à mot.", "Essayer Tajweed Tutor AI →"
    else:
        text, button = "Your recitation deserves real feedback. Recite a verse and get a word-by-word analysis.", "Try Tajweed Tutor AI →"
    return f'<div class="cta"><p>{text}</p><a href="{url}">{button}</a></div>'


def page(meta, body_html, alternates, title, description, image):
    return (
        "<!doctype html>\n"
        f'<html lang="{meta["lang"]}"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f'<meta name="description" content="{html.escape(description)}">\n'
        f'<meta property="og:title" content="{html.escape(title)}">\n'
        f'<meta property="og:description" content="{html.escape(description)}">\n'
        f'<meta property="og:image" content="{image}">\n'
        '<meta property="og:type" content="article">\n'
        '<meta name="theme-color" content="#1a1a2e">\n'
        f"{alternates}\n"
        f"<style>{CSS}</style></head><body>\n"
        '<header><a class="brand" href="/">'
        f'<img src="/assets/logo.jpg" alt="Tajweed Tutor AI">Blog Tajweed</a>'
        f'<a class="pill" href="{APP_URL}">Ouvrir l\'appli</a></header>\n'
        f"<main>{body_html}</main>\n"
        f'<footer><span>© Tajweed Tutor AI · Apprendre le tajwid avec précision</span>'
        f'<a href="{APP_URL}">tajweedtutorai.com</a></footer>\n'
        "</body></html>\n"
    )


def benefits_html():
    items = [
        ("01", "Le sens", "Une lettre mal sortie peut changer le mot, et parfois le sens."),
        ("02", "La transmission", "Une manière de réciter reçue de génération en génération."),
        ("03", "La beauté", "Réciter posément, c'est ce que demande le Coran lui-même."),
    ]
    cards = "".join(
        f'<div class="benefit"><b>{n}</b><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>'
        for n, t, d in items
    )
    return f'<h2 class="section">Pourquoi le tajwid compte</h2><div class="benefits">{cards}</div>'


def index_page(groups):
    sections = []
    for lang, items in groups.items():
        if not items:
            continue
        cards = []
        for i, m in enumerate(items, 1):
            cards.append(
                f'<a class="card" href="/{lang}/{m["slug"]}/">'
                f'<span class="num">Article {i:02d} · {html.escape(m["date"])}</span>'
                f'<h3>{html.escape(m["title"])}</h3>'
                f'<p>{html.escape(m["description"])}</p>'
                f'<span class="more">Lire l\'article →</span></a>'
            )
        heading = "Articles en français" if lang == "fr" else "Articles in English"
        sections.append(f'<h2 class="section lang-title" id="{lang}">{heading}</h2><div class="grid">{"".join(cards)}</div>')

    hero = (
        '<section class="hero">'
        '<span class="kicker">Le tajwid, expliqué simplement</span>'
        '<h1>Récite le Coran<br><span>avec les bonnes règles</span></h1>'
        '<p class="lead">Makharij, madd, ghunna, qalqala : des guides clairs pour comprendre ce que tu prononces, '
        'et pourquoi chaque lettre compte.</p>'
        '<div class="actions">'
        '<a class="pill" href="#fr">Commencer par les articles →</a>'
        f'<a class="ghost" href="{APP_URL}">Analyser ma récitation</a>'
        '</div></section>'
    )
    banner = (
        '<section class="banner"><h2>Passe de la théorie à la pratique</h2>'
        '<p>Récite un verset et reçois une analyse mot à mot, avec les erreurs expliquées.</p>'
        f'<a class="pill" href="{APP_URL}">Essayer Tajweed Tutor AI →</a></section>'
    )
    body = hero + benefits_html() + "".join(sections) + banner
    return page(
        {"lang": "fr"}, body, "",
        "Blog Tajweed : apprendre le tajwid", "Articles sur le tajwid et la récitation du Coran : règles, makharij, madd, ghunna et qalqala.",
        f"{SITE_URL}/assets/logo.jpg",
    )


def copy_static():
    for rel in COPY_DIRS:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, OUT / rel, dirs_exist_ok=True)


def main():
    if not CONTENT.is_dir():
        sys.exit("Dossier content/ introuvable")

    articles = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = parse(path)
        missing = [key for key in REQUIRED if not meta.get(key)]
        if missing:
            sys.exit(f"{path.name} : champs manquants {missing}")
        if not SLUG_RE.match(meta["slug"]):
            sys.exit(f"{path.name} : slug invalide (minuscules, chiffres, tirets)")
        if meta["lang"] not in LANGS:
            sys.exit(f"{path.name} : langue inconnue '{meta['lang']}'")
        if not DATE_RE.match(meta["date"]):
            sys.exit(f"{path.name} : date au format AAAA-MM-JJ attendue")
        articles.append((meta, body))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    copy_static()

    sitemap_urls = [(f"{SITE_URL}/", None)]
    groups = {lang: [] for lang in LANGS}

    for meta, body in articles:
        lang, slug = meta["lang"], meta["slug"]
        target = OUT / lang / slug
        if target.exists():
            sys.exit(f"Doublon : {lang}/{slug}")
        target.mkdir(parents=True)

        url = f"{SITE_URL}/{lang}/{slug}/"
        alternates = f'<link rel="canonical" href="{url}">\n<link rel="alternate" hreflang="{lang}" href="{url}">'
        if meta.get("alt"):
            other = meta["alt"].strip("/").split("/")[0]
            alternates += f'\n<link rel="alternate" hreflang="{other}" href="{SITE_URL}{meta["alt"]}">'

        body_html = (
            f'<article><span class="eyebrow">Tajwid · {LANGS[lang]}</span>'
            f"<h1>{html.escape(meta['title'])}</h1>"
            f'<p class="desc">{html.escape(meta["description"])}</p>'
            f"{markdown_to_html(body)}{cta(lang, slug)}"
            f'<a class="back" href="/">← Retour au blog</a></article>'
        )
        (target / "index.html").write_text(
            page(meta, body_html, alternates, meta["title"], meta["description"], f"{SITE_URL}/assets/logo.jpg"),
            encoding="utf-8",
        )
        groups[lang].append(meta)
        sitemap_urls.append((url, meta["date"]))

    (OUT / "index.html").write_text(index_page(groups), encoding="utf-8")

    entries = []
    for loc, lastmod in sitemap_urls:
        lastmod_xml = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        entries.append(f"  <url><loc>{loc}</loc>{lastmod_xml}</url>")
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    if CUSTOM_DOMAIN:
        (OUT / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")

    print(f"OK : {len(articles)} article(s), {len(sitemap_urls)} URL dans le sitemap -> docs/")


if __name__ == "__main__":
    main()
