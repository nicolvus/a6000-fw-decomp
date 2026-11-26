import re
from pathlib import Path
ROOT=Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
def strings(p, minlen=6):
    b=Path(p).read_bytes()
    return set(m.group().decode('latin1') for m in re.finditer(rb'[\x20-\x7e]{%d,}'%minlen, b))
a=strings(ROOT/'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin')
b=strings('/tmp/avcam_cfw.bin')
print('cadenas 3.21:', len(a), ' cfw(3.38):', len(b))
print('solo en 3.21:', len(a-b), ' solo en 3.38:', len(b-a))
import sys
pat=re.compile(r'(?i)(movie|play|thumb|mp4|ifo|decod|ldec|dsp|stream|avc|hevc|frame ?rate|1920|1080|hdmi|dvp|repro)')
sa=sorted(x for x in (a-b) if pat.search(x))
sb=sorted(x for x in (b-a) if pat.search(x))
print('\n--- solo en 3.21 (reproduccion) ---')
for x in sa[:40]: print('  ', x[:110])
print('\n--- solo en 3.38 (reproduccion) ---')
for x in sb[:40]: print('  ', x[:110])
