import struct, sys
F="/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so"
d=open(F,'rb').read()
TA,TS=0x120228,0x683c5c
targets={int(x,16) for x in sys.argv[1:]}
res=[]
for a in range(TA,TA+TS-4,2):
    hw=struct.unpack_from('<H',d,a)[0]
    tgt=None; ln=2
    if (hw&0xF800)==0x4800:
        tgt=((a+4)&~3)+(hw&0xff)*4
    elif hw==0xF8DF:
        hw2=struct.unpack_from('<H',d,a+2)[0]
        tgt=((a+4)&~3)+(hw2&0xfff); ln=4
    if tgt in targets:
        res.append((a,ln,tgt,struct.unpack_from('<I',d,tgt)[0]))
for a,ln,t,v in res:
    print("%#010x (len%d) -> [%#x] = %#010x"%(a,ln,t,v))
print(len(res),"hits")
