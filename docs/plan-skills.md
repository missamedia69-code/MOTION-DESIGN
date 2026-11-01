# Plan d'usage des skills du moteur MOTION-DESIGN

Ce document décrit **tous les skills installés dans le moteur**, leur rôle,
quand les mobiliser, et comment ils s'enchaînent dans le pipeline de
production (exemple de référence : la pub MISSA TV 360, `projects/missa-tv-360-v6`).

Les skills vivent dans `.agents/skills/` (miroir `.claude/skills/`), enregistrés
dans `skills-lock.json` (source GitHub + hash). Pour en ajouter un :
copier le dossier du skill dans les deux répertoires et ajouter l'entrée au
lock (source, sourceType, skillPath, computedHash = sha256 du SKILL.md).

---

## 1. Le nouveau skill intégré : `motion-design` (LottieFiles)

Source : `lottiefiles/motion-design-skill`. Skill **transverse** : il ne
produit pas de code HyperFrames, il fournit la *culture motion* appliquée à
toute animation (GSAP, CSS, Lottie, Spring…).

### Contenu et usage de chaque sous-module

| Fichier | Rôle | Usage dans le pipeline |
|---|---|---|
| `SKILL.md` | Checklist 8 étapes + arbre de décision | À ouvrir **avant** de chorégraphier une scène : cible émotionnelle, personnalité de mouvement, easing, hiérarchie, staggering, revue |
| `director/core-philosophy.md` | Le mouvement = émotion, pas décoration | Choisir l'intention de chaque scène (joie, urgence, élégance…) avant d'animer |
| `director/emotion-mapping.md` | Table émotion → paramètres (vitesse, easing, amplitude) | Ex. scène « prix » = urgency/impact ; scène finale = pride/confidence |
| `director/motion-personality.md` | Archétypes de personnalité de marque (playful, premium, bold…) | Fixer l'identité motion de la marque (MISSA = bold + playful) et la tenir sur toutes les scènes |
| `director/disney-principles.md` | 12 principes (squash & stretch, anticipation, follow-through…) | Donner du caractère aux pops/entrées (back.out = anticipation/overshoot) |
| `director/choreography.md` | Ordonnancement multi-éléments, regards, ordre de lecture | Séquencer titres → badges → captions ; stagger des cartes contenus |
| `director/decision-framework.md` | Arbitrer durée/easing selon le contexte | Choisir .4–.6 s power3.out pour entrées fonctionnelles, back.out pour accents |
| `director/narrative-structure.md` | Arc hook → développement → CTA | Caler la structure des pubs (hook problème → révélation → preuve → prix → CTA) |
| `director/context-adaptation.md` | Adapter le motion au format (9:16, 1:1, durée, plateforme) | Déclinaisons Reels/Stories/carré : amplitudes et tailles réduites |
| `patterns/entrance-exit.md` | Modèles d'entrée/sortie | Entrées y+autoAlpha+scale, sorties en fondu de scène (crossfades .sin) |
| `patterns/multi-element.md` | Stagger, grille 1/3, cascades | Pops séquentiels des 4 cartes contenus, badges ✕ en cascade |
| `patterns/ambient-continuous.md` | Mouvements continus d'ambiance | Ken Burns, flottement de la box, pulsation du glow, hue-rotate |
| `patterns/state-feedback.md` | Feedback d'état (succès, erreur, chargement) | Badges ✕ (douleur) → verts/CTA (résolution) |
| `reference/timing-easing-tables.md` | Tables durées/easings recommandées | Référence rapide lors de l'écriture des timelines GSAP |
| `reference/property-selection.md` | Quelle propriété animer (transform > layout) | Toujours scale/opacity/translate, jamais width/top |
| `reference/quality-checklist.md` | Checklist de revue finale | Relire chaque scène avant rendu looks (lisibilité, rythme, cohérence) |
| `reference/troubleshooting.md` | Diagnostiquer un motion raté | Corriger chevauchements, temps morts, eases par défaut |

**Règle d'emploi** : `motion-design` est consulté en phase *direction* (avant
l'écriture du HTML) et en phase *revue* (quality-checklist après la planche de
frames). Il complète `hyperframes-animation` (qui, lui, connaît les règles
techniques HyperFrames).

---

## 2. Catalogue des 22 skills et déclencheurs

### Noyau HyperFrames (toujours)
- **hyperframes** — *point d'entrée obligatoire* pour toute demande de vidéo/
  animation. C'est lui qui route vers les skills spécialisés. Toujours lire en
  premier.
- **hyperframes-core** — contrat de composition : `data-start/duration/
  track-index`, `class="clip"`, structure HTML renderable. À consulter à chaque
  écriture/édition d'`index.html`.
- **hyperframes-cli** — boucle dev CLI : `check`, `render`, `doctor`,
  `preview`, diagnostics d'échec de build/render. Utilisé à **chaque** itération
  (check 0 erreur → draft → planche → looks).
- **hyperframes-animation** — règles d'animation HyperFrames : blueprints de
  scènes multi-phases, transitions, techniques motion. Pair de `motion-design`.
- **hyperframes-keyframes** — punch-in/out, zooms, Ken Burns, reframes,
  mouvements caméra seek-safe. Pour les « clips » animés des cartes contenus.
- **hyperframes-audio** — mixage une fois l'audio placé : ducking de la musique
  sous la VO, fades, gains, automation. À utiliser pour équilibrer VO/musique/SFX.
- **hyperframes-creative** — direction créative non-animation : design spec,
  palettes, typo, narration, beats. Pour cadrer un nouveau projet.
- **hyperframes-registry** — chercher/installer des blocs du registre **avant**
  de construire un visuel à la main.
- **hyperframes-studio** — travail avec un humain dans Studio : planifier avant
  d'éditer, timeline lisible (une piste captions…).

### Médias
- **media-use** — « Media OS » : résout BGM, SFX, images, logos, voix, grade/LUT
  en fichiers locaux figés. C'est le skill qui a fourni les SFX pro
  (`whoosh`, `pop`, `riser`, `impact`, `sparkle`) et la recette des grades.
  À mobiliser dès qu'un média externe est requis.
- **embedded-captions** — captions incrustés sur vidéo talking-head (35 styles).
  Pour des déclinaisons avec présentateur.

### Workflows spécialisés (routage par type de brief)
- **product-launch-video** — URL/brief produit → vidéo promo/launch. *C'est le
  workflow naturel de la pub MISSA TV 360.*
- **faceless-explainer** — texte arbitraire → explainer sans footage.
- **general-video** — composition libre quand aucun workflow spécialisé ne colle
  (multi-scènes longs, sizzles, montages).
- **motion-graphics** — unité courte motion-first sans narration : kinetic type,
  logo sting, data-viz, lower-third.
- **music-to-video** — piste audio → vidéo synchronisée sur les beats.
- **pr-to-video** — PR GitHub → vidéo explicative de changements de code.
- **remotion-to-hyperframes** — portage Remotion → HyperFrames (uniquement sur
  demande explicite).
- **slideshow** — deck navigable (pas un MP4). Confirmer avant de produire.
- **talking-head-recut** — overlays graphiques timed sur interview/podcast.
- **figma** — import Figma → assets + tokens + storyboard → motion reconstruit.

---

## 3. Pipeline type (qui mobilise quoi)

1. **Brief** → `hyperframes` (routing) + `product-launch-video` ou `general-video`.
2. **Direction créative** → `hyperframes-creative` (palette/typo/narration) +
   `motion-design/director` (émotion, personnalité, arc narratif).
3. **Médias** → `media-use` (logo via `entrees/`, photos réelles, SFX, voix) ;
   `figma` si design fourni.
4. **Composition** → `hyperframes-core` (structure) + `hyperframes-animation` /
   `hyperframes-keyframes` (mouvements) + `motion-design/patterns` +
   `reference/timing-easing-tables` (easing/durées).
5. **Captions** → captions natifs de la compo (style pub) ou
   `embedded-captions` (talking-head).
6. **Audio** → VO (`tts`/voix choisie), BGM+SFX (`media-use`), puis mix via
   `hyperframes-audio` (ducking VO, fades).
7. **Contrôle** → `hyperframes-cli check` (0 erreur) + rendu draft + planche de
   frames + `motion-design/reference/quality-checklist`.
8. **Rendu & livraison** → `hyperframes-cli render` looks, mix final ffmpeg,
   artefact `present_file`, copie `livrables/`, commit+push.

---

## 4. Table de routage rapide

| Besoin | Skill |
|---|---|
| « fais-moi une vidéo » (tout) | hyperframes → routing |
| pub / promo produit | product-launch-video |
| explainer depuis du texte | faceless-explainer |
| vidéo libre multi-scènes | general-video |
| sting logo / kinetic type / data-viz | motion-graphics |
| vidéo calée sur une musique | music-to-video |
| vidéo depuis une PR | pr-to-video |
| deck interactif | slideshow |
| habiller un talking-head | talking-head-recut / embedded-captions |
| design Figma fourni | figma |
| portage Remotion | remotion-to-hyperframes |
| trouver BGM/SFX/logo/grade | media-use |
| écrire la compo (contrat) | hyperframes-core |
| animer (règles HF) | hyperframes-animation / hyperframes-keyframes |
| animer (goût, émotion, easing) | motion-design |
| mixer l'audio | hyperframes-audio |
| checker / rendre / diagnostiquer | hyperframes-cli |

---

## 5. Conventions maison (rappels)

- Livrables via `present_file` + copie dans `livrables/` (poussée sur GitHub).
- Sources client déposées dans `entrees/` (via l'interface web GitHub).
- Rendus temporaires dans `.cache/rendus/` (jamais dans git).
- Répondre et documenter en français ; logo toujours affiché carré, jamais
  étiré ; voix conversationnelle validée par le client.
