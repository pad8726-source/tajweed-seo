# Blog SEO et contenu Tajweed Tutor AI (version gratuite)

Blog statique + lot hebdomadaire de publications sociales, sans budget publicitaire.

## Structure

- `content/` : articles en Markdown (un fichier par article et par langue).
- `tools/build.py` : génère `docs/` (pages, sitemap, robots.txt, CNAME).
- `tools/content_pack.py` : génère `social/packs/AAAA-Wxx.md`, 5 publications par semaine.
- `social/ideas.json` : banque d'idées (script, légende, hashtags). Ajoute-en librement, il en faut au moins 5.
- `.github/workflows/weekly.yml` : lot hebdo chaque lundi, build à chaque modification de `content/`.

## Mise en place (une fois)

1. Créer un dépôt GitHub **public** `tajweed-seo` (Pages gratuit seulement sur dépôt public).
2. Y pousser ce dossier.
3. Settings > Actions > General > Workflow permissions : **Read and write**.
4. Settings > Pages : Source = *Deploy from a branch*, branche `main`, dossier `/docs`.
5. Chez le registrar du domaine : créer un enregistrement CNAME `blog` pointant vers `TON-COMPTE.github.io`.
6. Settings > Pages > Custom domain : `blog.tajweedtutorai.com`, puis cocher *Enforce HTTPS* une fois le certificat prêt.
7. Dans Google Search Console, ajouter la propriété `blog.tajweedtutorai.com` et soumettre `sitemap.xml`.

## Ajouter un article

Créer `content/AAAA-MM-JJ-slug.md` :

```
---
title: Titre de l'article
description: Description courte (moins de 160 caractères).
lang: fr
slug: slug-en-minuscules
date: 2026-11-19
alt: /en/slug-anglais/
---

Texte en Markdown : ## titres, - listes, **gras**, [liens](https://...).
```

Puis `git push`. Le workflow reconstruit le blog.

## Lancer en local

```
python3 tools/build.py
python3 tools/content_pack.py
```

## Règles du contenu

- Pas de promesse de fonctionnalité non activée en production (ex. les qirāʾāt marquées « Bientôt », le mode live).
- Pas de faux témoignages, faux profils ni faux enseignants.
- Les publications restent manuelles : TikTok Studio et Meta Business Suite, depuis le lot de la semaine.
