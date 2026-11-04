# DÉCISIONS DU PROPRIÉTAIRE — question groupée unique de l'étape 0

> Réponses reçues le **4 novembre 2026** (une seule question groupée, conformément à la section D.1/M).
> Elles complètent `SPEC-V2.md` et `RAPPORT-ETAPE-0.md`.

> ⚠️ **RÉVISION 1.1 — 4 novembre 2026 (retour du propriétaire sur le WIP)** : l'application facture **XAF 1 000 / mois** et **XAF 10 000 / an** ; 12 × 1 000 = **12 000**, l'écart de 2 000 XAF = **2 MOIS OFFERTS** (et non 7). À l'oral/sous-titre : « mille francs CFA » / « dix mille francs CFA ». « Moins de trente francs par jour » reste exact (10 000 / 365 = 27,4). Toute mention antérieure de 2 000 / 24 000 / 14 000 / 7 mois est **caduque**.

| Question | Réponse | Conséquence |
|---|---|---|
| Section C : éléments manquants | **« le lgog est dans asset »** (= « le logo est dans asset ») | `[LOGO_OFFICIEL]` est **résolu** : `assets/images/logo-missa.png`, copié en `assets/img/logo-officiel.png`. Voir `assets/img/README.md` pour la réserve sur l'identité bleu/vert et l'absence de transparence. Les 6 autres éléments restent manquants → **placeholders visibles** + liste dans le rapport final (règle de la section C). |
| `[VOIX]` | **`voix_temporaire`** — « VO de travail temporaire » | Une piste de repère est générée **uniquement pour caler `onsets.json` et le montage**. Elle n'est **pas** la voix du film : `assets/audio/voix.mp3` reste attendu et **sera substituée avant tout rendu final**. Le point d'arrêt 2 reste ouvert. |
| `[MUSIQUES_CC0]` | **`je_fournis`** — « Je fournis les 2 morceaux » | Deux pistes CC0 (tension 0→16,0 s ; élan 16,0→59 s) sont attendues. En attendant : `MUSIC=""` dans `build-audio.sh`, pistes musicales en silence, licences à vérifier page par page par le propriétaire. Le point d'arrêt 6 reste ouvert. |
| **Point d'arrêt 1 — script** | **`valide`** — « Validé, on passe à la voix » | `SCRIPT.md` (G.2 + G.3) est **validé mot à mot**. L'étape 2 peut démarrer. Aucune correction du texte VO. |
| Forme de marque (L.10) | **`360`** — « MISSA TV 360 » | Le film utilise **« MISSA TV 360 »** (sans « + », sans « PLUS »). Le logo fourni porte bien la pastille « 360 ». À l'oral : « Missa TV trois cent soixante ». |

## Règles qui restent fermes malgré ces réponses

- **Aucune image IA, aucune photo, aucun personnage photoréaliste** (section A).
- **Aucun opérateur/marque tiers**, décodeur/chaînes/logos génériques (A.3, L.1).
- Montants à l'écran **`XAF 1 000 / mois`** et **`XAF 10 000 / an`** ; à l'oral/sous-titre
  **« mille francs CFA »** / **« dix mille francs CFA »** ; **2 mois offerts** ;
  **« moins de trente francs par jour »** (section B). Écriture `XAF` par défaut, variante `FCFA`
  non retenue.
- Durée **59,0 s exactes**, 1080×1920, 30 i/s, sous-titre mot à mot dans la bande y 1280-1400.
- **Aucune clé, aucune publication** (D.1). Exception demandée explicitement par le propriétaire
  le 04/11 : les **livrables WIP** sont commités/poussés sur `arena/cc667b6c-motion-design`
  uniquement, pour qu'il les voie sur GitHub. Aucun élément de la section C n'est inventé :
  ce qui manque s'affiche entre crochets à l'écran.
- Le spot 50 s et ses 10 images générées restent **archivés, non réutilisés**.
