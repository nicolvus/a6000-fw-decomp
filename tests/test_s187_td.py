"""Tests del hito S187 — módulo [TD]."""
import json

def test_td_counts():
    d=json.load(open('analysis/s187_td/td_strings.json'))
    assert len(d['a6000'])==73
    assert len(d['a7s'])==73
    assert len(d['a6300'])==84
    def core(s):
        t=s
        if t.startswith('[TD]:'):
            t=t[len('[TD]:'):].strip()
        elif t.startswith('[TD]'):
            t=t[len('[TD]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b
    assert len(a&c)==73
    assert len(c-a)==11
