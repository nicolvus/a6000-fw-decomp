"""Tests del hito S194 — módulo [PNL]."""
import json

def test_pnl_counts():
    d=json.load(open('analysis/s194_pnl/pnl_strings.json'))
    assert len(d['a6000'])==41
    assert len(d['a7s'])==41
    assert len(d['a6300'])==41
    def core(s):
        t=s
        if t.startswith('[PNL]:'):
            t=t[len('[PNL]:'):].strip()
        elif t.startswith('[PNL]'):
            t=t[len('[PNL]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==37
    assert len(a-b)==4
    assert len(b-a)==4
    assert len(a&c)==37
    assert len(a-c)==4
    assert len(c-a)==4
    assert b==c
    assert len(b&c)==41
