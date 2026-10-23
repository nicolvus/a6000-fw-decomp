"""Tests del hito S186 — sub-etiqueta [BL]."""
import json

def test_bl_counts():
    d=json.load(open('analysis/s186_bl/bl_strings.json'))
    assert len(d['a6000'])==154
    assert len(d['a7s'])==75
    assert len(d['a6300'])==96