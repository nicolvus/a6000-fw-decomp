"""Sondeo estático reproducible; solo lee ELF y emite JSON por stdout."""
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from func_owner import owner
from rtti_vtables import Elf, recover, self_check

LIB = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib'

def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=True).stdout

def main():
    lib = LIB / (sys.argv[1] if len(sys.argv) > 1 else 'libmpr.so')
    e = Elf(str(lib))
    r = (json.loads((ROOT / 'analysis/session20/evidence/libobj-rtti-vtables.json').read_text())
         if lib.name == 'libObj.so' else recover(e))
    self_check(e, r)
    syms = {}
    for line in run('llvm-nm', '-D', '-C', str(lib)).splitlines():
        p = line.split(maxsplit=2)
        if len(p) == 3 and p[1] in 'Tt':
            syms[int(p[0], 16) & ~1] = p[2]
    relplt = {}
    sec = e.secs['.rel.plt']
    for off in range(sec['off'], sec['off'] + sec['size'], 8):
        where, info = struct.unpack_from('<II', e.d, off)
        relplt[where] = e.syms[info >> 8][0]
    # Decode ARM PLT arithmetic; Thumb veneers start bx pc; nop.
    plt = {}
    sec = e.secs['.plt']
    for va in range(sec['addr'], sec['addr'] + sec['size'] - 12, 4):
        a, b, c = (e.u32(va + i) for i in (0, 4, 8))
        if a & 0xfffff000 == 0xe28fc000 and b & 0xfffff000 == 0xe28cc000 and c & 0xfffff000 == 0xe5bcf000:
            def imm(w):
                n, shift = w & 255, ((w >> 8) & 15) * 2
                return ((n >> shift) | (n << (32 - shift))) & 0xffffffff if shift else n
            got = va + 8 + imm(a) + imm(b) + (c & 0xfff)
            if got in relplt:
                plt[va] = (got, relplt[got])
                if e.u32(va - 4) == 0x46c04778:
                    plt[va - 4] = (got, relplt[got])
    if lib.name == 'libObj.so':
        dis = Path('/tmp/s20work/libObj-full.disasm').read_text()
    else:
        dis = run('llvm-objdump', '-d', '--no-show-raw-insn', '--triple=thumbv7-linux-gnueabi', str(lib))
    calls = []
    lines = []
    for line in dis.splitlines():
        m = re.match(r'\s*([0-9a-f]+):\s+(.*)', line)
        if not m:
            continue
        va, ins = int(m[1], 16), m[2]
        ins = re.sub(r'^(?:[0-9a-f]{2,8}\s+)+', '', ins)
        lines.append((va, line))
        m = re.match(r'(blx?|b(?:\.w)?)\s+0x([0-9a-f]+)', ins)
        if m:
            target = int(m[2], 16)
            calls.append((va, target, plt.get(target, (None, syms.get(target, '')))[1], m[1]))
    starts = sorted(set(syms) | {int(x, 16) for x in r['methods_by_entry']} | {b for _, b, _, op in calls if b not in plt and op in ('bl', 'blx')})
    targets = [int(x, 16) for x in sys.argv[2:] if ':' not in x]
    pattern = re.compile('PreReg|GetEntryIdFromDirectoryFileNumber|WriteStill|Dcf.*(Reg|Commit|Cancel)|Reg.*Dcf', re.IGNORECASE)
    selected = set(targets) | {a for a, n in syms.items() if pattern.search(n)}
    selected_names = {n for n, v in e.syms if v is not None and v & ~1 in selected}
    virtual_entries = {int(a, 16): methods for a, methods in r['methods_by_entry'].items()}
    def own(a):
        return owner(a, starts, virtual_entries, syms)
    out = {'library': str(lib.relative_to(ROOT)), 'sha256': hashlib.sha256(e.d).hexdigest(),
           'rtti': {c['name']: c for c in r['classes'].values() if c['name'] in ('MMgr', 'MMgrIf', 'AviMMgr', 'DiscMMgr', 'StillRecorder', 'StillRecorderIf', 'StillWriterFilter', 'FeaCore')},
           'symbols': {hex(a): n for a, n in syms.items() if a in selected},
           'virtuals': {hex(a): r['methods_by_entry'].get(hex(a), []) for a in selected},
           'plt': {hex(a): {'got': hex(g), 'symbol': n} for a, (g, n) in plt.items() if pattern.search(n) or n in selected_names},
           'callers': [dict(own(a), target=hex(b), symbol=n, opcode=op) for a, b, n, op in calls if b in selected or pattern.search(n)],
           'references': {hex(t): [{'va': hex(w), 'symbol': n} for w, (v, n) in e.rel.items() if v is not None and v & ~1 == t] for t in selected},
           'windows': {}, 'outgoing': {}, 'literals': {}, 'window_owners': {}}
    for spec in sys.argv[2:]:
        if ':' in spec:
            lo, hi = (int(x, 16) for x in spec.split(':'))
            window_lines = [(a,s) for a,s in lines if lo <= a < hi]
            out['windows'][spec] = '\n'.join(line for a, line in window_lines)
            out['window_owners'][spec] = own(lo)
            out['outgoing'][spec] = [{'va':hex(a), 'target':hex(b), 'symbol':n, 'opcode':op} for a,b,n,op in calls if lo <= a < hi]
            literals = []
            for a,line in window_lines:
                m = re.search(r'ldr(?:\.w)?\s+(r\d+), \[pc,.*?@ 0x([0-9a-f]+)', line)
                if not m:
                    continue
                w = int(m[2],16)
                if e.off(w) is None:
                    continue
                v=e.u32(w)
                item={'va':hex(a), 'pool':hex(w), 'value':hex(v)}
                pc_uses = [((b+4)+v)&0xffffffff for b,s in window_lines if a<b<a+28 and re.search(r'add\s+'+m[1]+', pc',s)]
                for dest in [v] + pc_uses[:1]:
                    try:
                        s=e.cstr(dest)
                    except (ValueError, TypeError):
                        continue
                    if 3<len(s)<300 and all(32<=ord(ch)<127 or ch in '\n\t\r' for ch in s):
                        item['string']=s;item['string_va']=hex(dest)
                literals.append(item)
            out['literals'][spec]=literals
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
