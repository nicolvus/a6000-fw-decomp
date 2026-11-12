"""T9 — ISP emulado en la ventana en vivo: shader WebGL2 con las curvas reales de `av-cam.bin` + panel de depuración que escribe los ids de Backup de PP.

El pipeline y el estado (REAL/APROX/NO_VERIFICADO) de cada etapa están en `scripts/gui/isp/modelo.py` (referencia en CPU) y en docs/gui/g23-isp-bionz-emulado.md.
Puntos: GET /isp/tablas.json (parámetros, curvas, ids, etapas), GET /isp/curvas.bin (u16 LE, 2048 por curva, en el orden de `curvas`),
GET /isp/estado?perfil=N (valores del perfil en la NVRAM emulada), POST /isp/nv ({perfil, cambios:{ajuste:valor}} → registros de Backup en nvram.json del perfil).
"""
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "isp"))
import modelo as M

ETAPAS = [  # (etapa, estado, fuente)
    ("Entrada sRGB→lineal × exposición", "APROX", "el RAW del sensor no existe en la emulación; la exposición (nivel de entrada de la LUT) es ajustable"),
    ("Black Level", "APROX", "orden y existencia por G16; paso por unidad sin verificar"),
    ("Matriz de color (Backup 0x30001)", "REAL (valores) / APROX (uso)", "matrices del volcado real; solo Movie=índice 0 verificado; se aplican sobre sRGB lineal"),
    ("Gamma: curva por número (2048 pt)", "REAL", "av-cam.bin A6000/A7S/A6300; asignación valor app→curva por G25/G18; foto Still = gamma 0"),
    ("Saturación / Color Phase / Color Depth", "APROX", "−8 = B&W es REAL (G27); escalas y pesos por tono sin verificar"),
    ("Detail", "APROX", "máscara de enfoque sobre la luminancia; sin dato del firmware"),
    ("Black Gamma, Knee, YCbCr/rango", "NO_VERIFICADO", "no implementado; la cola de 13 u16 de cada curva (rodilla/rango) no está decodificada"),
]

HTML = """<fieldset id="isp"><legend>ISP (BIONZ X emulado)</legend>
<label><input type="checkbox" id="isp_on"> aplicar a imagen, disparo y vídeo</label>
<label>Perfil <select id="isp_pp"></select></label>
<label>Exposición de entrada <input type="range" id="isp_k" min="0.25" max="8" step="0.05" value="2"> <span id="isp_kv">2.0</span></label>
<label>Obturador (MEDIDO) <select id="isp_ob"><option value="">Mecánico (referencia)</option><option value="efcs_mec_bandas">EFCS activado</option><option value="silent_mec_bandas">Silent</option></select>
<select id="isp_ob2"></select></label><div id="isp_par"></div><div id="isp_info"><small></small></div><details><summary>Etapas</summary><small id="isp_et"></small></details></fieldset>"""

JS = r"""
var ISP={on:false,gl:null,t:null,perfil:0,p:{},k:2,curvas:[],q:null,kk:null,_nv:0,
async init(){this.t=await (await fetch('/isp/tablas.json')).json();this.curvas=this.t.curvas;
const sel=document.getElementById('isp_pp');this.t.perfiles.forEach((n,i)=>sel.add(new Option(n,i)));
document.getElementById('isp_et').innerHTML=this.t.etapas.map(e=>`<br>${e[0]}: <b>${e[1]}</b> — ${e[2]}`).join('');
const par=document.getElementById('isp_par');par.innerHTML='';
for(const [i,d] of Object.entries(this.t.params)){const L=document.createElement('label');L.textContent=d.etiqueta+' ';
let ctl;if(d.opciones){ctl=document.createElement('select');for(const [v,n] of Object.entries(d.opciones))ctl.add(new Option(n,v))}
else{ctl=document.createElement('input');ctl.type='range';ctl.min=d.min;ctl.max=d.max;ctl.step=1;const o=document.createElement('span');o.id='isp_v_'+d.id;L.append(ctl,' ',o);ctl.oninput=()=>{o.textContent=ctl.value}}
ctl.id='isp_c_'+d.id;ctl.dataset.id=d.id;if(!d.opciones)ctl.title=`clave de ajuste ${i}`;ctl.addEventListener('input',()=>this.cambia(d.id,+ctl.value));
if(d.opciones)L.append(ctl);par.append(L)}
sel.onchange=()=>this.carga(+sel.value);const o2=document.getElementById('isp_ob2');this.t.obturador.forEach((f,i)=>o2.add(new Option(`${f.velocidad} · tanda ${f.tanda}`,i)));document.getElementById('isp_ob').onchange=o2.onchange=()=>pinta();
document.getElementById('isp_on').onchange=e=>{this.on=e.target.checked;pinta()};
document.getElementById('isp_k').oninput=e=>{this.k=+e.target.value;document.getElementById('isp_kv').textContent=this.k.toFixed(2);pinta()};
const pc=await (await fetch('/isp/curvas.bin')).arrayBuffer();const u=new Uint16Array(pc),n=this.curvas.length;this.lut=new Float32Array(u.length);for(let i=0;i<u.length;i++)this.lut[i]=u[i]/1023;
this.nl=n;await this.carga(0)},
async carga(pf){this.perfil=pf;const e=await (await fetch('/isp/estado?perfil='+pf)).json();this.p=Object.assign({},this.t.neutro,e.valores);
for(const d of Object.values(this.t.params)){const c=document.getElementById('isp_c_'+d.id);c.value=this.p[d.id];const o=document.getElementById('isp_v_'+d.id);if(o)o.textContent=c.value}this.info();pinta()},
cambia(id,v){this.p[id]=v;this.info();pinta();clearTimeout(this._nv);this._nv=setTimeout(()=>fetch('/isp/nv',{method:'POST',body:JSON.stringify({perfil:this.perfil,cambios:{[id]:v}})}),150)},
curvaNombre(){return this.t.curva_de_gamma[this.p.gamma]},
info(){const n=this.curvaNombre();document.querySelector('#isp_info small').innerHTML=`Backup ids del perfil ${this.t.perfiles[this.perfil]}: gamma ${this.t.ids[this.perfil][7].toString(16)}, saturación ${this.t.ids[this.perfil][29].toString(16)}…<br>`+
`Curva activa: <b>${n.nombre}</b> (${n.clave}, gamma nº ${n.numero}) · ${n.estado}`},
nota(){return ` [ISP: ${this.on?'curva REAL '+this.curvaNombre().clave+'; matriz REAL; resto APROX/NO_VERIFICADO':'desactivado: entrada sin procesar'}]`},
gl_init(){const cv=this.cv=document.createElement('canvas');const gl=this.gl=cv.getContext('webgl2',{premultipliedAlpha:false,preserveDrawingBuffer:true});if(!gl){this.on=false;return false}
const vs=`#version 300 es
in vec2 a;out vec2 uv;void main(){uv=a*.5+.5;uv.y=1.-uv.y;gl_Position=vec4(a,0,1);}`;
const fs=`#version 300 es
precision highp float;uniform sampler2D img;uniform highp sampler2D lut;uniform float k,bl,row,sat,ph,det;uniform mat3 M;uniform float d[6];uniform float bd[8];uniform vec2 px;in vec2 uv;out vec4 o;
const vec3 W=vec3(.2126,.7152,.0722);const float H[6]=float[6](0.,2.0943951,4.1887902,3.1415927,5.2359878,1.0471976);
vec3 s2l(vec3 v){return mix(pow((v+.055)/1.055,vec3(2.4)),v/12.92,lessThanEqual(v,vec3(.04045)));}
float L(float x){float f=clamp(x,0.,1.)*2047.;int i=min(int(f),2046);float t=f-float(i);return mix(texelFetch(lut,ivec2(i,int(row)),0).r,texelFetch(lut,ivec2(i+1,int(row)),0).r,t);}
void main(){vec3 c=texture(img,uv).rgb;
if(det!=0.){float a=dot(c,W),b=0.;b+=dot(texture(img,uv+vec2(px.x,0)).rgb,W);b+=dot(texture(img,uv-vec2(px.x,0)).rgb,W);b+=dot(texture(img,uv+vec2(0,px.y)).rgb,W);b+=dot(texture(img,uv-vec2(0,px.y)).rgb,W);c+=det*(a-b*.25);}
float fy=clamp(uv.y*8.-.5,0.,7.);int fi=min(int(fy),6);float gb=mix(bd[fi],bd[fi+1],fy-float(fi));vec3 l=s2l(clamp(c,0.,1.))*k*gb;l=max(l-bl,0.);l=max(M*l,0.);vec3 y=vec3(L(l.r),L(l.g),L(l.b));
float lu=dot(y,W),cb=(y.b-lu)/1.8556,cr=(y.r-lu)/1.5748;float cs=cos(ph),sn=sin(ph);float cb2=cb*cs-cr*sn,cr2=cb*sn+cr*cs;float h=atan(cr2,cb2),g=0.;
for(int i=0;i<6;i++){float w=max(cos(h-H[i]),0.);g+=w*w*d[i];}
g=sat*(1.+g);cb2*=g;cr2*=g;float r=lu+1.5748*cr2,b=lu+1.8556*cb2,gg=(lu-.2126*r-.0722*b)/.7152;o=vec4(clamp(vec3(r,gg,b),0.,1.),1);}`;
const sh=(t,s)=>{const x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(x));return x};
const pr=this.pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,vs));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,fs));gl.linkProgram(pr);gl.useProgram(pr);
const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);const a=gl.getAttribLocation(pr,'a');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
const tx=(u)=>{const t=gl.createTexture();gl.activeTexture(gl.TEXTURE0+u);gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);return t};
this.timg=tx(0);gl.activeTexture(gl.TEXTURE1);const tl=tx(1);gl.texImage2D(gl.TEXTURE_2D,0,gl.R32F,2048,this.nl,0,gl.RED,gl.FLOAT,this.lut);
this.u=n=>gl.getUniformLocation(pr,n);gl.uniform1i(this.u('img'),0);gl.uniform1i(this.u('lut'),1);this.pre=document.createElement('canvas');return true},
params(){const p=this.p,t=this.t,gl=this.gl,u=this.u;const m=t.matrices[t.matriz_de_color[p.color_mode]??t.matriz_defecto];
gl.uniform1f(u('k'),this.k);gl.uniform1f(u('bl'),p.black_level*t.pasos.black);gl.uniform1f(u('row'),this.curvas.indexOf(this.curvaNombre().clave));
gl.uniformMatrix3fv(u('M'),false,new Float32Array([m[0]/1024,m[3]/1024,m[6]/1024,m[1]/1024,m[4]/1024,m[7]/1024,m[2]/1024,m[5]/1024,m[8]/1024]));
gl.uniform1f(u('sat'),Math.max(0,1+p.saturation*t.pasos.sat));gl.uniform1f(u('ph'),p.phase*t.pasos.fase*Math.PI/180);
gl.uniform1fv(u('d'),new Float32Array(['r','g','b','c','m','y'].map(c=>p['cd_'+c]*t.pasos.depth)));gl.uniform1f(u('det'),p.det_level*t.pasos.detalle);gl.uniform1fv(u('bd'),new Float32Array(this.bandas()))},
bandas(){const m=document.getElementById('isp_ob').value,f=this.t.obturador[+document.getElementById('isp_ob2').value];let b=m&&f?f[m].slice():[];
if(!b.some(v=>v!==null))return new Float32Array(8).fill(1);b=b.map((v,i)=>{if(v!==null)return v;let r=null,dm=9;b.forEach((w,j)=>{if(w!==null&&Math.abs(i-j)<dm){dm=Math.abs(i-j);r=w}});return r});return b},
dibuja(g,s,dx,dy,w,h,W,H){if(!this.gl&&!this.gl_init()){g.drawImage(s,dx,dy,w,h);return}
const pre=this.pre,cv=this.cv,gl=this.gl;if(pre.width!=W||pre.height!=H){pre.width=cv.width=W;pre.height=cv.height=H}
const q=pre.getContext('2d');q.fillStyle='#000';q.fillRect(0,0,W,H);q.drawImage(s,dx,dy,w,h);gl.viewport(0,0,W,H);
gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,this.timg);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,pre);
this.params();gl.uniform2f(this.u('px'),1/W,1/H);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);g.drawImage(cv,0,0)},
/* punto de control para pruebas: aplica el shader a un color sRGB 8 bits y devuelve el RGB de salida 8 bits */
sonda(rgb){const W=4,H=4,p=document.createElement('canvas');p.width=W;p.height=H;const c=p.getContext('2d');c.fillStyle=`rgb(${rgb})`;c.fillRect(0,0,W,H);
const g=document.createElement('canvas').getContext('2d');g.canvas.width=W;g.canvas.height=H;const on=this.on;this.on=true;this.dibuja(g,p,0,0,W,H,W,H);this.on=on;return Array.from(g.getImageData(1,1,1,1).data.slice(0,3))}};
ISP.init().catch(e=>{document.getElementById('isp_info').textContent='ISP: '+e.message});
"""


def _bandas() -> list:
    f = M.DIR / "obturador_bandas.json"
    return json.loads(f.read_text())["filas"] if f.is_file() else []


def _tablas_json(t: "M.Tablas") -> dict:
    claves = sorted({*M.CURVA_VIDEO.values(), *M.CURVA_FOTO.values()})
    estado = {"a6000": "REAL (A6000)", "a7s": "REAL (A7S, instalada por el CFW)", "a6300": "REAL (A6300, instalada por el CFW)"}
    def num(k): return int(k.split("_")[1][1:], 16)
    c_gamma = {str(g): {"clave": k, "numero": num(k), "nombre": M.GAMMA_NOMBRES[g], "estado": estado[k.split("_")[0]] + ("; identificación de la curva con el nombre: INFERENCIA (G16)" if g in (3, 10, 11) else "")}
               for g, k in M.CURVA_VIDEO.items()}
    perf = [f"PP{i + 1}" for i in range(9)] + ["Off (bloque neutro)", "PP10"]
    params = {str(i): {"id": v[0], "etiqueta": v[1], "min": v[2], "max": v[3]} for i, v in M.PARAMS.items() if v[0] not in ("color_level", "bg_range", "bg_level", "knee_mode")}
    params["7"]["opciones"] = {str(g): n for g, n in M.GAMMA_NOMBRES.items()}
    params["0"]["opciones"] = {str(g): n for g, n in M.COLOR_NOMBRES.items() if g != 8}
    return {"curvas": claves, "curva_de_gamma": c_gamma, "perfiles": perf, "params": params, "neutro": M.NEUTRO, "etapas": ETAPAS,
            "matrices": t.matrices.__mul__(1024).round().astype(int).reshape(-1, 9).tolist(), "matriz_de_color": {str(k): v for k, v in M.MATRIZ_COLOR.items()}, "matriz_defecto": M.MATRIZ_DEFECTO,
            "pasos": {"black": M.PASO_BLACK, "sat": M.PASO_SAT, "fase": M.PASO_FASE_GRADOS, "depth": M.PASO_DEPTH, "detalle": 0.15},
            "ids": t.pp_ids, "obturador": _bandas()}


def maneja(h, metodo: str, ruta: str, cuerpo: bytes, vm) -> bool:
    """Atiende /isp/*; `vm` expone `.nvram` ({id: bytes}) y `.nv("<id hex> <datos hex>")` (live.py). Devuelve False si no es suya."""
    u = urlparse(ruta)
    if not u.path.startswith("/isp/"):
        return False
    t = M.Tablas()

    def resp(datos: bytes, tipo: str, codigo: int = 200) -> None:
        h.send_response(codigo)
        h.send_header("Content-Type", tipo)
        h.send_header("Content-Length", str(len(datos)))
        h.end_headers()
        h.wfile.write(datos)

    js = lambda o, c=200: resp(json.dumps(o).encode(), "application/json", c)
    if metodo == "GET" and u.path == "/isp/tablas.json":
        js(_tablas_json(t))
    elif metodo == "GET" and u.path == "/isp/curvas.bin":
        resp(b"".join(t.curvas[k].astype("<u2").tobytes() for k in _tablas_json(t)["curvas"]), "application/octet-stream")
    elif metodo == "GET" and u.path == "/isp/estado":
        p = int(parse_qs(u.query).get("perfil", ["0"])[0])
        js({"perfil": p, "valores": M.ajustes_desde_nvram(t, p, vm.nvram) if 0 <= p <= 10 else {}})
    elif metodo == "POST" and u.path == "/isp/nv":
        try:
            d = json.loads(cuerpo)
            ops = M.nvram_ops(t, int(d["perfil"]), {k: int(v) for k, v in d["cambios"].items()})
        except (ValueError, KeyError, IndexError) as e:
            return js({"error": str(e)}, 400) or True
        for i, b in ops.items():
            vm.nv(f"{i:x} {b.hex()}")
        js({"escritos": {hex(i): b.hex() for i, b in ops.items()}})
    else:
        h.send_error(404)
    return True
