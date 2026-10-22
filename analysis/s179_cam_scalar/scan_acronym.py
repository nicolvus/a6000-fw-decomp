#!/usr/bin/env python3
"""S179 - base textual de la sigla CAM_SCALAR / SCALAR."""
import re, os
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
D={k:open(v,'rb').read() for k,v in BINS.items()}
pats = [b"CAM_SCALAR", b"SCALAR", b"Scalar", b"scalar", b"CAM_SCAL", b"CamScalar", b"cam_scalar"]
for p in pats:
    print(p.decode(), {k: D[k].count(p) for k in D})
print()
# RTTI con 'Scalar' en A6000
txt = re.findall(rb"[ -~]{6,200}", D["A6000"])
for t in txt:
    if b"Scalar" in t or b"SCALAR" in t:
        print(t.decode("latin1"))
