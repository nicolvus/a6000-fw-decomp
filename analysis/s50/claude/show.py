import json,sys
# uso: show.py salida.jsonl [maxchars]; imprime el payload sin el perfil de análisis
mx=int(sys.argv[2]) if len(sys.argv)>2 else 1500
for l in open(sys.argv[1]):
    r=json.loads(l); c=r['call']
    try: p=json.loads(r['result']['content'][0]['text'])
    except Exception: p=r.get('result',r)
    for k in ('evidence_id','subject','provider','analysis_profile','coverage'): 
        if isinstance(p,dict): p.pop(k,None)
    print('##',c['tool'],json.dumps(c['args']),'|',json.dumps(p)[:mx])
