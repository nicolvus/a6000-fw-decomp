#!/usr/bin/env python3
"""Build script for S611 IMAGING_RSRC module analysis."""
import json
import sys

def main():
    with open("imaging_rsrc.json", "r") as f:
        data = json.load(f)
    
    print(f"Module: {data['module']}")
    print(f"Traces: {data['traces']}")
    print(f"Prefix: '{data['prefix']}' (length: {data['prefix_length']})")
    print(f"Core prefix: '{data['core_prefix']}' (length: {data['core_prefix_length']})")
    print(f"Composite prefix length: {data['composite_prefix_length']}")
    print(f"Shutter line: {data['shutter_line']}")
    print(f"Logger dual: {data['logger_dual']}")
    print(f"Global logger: {data['global_logger']}")
    print()
    print("Traces with twins:")
    for ts in data['trace_strings']:
        print(f"  {ts['vaddr']}: {ts['text']}")
        print(f"    -> core: {ts['core_text']}")
    print()
    print("Differential:")
    for fw, info in data['differential'].items():
        print(f"  {fw}: imaging_rsrc={info['imaging_rsrc_token_count']}, golfshot={info['golfshot_token_count']}, prefixes={info['prefixes']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())