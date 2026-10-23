#!/usr/bin/env python3
"""Build script for S609 CAMERA_IS/DIST module analysis."""
import json
import sys

def main():
    with open("dist.json", "r") as f:
        data = json.load(f)
    
    print(f"Module: {data['module']}")
    print(f"Traces: {data['traces']}")
    print(f"Prefix: '{data['prefix']}' (length: {data['prefix_length']})")
    print(f"Shutter line: {data['shutter_line']}")
    print(f"Logger dual: {data['logger_dual']}")
    print(f"Global logger: {data['global_logger']}")
    print()
    print("Traces:")
    for ts in data['trace_strings']:
        print(f"  {ts['vaddr']}: {ts['text']}")
    print()
    print("Differential:")
    for fw, info in data['differential'].items():
        print(f"  {fw}: token_count={info['token_count']}, parent_token_count={info['parent_token_count']}, prefixes={info['prefixes']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())