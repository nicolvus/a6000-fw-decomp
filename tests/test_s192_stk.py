"""Tests del hito S192 — sub-etiqueta [STK]."""
import json

def test_stk_counts():
    d=json.load(open('analysis/s192_stk/stk_strings.json'))
    assert len(d['a6000'])==76
    assert len(d['a7s'])==76
    assert len(d['a6300'])==0
