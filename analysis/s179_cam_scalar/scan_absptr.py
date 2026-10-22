#!/usr/bin/env python3
"""S179 - punteros absolutos de 4 bytes a las 34 cadenas prefijadas y a sus gemelos."""
import json, struct
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
D={k:open(v,'rb').read() for k,v in BINS.items()}
rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
res=[]
for r in rows:
    a=int(r["vaddr"],16); t=int(r["gemelo"],16)
    row={"vaddr":r["vaddr"],"gemelo":r["gemelo"],"texto":r["texto"]}
    for k,d in D.items():
        for lab,addr in (("nuevo",a),("gemelo",t)):
            pat=struct.pack("<I",addr)
            hits=[]; i=d.find(pat)
            while i>=0:
                hits.append(i+BASE); i=d.find(pat,i+1)
            row[f"abs_{k}_{lab}"]=hits
    res.append(row)
    tot=sum(len(v) for k,v in row.items() if k.startswith("abs_"))
    print(f"{r['vaddr']} twin={r['gemelo']} abs_total={tot} " + " ".join(f"{k}={len(v)}" for k,v in row.items() if k.startswith("abs_") and v))
json.dump(res,open("analysis/s179_cam_scalar/abs_ptrs.json","w"),indent=1)
print()
print("cadenas con algun puntero absoluto:",sum(1 for r in res if any(v for k,v in r.items() if k.startswith("abs_"))))
