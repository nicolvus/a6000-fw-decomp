#!/usr/bin/env python3
"""Build script for S618 DET_DIR module analysis."""
import json
import sys

def main():
    with open("det_dir.json", "r") as f:
        data = json.load(f)
    
    print(f"Module: {data['module']}")
    print(f"Standalone traces: {data['traces']}")
    print(f"Note: {data['note']}")
    print(f"Related module: {data['related_module']}")
    print(f"Shutter line: {data['shutter_line']}")
    print()
    print("Differential:")
    for fw, info in data['differential'].items():
        print(f"  {fw}: standalone_token_count={info.get('standalone_token_count', 0)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())