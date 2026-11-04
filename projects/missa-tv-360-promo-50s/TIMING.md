# Timeline de production — 50 s · 9:16

> Généré par `timing/generate.py` à partir des **durées réelles** des 6
> segments VO (`assets/vo/seq-*.mp3`). La voix n'est ni accélérée ni
> ralentie : les respirations sont des silences visuels occupés par les
> animations, les SFX et les mains sur les plans.

**VO totale : 49.50 s** · **respirations : 0.50 s** · **durée finale : 50.00 s**

| Ség. | Séquence | Début | VO (durée) | Fin VO | Respiration | Fin |
|---|---|---|---|---|---|---|
| 01 | Accroche « En Afrique » | 0.00 s | 6.18 s | 6.18 s | 0.00 s | 6.18 s |
| 02 | Mosaïque des 10 univers | 6.18 s | 15.18 s | 21.36 s | 0.00 s | 21.36 s |
| 03 | Faible débit / données | 21.36 s | 6.26 s | 27.62 s | 0.38 s | 28.00 s |
| 04 | Essai 24 h | 28.00 s | 6.40 s | 34.40 s | 0.00 s | 34.40 s |
| 05 | Prix + activation | 34.40 s | 10.36 s | 44.76 s | 0.00 s | 44.76 s |
| 06 | Signature | 44.76 s | 5.12 s | 49.88 s | 0.12 s | 50.00 s |

## Sous-titres

`subtitles.srt` contient les 20 repères, redistribués dans chaque segment
au prorata de la longueur du texte. Les respirations ne portent aucun
sous-titre. Si la VO est réenregistrée, relancer ce script suffit à tout
recaler.

## Piste audio

Poser `seq-01…06.mp3` aux instants `Début` du tableau ; mixer les 10 SFX
de `sfx/wav/` selon `SCRIPT.md`.

`assets/voix-off.mp3` est la prise continue de référence (44.32 s),
conservée pour écouter le timbre : elle n'est **pas** utilisée au montage,
car elle ne permet pas de placer les respirations aux bons endroits.
Les segments bruts (avant rognage des silences TTS) restent dans
`assets/vo/raw/` ; `trim_silence.py` régénère les versions propres.
