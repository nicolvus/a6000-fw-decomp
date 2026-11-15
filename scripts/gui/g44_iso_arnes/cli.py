import sys,json,time,base64,urllib.request,http.client
P=8631
def tecla(k,n=1,esp=1.2):
    for _ in range(n):
        for v in (1,0):
            urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{P}/tecla",json.dumps({"k":k,"v":v}).encode()),timeout=5).read(); time.sleep(.15)
        time.sleep(esp)
def foto(nombre):
    urllib.request.urlopen(f"http://127.0.0.1:{P}/refrescar",timeout=5) if False else urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{P}/refrescar",b""),timeout=5).read()
    c=http.client.HTTPConnection("127.0.0.1",P,timeout=20);c.request("GET","/eventos");r=c.getresponse()
    t=time.time()
    while time.time()-t<15:
        l=r.readline()
        if l.startswith(b"data: "):
            open(nombre,"wb").write(base64.b64decode(l[6:]));break
    c.close()
if __name__=="__main__":
    a=sys.argv[1:]
    for x in a:
        if x.startswith("foto:"): foto(x[5:])
        elif ":" in x: k,n=x.split(":");tecla(k,int(n))
        else: tecla(x)
