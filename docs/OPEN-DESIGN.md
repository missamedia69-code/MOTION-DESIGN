# Éléments repris d'OpenDesign (nexu-io/open-design)

Source : https://github.com/nexu-io/open-design, commit `07a86b1` (2026-11-09).
Seule une sélection utile aux pubs motion design a été reprise ; licences d'origine conservées
dans chaque dossier (`LICENSE`), provenance tracée dans `skills-lock.json`
(`"source": "nexu-io/open-design"`). **Aucun de leurs scripts n'est exécuté automatiquement.**

## Skills ajoutés (`.agents/skills/`, miroirs `.claude/skills/` et `agent/skills/`)

### Modèles de plans vidéo (HTML, compatibles HyperFrames) — Apache-2.0

Chaque dossier contient `SKILL.md` (mode d'emploi), `example.html` (le plan animé) et `example.md`.

| Skill | Plan | Usage pub |
|---|---|---|
| `frame-logo-outro` | logo assemblé par morceaux + halo lumineux + slogan | **fin de pub / carte de fin** |
| `frame-light-leak-cinema` | fuite de lumière, grain, bandes cinéma, grand titre | ouverture « cinéma », carton de chapitre |
| `frame-glitch-title` | titre numérique « glitch » | transition, accroche énergique |
| `frame-liquid-bg-hero` | fond fluide animé + phrase forte | ouverture, fond d'accroche |
| `frame-data-chart-nyt` | graphique éditorial animé | chiffres clés, preuve sociale |
| `vfx-text-cursor` | révélation de texte avec traînée lumineuse | phrase-choc mot à mot |
| `video-hyperframes` | animation image par image continue | base de plan |
| `mockup-device-3d` | téléphone + ordinateur en 3D avec écran HTML | mise en scène d'une appli |
| `poster-hero` | affiche verticale percutante | visuel 9:16, statut WhatsApp |

### Bibliothèques et méthodes — MIT

| Skill | Contenu |
|---|---|
| `motion-lab` | 160 exemples d'effets animés (HTML/CSS/JS + paramètres), index chinois/anglais |
| `huashu-art-motion` | 35 recettes de styles artistiques, 9 grammaires d'explication, storyboard |
| `oil-motion` | effets à partir de vidéos / séquences d'images (scripts Python/TS fournis, à lire avant usage) |
| `review-animations` | relecture critique des animations (exigence Emil Kowalski) |

## Guides de métier (`docs/craft/`) — Apache-2.0

`animation-discipline.md` (quand animer, durées, courbes, accessibilité), `anti-ai-slop.md`
(éviter l'effet « généré par IA »), `color.md`, `typography.md`, `typography-hierarchy.md`,
`laws-of-ux.md`.

## Règles d'utilisation dans ce dépôt

1. **Rendre autonome avant rendu** : les `example.html` chargent Tailwind (`cdn.tailwindcss.com`) et
   des polices Google Fonts. Le rendu HyperFrames doit être déterministe et hors CDN : copier les
   polices dans `projects/<pub>/vendor/` (`@font-face` local) et remplacer Tailwind CDN par du CSS
   écrit ou compilé (voir docs/HYPERFRAMES.md, procédure H2).
2. **Adapter, ne pas recopier tel quel** : couleurs, typo et logo de la marque cliente ; textes en français.
3. Pour les icônes et objets 3D, utiliser `./md elements` (docs/ELEMENTS.md).

## Non repris (volontairement)

- L'application OpenDesign elle-même (interface web/desktop).
- Les 154 `design-systems` : beaucoup imitent de vraies marques (Airbnb, BMW, Stripe…).
- Les skills liés à des API payantes (fal-*, venice-*, replicate, sora…) et les fiches « curated »
  vides qui renvoient vers d'autres dépôts.
- Leur `motion-design` (doublon avec le skill existant du même nom).
