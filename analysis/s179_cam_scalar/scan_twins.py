#!/usr/bin/env python3
"""S179 - gemelos exactos en +14 (patron 'se reescribe el logging')."""
import json, os
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
D={k:open(v,'rb').read() for k,v in BINS.items()}
G=json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
G7=json.load(open("analysis/s169_drive_api/pic_refs_strict_a7s.json"))
G63=json.load(open("analysis/s169_drive_api/pic_refs_strict_a6300.json"))
S=json.load(open("analysis/s179_cam_scalar/strings_raw.json"))["A6000"]
PRE=b"[CAM_SCALAR]: "
out=[]
ok=0
for s in S:
    a=s["vaddr"]; o=a-BASE
    full=D["A6000"][o:D["A6000"].find(b"\x00",o)]
    assert full.startswith(PRE), hex(a)
    twin_text=full[14:]
    t=a+14
    assert D["A6000"][t-BASE:t-BASE+len(twin_text)]==twin_text
    a7 = D["A7S"].count(twin_text); a63 = D["A6300"].count(twin_text)
    r={"vaddr": hex(a), "prefijo": 14, "texto": full.decode("latin1"),
       "gemelo_addr": hex(t), "gemelo_texto": twin_text.decode("latin1"),
       "gemelo_en_A6000": D["A6000"].count(twin_text),
       "gemelo_en_A7S": a7, "gemelo_en_A6300": a63,
       "sitios_nuevo": G.get(hex(a), []), "sitios_gemelo_A6000": G.get(hex(t), []),
       "sitios_gemelo_A7S": G7.get(hex(t), [])}
    out.append(r)
    ok+=1
    print(f"{hex(a)} twin={hex(t)}  A6000={r['gemelo_en_A6000']} A7S={a7} A6300={a63}  "
          f"sit_nuevo={len(r['sitios_nuevo'])} sit_gem_A6000={len(r['sitios_gemelo_A6000'])}  {twin_text[:52]!r}")
json.dump(out, open("analysis/s179_cam_scalar/twins.json","w"), indent=1)
print("cadenas verificadas:", ok)
print("gemelos presentes en A7S:", sum(1 for r in out if r['gemelo_en_A7S']>0), "/", len(out))
print("gemelos presentes en A6300:", sum(1 for r in out if r['gemelo_en_A6300']>0), "/", len(out))
print("total sitios (nuevos):", sum(len(r['sitios_nuevo']) for r in out))
print("total sitios (gemelos A6000):", sum(len(r['sitios_gemelo_A6000']) for r in out))
