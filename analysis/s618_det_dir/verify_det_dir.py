#!/usr/bin/env python3
"""Verify script for S618 DET_DIR module analysis."""
import json
import sys

def main():
    with open("det_dir.json", "r") as f:
        data = json.load(f)
    
    # Verify trace count
    assert data['traces'] == 0, f"Expected 0 standalone traces, got {data['traces']}"
    assert len(data['trace_strings']) == 0
    
    # Verify shutter line
    assert data['shutter_line'] == "NEGATIVO ACOTADO"
    
    # Verify differential
    assert data['differential']['a6000_fw321']['standalone_token_count'] == 0
    assert data['differential']['a7s_fw320']['standalone_token_count'] == 0
    assert data['differential']['a6300_fw201']['standalone_token_count'] == 0
    
    # Verify related module
    assert data['related_module'] == "S617 (CAMERA_DEVICE/DET_DIR)"
    
    print("All verifications passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())