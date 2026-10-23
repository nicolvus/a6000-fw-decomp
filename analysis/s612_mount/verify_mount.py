#!/usr/bin/env python3
"""Verify script for S612 CAMERA_IS/MOUNT module analysis."""
import json
import sys

def main():
    with open("mount.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert len(data['trace_strings']) == data['traces'], f"Trace count mismatch: {len(data['trace_strings'])} != {data['traces']}"
    
    # Verify all trace strings have [CAMERA_IS][MOUNT]: [Error] prefix
    for ts in data['trace_strings']:
        assert ts['text'].startswith('[CAMERA_IS][MOUNT]: [Error] '), f"Missing prefix: {ts['text']}"
    
    # Verify prefix length
    assert data['prefix_length'] == 25, f"Prefix length mismatch: {data['prefix_length']} != 25"
    assert data['prefix'] == '[CAMERA_IS][MOUNT]: [Error] '
    
    # Verify differential
    assert data['differential']['a6000_fw321']['token_count'] == 5
    assert data['differential']['a7s_fw320']['token_count'] == 0
    assert data['differential']['a6300_fw201']['token_count'] == 0
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())