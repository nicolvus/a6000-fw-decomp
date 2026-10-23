"""Tests del hito S198 — módulo [ERR]."""
import json

def test_err_counts():
    d=json.load(open('analysis/s198_err/err_strings.json'))
    assert len(d['a6000'])==288
    assert len(d['a7s'])==281
    assert len(d['a6300'])==655
    def core(s):
        t=s
        if t.startswith('[ERR]:'):
            t=t[len('[ERR]:'):].strip()
        elif t.startswith('[ERR]'):
            t=t[len('[ERR]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==245
    assert len(a-b)==43
    assert len(b-a)==36
    assert len(a&c)==238
    assert len(a-c)==50
    assert len(c-a)==415
