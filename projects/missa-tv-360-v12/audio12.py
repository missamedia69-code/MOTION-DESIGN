# MISSA TV 360 v10 — musique originale (afro-pop / amapiano léger, 116 BPM) + SFX synthétiques.
# Tout est généré ici : aucun échantillon externe, aucun droit à gérer.
# Usage (depuis la racine du dépôt) : python3 projects/missa-tv-360-v10/audio10.py
import numpy as np, wave, os, json, bisect

SR = 44100
# recalage sur la voix fournie (align12.py → tmap.json)
_TM = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmap.json")))
DUR = _TM["duration"]


def M(t):
    o, n = _TM["old"], _TM["new"]
    i = min(max(bisect.bisect_right(o, t) - 1, 0), len(o) - 2)
    return n[i] + (n[i + 1] - n[i]) * (t - o[i]) / (o[i + 1] - o[i])

N = int(SR * DUR)
OUT = ".cache/audio12"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(360)

BPM = 116
BEAT = 60 / BPM
S16 = BEAT / 4

# Repères de la composition (index.html) : break avant le prix, drop sur les prix.
BREAK = (M(38.3), M(40.3))
DROP = M(40.3)


def save(name, sig, norm=0.9):
    sig = np.asarray(sig, dtype=np.float64)
    if sig.ndim == 1:
        sig = np.stack([sig, sig], 1)
    sig = sig / max(1e-9, np.max(np.abs(sig))) * norm
    w = wave.open(os.path.join(OUT, name), "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((sig * 32767).astype("<i2").tobytes()); w.close()


def env(L, a=0.005, d=4.0):
    t = np.arange(L) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t * d)


def lowpass(x, k):
    # moyenne glissante simple (filtre doux)
    if k <= 1:
        return x
    c = np.cumsum(np.concatenate(([0], x)))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate((np.full(k - 1, y[0]), y))


L_ = np.zeros(N); R_ = np.zeros(N)


def add(t0, x, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(x) <= 0:
        return
    if i0 < 0:
        x = x[-i0:]; i0 = 0
    i1 = min(N, i0 + len(x))
    l = np.sqrt(0.5 * (1 - pan)); r = np.sqrt(0.5 * (1 + pan))
    L_[i0:i1] += x[: i1 - i0] * gain * l * 1.414
    R_[i0:i1] += x[: i1 - i0] * gain * r * 1.414


def in_break(t):
    return BREAK[0] - 0.02 <= t < BREAK[1]


def section_gain(t):
    """Énergie par section (intro → montée → principal → relance → break → drop → final)."""
    if t < M(3.6): return 0.55
    if t < M(6.0): return 0.75
    if t < M(16.0): return 0.85
    if t < BREAK[0]: return 1.0
    if t < BREAK[1]: return 0.0
    return 1.1


# ── Instruments ───────────────────────────────────────────
def kick():
    L = int(0.32 * SR); t = np.arange(L) / SR
    f = 48 + 110 * np.exp(-t * 32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) + rng.standard_normal(L) * np.exp(-t * 180) * 0.15


def clap():
    L = int(0.22 * SR); t = np.arange(L) / SR
    n = rng.standard_normal(L)
    n = n - lowpass(n, 6)
    e = np.exp(-t * 28) + 0.6 * np.exp(-np.maximum(0, t - 0.012) * 30) * (t > 0.012)
    return n * e * 0.6


def shaker(acc):
    L = int(0.07 * SR); t = np.arange(L) / SR
    n = rng.standard_normal(L); n = n - lowpass(n, 3)
    return n * np.exp(-t * 70) * (0.22 if acc else 0.11)


def logdrum(f0, dur=0.32):
    # basse percussive « log drum » (signature amapiano) avec glissé de hauteur
    L = int(dur * SR); t = np.arange(L) / SR
    f = f0 * (1 + 0.5 * np.exp(-t * 40))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    return np.tanh(1.6 * x) * env(L, 0.003, 7.5)


def keys(freqs, dur):
    # piano électrique doux (accords)
    L = int(dur * SR); t = np.arange(L) / SR
    x = np.zeros(L)
    for f in freqs:
        x += (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6)
              + 0.12 * np.sin(2 * np.pi * f * 3.002 * t) * np.exp(-t * 9))
    return x * env(L, 0.01, 2.2) / len(freqs)


def pad(freqs, dur):
    L = int(dur * SR); t = np.arange(L) / SR
    x = np.zeros(L)
    for f in freqs:
        for det in (-0.004, 0.004):
            x += np.sin(2 * np.pi * f * (1 + det) * t) + 0.25 * np.sin(4 * np.pi * f * (1 + det) * t)
    a = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return x * a / (2 * len(freqs))


def pluck(f, dur=0.35):
    L = int(dur * SR); t = np.arange(L) / SR
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 14) + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t * 20)
    return x * env(L, 0.002, 9)


def noise_sweep(dur, up=True):
    L = int(dur * SR); t = np.arange(L) / SR
    n = rng.standard_normal(L)
    out = np.zeros(L); seg = int(0.02 * SR)
    for i in range(0, L, seg):
        p = i / L if up else 1 - i / L
        k = max(1, int(24 - 22 * p))
        out[i:i + seg] = (n - lowpass(n, k))[i:i + seg] if p > 0.5 else lowpass(n, k)[i:i + seg]
    a = (t / dur) ** 2 if up else (1 - t / dur) ** 2
    return out * a


# Accords (fa majeur, optimiste) : F – Dm – Bb – C, 2 temps… 1 mesure chacun
def hz(m): return 440 * 2 ** ((m - 69) / 12)
CH = [
    ([53, 57, 60, 65], 41),   # F
    ([50, 57, 62, 65], 38),   # Dm
    ([46, 53, 58, 62], 34),   # Bb
    ([48, 55, 60, 64], 36),   # C
]
BAR = 4 * BEAT
MEL = [72, 74, 77, 79, 81, 79, 77, 74]  # pentatonique de fa

nbars = int(DUR / BAR) + 1
for b in range(nbars):
    t0 = b * BAR
    chord, root = CH[b % 4]
    g = section_gain(t0)
    # accords
    if not in_break(t0) and t0 < DUR - 1.0:
        for k in (0, 1.5, 2.5):
            tk = t0 + k * BEAT
            if not in_break(tk) and tk < DUR - 1.0:
                add(tk, keys([hz(m) for m in chord], 1.2), 0.22 * max(g, 0.5), pan=-0.2)
        if t0 >= M(16.0):
            add(t0, pad([hz(m + 12) for m in chord[1:]], BAR), 0.07 * g, pan=0.25)
    for s in range(16):
        ts = t0 + s * S16
        if ts >= DUR - 0.8 or in_break(ts):
            continue
        g = section_gain(ts)
        if g == 0:
            continue
        # kick 4 temps à partir de la montée
        if s % 4 == 0 and ts >= M(6.0):
            add(ts, kick(), 0.85 * g)
        # clap sur 2 et 4
        if s in (4, 12) and ts >= M(3.6):
            add(ts, clap(), 0.45 * g, pan=0.1)
        # shaker
        add(ts, shaker(s % 2 == 1), 0.9 * g, pan=0.35)
        # log drum (motif amapiano)
        if s in (0, 3, 6, 10, 11, 14) and ts >= M(6.0):
            f = hz(root) * (2 ** (7 / 12) if s == 11 else 1)
            add(ts, logdrum(f), 0.55 * g)
        # mélodie pluck (section principale et final)
        if ts >= M(16.0) and s in (2, 6, 9, 13):
            note = MEL[(b * 4 + s // 4) % len(MEL)]
            add(ts, pluck(hz(note)), 0.12 * g, pan=0.4 if s % 2 else -0.4)

# Break : une seule note de basse qui pulse (suspense « Et ça coûte combien ? »)
for k in range(max(1, int((BREAK[1] - BREAK[0] - 0.15) / BEAT))):
    add(BREAK[0] + 0.15 + k * BEAT, logdrum(hz(29), 0.45), 0.5)
# Montée avant le drop + crash
add(DROP - 1.0, noise_sweep(1.0, True), 0.25)
crash = rng.standard_normal(int(1.6 * SR)); crash = (crash - lowpass(crash, 4)) * env(len(crash), 0.002, 2.6)
add(DROP, crash, 0.35)
add(M(48.6), crash, 0.3)
# Accord final majeur
add(DUR - 1.0 - BAR, pad([hz(m) for m in (65, 69, 72, 77)], BAR + 1.0), 0.12)
add(M(55.5), keys([hz(m) for m in (53, 57, 60, 65, 69)], 3.5), 0.35)

t = np.arange(N) / SR
fade = np.clip(t / 0.8, 0, 1) * np.clip((DUR - t) / 1.4, 0, 1)
L_ *= fade; R_ *= fade
save("music.wav", np.stack([L_, R_], 1), 0.85)

# ── SFX ───────────────────────────────────────────────────
SL = np.zeros(N); SRr = np.zeros(N)


def sfx(t0, x, gain=1.0, pan=0.0):
    i0 = int(M(t0) * SR); i1 = min(N, i0 + len(x))
    l = np.sqrt(0.5 * (1 - pan)); r = np.sqrt(0.5 * (1 + pan))
    SL[i0:i1] += x[: i1 - i0] * gain * l * 1.414
    SRr[i0:i1] += x[: i1 - i0] * gain * r * 1.414


def pop(f=700):
    L = int(0.09 * SR); tt = np.arange(L) / SR
    return np.sin(2 * np.pi * np.cumsum(f * np.exp(-tt * 18) + 200) / SR) * np.exp(-tt * 40)


def tic():
    L = int(0.04 * SR); tt = np.arange(L) / SR
    return np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 140)


def whoosh(d=0.6, up=True):
    return noise_sweep(d, up) * np.sin(np.pi * np.arange(int(d * SR)) / (d * SR))


def impact():
    L = int(0.9 * SR); tt = np.arange(L) / SR
    return np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-tt * 7)) / SR) * np.exp(-tt * 4.5) + rng.standard_normal(L) * np.exp(-tt * 30) * 0.3


def notes(seq, step=0.11, dur=0.5, d=6):
    L = int((step * len(seq) + dur) * SR); x = np.zeros(L)
    for i, m in enumerate(seq):
        o = int(i * step * SR); tt = np.arange(int(dur * SR)) / SR
        f = hz(m)
        x[o:o + len(tt)] += (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 10)) * np.exp(-tt * d)
    return x


def click():
    L = int(0.03 * SR); tt = np.arange(L) / SR
    return rng.standard_normal(L) * np.exp(-tt * 300) + np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 200)


def stamp():
    L = int(0.3 * SR); tt = np.arange(L) / SR
    return np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 14) + rng.standard_normal(L) * np.exp(-tt * 60) * 0.6


def ting():
    L = int(0.8 * SR); tt = np.arange(L) / SR
    return (np.sin(2 * np.pi * 2093 * tt) + 0.5 * np.sin(2 * np.pi * 3136 * tt)) * np.exp(-tt * 6)


def pages():
    L = int(0.06 * SR); tt = np.arange(L) / SR
    n = rng.standard_normal(L); return (n - lowpass(n, 3)) * np.sin(np.pi * tt / tt[-1]) * 0.6


def beep():
    L = int(0.14 * SR); tt = np.arange(L) / SR
    return np.sin(2 * np.pi * 1320 * tt) * np.minimum(1, (0.14 - tt) / 0.02) * np.minimum(1, tt / 0.005)


# S1 : pops d'icônes + aspiration
for i in range(14):
    sfx(0.15 + i * 0.12 + rng.uniform(0, .05), pop(500 + rng.uniform(0, 600)), 0.25, pan=rng.uniform(-.7, .7))
sfx(2.55, whoosh(1.0, True), 0.7)
# S2 : impact + jingle 2 notes sur « 360 »
sfx(3.6, impact(), 0.9)
sfx(4.75, notes([72, 79], 0.16, 0.7, 5), 0.5)
# S3 : tic à chaque pastille
for tt_ in (6.9, 7.65, 8.1, 8.65, 9.5, 10.6):
    sfx(tt_, tic(), 0.5, pan=0.2)
# S4 → S5 rideau
sfx(15.55, whoosh(0.6), 0.7)
# S5 : validation « stable »
sfx(21.2, notes([76, 84], 0.09, 0.5, 8), 0.35)
# S6 : bip de connexion + accord positif
sfx(23.3, beep(), 0.25); sfx(24.8, beep(), 0.25)
sfx(26.2, notes([65, 69, 72], 0.07, 0.8, 4), 0.35)
# S7 : trois notes montantes (une par appareil)
for tt_, m in ((29.35, 72), (30.05, 76), (30.6, 79)):
    sfx(tt_, notes([m], 0.1, 0.4, 7), 0.4)
sfx(31.05, whoosh(0.6), 0.7)
# S8 : ta-dam, clic, tic-tac joyeux, stamp
sfx(31.75, notes([67, 72], 0.14, 0.6, 5), 0.5)
sfx(33.35, click(), 0.6)
for k in range(10):
    sfx(34.45 + k * 0.12, tic(), 0.35, pan=-0.3 if k % 2 else 0.3)
sfx(36.0, stamp(), 0.7)
# S9 : whoosh du morphing
sfx(38.3, whoosh(0.4, False), 0.4)
# S10 : impacts légers + tintement
sfx(40.95, impact(), 0.35); sfx(41.0, ting(), 0.2)
sfx(42.8, impact(), 0.4); sfx(42.85, ting(), 0.2)
# S11 : pages, tampon, ta-da
for k in range(8):
    sfx(44.3 + k * 0.08, pages(), 0.4)
sfx(45.85, stamp(), 0.7)
sfx(46.0, notes([72, 76, 79], 0.08, 0.6, 5), 0.3)
# S12 → S13
sfx(48.25, whoosh(0.6), 0.7)
sfx(48.9, notes([72, 79], 0.16, 0.7, 5), 0.5)
# S14 : clic bouton + jingle final
sfx(54.6, click(), 0.5)
sfx(55.0, notes([72, 76, 79, 84], 0.1, 0.9, 4), 0.45)

save("sfx.wav", np.stack([SL, SRr], 1), 0.8)
print("musique + sfx ->", OUT)
