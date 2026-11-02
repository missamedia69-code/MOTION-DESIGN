"""Authoritative scene and French subtitle timings for all five exports.

Times are in seconds; every export is exactly 30 fps. The 59-second scene list
is used for the three dedicated aspect-ratio compositions. Shorts have their
own edits and captions, not a zoomed/accelerated 59-second video.
"""

SCENES = {
    "59": [
        (0.00, 3.70, "hook"), (3.70, 5.75, "repeat"),
        (5.75, 9.30, "zapping"), (9.30, 12.54, "mom"),
        (12.54, 14.00, "chorus"), (14.00, 18.50, "reveal"),
        (18.50, 23.70, "films"), (23.70, 28.50, "tv"),
        (28.50, 33.20, "audio"), (33.20, 35.30, "more"),
        (35.30, 42.00, "devices"), (42.00, 45.00, "month"),
        (45.00, 46.35, "reaction"), (46.35, 54.00, "year"),
        (54.00, 59.00, "cta"),
    ],
    "30": [
        (0.00, 3.30, "hook"), (3.30, 6.70, "reveal"),
        (6.70, 9.80, "films"), (9.80, 12.00, "tv"),
        (12.00, 17.70, "audio"), (17.70, 20.80, "month"),
        (20.80, 26.55, "year"), (26.55, 30.00, "cta"),
    ],
    "15": [
        (0.00, 2.80, "hook"), (2.80, 6.40, "reveal"),
        (6.40, 7.70, "tv"), (7.70, 9.15, "month"),
        (9.15, 12.10, "year"), (12.10, 15.00, "cta"),
    ],
}

# Two lines at most. SRT and burned-in captions are generated from this SAME list.
# Division of clauses follows the edited voice rather than a blind equal split.
CAPTIONS = {
    "59": [
        (0.12, 3.68, "Encore un abonnement...\npour revoir la même chose ?"),
        (3.72, 5.72, "Les mêmes chaînes.\nLes mêmes séries."),
        (5.75, 9.27, "Chaque mois, on paie...\net on zappe encore."),
        (9.33, 12.44, "Ça suffit ! Notre écran\nmérite mieux."),
        (12.55, 13.61, "On mérite mieux !"),
        (14.08, 17.40, "Missa TV trois cent soixante :\nton écran mérite mieux."),
        (18.50, 20.10, "Des milliers de films, séries,"),
        (20.10, 21.62, "documentaires et mangas."),
        (23.72, 25.84, "Des centaines de chaînes\nde télé en direct."),
        (28.50, 30.18, "Musique, podcasts..."),
        (30.18, 31.88, "des milliers de chaînes\nde radio,"),
        (31.88, 33.71, "jeux rétro et contenus\npour enfants."),
        (35.29, 38.11, "Sur télé Android, tablette\nou téléphone."),
        (38.12, 40.15, "Petit débit ? Un flux pensé"),
        (40.15, 42.26, "pour rester stable,\navec Internet."),
        (42.27, 44.52, "Deux mille francs CFA le mois."),
        (45.09, 45.79, "Et l’année ?"),
        (46.36, 48.70, "Dix mille francs CFA l’année."),
        (48.70, 50.38, "Sept mois offerts."),
        (50.38, 52.95, "Moins de trente francs\npar jour."),
        (54.06, 56.16, "Télécharge Missa TV\ntrois cent soixante."),
        (56.16, 57.78, "Ton écran mérite mieux !"),
        (57.79, 58.95, "On est ensemble !"),
    ],
    "30": [
        (0.22, 2.96, "Encore un abonnement\npour revoir la même chose ?"),
        (3.30, 4.11, "On mérite mieux !"),
        (4.11, 6.68, "Missa TV trois cent soixante."),
        (6.68, 9.75, "Des milliers de films, séries,\ndocumentaires et mangas."),
        (9.78, 11.95, "Des centaines de chaînes\nde télé en direct."),
        (12.00, 14.32, "Musique, podcasts,\ndes milliers de chaînes de radio"),
        (14.32, 16.08, "et jeux rétro."),
        (18.03, 19.74, "Deux mille francs CFA le mois."),
        (20.80, 23.65, "Dix mille francs CFA l’année :\nsept mois offerts."),
        (26.55, 27.94, "Télécharge l’appli."),
        (27.95, 29.63, "Ton écran mérite mieux !"),
    ],
    "15": [
        (0.16, 2.77, "Ton écran mérite mieux !"),
        (2.78, 5.00, "Missa TV trois cent soixante :"),
        (5.00, 7.61, "films, documentaires,\ntélé en direct, musique et radio."),
        (7.68, 9.12, "Deux mille francs CFA le mois,"),
        (9.16, 10.56, "dix mille francs CFA l’année."),
        (12.28, 13.60, "Télécharge l’appli !"),
    ],
}


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srts(directory):
    from pathlib import Path
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for version, cues in CAPTIONS.items():
        blocks = [f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}"
                  for i, (a,b,text) in enumerate(cues, 1)]
        path = directory / f"MISSA_TV_360_PUB_{version}S_fr.srt"
        path.write_text("\n\n".join(blocks)+"\n", encoding="utf-8")
        print(f"{path}: {len(cues)} cues")


if __name__ == "__main__":
    from pathlib import Path
    write_srts(Path(__file__).resolve().parents[2] / "livrables")
