#!/usr/bin/env python3
"""Verify script for S607 CAM_CMD module analysis."""
import json
import sys

def main():
    with open("cam_cmd.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert len(data['trace_strings']) == data['traces'], f"Trace count mismatch: {len(data['trace_strings'])} != {data['traces']}"
    
    # Verify all trace strings have [CAM_CMD]: prefix
    for ts in data['trace_strings']:
        assert ts['text'].startswith('[CAM_CMD]: '), f"Missing prefix: {ts['text']}"
    
    # Verify prefix length
    assert data['prefix_length'] == 10, f"Prefix length mismatch: {data['prefix_length']} != 10"
    assert data['prefix'] == '[CAM_CMD]: '
    
    # Verify differential
    assert data['differential']['a6000_fw321']['token_count'] == 6
    assert data['differential']['a7s_fw320']['token_count'] == 0
    assert data['differential']['a6300_fw201']['token_count'] == 0
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    # Verify typo
    assert data['typo'] == "Modlue -> Module"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())