"""S58-B.4: Tv(1/256 EV; 0x1000<->1 s) -> T (4382fa94 real) -> (n, shd, spl) con 0x4383d4d0 real, para 1/4000..1 s.
M SINTÉTICO (etiquetado): lt=4096 (16 us si 1 ud=1/256 us), vmax=4176, hmax=864, F=vmax*lt, svr=1, s0=0, fb=0, shmin=4; reloj 54 MHz.  No son valores del firmware por modo."""
import math, json
from wtrace import W
from timing_model import time_split
from a6_verify import real, AMB
def tv_code(t): return round(0x1000 + 256 * math.log2(1 / t))
w = W(ambito=[(0x4382f000, 0x43830000), (0x43900000, 0x43930000), (0x439c0000, 0x439d0000)], fill=0)
M = dict(s0=0, lt=4096, fb=0, F=4176 * 4096, vmax=4176, shmin=4, hmax=864, svr=1)
rows = []
w2 = W(ambito=AMB, fill=0)
for name, t in (('1/4000', 1 / 4000), ('1/1000', 1 / 1000), ('1/250', 1 / 250), ('1/60', 1 / 60), ('1/4', 1 / 4), ('1', 1.0)):
    tv = tv_code(t); T = w.call(0x4382fa94, tv); n, shd, spl, lines = time_split(T, M, 54_000_000)
    got = real(w2, T, M, 54_000_000)
    rows.append(dict(speed=name, tv=hex(tv), T_units=T, T_s_if_1_256us=T / 256e6, n=n, shd=shd, spl=spl, lines=lines, real=got))
    print(name, hex(tv), T, round(T / 256e6, 6), 's', 'n', n, 'shd', shd, 'spl', spl, 'real==model', got == (n, shd, spl))
json.dump(rows, open('out/a6000_timing_scenarios.json', 'w'), indent=1)
