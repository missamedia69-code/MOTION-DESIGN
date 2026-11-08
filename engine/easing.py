"""Courbes d'accélération (easing) exprimées en expressions ffmpeg.

Chaque courbe prend une progression linéaire `p` (expression ffmpeg bornée
0→1) et retourne l'expression easée. Les expressions sont destinées à être
placées entre apostrophes dans un filtre (overlay, scale, crop, rotate…).
"""
from __future__ import annotations

# Formules (@ = progression 0→1). Références : easings.net.
_FORMULAS: dict[str, str] = {
    "linear": "@",
    "ease_in": "pow(@,3)",
    "ease_out": "1-pow(1-@,3)",
    "ease_in_out": "if(lt(@,0.5),4*pow(@,3),1-pow(-2*@+2,3)/2)",
    "expo_out": "if(gte(@,1),1,1-pow(2,-10*@))",
    "back_out": "1+2.70158*pow(@-1,3)+1.70158*pow(@-1,2)",
    "back_in": "2.70158*pow(@,3)-1.70158*pow(@,2)",
    "elastic_out": "if(lte(@,0),0,if(gte(@,1),1,pow(2,-10*@)*sin((@*10-0.75)*2*PI/3)+1))",
    "snap": "1-pow(1-@,5)",
}

EASINGS = list(_FORMULAS)
DEFAULT = "ease_out"


def ease(name: str | None, p: str) -> str:
    """Applique la courbe `name` à l'expression de progression `p`."""
    name = name or DEFAULT
    if name not in _FORMULAS:
        raise SystemExit(f"ERREUR : easing inconnu '{name}'. Dispo : {', '.join(EASINGS)}")
    return "(" + _FORMULAS[name].replace("@", f"({p})") + ")"


def progress(t: str, start: float, dur: float) -> str:
    """Progression linéaire bornée 0→1 de `start` à `start+dur` (t = variable temps)."""
    dur = max(float(dur), 1e-3)
    if start:
        return f"min(max(({t}-{start:g})/{dur:g},0),1)"
    return f"min(max({t}/{dur:g},0),1)"


def evaluate(name: str, p: float) -> float:
    """Évalue la courbe en Python (tests, aperçus, compteurs)."""
    import math

    expr = _FORMULAS[name].replace("@", f"({p!r})")
    env = {
        "pow": pow, "sin": math.sin, "PI": math.pi,
        "lt": lambda a, b: a < b, "lte": lambda a, b: a <= b,
        "gte": lambda a, b: a >= b,
    }

    def _if(c, a, b):
        return a if c else b

    env["if_"] = _if
    expr = expr.replace("if(", "if_(")
    return float(eval(expr, {"__builtins__": {}}, env))  # noqa: S307 (formules internes)
