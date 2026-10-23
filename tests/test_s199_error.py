"""Tests del hito S199 — módulo [ERROR]."""
import json

def test_error_counts():
    d=json.load(open('analysis/s199_error/error_strings.json'))
    assert len(d['a6000'])==213
    assert len(d['a7s'])==213
    assert len(d['a6300'])==214
    def core(s):
        t=s
        if t.startswith('[ERROR]:'):
            t=t[len('[ERROR]:'):].strip()
        elif t.startswith('[ERROR]'):
            t=t[len('[ERROR]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b
    assert len(a&c)==207
    assert len(c-a)==1
