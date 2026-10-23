"""Tests del hito S182 — módulo [BT]."""
import json

def test_bt_counts():
    d=json.load(open('analysis/s182_bt/bt_strings.json'))
    assert len(d['a6000'])==44
    assert len(d['a7s'])==44
    assert len(d['a6300'])==44
    def core(s):
        t=s
        if t.startswith('[BT]:'):
            t=t[len('[BT]:'):].strip()
        elif t.startswith('[BT]'):
            t=t[len('[BT]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b==c
    assert len(a)==44