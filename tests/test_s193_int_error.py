"""Tests del hito S193 — módulo [INT_ERROR]."""
import json

def test_int_error_counts():
    d=json.load(open('analysis/s193_int_error/int_error_strings.json'))
    assert len(d['a6000'])==53
    assert len(d['a7s'])==53
    assert len(d['a6300'])==53
    def core(s):
        t=s
        if t.startswith('[INT_ERROR]:'):
            t=t[len('[INT_ERROR]:'):].strip()
        elif t.startswith('[INT_ERROR]'):
            t=t[len('[INT_ERROR]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b==c
    assert len(a)==53
