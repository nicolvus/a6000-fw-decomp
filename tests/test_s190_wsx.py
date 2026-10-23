"""Tests del hito S190 — módulo [WSX]."""
import json

def test_wsx_counts():
    d=json.load(open('analysis/s190_wsx/wsx_strings.json'))
    assert len(d['a6000'])==59
    assert len(d['a7s'])==59
    assert len(d['a6300'])==59
    def core(s):
        t=s
        if t.startswith('[WSX]:'):
            t=t[len('[WSX]:'):].strip()
        elif t.startswith('[WSX]'):
            t=t[len('[WSX]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b==c
    assert len(a)==59
