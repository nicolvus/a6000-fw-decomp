import json
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
MOD5=[b"\x05\x20", b"\x05\x30", b"\x00\x30"]     # movs r0,#5 / adds r0,#5 / adds r0,#0x20
LV6=[b"\x06\x21", b"\x06\x31"]                    # movs r1,#6 / adds r1,#6
FL1=[b"\x01\x22", b"\x01\x32"]                    # movs r2,#1 / adds r2,#1
ok=0; bad=[]
for r in rows:
    for s in r["sitios_nuevo"]:
        site=int(s,16); o=site-BASE
        buf=B[max(0,o-40):o+8]
        m=any(p in buf for p in MOD5)
        l=any(p in buf for p in LV6)
        f=any(p in buf for p in FL1)
        if m and l and f: ok+=1
        else: bad.append((hex(site),m,l,f))
print("patron (modulo 5, nivel 6, flag 1) en la ventana:",ok,"de 47")
for b in bad: print("  ",b)
