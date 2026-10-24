#!/usr/bin/env python3
"""Verify script for S611 IMAGING_RSRC module analysis."""
import json
import sys

def main():
    with open("imaging_rsrc.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert len(data['trace_strings']) == data['traces'], f"Trace count mismatch: {len(data['trace_strings'])} != {data['traces']}"
    
    # Verify all trace strings have [IMAGING_RSRC]: prefix
    for ts in data['trace_strings']:
        assert ts['text'].startswith('[IMAGING_RSRC]: '), f"Missing prefix: {ts['text']}"
        # Verify core has [GOLFSHOT] prefix
        assert ts['core_text'].startswith('[GOLFSHOT]'), f"Core missing [GOLFSHOT] prefix: {ts['core_text']}"
        # Verify composite structure
        expected = '[IMAGING_RSRC]: ' + ts['core_text']
        assert ts['text'] == expected, f"Composite mismatch: {ts['text']} != {expected}"
    
    # Verify prefix lengths
    assert data['prefix_length'] == 16, f"Prefix length mismatch: {data['prefix_length']} != 16"
    assert data['prefix'] == '[IMAGING_RSRC]: '
    assert data['core_prefix_length'] == 10, f"Core prefix length mismatch: {data['core_prefix_length']} != 10"
    assert data['core_prefix'] == '[GOLFSHOT]'
    assert data['composite_prefix_length'] == 26, f"Composite prefix length mismatch: {data['composite_prefix_length']} != 26"
    
    # Verify differential
    assert data['differential']['a6000_fw321']['imaging_rsrc_token_count'] == 5
    assert data['differential']['a6000_fw321']['golfshot_token_count'] == 5
    assert data['differential']['a7s_fw320']['imaging_rsrc_token_count'] == 0
    assert data['differential']['a7s_fw320']['golfshot_token_count'] == 5
    assert data['differential']['a6300_fw201']['imaging_rsrc_token_count'] == 0
    assert data['differential']['a6300_fw201']['golfshot_token_count'] == 5
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
