"""Tests del hito S189 — módulo [DEBUG]."""
import json

def test_debug_counts():
    d=json.load(open('analysis/s189_debug/debug_strings.json'))
    assert len(d['a6000'])==67
    assert len(d['a7s'])==37
    assert len(d['a6300'])==37
    def core(s):
        t=s
        if t.startswith('[DEBUG]:'):
            t=t[len('[DEBUG]:'):].strip()
        elif t.startswith('[DEBUG]'):
            t=t[len('[DEBUG]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==35
    assert len(a-b)==32
    assert len(b-a)==2
    assert len(a&c)==35
    assert len(a-c)==32
    assert len(c-a)==2
    assert len(b&c)==36
    assert len(b-c)==1
    assert len(c-b)==1
