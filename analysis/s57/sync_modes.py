"""S57-F: efecto de SyncMode (cfg[0]) del P2S sobre las escrituras MMIO de control (código real, formateador/commit)."""
import sys; sys.path.insert(0, '../s56')
from p2s_emu import P2S
out = {}
for mode in (0, 1, 2, 3):
    e = P2S(); e.u.mem_write(e.cfg, bytes([mode, 1, 0, 2, 0]))
    e.mmio.clear(); e.flags.clear()
    try:
        if mode == 2:
            e.call(0x436d5b74, e.P, e.cfg); e.call(0x436d5e04, e.P, 1, 0x40); e.call(0x43ad8dca, e.P)
        else:
            e.call(0x43ad8d1c, e.P); e.call(0x43ad9004, e.P, 1, 0x40); e.call(0x43ad8d38, e.P); e.call(0x43ad8de4, e.P, e.cfg)
    except Exception as ex: out[mode] = ('ERR', str(ex)); continue
    ctl = [(hex(a), sz, hex(v)) for a, sz, v in e.mmio if not (0xfc088340 <= a < 0xfc088540)]
    out[mode] = (ctl, e.flags)
if __name__ == '__main__':
    for m, (c, f) in out.items(): print('mode', m, c, '\n   flags', f)
