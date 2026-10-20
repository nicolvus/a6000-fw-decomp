"""Resuelve cadenas PC-relativas (ldr rX,[pc,#i]; add rX,pc) en un rango ELF Thumb-2 usando llvm-objdump.
Uso: python3 -I scripts/thumb_pc_strings.py lib.so 0xINI 0xFIN"""
import re, struct, subprocess, sys
lib, a, b = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
data = open(lib, 'rb').read()
out = subprocess.run(['llvm-objdump', '-d', '--triple=thumbv7', f'--start-address={a}', f'--stop-address={b}', lib],
                     capture_output=True, text=True).stdout
pend = {}
for l in out.splitlines():
    m = re.match(r'\s+([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+){1,2}\s*(\S+)\s+(.*)', l)
    if not m: continue
    addr, op, args = int(m.group(1), 16), m.group(2), m.group(3)
    mm = re.match(r'(r\d+|r1[0-2]), \[pc, #(0x[0-9a-f]+)\]', args)
    if op.startswith('ldr') and mm:
        base = ((addr + 4) & ~3) + int(mm.group(2), 16)
        pend[mm.group(1)] = struct.unpack_from('<I', data, base)[0]
    elif op == 'add' and re.match(r'(r\d+), pc', args):
        r = args.split(',')[0]
        if r in pend:
            s = (pend[r] + addr + 4) & 0xffffffff
            if s < len(data):
                e = data.find(b'\0', s)
                txt = data[s:e]
                if 3 <= len(txt) < 200 and all(32 <= c < 127 or c in (9, 10) for c in txt):
                    print(f'{addr:x}: {txt.decode()!r}')
