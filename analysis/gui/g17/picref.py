"""Referencias PIC Thumb (ldr rX,[pc,#i] ; ... ; add rX,pc) a una dirección en un ELF ARM (vaddr == offset en .text de estas .so)."""
import struct,sys,json
def refs(d, targets, text=(0, None), gap=24):
    T=set(targets); out={t:[] for t in T}; U=struct.unpack_from
    end=text[1] or len(d)-4
    pend={}  # reg -> (lit_value, addr)
    for o in range(text[0], end, 2):
        h=U('<H',d,o)[0]
        if (h&0xf800)==0x4800:  # ldr rX,[pc,#imm8*4]
            r=(h>>8)&7; lit=((o+4)&~3)+(h&0xff)*4
            if lit+4<=len(d): pend[r]=(U('<I',d,lit)[0],o)
        elif (h&0xff78)==0x4478:  # add rX, pc  (rdn = DN:Rdn)
            r=(h&7)|((h>>4)&8)
            if r in pend and o-pend[r][1]<=gap:
                v=(pend[r][0]+o+4)&0xffffffff
                if v in T: out[v].append(o)
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    names=[s.encode() for s in sys.argv[2:]]
    tg={}
    for n in names:
        i=-1
        while (i:=d.find(n,i+1))>=0:
            st=i
            while st>0 and d[st-1]!=0: st-=1
            tg[st]=d[st:st+90].split(b'\0')[0].decode('latin1')
    r=refs(d,tg)
    for t,v in r.items(): print(hex(t),[hex(x) for x in v],tg[t][:80])
