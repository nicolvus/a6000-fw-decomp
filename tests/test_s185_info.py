"""Tests del hito S185 — módulo [INFO]."""
import json

def test_info_counts():
    d=json.load(open('analysis/s185_info/info_strings.json'))
    assert len(d['a6000'])==58
    assert len(d['a7s'])==1
    assert len(d['a6300'])==37
    def core(s):
        t=s
        if t.startswith('[INFO]:'):
            t=t[len('[INFO]:'):].strip()
        elif t.startswith('[INFO]'):
            t=t[len('[INFO]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==1
    assert len(a-b)==57
    assert len(b-a)==0
    assert len(a&c)==1
    assert len(a-c)==57
    assert len(c-a)==36
