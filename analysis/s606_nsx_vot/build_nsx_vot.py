#!/usr/bin/env python3
"""Build script for S606 NSX_VOT module analysis."""
import json
import sys

def main():
    with open("nsx_vot.json", "r") as f:
        data = json.load(f)
    
    print(f"Module: {data['module']}")
    print(f"Traces: {data['traces']}")
    print(f"Prefix: '{data['prefix']}' (length: {data['prefix_length']})")
    print(f"Twin prefix: '{data['twin_prefix']}' (length: {data['twin_prefix_length']})")
    print(f"Shutter line: {data['shutter_line']}")
    print(f"Logger dual: {data['logger_dual']}")
    print(f"Global logger: {data['global_logger']}")
    print()
    print("Traces with twins:")
    for ts in data['trace_strings']:
        print(f"  {ts['vaddr']}: {ts['text']}")
        print(f"    -> twin: {ts['twin_vaddr']}: {ts['twin_text']} (delta: +{ts['delta']})")
    print()
    print("Differential:")
    for fw, info in data['differential'].items():
        print(f"  {fw}: nsx_vot={info['nsx_vot_token_count']}, trk={info['trk_token_count']}, prefixes={info['prefixes']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())