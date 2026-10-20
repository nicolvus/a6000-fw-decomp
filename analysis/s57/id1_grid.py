"""S57-A: rejilla de ID1 (A=idx1 de la tabla, B=idx2) por modo de arrastre x ShutMode x SSB x banderas, con código real."""
import sys, json
sys.path.insert(0, '.')
from emu57 import Emu, set_exposure, wire
MODES = [0xb, 1, 5, 0x10, 7, 0x12, 3, 0xa, 0xf, 0x18, 0x1a, 0x19, 0x2f]
def run(col_mode, shut, ssb=0, fill=0, **flags):
    e = Emu(fill=fill); e.new_obj()
    col = MODES.index(col_mode)
    e.setf(0x170, col_mode, 4); e.setf(0x174, col_mode, 4)
    e.call(0x436d6570, e.O, col)                 # carga de columna de la matriz en registros sombra
    base = e.id1()
    for k, v in flags.items(): e.setf(int(k[1:], 16), v, 4 if k == 'f27c' else 1)
    set_exposure(e, shut)
    se = e.id1()
    if ssb: e.setf(0x268, 1)
    e.mmio.clear(); e.flags.clear()
    e.call(0x436d839c, e.O, 1)
    w = wire(e)
    seq = [d for tx in w for a, d in tx if a == 1]
    return dict(base=base, after_setexp=se, post=e.id1(), wire_id1=seq, ssb_cleared=e.getf(0x268) == 0)
if __name__ == '__main__':
    out = []
    for m in MODES:
        for s in range(5):
            for ssb in (0, 1):
                r = run(m, s, ssb); r.update(mode=m, shut=s, ssb=ssb); out.append(r)
    json.dump(out, open('id1_grid.json', 'w'), indent=0)
    for r in out:
        if r['ssb'] == 0: print(hex(r['mode']), r['shut'], [hex(x) for x in r['base']], [hex(x) for x in r['after_setexp']], [hex(x) for x in r['wire_id1']])
