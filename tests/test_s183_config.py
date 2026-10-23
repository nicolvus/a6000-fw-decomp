"""Tests del hito S183 — módulo [CONFIG]."""
import json

def test_config_counts():
    d=json.load(open('analysis/s183_config/config_strings.json'))
    assert len(d['a6000'])==47
    assert len(d['a7s'])==47
    assert len(d['a6300'])==47
    def core(s):
        t=s
        if t.startswith('[CONFIG]:'):
            t=t[len('[CONFIG]:'):].strip()
        elif t.startswith('[CONFIG]'):
            t=t[len('[CONFIG]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b==c
    assert len(a)==47
