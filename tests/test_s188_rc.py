"""Tests del hito S188 — módulo [RC]."""
import json

def test_rc_counts():
    d=json.load(open('analysis/s188_rc/rc_strings.json'))
    assert len(d['a6000'])==69
    assert len(d['a7s'])==69
    assert len(d['a6300'])==71
    def core(s):
        t=s
        if t.startswith('[RC]:'):
            t=t[len('[RC]:'):].strip()
        elif t.startswith('[RC]'):
            t=t[len('[RC]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b
    assert len(a&c)==69
    assert len(c-a)==2
