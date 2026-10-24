#!/usr/bin/env python3
"""Verify script for S608 MOUNT_INFO module analysis."""
import json
import sys

def main():
    with open("mount_info.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert len(data['trace_strings']) == data['traces'], f"Trace count mismatch: {len(data['trace_strings'])} != {data['traces']}"
    
    # Verify all trace strings have [MOUNT_INFO]: prefix
    for ts in data['trace_strings']:
        assert ts['text'].startswith('[MOUNT_INFO]: '), f"Missing prefix: {ts['text']}"
        # Verify core has [BL] prefix (no space after ])
        assert ts['core_text'].startswith('[BL]'), f"Core missing [BL] prefix: {ts['core_text']}"
        # Verify composite structure
        expected = '[MOUNT_INFO]: ' + ts['core_text']
        assert ts['text'] == expected, f"Composite mismatch: {ts['text']} != {expected}"
    
    # Verify prefix lengths
    assert data['prefix_length'] == 14, f"Prefix length mismatch: {data['prefix_length']} != 14"
    assert data['prefix'] == '[MOUNT_INFO]: '
    assert data['core_prefix_length'] == 4, f"Core prefix length mismatch: {data['core_prefix_length']} != 4"
    assert data['core_prefix'] == '[BL]'
    assert data['composite_prefix_length'] == 18, f"Composite prefix length mismatch: {data['composite_prefix_length']} != 18"
    
    # Verify differential
    assert data['differential']['a6000_fw321']['mount_info_token_count'] == 6
    assert data['differential']['a6000_fw321']['bl_token_count'] == 6
    assert data['differential']['a7s_fw320']['mount_info_token_count'] == 0
    assert data['differential']['a7s_fw320']['bl_token_count'] == 70
    assert data['differential']['a6300_fw201']['mount_info_token_count'] == 0
    assert data['differential']['a6300_fw201']['bl_token_count'] == 70
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
