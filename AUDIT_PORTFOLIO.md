# Audit complet — Portfolio Deremy Jules

> Audit réalisé le 3 mai 2026 sur l'état du dépôt `projet/astro`.
> Stack identifiée : Astro 6 (template Blog) + MDX + Sitemap + Sharp.
> Hébergement annoncé : GitHub Pages.

---

## PHASE 1 — Exploration & cartographie

### 1.1 Stack technique réelle

| Couche | Détail |
|---|---|
| Framework | Astro `^6.0.8` (template `blog`) |
| Intégrations | `@astrojs/mdx ^5.0.2`, `@astrojs/sitemap ^3.7.1`, `@astrojs/rss ^4.0.17` |
| Image | `sharp ^0.34.3` (présent mais sous-exploité, voir §2.3) |
| TypeScript | `astro/tsconfigs/strict` + `strictNullChecks` |
| Runtime | Node `>=22.12.0` |
| Style | CSS vanilla scoped (un `<style>` par page), variables CSS dans `global.css` |
| Contenu | Content Collections (`src/content/blog/*.md`) |
| Analyse data | Scripts Python isolés dans `src/analysis/rlc/` (Plotly, Pandas) |

Aucune dépendance JS côté client n'est expédiée — c'est un site 100% statique. Bon point.

### 1.2 Arborescence (hors `node_modules`, `dist`, `.astro`)

```
astro/
├── astro.config.mjs              ← site = "https://example.com" 🔴
├── tsconfig.json
├── package.json                  ← name: "projet" (générique)
├── README.md                     ← README par défaut Astro, jamais personnalisé
├── .gitignore
├── public/
│   ├── favicon.ico, favicon.svg
│   ├── fonts/atkinson-{regular,bold}.woff
│   ├── images/                   ← 5 images, dont une de 17 Mo 🔴
│   │   ├── Avion.jpeg            (1.3 Mo)
│   │   ├── Me&goat.jpg           (1.7 Mo, & dans le nom 🟠)
│   │   ├── Withbro.jpg           (724 Ko)
│   │   ├── hackteam.jpg          (2.2 Mo)
│   │   └── pc.png                (17 Mo 🔴)
│   │   ❌ raspberry.jpg          (référencé dans tools.astro mais ABSENT 🔴)
│   └── charts/                   ← 13 fichiers Plotly HTML autonomes (iframes)
└── src/
    ├── consts.ts                 ← SITE_TITLE / SITE_DESCRIPTION
    ├── content.config.ts         ← Schéma Zod du blog
    ├── styles/global.css
    ├── components/
    │   ├── BaseHead.astro        (méta, OG, Twitter, RSS, sitemap, fonts)
    │   ├── Header.astro          (nav + 3 liens sociaux)
    │   ├── HeaderLink.astro
    │   ├── Footer.astro
    │   └── FormattedDate.astro
    ├── layouts/
    │   └── BlogPost.astro        (utilisé seulement par les articles)
    │   ❌ Aucun Layout générique pour les pages — chaque page redéclare <html><head><body>
    ├── content/blog/
    │   └── from-business-to-data.md   (un seul article)
    ├── assets/                   ← images placeholder Astro non utilisées
    │   └── blog-placeholder-{1..5}.jpg + about
    ├── pages/
    │   ├── index.astro           (Home)
    │   ├── about.astro
    │   ├── projects.astro
    │   ├── tools.astro
    │   ├── projects/
    │   │   ├── altia.astro
    │   │   ├── samsung-analytics.astro
    │   │   ├── web3.astro        (RLC)
    │   │   └── ecommerce.astro
    │   ├── blog/
    │   │   ├── index.astro
    │   │   └── [...slug].astro
    │   └── rss.xml.js
    │   ❌ Pas de 404.astro
    └── analysis/rlc/             (sources Python — devraient être hors src/, voir §2.6)
```

### 1.3 Fichiers de configuration

- `astro.config.mjs` : `site: 'https://example.com'` — **placeholder jamais remplacé**. Casse `canonical`, `Open Graph`, `sitemap`, `RSS`. Bug critique pour le SEO et le partage.
- `tsconfig.json` : strict, OK.
- `.gitignore` : couvre `dist/`, `.astro/`, `node_modules/`, `.env*`, `.DS_Store`. OK — mais `.DS_Store` est encore présent dans le repo, ce qui veut dire qu'ils ont été commités avant l'ajout de la règle (voir §2.6).
- Aucun `.env.example`, aucun `.nvmrc`, aucun `.editorconfig`, aucun `.prettierrc`, aucun `.eslintrc`, aucun workflow `.github/`. Pour un portfolio développeur c'est minimal mais cohérent (site statique sans secrets).

### 1.4 Structure générale

10 routes au total : Home, About, Projects (index + 4 cas), Tools, Blog (index + slug). 1 article publié. Le code suit la convention Astro de manière propre, mais **sans factorisation** : chaque page redéclare son `<!doctype>`, son `<html>`, son `<head>`, ses styles. Ça représente ~300 lignes de duplication (voir §2.1).

---

## PHASE 2 — Audit du code

### 2.1 Qualité & lisibilité

**Ce qui va bien**
- Variables CSS centralisées dans `global.css` (`--accent`, `--bg`, etc.) — palette cohérente.
- TypeScript strict actif, `interface Props` correctement typé dans `BaseHead.astro` et `FormattedDate.astro`.
- Composants découpés proprement (`Header`, `Footer`, `HeaderLink`, `BaseHead`).
- Naming des fichiers de page cohérent (`kebab-case`, pluriels logiques).

**Ce qui ne va pas**

🟠 **Aucun layout partagé pour les pages** (sauf le blog). Chaque page d'`src/pages/` redéfinit la même coquille HTML :

```astro
<!doctype html>
<html lang="en">
  <head>
    <BaseHead ... />
    <style>/* 200+ lignes de CSS scoped */</style>
  </head>
  <body>
    <Header />
    <main>...</main>
    <Footer />
  </body>
</html>
```

C'est dupliqué dans 7 fichiers (`index`, `about`, `projects`, `tools`, et les 4 sous-pages projet). **Correction** : créer `src/layouts/BasePage.astro` qui prend `title`, `description` et `<slot />`, puis remplacer la coquille dans chaque page.

🟠 **CSS dupliqué massivement**. Les blocs `.project-tag`, `.tech-tag`, `.section-label`, `.divider`, `.meta-grid`, `.meta-item`, `.learnings`, `.learning-item`, `.nav-projects`, `.back-link` sont **copiés-collés à l'identique** dans `altia.astro`, `samsung-analytics.astro`, `web3.astro` et `ecommerce.astro`. Estimation : ~600 lignes de CSS strictement redondant.
**Correction** : extraire ces classes vers `global.css` ou créer `src/styles/project.css` importé par un layout `ProjectLayout.astro`.

🟡 **Absence totale de commentaires** dans les pages métier. Pour un portfolio ce n'est pas grave, mais une ou deux balises `{/* Section X */}` aideraient à se relire.

🟡 **`name` du package = `"projet"`** — générique. Renommer en `deremy-portfolio` ou `jules-deremy-site`.

### 2.2 Bonnes pratiques

🟠 **DRY** : voir §2.1.

🟠 **`target="_blank"` sans `rel="noopener noreferrer"`** sur quasiment tous les liens externes. Risque mineur de tabnabbing, et c'est aussi un point checké par Lighthouse.
**Fichiers concernés** :
- `src/components/Header.astro` lignes 16, 22 — liens LinkedIn et GitHub
- `src/components/Footer.astro` lignes 12, 13 — idem
- `src/pages/projects/web3.astro` ligne 335 — lien Dune
- `src/pages/projects/ecommerce.astro` ligne 375 — lien GitHub

**Correction** :
```astro
<a href="https://..." target="_blank" rel="noopener noreferrer">…</a>
```

🟡 **Le composant `HeaderLink` calcule `isActive` proprement** mais utilise un nommage CSS qui se base sur la cascade : la classe `active` est appliquée à `<a>`, mais les styles `.internal-links a.active` sont définis dans `Header.astro` (parent). Ça marche mais c'est fragile — si on réutilisait `HeaderLink` ailleurs, le style ne suivrait pas. À documenter ou à internaliser.

### 2.3 Performance

🔴 **`public/images/pc.png` = 17 Mo**. C'est probablement le plus gros problème de performance du site. Une PNG full-resolution chargée en `<img>` non optimisée. À 17 Mo, sur un mobile en 4G, ça gèle la page.
**Correction** :
1. Convertir en WebP : `cwebp -q 80 pc.png -o pc.webp` → typiquement <500 Ko.
2. Mieux : déplacer dans `src/assets/` et utiliser `<Image>` d'Astro (Sharp est déjà installé) :
```astro
import { Image } from 'astro:assets';
import pc from '../assets/pc.png';
<Image src={pc} alt="..." widths={[400, 800]} sizes="(max-width: 600px) 100vw, 400px" />
```
Astro génèrera AVIF/WebP responsifs automatiquement.

🟠 **Toutes les images de `public/images/` sont non-optimisées** (1-17 Mo). Total ~22 Mo pour 5 images sur un site qui en charge 4 sur la page About. Même traitement à appliquer.

🟠 **Iframes Plotly non lazy-loadées**. Chaque chart Plotly fait ~4 Mo (Plotly.js inclus dans le HTML). Sur `web3.astro` il y en a **5**, sur `ecommerce.astro` **6**. Soit jusqu'à ~25 Mo de JS inutile au premier paint.
**Correction** :
```html
<iframe src="..." height="420" loading="lazy" title="..."></iframe>
```
Toutes les iframes doivent avoir `loading="lazy"` ET un `title` (pour l'a11y). Actuellement seule la moitié des iframes a un `title`.

🟠 **Plotly est chargé 5 fois sur la même page** (un fichier HTML par chart, chacun re-embed Plotly.js). Sur `ecommerce.astro`, c'est ~25 Mo téléchargés alors qu'un seul Plotly de 4 Mo suffirait.
**Correction long terme** : utiliser `Plotly.write_html(..., include_plotlyjs='cdn')` côté Python pour que tous les charts pointent vers la même CDN, ou intégrer Plotly directement dans la page Astro et n'envoyer que les `figure.to_json()`.

🟡 **`box-shadow` triple sur `.card`** dans `global.css` — sympa visuellement, coûteux au repaint. À garder mais à surveiller si ajout d'animations.

🟡 **Animation `pulse` infinie** dans le Hero (le point vert qui pulse). Reflow CSS continu, mineur mais à savoir.

### 2.4 Accessibilité

**Ce qui va bien**
- `aria-label` sur les icônes sociales du Header.
- `alt` présent sur toutes les `<img>` (sauf l'image hero du blog : `alt=""` ligne 63 de `BlogPost.astro` — discutable mais acceptable si décoratif).
- Police Atkinson Hyperlegible (très bien pour la lisibilité, choix conscient).
- Classe `.sr-only` définie correctement.
- Contraste : `--accent` (#0D9488) sur `--accent-light` (#CCFBF1) — ratio ~4.7:1, OK pour AA.
- `<time datetime="...">` correctement utilisé dans `FormattedDate`.

**Ce qui ne va pas**

🟠 **`<html lang="en">` partout, mais le site est destiné à un marché Genève/France**. Si tu vises aussi du recruteur francophone, soit tu passes en `fr`, soit tu maintiens l'anglais et tu assumes 100% du contenu anglais (ce n'est pas le cas, voir §3 pour les `title=` d'iframes en français).

🟠 **`<iframe>` sans titre dans `web3.astro`** (5 sur 5 sans title). C'est un échec WCAG 2.1 (4.1.2). Corrigé sur `ecommerce.astro` mais oublié sur `web3.astro`.

🟠 **Aucun `skip to content`**. Pour la nav clavier, ajouter au début du `<body>` :
```html
<a href="#main-content" class="sr-only">Skip to content</a>
```
et `id="main-content"` sur `<main>`.

🟡 **Boutons sociaux** (Header) : SVG inline sans `<title>` interne. L'`aria-label` couvre le besoin, mais ajouter `<title>LinkedIn</title>` à l'intérieur du SVG améliore le rendu screen reader.

🟡 **Animation `pulse`** : aucun `prefers-reduced-motion` respecté. Ajouter :
```css
@media (prefers-reduced-motion: reduce) {
  .hero-eyebrow-dot { animation: none; }
  .project-card, .post-card, .btn { transition: none; }
}
```

🟡 **Couleurs sémantiques uniquement**. Les badges `MVP on hold` (couleur orange) sont distingués par couleur seule sans icône ni texte additionnel — limite pour le daltonisme. Le statut `Setting up` même problème.

### 2.5 SEO technique

**Ce qui va bien**
- `BaseHead.astro` est solide : `meta description`, `og:*`, `twitter:*`, `canonical`, `link rel="sitemap"`, RSS auto-discovery.
- Sitemap généré (`@astrojs/sitemap`).
- Structure HTML sémantique correcte (`<header>`, `<main>`, `<footer>`, `<section>`, `<article>` dans le blog).
- `<title>` unique et descriptif sur chaque page.

**Ce qui ne va pas**

🔴 **`site: 'https://example.com'` dans `astro.config.mjs`**. Conséquences :
- Tous les `<link rel="canonical">` pointent vers `example.com/...`
- Le sitemap publié liste `example.com/about`, etc.
- Les `og:image`, `og:url`, `twitter:url` pointent vers `example.com`
- Le RSS `xmlns:atom self` pointe vers `example.com`

→ Google indexera mal et les previews LinkedIn/Twitter seront cassées.
**Correction immédiate** : remplacer par l'URL prod (par ex. `https://jules-deremy.github.io` ou ton domaine custom).

🔴 **Pas de `robots.txt`**. À créer dans `public/robots.txt` :
```
User-agent: *
Allow: /
Sitemap: https://<TON_URL>/sitemap-index.xml
```

🟠 **Pas d'image OG par défaut adaptée**. `BaseHead` retombe sur `assets/blog-placeholder-1.jpg` (placeholder Astro générique). Une image OG dédiée 1200x630 avec ton nom + titre améliorerait les partages LinkedIn / X / Slack.

🟠 **Pas de balisage JSON-LD `Person`**. Pour un portfolio personnel c'est l'élément structuré le plus utile :
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Jules Deremy",
  "jobTitle": "Data Analyst",
  "url": "https://...",
  "sameAs": [
    "https://www.linkedin.com/in/jules-deremy",
    "https://github.com/Jules-Deremy"
  ]
}
</script>
```

🟡 **Pas de `<meta name="author">`** ni `<meta name="theme-color">`.

🟡 **Pas d'`<meta name="keywords">`** — c'est OK, Google ne s'en sert plus, mais Bing/DDG si.

🟡 **Single H1 par page** — bien. À conserver. Vérifier que `index.astro` n'a qu'un seul H1 (c'est le cas).

### 2.6 Responsive

**Ce qui va bien**
- `clamp()` utilisé sur les H1 (`clamp(2em, 5vw, 3.4em)`) — fluide.
- Media queries `max-width: 600px` / `720px` cohérentes.
- `grid-template-columns: repeat(auto-fill, minmax(...))` partout — auto-responsive.
- Header collapse correctement (les social icons disparaissent <600px).

**Ce qui ne va pas**

🟠 **Largeur fixe `width: 740px`** sur `<main>` dans `global.css`. C'est combiné à `max-width: calc(100% - 2em)` donc ça fonctionne, mais `width: 100%; max-width: 740px;` est plus idiomatique et évite des reflows.

🟡 **`.timeline-item` sur mobile** : grid `110px 1fr` non remplacé en mobile. Sur petit écran les années sont écrasées à 110px alors qu'elles pourraient passer au-dessus du contenu. Tester sous 360px.

🟡 **Photos About** (`Me&goat.jpg`, `hackteam.jpg`) : `height: 240px` fixe sans ratio adaptatif. Sur très petit mobile l'image se crop différemment de ce qui est attendu.

### 2.7 Sécurité

**Ce qui va bien**
- Pas de secrets exposés dans le repo (vérifié : aucun `.env`, aucune clé API en dur).
- Pas de `dangerouslySetInnerHTML` ni équivalent.
- Pas d'utilisation de `eval`.

**Ce qui ne va pas**

🟠 **`target="_blank"` sans `rel="noopener noreferrer"`** — déjà mentionné. C'est une vulnérabilité réelle (tabnabbing).

🟠 **Pas d'en-têtes de sécurité configurés**. Sur GitHub Pages ce n'est pas configurable mais sur Vercel/Netlify/Cloudflare on peut ajouter CSP, X-Content-Type-Options, etc. À considérer si tu changes d'hébergeur.

🟡 **Iframes sans `sandbox`**. Tes charts Plotly proviennent de ton propre `public/`, donc le risque est nul, mais par principe ajouter `sandbox="allow-scripts"` aux iframes Plotly est une bonne hygiène.

### 2.8 Gestion des erreurs

🔴 **Pas de page 404 personnalisée**. Astro génère un `404.html` générique. Créer `src/pages/404.astro` :
```astro
---
import BaseHead from '../components/BaseHead.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
---
<!doctype html>
<html lang="en">
  <head><BaseHead title="404 — Page not found" description="..." /></head>
  <body>
    <Header />
    <main>
      <h1>404</h1>
      <p>This page doesn't exist (yet). <a href="/">Back home</a></p>
    </main>
    <Footer />
  </body>
</html>
```

🟠 **État vide du blog** : `blog/index.astro` ligne 137-138 affiche "No posts yet. Check back soon." — bien géré ✅. C'est un bon exemple à suivre pour le reste.

🟠 **`projects.astro` ligne 232-242** : carte "More projects coming soon" — correct mais en dashed border opacité 0.6, c'est bien.

🟡 **Pas de fallback si `getCollection` échoue** dans `blog/index.astro`. Très improbable en build static, mais à savoir.

### 2.9 Hygiène du repo

🟠 **`.DS_Store` versionnés** (visible dans le `find`). Le `.gitignore` les exclut maintenant, mais ils sont déjà dans l'historique. À nettoyer :
```bash
git rm --cached -r $(find . -name ".DS_Store" -not -path "./node_modules/*")
git commit -m "chore: remove .DS_Store from tracking"
```

🟠 **`src/analysis/rlc/`** : scripts Python (`analyse.py`, `token_analysis.py`) + données CSV + charts HTML générés. Ces fichiers ne sont **pas utilisés par Astro** (les charts servis sont dans `public/charts/`). Ils gonflent le repo et exposent ta data brute. Deux options :
1. Les sortir de `src/` (par ex. `analysis/rlc/` à la racine, ou un repo séparé), et juste copier les `.html` finaux dans `public/charts/`.
2. Les laisser mais déplacer dans `tools/` ou `scripts/` à la racine, **hors `src/`**.

🟡 **Charts dupliqués** : les mêmes `chart1..5.html` sont à la fois dans `public/charts/` et dans `src/analysis/rlc/charts/`. Source de divergence.

🟡 **Pas de `.editorconfig`** — utile pour assurer la cohérence d'indentation entre VS Code et un éventuel collaborateur.

---

## PHASE 3 — Audit du contenu

### 3.1 Hero / Introduction (Home)

**Forces**
- Accroche claire et personnelle : *"Hi, I'm Deremy. Data analyst with a builder mindset."*
- Eyebrow status `Open to opportunities · Geneva area` avec dot animé — efficace pour signaler la disponibilité.
- Sous-titre concis qui positionne le mix analytics / Web3 / privacy.
- 2 CTA bien hiérarchisés (View my work / About me).

**Faiblesses**
- 🟡 *"builder mindset"* est un peu cliché LinkedIn. Si tu veux le garder, prouve-le immédiatement après — tu le fais en partie avec "Currently" mais pas dans le hero.
- 🟡 La proposition de valeur ne dit pas **pour qui** tu construis. Une ligne du type "I help [companies / Web3 teams / brands] turn messy data into business decisions" rendrait plus opérationnel.
- 🟡 Pas de date de disponibilité explicite dans le hero (elle est dans le footer et plus bas). À monter.

### 3.2 À propos (About)

**Forces**
- Storytelling honnête, ton authentique : *"I do not pretend to know everything"*.
- Timeline claire avec rôle + contexte.
- Section "How I work" = 3 valeurs précises et différenciantes (curiosité, propreté des données, humilité).
- "Outside of work" donne de la personnalité (boxe, aviation, Pi 5, Corse).

**Faiblesses**
- 🟠 **Timeline** : 3 entrées sont labellisées **2024** d'affilée (Cheil, Master's, iExec). Le lecteur ne sait plus dans quel ordre lire. Ajouter le mois (Nov 2024, Sep 2024, Jan 2024) ou repenser la granularité (par ex. *"2024–2026"* pour Cheil).
- 🟠 **`Cheil France — Digital Data Analyst`** : tu écris "Two years managing analytics for Samsung France" alors que dans `samsung-analytics.astro` la durée est *"Nov 2024 – Sept 2026"*, soit **22 mois et non 24**. À uniformiser ("Almost 2 years" ou "22 months" — les deux fonctionnent).
- 🟡 *"Not your typical data analyst"* est un titre fort, mais légèrement défensif. Préfère une formulation positive du type *"From business school to data — by way of Web3"*.
- 🟡 Aucune mention de **langues parlées** (tu es franco-corse, tu as fait des entretiens en anglais à iExec — c'est un atout pour Genève multilingue).
- 🟡 Aucune mention de **certifications** (Adobe Analytics, GA4, dbt, etc. — même celles de Coursera comptent).

### 3.3 Compétences (Skills)

**Forces**
- Skills bar visible dès le hero (10 tags).
- Page "Tools" séparée avec descriptions personnelles — beaucoup mieux que la liste plate type LinkedIn.

**Faiblesses**
- 🟠 **Aucun niveau de maîtrise indiqué**. Dans la page Tools, tu écris parfois "Intermediate level, used with Snowflake" pour SQL — bien. Mais pour Adobe Analytics, Power BI ou Python, le lecteur ne sait pas si tu es senior ou junior. Ajouter explicitement (Beginner / Intermediate / Advanced) ou en mots ("daily for 2 years", "comfortable with").
- 🟠 La skills bar de la home contient `Snowflake`, `Web3`, `Prompt Engineering` mais ces compétences ne sont **pas reprises ni détaillées ailleurs**. `Snowflake` n'est mentionné qu'une fois ("Intermediate level"), `Prompt Engineering` jamais ailleurs. Soit tu les enlèves, soit tu les illustres.
- 🟡 Pas de séparation "Data Analytics / Programming / BI / DataViz / Cloud" — la liste est plate. Pour un recruteur ça aiderait à scanner.
- 🟡 `n8n` est listé comme skill mais positionné en Dev tools. C'est plutôt un outil d'automatisation / no-code. À reclasser.

### 3.4 Projets (Projects)

**Forces**
- 4 projets déployés en pages dédiées avec un schéma cohérent (hero, meta-grid, problème/solution, tech stack, learnings, navigation).
- Chaque projet a une **honest status** ("MVP on hold", "Resuming after graduation") — très professionnel et rare.
- Section "What I learned" sur chaque projet : excellent.
- Chiffres concrets sur RLC (57K transferts, 356M RLC, 6.3M USD) et Ecommerce (£10.3M, 540K transactions). Crédibilité immédiate.

**Faiblesses**
- 🔴 **`ecommerce.astro` ligne 375 : lien GitHub cassé**. `https://github.com/julesderemy/portfolio` n'existe pas ; ton vrai handle est `Jules-Deremy` (cf. Header/Footer). Le lien retournera 404.
- 🟠 **Samsung Analytics — pas de lien actionnable**. Logique (NDA), mais ajouter une preuve quelconque : screenshots floutés, témoignage manager, ou au minimum un lien LinkedIn vers un post où tu en parles.
- 🟠 **Altia — pas de lien vers une démo, un site, un pitch deck, un repo**. Même un PDF du pitch ou une vidéo de 90 secondes renforcerait. Sinon le lecteur n'a que ta parole.
- 🟠 **Web3 (RLC)** : le lien Dune est actif ✅. Mais pas de lien GitHub vers le code Python de l'analyse — alors qu'on voit dans `src/analysis/rlc/` que le code existe.
- 🟠 **Ecommerce — Tableau Public placeholder** : *"Tableau Public dashboard coming soon"* affiché publiquement. Soit tu publies, soit tu retires le placeholder.
- 🟠 **Page projets — placeholder "More projects coming soon"** : OK mais limite à 1 placeholder. Si dans 6 mois rien n'a été ajouté, ça envoie un signal négatif.
- 🟡 **Tags incohérents entre la home et la page projets**. Sur la home le projet RLC est tagué *"On-chain · Research · Python · SQL"* (ligne 365 de `index.astro`). Sur `projects.astro` c'est *"On-chain · SQL · Python"*. Sur la page détail c'est *"On-chain · SQL · Python · Dune Analytics"*. Uniformiser.
- 🟡 **Aucun visuel "before/after"** ni metric d'impact business (par ex. "réduit le temps de reporting de 40%"). Les projets décrivent le quoi et le comment, peu le résultat business mesurable.
- 🟡 **Web3 — nav-projects oublie Ecommerce** : ligne 463-464 navigue Samsung ↔ All projects, sans inclure Ecommerce. Idem dans `ecommerce.astro` ligne 575 navigue Web3 ↔ All. La chaîne Altia → Samsung → Web3 → Ecommerce doit être circulaire et complète.

### 3.5 Contact

**Forces**
- CTA "Get in touch" visible 2x sur la home et sur la page About.
- Email cliquable partout (Header + Footer + buttons).
- Lien LinkedIn et GitHub partout.

**Faiblesses**
- 🟠 **Pas de page Contact dédiée**. Pour un portfolio pro, une page `/contact` avec formulaire + adresse + LinkedIn + Calendly (15 min discovery call) est attendu. Actuellement tout repose sur un `mailto:` — ce qui marche mais c'est minimal.
- 🟠 **Pas de lien Calendly / Cal.com** pour caler un appel. C'est l'élément le plus efficace pour un job-seeking actif.
- 🟡 **Pas de signal "j'ai répondu sous 24h en moyenne"** ou équivalent. Petit détail qui rassure.
- 🟡 Email = `jules.deremy0@gmail.com` (gmail). Pour un site `jules-deremy.<tld>`, un alias `hello@<tld>` fait plus pro.

### 3.6 Ton & cohérence éditoriale

**Forces**
- Ton homogène sur tout le site : sobre, factuel, légèrement modeste mais sans fausse humilité. C'est rafraîchissant.
- Pas de jargon gratuit. Tu expliques ("MPC = Multi-Party Computation").
- Première personne assumée ("I", "I learned"), pas de troisième personne corporate.

**Faiblesses**
- 🟠 **Mélange anglais / français dans les `title=` d'iframes** (`ecommerce.astro`) : "Revenue mensuel — UCI Online Retail 2010–2011", "Top 10 produits par revenue", "Heatmap des commandes par heure et jour de la semaine". Pages en anglais, métadonnées en français. À uniformiser (probablement en anglais partout, ou alors basculer le site en français).
- 🟡 **Petits anglicismes** : "I am still building" (OK), "I do not" (forme non-contractée systématique → un peu raide). Mélanger avec quelques contractions ("I'm", "I don't") rendrait plus naturel sans sacrifier le sérieux.
- 🟡 **Apostrophes typographiques mixtes** : `’` dans certains paragraphes (ex. *"I'm excited to share"* ligne 237 de `projects.astro` avec une vraie apostrophe typographique `’`) et `'` ASCII ailleurs. Choisir une convention.

### 3.7 Liens externes

| Lien | Page(s) | Statut |
|---|---|---|
| `https://www.linkedin.com/in/jules-deremy` | Header, Footer | ✅ |
| `https://github.com/Jules-Deremy` | Header, Footer | ✅ |
| `mailto:jules.deremy0@gmail.com` | Partout | ✅ |
| `https://dune.com/jules_deremy/rlc-token-...` | web3.astro | ✅ (à vérifier en prod) |
| **`https://github.com/julesderemy/portfolio`** | **ecommerce.astro** | 🔴 **Cassé — handle incorrect** |
| Twitter / X | — | ❌ Absent (volontaire ?) |
| CV PDF | — | ❌ Absent (cf. §4.C) |
| Calendly | — | ❌ Absent |

---

## PHASE 4 — Rapport d'audit

### A. Points forts

1. **Architecture Astro propre** — site 100% statique, zero JS shipped par défaut, performance brute excellente côté framework.
2. **Identité visuelle cohérente** — palette teal `#0D9488` + crème `#F7F9F8` + Atkinson Hyperlegible, lisible et signature.
3. **`BaseHead.astro` exhaustif** — title, description, canonical, OG, Twitter, sitemap, RSS auto-discovery, font preload. Le seul bug est le `site` placeholder.
4. **Storytelling personnel** — ta page About sonne juste, ne récite pas un CV, montre du caractère.
5. **Honest status sur chaque projet** — *"MVP on hold"*, *"resuming after graduation"*, *"Setting up this week"*. Honnêteté rare et professionnelle.
6. **Données chiffrées concrètes** sur les projets (57K transferts RLC, £10.3M revenue Ecommerce, 100+ tags Adobe Launch). Crédibilité immédiate.
7. **Section "What I learned"** sur chaque projet : montre la prise de recul et la maturité analytique.
8. **Page Tools / Uses** — pratique et différenciante (rare dans les portfolios juniors).
9. **Sitemap, RSS, content collections** correctement configurés.
10. **Accessibilité de base** : alt texts, aria-labels, classe sr-only, police Atkinson.

### B. Problèmes identifiés (priorisés)

| # | Catégorie | Priorité | Problème | Fichier | Correction |
|---|---|---|---|---|---|
| B1 | SEO | 🔴 Critique | `site: 'https://example.com'` placeholder casse canonical, sitemap, OG, RSS | `astro.config.mjs:9` | Remplacer par l'URL prod réelle |
| B2 | Contenu | 🔴 Critique | Image `/images/raspberry.jpg` référencée mais inexistante | `src/pages/tools.astro:187` | Ajouter le fichier OU retirer la `<figure>` |
| B3 | Contenu | 🔴 Critique | Lien GitHub cassé `julesderemy/portfolio` (handle incorrect) | `src/pages/projects/ecommerce.astro:375` | `https://github.com/Jules-Deremy/<repo>` |
| B4 | Performance | 🔴 Critique | `pc.png` = 17 Mo non optimisé | `public/images/pc.png` | Convertir WebP <500 Ko, déplacer en `src/assets/`, utiliser `<Image>` |
| B5 | UX | 🔴 Critique | Pas de page 404 personnalisée | manquant | Créer `src/pages/404.astro` |
| B6 | SEO | 🔴 Critique | Pas de `robots.txt` | manquant | Créer `public/robots.txt` |
| B7 | Performance | 🟠 Important | 4 autres images 700 Ko – 2.2 Mo non optimisées | `public/images/*` | WebP + `<Image>` |
| B8 | Performance | 🟠 Important | Iframes Plotly sans `loading="lazy"` | `web3.astro`, `ecommerce.astro` | Ajouter `loading="lazy"` |
| B9 | Accessibilité | 🟠 Important | 5 iframes sans `title=` dans `web3.astro` | `web3.astro:354,367,380,394,407` | Ajouter `title` à chaque iframe |
| B10 | Sécurité | 🟠 Important | `target="_blank"` sans `rel="noopener noreferrer"` | Header, Footer, web3, ecommerce | Ajouter `rel="noopener noreferrer"` |
| B11 | DRY | 🟠 Important | Pas de Layout partagé pour les pages | toutes les pages sauf blog | Créer `src/layouts/BasePage.astro` |
| B12 | DRY | 🟠 Important | CSS dupliqué dans les 4 pages projets (~600 lignes) | `projects/*.astro` | Extraire vers `global.css` ou `ProjectLayout.astro` |
| B13 | Contenu | 🟠 Important | Cheil "Two years" mais durée réelle = 22 mois (Nov 24 → Sept 26) | `about.astro:330`, `samsung-analytics.astro:249` | Uniformiser |
| B14 | Contenu | 🟠 Important | Timeline About : 3 items avec année "2024" sans ordre clair | `about.astro:319-360` | Ajouter mois ou bornes (ex. "2024–2026") |
| B15 | Contenu | 🟠 Important | Tableau Public placeholder publié | `ecommerce.astro:484-501` | Publier ou supprimer le bloc |
| B16 | UX | 🟠 Important | Pas de page Contact dédiée ni Calendly | manquant | Créer `/contact` |
| B17 | SEO | 🟠 Important | Pas d'image OG dédiée (fallback = placeholder Astro) | `BaseHead.astro:6` | Créer `public/og-image.png` 1200×630 personnalisé |
| B18 | SEO | 🟠 Important | Pas de JSON-LD `Person` | `BaseHead.astro` | Ajouter le bloc structured data |
| B19 | Contenu | 🟠 Important | Niveaux de skills non précisés sur la home | `index.astro:319-329` | Ajouter niveaux ou regrouper par maîtrise |
| B20 | Contenu | 🟠 Important | Skills home (Snowflake, Prompt Engineering) jamais détaillés ailleurs | `index.astro:325,328` | Détailler ou retirer |
| B21 | Hygiène | 🟠 Important | Code Python (`src/analysis/rlc/`) inutilement dans `src/` | `src/analysis/` | Déplacer hors `src/` |
| B22 | Hygiène | 🟠 Important | `.DS_Store` versionnés | partout | `git rm --cached` + commit |
| B23 | Accessibilité | 🟡 Mineur | Pas de "Skip to content" | toutes pages | Ajouter le lien d'évitement |
| B24 | Accessibilité | 🟡 Mineur | Pas de `prefers-reduced-motion` | `global.css`, `index.astro` | Ajouter media query |
| B25 | Contenu | 🟡 Mineur | Mélange anglais/français dans `title=` iframes | `ecommerce.astro:396-467` | Tout passer en anglais |
| B26 | Performance | 🟡 Mineur | Plotly.js embarqué dans chaque chart HTML (~4 Mo × 5–6) | `public/charts/*.html` | Régénérer avec `include_plotlyjs='cdn'` |
| B27 | UX | 🟡 Mineur | Nav projets non circulaire (Web3 ↔ All ; Ecommerce ↔ All) | `projects/*.astro` | Chaîner Altia → Samsung → Web3 → Ecommerce → Altia |
| B28 | Code | 🟡 Mineur | Tags projet incohérents entre home / index projets / page détail | `index.astro`, `projects.astro`, `web3.astro` | Source unique |
| B29 | Code | 🟡 Mineur | `package.json` name = `"projet"` | `package.json:2` | Renommer `deremy-portfolio` |
| B30 | Code | 🟡 Mineur | README = template Astro par défaut | `README.md` | Réécrire pour ton projet |
| B31 | Hygiène | 🟡 Mineur | Pas de `.editorconfig`, `.prettierrc`, `.nvmrc` | manquant | Ajouter pour la rigueur dev |
| B32 | Contenu | 🟡 Mineur | Filename `Me&goat.jpg` contient `&` (caractère spécial URL) | `public/images/` | Renommer `me-and-goat.jpg` |
| B33 | Contenu | 🟡 Mineur | Pas de Twitter/X dans les liens sociaux | Header, Footer | Ajouter ou justifier l'absence |

### C. Ce qui manque (gaps de portfolio professionnel)

**Fichiers techniques manquants**
- ❌ `public/robots.txt`
- ❌ `src/pages/404.astro`
- ❌ `public/og-image.png` (image OG dédiée)
- ❌ `apple-touch-icon.png` (iOS home screen)
- ❌ `site.webmanifest` (PWA basique, optionnel)
- ❌ README de projet personnalisé (actuel = template Astro)
- ❌ `LICENSE` (si tu open-sources le repo)
- ❌ `.github/workflows/deploy.yml` visible (si déploiement GitHub Pages)
- ❌ `.editorconfig`, `.prettierrc`, `.nvmrc`

**Éléments de contenu manquants**
- ❌ **CV téléchargeable en PDF** (lien dans Header / About / Contact)
- ❌ **Page Contact dédiée** avec formulaire (Formspree/Netlify Forms) ou Calendly
- ❌ **Section témoignages / recommandations** (idéalement 2-3 quotes de manager Cheil, prof, partenaire Altia)
- ❌ **Section certifications / diplômes** (Master, BIA, certifs Adobe/Google/Coursera)
- ❌ **Niveaux de langues** (FR natif, EN avancé, ES/IT/CN…)
- ❌ **Section "Now"** dynamique (tu as "Currently" sur la home — peut devenir une page `/now` style nownownow.com)
- ❌ **Plus de contenu blog** (1 seul article publié — viser 1/mois minimum)
- ❌ **Newsletter / RSS visible** (le RSS existe mais aucun bouton "Subscribe")
- ❌ **Métriques d'impact business** sur les projets (KPIs, % d'amélioration, ROI)
- ❌ **Vidéo / loom de présentation** (90 sec) — différencie énormément
- ❌ **Timeline plus visuelle** dans About (mois/année, durées explicites)

**Fonctionnalités absentes**
- ❌ **Dark mode** (palette teal s'y prête bien)
- ❌ **Toggle de langue FR/EN** (utile pour Genève)
- ❌ **Recherche dans le blog** (Pagefind, ultra léger)
- ❌ **Tags / catégories** sur les articles
- ❌ **Analytics privacy-friendly** (Plausible, Umami, Cabin) — pour mesurer ce qui marche
- ❌ **Cookies banner** (non requis si pas de tracking — à confirmer une fois Analytics ajouté)
- ❌ **Lien direct vers projets sur la home** (les cartes projet n'ont pas de tag visible "Lire l'étude de cas →")

**Éléments de crédibilité manquants**
- ❌ Logos clients (Samsung, iExec, Cheil) avec leur permission visuelle
- ❌ Liens vers articles publiés / interventions / conférences
- ❌ Mentions "as seen on / featured in" si applicable
- ❌ Stats GitHub (commits/an, contributions OSS) — embed shields.io

### D. Recommandations priorisées

#### Niveau 1 — À faire immédiatement (bloquants ou très impactants, < 2h)

1. **Corriger `site` dans `astro.config.mjs`** (B1). Une ligne, fixe le SEO, le sitemap, l'OG.
2. **Réparer le lien GitHub Ecommerce** (B3) avec ton vrai handle.
3. **Réparer ou retirer l'image Raspberry manquante** (B2). Soit tu ajoutes `raspberry.jpg`, soit tu commentes le bloc.
4. **Optimiser `pc.png`** (B4). Conversion WebP + déplacement vers `src/assets` + composant `<Image>`. Gain : -16 Mo.
5. **Créer `public/robots.txt`** (B6).
6. **Créer `src/pages/404.astro`** (B5).
7. **Ajouter `rel="noopener noreferrer"` sur tous les `target="_blank"`** (B10).
8. **Ajouter `loading="lazy"` + `title=` sur toutes les iframes** (B8, B9).
9. **Uniformiser la durée Cheil** (B13) et la chronologie de la timeline About (B14).
10. **Retirer ou publier le placeholder Tableau Public** (B15).

#### Niveau 2 — À faire dans les 2 semaines

11. **Créer `BasePage.astro` et `ProjectLayout.astro`** (B11, B12). Refactor de fond — paie sur tout ajout futur.
12. **Optimiser les autres images** (B7) avec `<Image>`.
13. **Ajouter une page Contact** avec formulaire et Calendly (B16).
14. **Ajouter un CV PDF téléchargeable** (lien Header + bouton About).
15. **Image OG personnalisée** (B17) — un Figma rapide 1200×630 avec ton nom + tagline.
16. **JSON-LD `Person`** dans `BaseHead.astro` (B18).
17. **Niveaux de skills explicites** (B19) et nettoyage des skills orphelines (B20).
18. **Déplacer `src/analysis/` hors de `src/`** (B21) et nettoyer les `.DS_Store` (B22).
19. **Skip to content + prefers-reduced-motion** (B23, B24).
20. **Renommer `Me&goat.jpg`** (B32).
21. **Réécrire le README** (B30) et renommer le `package.json` (B29).

#### Niveau 3 — Améliorations à long terme

22. **Plus d'articles de blog** (1/mois) — c'est ce qui fait revenir les recruteurs.
23. **Section témoignages** (3 quotes minimum) — la crédibilité maximum.
24. **Dark mode** + **toggle FR/EN**.
25. **Analytics privacy-friendly** (Plausible / Umami).
26. **Recherche blog** avec Pagefind (5 min à intégrer).
27. **Refactor Plotly** : sortir Plotly de chaque HTML (CDN), ou intégrer en natif via `<script>` sur la page projet.
28. **Vidéo loom de 90 sec** sur la home, embarquée en `<video>` ou link YouTube unlisted.
29. **Page `/now`** dynamique (recommandée par Derek Sivers).
30. **Newsletter** (Buttondown, ConvertKit ou simple RSS-to-email).

---

## PHASE 5 — Checklist portfolio développeur professionnel

### Identité & message
- ✅ Nom et titre clairs sur la home
- ✅ Tagline / proposition de valeur
- ✅ Photo / portrait personnel (présent dans About, pas en home — acceptable)
- ✅ Disponibilité affichée (eyebrow + footer)
- ❌ CV téléchargeable en PDF
- ❌ Vidéo de présentation 60-90 sec
- ❌ Niveaux de langues parlées

### Navigation & structure
- ✅ Header sticky avec liens principaux
- ✅ Footer avec liens sociaux
- ✅ État "active" sur le lien courant
- ✅ Liens sociaux (LinkedIn, GitHub, Email)
- ❌ Page Contact dédiée
- ❌ Lien vers CV
- ❌ Calendly / cal.com

### Contenu — Projets
- ✅ Page index Projects
- ✅ Études de cas dédiées (4)
- ✅ Tech stack visible par projet
- ✅ Section "What I learned" par projet
- ✅ Statut honnête par projet (MVP on hold, etc.)
- ✅ Chiffres concrets / KPIs par projet
- ❌ Lien GitHub fonctionnel pour chaque projet (1 cassé)
- ❌ Live demo / pitch deck pour Altia
- ❌ Témoignages clients
- ❌ Métriques d'impact business explicites

### Contenu — À propos
- ✅ Storytelling personnel
- ✅ Timeline parcours
- ✅ Valeurs / méthode de travail
- ✅ Centres d'intérêt
- ❌ Certifications listées
- ❌ Recommandations LinkedIn embarquées
- ❌ Logos clients/écoles

### Contenu — Compétences
- ✅ Skills bar visible
- ✅ Page Tools / Uses détaillée
- ❌ Niveaux de maîtrise
- ❌ Catégorisation par domaine

### Contenu — Blog
- ✅ Section blog active
- ✅ Article publié (1)
- ✅ RSS feed
- ✅ Metadata (date, description)
- ❌ Plusieurs articles (au moins 3-5)
- ❌ Tags / catégories
- ❌ Recherche
- ❌ Bouton "Subscribe" visible

### Technique — Performance
- ✅ Site statique (Astro)
- ✅ Police préchargée
- ✅ Pas de JS shipped par défaut
- ❌ Images optimisées (WebP/AVIF)
- ❌ Lazy loading des iframes
- ❌ Plotly partagé en CDN
- ❌ Lighthouse > 90 sur tous les axes (à mesurer après corrections)

### Technique — SEO
- ✅ Title unique par page
- ✅ Meta description
- ✅ Canonical URL
- ✅ Open Graph
- ✅ Twitter Card
- ✅ Sitemap.xml généré
- ✅ RSS feed
- ❌ `site` URL correcte (placeholder à corriger)
- ❌ robots.txt
- ❌ JSON-LD Person
- ❌ Image OG dédiée

### Technique — Accessibilité
- ✅ alt sur les images
- ✅ aria-label sur les icônes
- ✅ Police accessible (Atkinson Hyperlegible)
- ✅ Contraste suffisant
- ✅ Classe sr-only
- ❌ Skip to content
- ❌ prefers-reduced-motion
- ❌ Title sur toutes les iframes
- ❌ Lang correct si bilingue
- ❌ Test lecteur d'écran complet

### Technique — Sécurité & robustesse
- ✅ Pas de secrets exposés
- ✅ HTTPS (assuré par GitHub Pages)
- ❌ rel="noopener noreferrer" sur target="_blank"
- ❌ Page 404 personnalisée
- ❌ Headers CSP (impossible sur GH Pages mais à noter)

### Technique — Hygiène repo
- ✅ .gitignore propre
- ✅ TypeScript strict
- ❌ README personnalisé
- ❌ LICENSE
- ❌ .editorconfig / .prettierrc / .nvmrc
- ❌ .DS_Store hors versionning
- ❌ Code de scripts (Python) hors `src/`
- ❌ package.json `name` personnalisé

### Différenciation & polish
- ✅ Identité visuelle cohérente
- ✅ Ton personnel et authentique
- ✅ Page Tools (rare)
- ✅ Honest status (rare)
- ❌ Dark mode
- ❌ Toggle FR/EN
- ❌ Analytics privacy-friendly
- ❌ Page /now
- ❌ Easter egg ou détail mémorable

---

## Conclusion

Ton portfolio est **au-dessus de la moyenne pour un junior data analyst** — choix Astro pertinent, identité visuelle propre, ton authentique, projets crédibles avec chiffres et apprentissages. Les fondations sont saines.

Mais **3 bugs critiques cassent la promesse pro** : (1) le `site` placeholder qui fait planter le SEO, (2) un lien GitHub mort sur ta page Ecommerce, (3) une image Raspberry référencée mais inexistante. Ces 3 corrections représentent ~30 minutes de travail et changent tout.

À court terme (2 semaines), le travail à valeur la plus forte est : **optimiser les images** (-22 Mo), **factoriser les layouts**, **ajouter un CV PDF**, **page Contact + Calendly**. C'est ce qui transforme un portfolio "joli" en portfolio "qui convertit".

À long terme, ce qui manque le plus pour passer du junior au confirmé visible, ce sont **les preuves sociales** (témoignages, certifications, blog actif) et **les métriques d'impact business** sur les projets. Tu sais raconter ce que tu as fait — la prochaine étape est de prouver l'impact mesurable.

— Audit terminé.
