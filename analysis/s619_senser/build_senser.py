#!/usr/bin/env python3
"""Build script for S619 SENSER module analysis."""
import json
import sys

def main():
    with open("senser.json", "r") as f:
        data = json.load(f)
    
    print(f"Module: {data['module']}")
    print(f"Traces: {data['traces']}")
    print(f"Prefixes: {data['prefixes']} (lengths: {data['prefix_lengths']})")
    print(f"Shutter line: {data['shutter_line']}")
    print(f"Logger dual: {data['logger_dual']}")
    print(f"Global logger: {data['global_logger']}")
    print()
    print("Traces:")
    for ts in data['trace_strings']:
        print(f"  {ts['vaddr']}: {ts['text']} (level: {ts['level']})")
    print()
    print("Differential:")
    for fw, info in data['differential'].items():
        print(f"  {fw}: token_count={info.get('token_count', 0)}, related_strings_count={info.get('related_strings_count', 0)}, prefixes={info.get('prefixes', [])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())