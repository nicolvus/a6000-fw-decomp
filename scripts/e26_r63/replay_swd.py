import re,sys
st={}; out=[]
for l in open(sys.argv[1]):
    m=re.match(r'(\S+) inicial (\w+): (.*)',l)
    if m:
        a=int(m.group(2),16)
        for k,w in enumerate(m.group(3).split()): st[a+4*k]=w
        continue
    m=re.match(r'(\S+) \+(\d+)ms (.*)',l)
    if not m: continue
    for a,o,n in re.findall(r'(\w+):(\w+)->(\w+)',m.group(3)): st[int(a,16)]=n
    if st.get(0x8401ca2c,'')[4:6] in ('d4','c4'):
        b=lambda a: bytes.fromhex(st[a&~3])[a&3]
        pkt=bytes.fromhex(''.join(st[0x83ed4948+4*i] for i in range(4)))
        regs={hex(a):st[a] for a in sorted(st) if 0x8401c670<=a<0x8401c7e8}
        key=(pkt.hex(),tuple(regs.values()))
        if not out or out[-1][1]!=key:
            out.append((m.group(1),key,regs,b))
            r5A=(b(0x8401c742)<<8)|b(0x8401c746); r5B=(b(0x8401c682)<<8)|b(0x8401c686)
            print(m.group(1),'ID1',st[0x8401ca2c][4:6],'A:',' '.join(st[a] for a in range(0x8401c740,0x8401c770,4)),'B:',' '.join(st[a] for a in range(0x8401c670,0x8401c6b0,4)),'pkt',pkt.hex(),'Tv=%04x'%int.from_bytes(pkt[2:4],'little'),'pkt1=%02x'%pkt[1],'r5A=%d r5B=%d'%(r5A,r5B),'dur',st[0x83eee76c])
