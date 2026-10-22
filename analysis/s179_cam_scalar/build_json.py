#!/usr/bin/env python3
"""S179 - genera analysis/s179_cam_scalar/cam_scalar.json"""
import json, os, re
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def P(*a): return os.path.join(ROOT,*a)
BASE=0x43541000
BINS={"A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"}
D={k:open(P(v),'rb').read() for k,v in BINS.items()}
S=json.load(open(P("analysis/s179_cam_scalar/strings_raw.json")))["A6000"]
PIC=json.load(open(P("analysis/s179_cam_scalar/pic_full.json")))
TW={t["vaddr"]:t for t in json.load(open(P("analysis/s179_cam_scalar/twins.json")))}
VER=json.load(open(P("analysis/s179_cam_scalar/pic_verified.json")))
FUNC=json.load(open(P("analysis/s179_cam_scalar/func_map.json")))["funciones"]
ABS=json.load(open(P("analysis/s179_cam_scalar/abs_ptrs.json")))
NAMES={"req_sequence_create_stream","req_tool_get_image_info","req_filter_develop","req_filter_miniature",
"req_filter_face_nr","req_filter_soft_focus","req_image_destruct","req_image_clone","req_image_extract",
"req_image_insert","req_image_parse","req_raw_image_parse","Start_Develop","Start_FaceNr","Start_SoftFocus",
"Start_Miniature","Start_Extract","Start_Insert","Start_Parse","Start_RawParse","Start_Clone",
"Start_CreateStream","CheckMemory","CheckDMMforClone","ShareDMMforClone","ConvertAspectForStill",
"SetSpecialSequence","copyStdYc","ToolGetImageInfo","HAPI_Filter_TBOX.cpp","CS_Command.cpp"}
# mapa funcion -> cadenas (nuevas)
byfunc={}
for r in PIC:
    for s in r["sitios_nuevo"]:
        byfunc.setdefault(s, []).append(r["vaddr"])
def func_of(addr):
    best=None
    for f in FUNC:
        st=int(f["func"],16)
        if st<=addr and (best is None or st>best): best=st
    return hex(best) if best else None
cadenas=[]
for r in PIC:
    a=r["vaddr"]; t=TW[a]; g=t["gemelo_addr"]
    cadenas.append({
      "vaddr":a, "longitud_texto":len(r["texto"]), "texto":r["texto"],
      "nucleo":r["texto"][14:], "nucleo_vaddr":g,
      "gemelo_exacto_en_+14":True,
      "n_sitios_pic_estrictos":r["n_sitios_nuevo"], "sitios_pic":r["sitios_nuevo"],
      "n_sitios_pic_gemelo":r["n_sitios_gemelo"], "sitios_pic_gemelo":r["sitios_gemelo"],
      "funciones":sorted({func_of(int(s,16)) for s in r["sitios_nuevo"]}),
      "nucleo_en_A7S":t["gemelo_en_A7S"], "nucleo_en_A6300":t["gemelo_en_A6300"],
      "punteros_absolutos_4B":0,
      "muerto": r["n_sitios_nuevo"]==0,
    })
ver_site={v["site"]:v for v in VER}
res={
 "hito":"S179",
 "titulo":"el modulo [CAM_SCALAR] (34 trazas) de la A6000 fw3.21",
 "base_vaddr":"0x43541000",
 "metodo":"regla PIC estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py); mapa global reutilizado, no re-barrado",
 "cifras":{
   "cadenas_con_token":len(S),
   "apariciones_token_A6000":D["A6000"].count(b"[CAM_SCALAR]"),
   "apariciones_token_A7S":D["A7S"].count(b"[CAM_SCALAR]"),
   "apariciones_token_A6300":D["A6300"].count(b"[CAM_SCALAR]"),
   "rango_cadenas":[min(c["vaddr"] for c in cadenas), max(c["vaddr"] for c in cadenas)],
   "sitios_pic_nuevos":sum(c["n_sitios_pic_estrictos"] for c in cadenas),
   "sitios_pic_gemelo_+14":sum(c["n_sitios_pic_gemelo"] for c in cadenas),
   "pares_pic_verificados_a_mano":len(VER),
   "fallos_verificacion":sum(1 for v in VER if not v["ok"]),
   "reuso_de_registro":sum(1 for v in VER if v["kill"]),
   "cadenas_con_referencia":sum(1 for c in cadenas if c["n_sitios_pic_estrictos"]>0),
   "cadenas_muertas":sum(1 for c in cadenas if c["muerto"]),
   "gemelos_en_A7S":sum(1 for c in cadenas if c["nucleo_en_A7S"]>0),
   "gemelos_en_A6300":sum(1 for c in cadenas if c["nucleo_en_A6300"]>0),
   "funciones_emisoras":len(FUNC),
   "discrepancias_local_vs_mapa_global":0,
   "destinos_mapa_global":17525,
 },
 "cadenas":cadenas,
 "funciones":FUNC,
 "verificacion_pic":VER,
 "diferencial":{
   "token":{"A6000":34,"A7S":0,"A6300":0},
   "nucleos_sin_prefijo_presentes":{"A6000":34,"A7S":34,"A6300":34},
   "gemelo_exacto_en_mas_14":{"A6000":34},
   "patron":"se reescribe el logging: la A6000 anade la traza [CAM_SCALAR]: (modulo 5, nivel 6) y CONSERVA la traza vieja sin prefijo via el logger global 0x43902718",
   "codigo_equivalente":{"A7S":"HAPI Manager 0x4382d49c (unica traza, logger global 0x438f7114)",
                         "A6300":"HAPI Manager 0x438c8dxx (unica traza)"},
   "ficheros":{"A6000":["HAPI_Filter_TBOX.cpp","CS_Command.cpp","ImageParamCapture_SyncBranch.cpp"],
               "A7S":["HAPI_Filter_TBOX.cpp","CS_Command.cpp"],
               "A6300":["HAPI_Filter_TBOX.cpp","CS_Command.cpp"]},
   "tabla_msg_id":{"rango":"0x5001-0x5017","entradas":23,"base_tbh":"0x4380a72c"},
 },
 "sigla":{
   "CAM_SCALAR_apariciones_A6000":D["A6000"].count(b"CAM_SCALAR"),
   "CamScalar":D["A6000"].count(b"CamScalar"),
   "cam_scalar":D["A6000"].count(b"cam_scalar"),
   "CAM_SCAL_apariciones":D["A6000"].count(b"CAM_SCAL"),
   "nota":"sin base textual: las 34 apariciones de CAM_SCALAR son exactamente las 34 trazas",
 },
 "negativo_linea_obturador":{
   "terminos_con_0_coincidencias":["shutter","silent","curtain","electro","mech","obtur","iso","apert",
     "sensor","readout","shut","svd","shd","spl","frame","imager","drive","brack","sweep","interval",
     "still","movie","focus","ae ","af ","sync","vsync","scan"],
   "terminos_con_coincidencias":{"expos":1,"ExposureCount":1,"RecordCount":2,"CapMode":1,"CAP_SINGLE":1,
     "DMM":2,"RAW":1,"YC":5,"SDS":1,"HAPI":4,"NR Level":1},
 },
 "nombres_auxiliares":sorted(NAMES),
}
json.dump(res,open(P("analysis/s179_cam_scalar/cam_scalar.json"),"w"),indent=1,ensure_ascii=False)
print("cadenas:",len(cadenas)," sitios nuevos:",res['cifras']['sitios_pic_nuevos'])
