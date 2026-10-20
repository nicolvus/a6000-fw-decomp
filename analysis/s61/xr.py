"""S61: utilidades de referencias cruzadas sobre el barrido Capstone de A6000 (cacheado)."""
import bisect
import os
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import cache, ins_list

L = ins_list("A6000")
ADDR = [x[0] for x in L]


def _calls():
    c = cache("s61_calls.pkl")
    if os.path.exists(c):
        return pickle.load(open(c, "rb"))
    d = {}
    for a, m, o in L:
        if m in ("bl", "blx", "b.w", "b") and o.startswith("#"):
            d.setdefault(int(o[1:], 16), []).append(a)
    with open(c, "wb") as fh:
        pickle.dump(d, fh)
    return d


CALLS = _calls()


def func_start(a, maxback=6000):
    """Último `push {.., lr}` anterior a `a` (heurística; verificar contra bytes)."""
    i = bisect.bisect_right(ADDR, a) - 1
    for k in range(i, max(0, i - maxback), -1):
        _, m, o = L[k]
        if m.startswith("push") and "lr" in o:
            return L[k][0]
    return None


def callers(t):
    return CALLS.get(t, [])


def instrs(a, b):
    i = bisect.bisect_left(ADDR, a)
    j = bisect.bisect_left(ADDR, b)
    return L[i:j]
