#!/usr/bin/env python3
"""Verify script for S606 NSX_VOT module analysis."""
import json
import sys

def main():
    with open("nsx_vot.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert len(data['trace_strings']) == data['traces'], f"Trace count mismatch: {len(data['trace_strings'])} != {data['traces']}"
    
    # Verify all trace strings have [NSX_VOT]: prefix
    for ts in data['trace_strings']:
        assert ts['text'].startswith('[NSX_VOT]: '), f"Missing prefix: {ts['text']}"
        # Verify twin has [TRK]: prefix
        assert ts['twin_text'].startswith('[TRK]: '), f"Twin missing prefix: {ts['twin_text']}"
        # Verify core text matches (after prefix)
        core_nsx = ts['text'][10:]  # after "[NSX_VOT]: "
        core_trk = ts['twin_text'][6:]  # after "[TRK]: "
        assert core_nsx == core_trk, f"Core mismatch: '{core_nsx}' != '{core_trk}'"
    
    # Verify prefix lengths
    assert data['prefix_length'] == 10, f"Prefix length mismatch: {data['prefix_length']} != 10"
    assert data['prefix'] == '[NSX_VOT]: '
    assert data['twin_prefix_length'] == 6, f"Twin prefix length mismatch: {data['twin_prefix_length']} != 6"
    assert data['twin_prefix'] == '[TRK]: '
    
    # Verify differential
    assert data['differential']['a6000_fw321']['nsx_vot_token_count'] == 7
    assert data['differential']['a6000_fw321']['trk_token_count'] == 7
    assert data['differential']['a7s_fw320']['nsx_vot_token_count'] == 0
    assert data['differential']['a7s_fw320']['trk_token_count'] == 7
    assert data['differential']['a6300_fw201']['nsx_vot_token_count'] == 0
    assert data['differential']['a6300_fw201']['trk_token_count'] == 7
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())