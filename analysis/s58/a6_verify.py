"""S58-A.4: valida time_split (modelo Python) contra el código real 0x4383d4d0 en Unicorn con M, T, clk aleatorios."""
import random
from wtrace import W
from timing_model import time_split
AMB = [(0x4383d4d0, 0x4383d5b8), (0x43550000, 0x43570000), (0x43b00000, 0x43b10000)]
MB, OUT = 0x45400000, 0x45500000
def real(w, T, M, clk):
    w.u.mem_write(MB, bytes(0x40))
    w.w32(MB + 0x00, M['s0']); w.w32(MB + 4, M['lt']); w.w32(MB + 8, M['fb']); w.w16(MB + 0x10, M['vmax']); w.w16(MB + 0x14, M['shmin'])
    w.u.mem_write(MB + 0x16, bytes([M['svr']])); w.w32(MB + 0x20, M['F']); w.w16(MB + 0x2c, M['hmax'])
    w.u.mem_write(OUT, bytes(16))
    w.call(0x4383d4d0, T, MB, clk, OUT, stack=(OUT + 4, OUT + 8))
    return w.r32(OUT), w.r16(OUT + 4), w.r32(OUT + 8)
def main():
  rnd = random.Random(58); ok = tot = 0; bad = []
  for k in range(300):
      M = dict(s0=rnd.choice([0, 1_000_000, rnd.randrange(1 << 28)]), lt=rnd.choice([1, 4_096_000, rnd.randrange(1, 1 << 24)]), fb=rnd.randrange(1 << 20),
               F=rnd.choice([1, 17_100_000_000 // 256, rnd.randrange(1, 1 << 22)]), vmax=rnd.choice([4176, 1300, rnd.randrange(1 << 16)]), shmin=rnd.randrange(0, 40),
               hmax=rnd.choice([0, 864, rnd.randrange(1 << 12)]), svr=rnd.choice([1, 2, 4, rnd.randrange(1, 8)]))
      T = rnd.choice([rnd.randrange(1 << 32), rnd.randrange(1 << 24), rnd.randrange(1 << 20) * 256]); clk = rnd.choice([0, 54_000_000, 72_000_000, 143_000_000])
      for fill in (0, 0xa5):
          w = W(ambito=AMB, fill=fill)
          got = real(w, T, M, clk); n, shd, spl, _ = time_split(T, M, clk)
          tot += 1; good = got == (n, shd, spl)
          ok += good
          if not good and len(bad) < 5: bad.append((T, M, clk, got, (n, shd, spl)))
  print('time_split modelo == código real:', ok, '/', tot)
  for b in bad: print(b)

if __name__ == '__main__': main()
