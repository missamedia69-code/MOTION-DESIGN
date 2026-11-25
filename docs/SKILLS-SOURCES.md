# Sources et licences des skills

150 skills, installés dans trois miroirs (`.agents/skills/` canonique, `.claude/skills/` liens, `agent/skills/` copies). Cohérence : `make skills-check`. Chaque skill tiers garde son fichier `LICENSE` (et `NOTICE` le cas échéant).

## Ajouts du moteur 2.1 (recherche GitHub, novembre 2026)

| Source | Licence | Skills |
|---|---|---|
| [Tejashmakwana/motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing) | Apache-2.0 (GSAP fourni sous licence GreenSock « no charge » : voir NOTICE) | `motionmaxxing` |
| [alchaincyf/huashu-motion](https://github.com/alchaincyf/huashu-motion) | MIT (le personnage « Huashu » n'est pas sous licence ; la CLI `om` est récupérée via `npx huashu-motion`) | `huashu-motion` |
| [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) | MIT (rédigé en indonésien) | `bang-motion` |
| [charlie947/motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills) | MIT | `animated-chart`, `brand-intake`, `milestone-reveal`, `motion-brief-writer`, `motion-effects`, `reel-export`, `reference-to-motion`, `title-sequence-3d` |
| [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) | MIT | `business-motion-film` |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | `gsap-core`, `gsap-frameworks`, `gsap-performance`, `gsap-plugins`, `gsap-react`, `gsap-scrolltrigger`, `gsap-timeline`, `gsap-utils` |
| [iart-ai/ad-video-skills](https://github.com/iart-ai/ad-video-skills) | MIT | `ad-creative-video`, `launch-video`, `testimonial-video` |
| [iart-ai/ecommerce-video-skills](https://github.com/iart-ai/ecommerce-video-skills) | MIT | `product-demo-video`, `promo-video` |
| [iart-ai/kinetic-typography-skills](https://github.com/iart-ai/kinetic-typography-skills) | MIT | `kinetic-typography` |
| [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | MIT | `animation-principles`, `beat-sync-editing`, `color-motion`, `logo-animation`, `motion-art-direction`, `motion-background`, `shot-composition` |
| [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) | MIT | `caption-animation`, `countdown-video`, `lower-thirds`, `short-form-video` |
| [lovisdotio/motion2code](https://github.com/lovisdotio/motion2code) | MIT | `motion2code` |

Écartés pour licence non commerciale : `feitangyuan/onetake`, `Vincentwei1021/video-talkcraft`. `Vincentwei1021/video-shotcraft` (Apache-2.0) écarté car il dépend de Remotion (licence payante pour les entreprises de plus de 3 personnes).

## Branchements dans le moteur

- `engine/verify.py` (`./md verifier`, MCP `md_verify`, automatique après `./md render`) appelle `motionmaxxing/scripts/look.py`.
- La grammaire « pro » du compositeur (`engine/ads.py`) applique les lois mesurées de `motionmaxxing` (coupes en mouvement, entrées depuis le surdimensionné, presque aucun fondu, aucune image morte, fin courte).
- `engine/beats.py` (`./md rythme`, MCP `md_rythme`) applique `beat-sync-editing` : coupes sur les mesures.
- Les règles « pro » de `engine/lint.py` reprennent les interdits de `motionmaxxing` et les tests anti-présentation de `bang-motion`.

## Skills déjà présents

| Source | Licence | Skills |
|---|---|---|
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | MIT | `motion-design` |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | AGPL-3.0 ⚠ (usage interne libre ; redistribuer le dépôt impose de partager le code) | `3d-asset-generation`, `acestep`, `agents`, `ai-video-gen`, `atlas-cloud`, `avatar-video`, `azure-speech-to-text`, `azure-text-to-speech`, `beautiful-mermaid`, `bfl-api`, `character-animation-qa`, `comfyui` … (+59) |
| [frankxai/awesome-motion-design-agent-skills](https://github.com/frankxai/awesome-motion-design-agent-skills) | CC0-1.0 | `generative-media-director`, `motion-director`, `remotion-video-agent`, `site-motion-excellence-director`, `web-motion-auditor` |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | `embedded-captions`, `faceless-explainer`, `figma`, `general-video`, `hyperframes`, `hyperframes-animation`, `hyperframes-audio`, `hyperframes-cli`, `hyperframes-core`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry` … (+9) |
| [kylezantos/design-motion-principles](https://github.com/kylezantos/design-motion-principles) | voir le dépôt source | `design-motion-principles` |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | voir le dépôt source | `frame-data-chart-nyt`, `frame-glitch-title`, `frame-light-leak-cinema`, `frame-liquid-bg-hero`, `frame-logo-outro`, `huashu-art-motion`, `mockup-device-3d`, `motion-lab`, `oil-motion`, `poster-hero`, `review-animations`, `vfx-text-cursor` … (+1) |
