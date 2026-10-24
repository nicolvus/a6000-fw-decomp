#!/usr/bin/env python3
"""Verify script for S616 LENS_PDR module analysis."""
import json
import sys

def main():
    with open("lens_pdr.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert len(data['trace_strings']) == data['traces'], f"Trace count mismatch: {len(data['trace_strings'])} != {data['traces']}"
    
    # Verify all trace strings have [LENS_PDR]: prefix
    for ts in data['trace_strings']:
        assert ts['text'].startswith('[LENS_PDR]: '), f"Missing prefix: {ts['text']}"
    
    # Verify prefix length
    assert data['prefix_length'] == 12, f"Prefix length mismatch: {data['prefix_length']} != 12"
    assert data['prefix'] == '[LENS_PDR]: '
    
    # Verify differential
    assert data['differential']['a6000_fw321']['token_count'] == 4
    assert data['differential']['a7s_fw320']['token_count'] == 0
    assert data['differential']['a6300_fw201']['token_count'] == 0
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
