# Skills & ressources motion design (annuaire du moteur)

État des lieux des dépôts proposés, **vérifiés sur GitHub** le 2026-11-03, et de
leur intégration dans le moteur. Tous les liens ci-dessous pointent vers les
dépôts réels (certains liens fournis pointaient vers `github.com/topics/remotion`
ou une page d'organisation).

Conventions du moteur : `.agents/skills/` = référence canonique,
`.claude/skills/` = liens symboliques (Claude Code), `agent/skills/` = copies
(Eve), `skills-lock.json` = verrou maintenu par `npx skills`.

---

## 1. Installés dans le moteur

| Source | Skills | Contenu | Commande utilisée |
|---|---|---|---|
| [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) | 21 | Noyau HyperFrames + workflows vidéo | déjà présent |
| [`LottieFiles/motion-design-skill`](https://github.com/LottieFiles/motion-design-skill) | 1 (`motion-design`) | Culture motion : émotion, easing, chorégraphie | `npx skills add LottieFiles/motion-design-skill --skill motion-design -a claude-code -a eve -y` |
| [`kylezantos/design-motion-principles`](https://github.com/kylezantos/design-motion-principles) | 1 (`design-motion-principles`) | Création **ou** audit de motion UI (Emil Kowalski, Jakub Krehel, Jhey Tompkins), rapport HTML | `npx skills add kylezantos/design-motion-principles --skill design-motion-principles -a claude-code -a eve -y` |
| [`frankxai/awesome-motion-design-agent-skills`](https://github.com/frankxai/awesome-motion-design-agent-skills) | 5 | GSAP / Motion / Remotion / Lottie / Rive, direction et audit de motion web : `motion-director`, `web-motion-auditor`, `site-motion-excellence-director`, `remotion-video-agent`, `generative-media-director` | `npx skills add frankxai/awesome-motion-design-agent-skills --skill <5 noms> -a claude-code -a eve -y` |
| [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage) | 79 | Système de production vidéo agentique : GSAP (8), Three.js/WebGL (11), Remotion (2), Manim (3), Lottie, Framer Motion, data-viz, ffmpeg, outils vidéo, fournisseurs TTS/image/vidéo | `npx skills add calesthio/OpenMontage --skill <79 noms> -a claude-code -a eve -y` |

**Total : 107 skills**, tous présents dans les 3 répertoires et tracés dans
`skills-lock.json` (`npx skills list --json` → 107 `tracked`).

### OpenMontage : exclusions assumées

- **10 noms en collision** avec le noyau HeyGen ont été **conservés tels quels**
  (pas d'écrasement) : `hyperframes`, `hyperframes-animation`,
  `hyperframes-cli`, `hyperframes-core`, `hyperframes-creative`,
  `hyperframes-registry`, `media-use`, `motion-graphics`, `music-to-video`,
  `remotion-to-hyperframes`. La version OpenMontage de
  `hyperframes-animation` pèse à elle seule ~39 Mo.
- **2 skills au frontmatter YAML invalide** sont ignorés par la CLI :
  `canvas-procedural-animation`, `character-rigging`.
- Les skills « fournisseurs » (`elevenlabs`, `azure-*`, `kling-official`,
  `seedance-*`, `setup-api-key`, …) sont installés **à titre documentaire** :
  ils exigent des clés d'API et ne sont pas mobilisables dans le sandbox.
- `hyperframes-media` et `website-to-video` livrent 76 petits SFX `.mp3`
  (~5 Mo au total). Conformément au `.gitignore` du dépôt (« vidéos/audio non
  versionnés »), ils restent **non versionnés** : après un clone frais,
  `npx skills experimental_install --force` les restaure depuis GitHub.

### Routage rapide des nouveaux skills

| Besoin | Skill(s) |
|---|---|
| Animation web / timelines / ScrollTrigger | `gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-react`, `gsap-plugins`, `gsap-*`, `framer-motion` |
| Composants Remotion | `remotion`, `remotion-best-practices`, `remotion-video-agent` |
| Lottie / Bodymovin | `lottie-bodymovin` |
| WebGL / 3D | `threejs-*`, `3d-asset-generation` |
| Data-viz animée | `d3-viz`, `beautiful-mermaid`, `manim-composer` |
| Kinetic type / Manim | `manimce-best-practices`, `manimgl-best-practices` |
| Style, direction, audit | `visual-style`, `motion-director`, `design-motion-principles`, `web-motion-auditor` |
| Outils vidéo / ffmpeg | `ffmpeg`, `video-toolkit`, `video-edit`, `create-video`, `website-to-video` |

---

## 2. À installer à la demande (paquets lourds)

Ces deux skills sont **volontairement non installés** : ils embarquent des
médias lourds que le `.gitignore` du dépôt exclut (`*.mp3`) ou qui gonfleraient
inutilement le clone (~74 Mo à eux deux, dont une police TTF de 17 Mo).

| Dépôt | Volume | Contenu | Installation |
|---|---|---|---|
| [`Vincentwei1021/video-shotcraft`](https://github.com/Vincentwei1021/video-shotcraft) | ~51 Mo / 1218 fichiers (24 Mo de MP3, 15 Mo de PNG) | Promos produit cinématiques Remotion, 124 recettes de plans, 150 previews, sync au beat, export JianYing/CapCut | `npx skills add Vincentwei1021/video-shotcraft -a claude-code -a eve -y` |
| [`Vincentwei1021/anything2explainer`](https://github.com/Vincentwei1021/anything2explainer) | ~22 Mo / 209 fichiers (17 Mo de TTF) | Sujet → vidéo explicative Remotion (VO TTS, sous-titres, barre de progression) | `npx skills add Vincentwei1021/anything2explainer -a claude-code -a eve -y` |

Après installation, penser à `git add -f` les médias réellement nécessaires ou
à les déplacer dans `assets/` via `./md install`.

---

## 3. Annuaires, prompts et ressources (pas des skills)

Aucun `SKILL.md` dans ces dépôts : ils se consultent, ils ne s'installent pas
avec `npx skills add`.

| Dépôt | Nature |
|---|---|
| [`iart-ai/motion-skills`](https://github.com/iart-ai/motion-skills) | Showcase (README + GIF + outils de vérification) ; annonce 50 skills / 14 packs hébergés ailleurs |
| [`zhuyansen/awesome-claude-video-skills`](https://github.com/zhuyansen/awesome-claude-video-skills) | Annuaire de ~180 repos vidéo pour agents, classés et notés sur la sécurité (EN / 中文) |
| [`motionvideohq/motionvideo.xyz`](https://github.com/motionvideohq/motionvideo.xyz) | Annuaire de vidéos IA, prompts et skills pour apprendre le motion design aux agents |
| [`motionvideohq/awesome-gemini-4-argon-motion-design`](https://github.com/motionvideohq/awesome-gemini-4-argon-motion-design) | Vidéos virales + prompts Gemini réutilisables |
| [`motionvideohq/awesome-opus-5-5-motion-design`](https://github.com/motionvideohq/awesome-opus-5-5-motion-design) | Vidéos virales + prompts Opus réutilisables |
| [`beast-ofcourse/awesome-motion-graphics`](https://github.com/beast-ofcourse/awesome-motion-graphics) | Ressources gratuites : polices, effets, shaders, particules, transitions, gradients, templates |

---

## 4. Maintenance

```bash
npx skills list --json                                     # état des 107 skills
npx skills experimental_install --dry-run --frozen-lockfile  # lock cohérent
make skills-check                                          # 3 miroirs + lock
npx skills update <nom> -y                                # mise à jour ciblée
npx skills experimental_install --force                    # réinstallation complète
```

Procédure d'ajout détaillée : [plan-skills.md](plan-skills.md).
Règle : ne jamais éditer `skills-lock.json` à la main ; ne jamais installer un
skill dont le nom existe déjà sans avoir décidé quelle version faire autorité.
