"""Tests del hito S191 — sub-etiqueta [GOLFSHOT]."""
import json

def test_golfshot_counts():
    d=json.load(open('analysis/s191_golfshot/golfshot_strings.json'))
    assert len(d['a6000'])==65
    assert len(d['a7s'])==65
    assert len(d['a6300'])==64
