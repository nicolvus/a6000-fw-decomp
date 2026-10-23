#!/usr/bin/env python3
"""Build script for S608 MOUNT_INFO module analysis."""
import json
import sys

def main():
    with open("mount_info.json", "r") as f:
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
    print("Traces:")
    for ts in data['trace_strings']:
        print(f"  {ts['vaddr']}: {ts['text']}")
    print()
    print("Differential:")
    for fw, info in data['differential'].items():
        print(f"  {fw}: mount_info={info['mount_info_token_count']}, bl={info['bl_token_count']}, prefixes={info['prefixes']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())