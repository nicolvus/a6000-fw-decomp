#!/usr/bin/env python3
"""S177 — consolida todos los datos del hito [CAM_FUNC_MGR] en
analysis/s177_cam_func_mgr/cam_func_mgr.json
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "analysis/s177_cam_func_mgr")


def j(name):
    return json.load(open(os.path.join(D, name)))


strs = j("cfm_strings_raw.json")
pic = j("cfm_pic_sites.json")
fm = j("cfm_func_map.json")
ver = j("cfm_pic_verificado.json")
pre = j("cfm_prefijo.json")
diff = j("cfm_diff.json")
mark = j("cfm_markers.json")
ft = j("cfm_functable.json")
dual = j("cfm_dual_log.json")

# fichero fuente por función emisora, a partir del "wrapper de traza" propio
# de cada fichero (el `bl` siguiente a cada sitio) y de la referencia PIC
# más próxima al nombre de fichero.
WRAP_FILE = {
    "0x43787ac4": "api/capcon_api_cam.cpp",
    "0x4380196c": "Function/FunctionNotify.cpp",
    "0x43803d80": "Function/FunctionSetParam.cpp",
    "0x43805604": "Function/LRBridge.cpp",
    "0x4380947c": "api/capcon_api_businessif.cpp",
    "0x43809600": "api/capcon_api_businessif.cpp",
    "0x43809a64": "wrapper/CamMain.cpp",
}
sitio_wrap = {}
for s in dual["sitios"]:
    if s["bl_nuevo"]:
        sitio_wrap[s["sitio"]] = s["bl_nuevo"][1]

funcs = []
for f in fm["funciones"]:
    ss = [s for s in f["sitios"]]
    wraps = sorted({sitio_wrap.get(s["sitio"]) for s in ss if s["sitio"] in sitio_wrap})
    funcs.append({
        "func": f["func"],
        "n_sitios": f["n_sitios"],
        "sitios": [s["sitio"] for s in ss],
        "cadenas": sorted({s["string_addr"] for s in ss}),
        "textos": sorted({s["texto"] for s in ss}),
        "fichero_fuente": WRAP_FILE.get(wraps[0]) if wraps else None,
        "wrapper_traza": wraps[0] if wraps else None,
    })

out = {
    "hito": "S177",
    "modulo": "[CAM_FUNC_MGR]",
    "base_vaddr": "0x43541000",
    "firmwares": {
        "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
        "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                      "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
        "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                        "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    },
    "contadores": {
        "n_cadenas_A6000": strs["A6000_fw321"]["n_cadenas_unicas"],
        "n_ocurrencias_token_A6000": strs["A6000_fw321"]["n_ocurrencias_token"],
        "n_ocurrencias_token_A7S": strs["A7S_fw320"]["n_ocurrencias_token"],
        "n_ocurrencias_token_A6300": strs["A6300_fw201"]["n_ocurrencias_token"],
        "rango_cadenas": [pic["cadenas"][0]["vaddr"], pic["cadenas"][-1]["vaddr"]],
        "n_sitios_pic_regla_estricta": pic["n_sitios_total"],
        "n_funciones_emisoras": len(funcs),
        "n_cadenas_muertas": pic["n_muertas"],
        "cadenas_muertas": pic["muertas"],
        "n_pares_pic_verificados_a_mano": len(ver),
        "n_pares_pic_sin_reuso_registro": sum(1 for v in ver if v["flag"] == "ok"),
        "n_con_gemelo_exacto_en_mas16": pre["n_gemelo_mas16"],
        "longitud_prefijo_bytes": pre["prefijo_bytes"],
        "n_nucleos_en_A7S": diff["nucleos_encontrados"]["A7S_fw320"],
        "n_nucleos_en_A6300": diff["nucleos_encontrados"]["A6300_fw201"],
        "n_sitios_con_doble_instrumentacion": dual["n_dual"],
        "n_clases_rtti_Camera_Function": len(mark["A6000_fw321"]["rtti"]),
        "n_clases_rtti_Camera_Function_A7S": len(mark["A7S_fw320"]["rtti"]),
        "n_clases_rtti_Camera_Function_A6300": len(mark["A6300_fw201"]["rtti"]),
        "n_entradas_tabla_funciones": len(ft["entradas"]),
        "module_id_log": 3,
        "level_log": 13,
    },
    "cadenas": pic["cadenas"],
    "funciones": funcs,
    "tabla_funciones": ft,
    "pic_verificado": ver,
    "doble_instrumentacion": dual,
    "marcadores": mark,
    "diferencial_nucleos": diff["filas"],
    "clases_rtti": [
        {"texto": x["texto"], "vaddr": x["vaddr"]} for x in mark["A6000_fw321"]["rtti"]],
    "ficheros_fuente": [
        {"texto": x["texto"], "vaddr": x["vaddr"]} for x in mark["A6000_fw321"]["paths"]
        if x["texto"] != "tsk/tskAvcAudioModule.cpp"] + [
        {"texto": "EventDispatcher.cpp", "vaddr": "0x43cafca6"},
        {"texto": "ExecModeHandler.cpp", "vaddr": "0x43cafd3f"},
        {"texto": "ExecReleaseHandler.cpp", "vaddr": "0x43cafda7"},
        {"texto": "RawDevHandler.cpp", "vaddr": "0x43cafed5"},
        {"texto": "ReplyHandler.cpp", "vaddr": "0x43cb000b"},
        {"texto": "SendChannel.cpp", "vaddr": "0x43cb005d"},
    ],
    "lrb_type_ids": {
        "0": "REQ_APP_SND", "1": "APP", "2": "APP_CMP",
        "3": "REQ_V2ND_SND", "4": "V2ND", "5": "V2ND_CMP",
        "6": "REQ_VSYNC_CUST_SND", "7": "VSYNC_CUST", "8": "VSYNC_CUST_CMP",
        "9": "REQ_FSPSUM_SND", "10": "FSPSUM", "11": "FSPSUM_CMP",
    },
    "lrb_type_ids_evidencia": {
        "REQ_APP_SND": "0x43805ec0 (cbz type_id==0)",
        "APP": "0x43805ef6 (cmp r2,#1)",
        "APP_CMP": "0x43805f2a (cmp r3,#2)",
        "REQ_V2ND_SND": "0x4380601a (cmp r0,#3)",
        "V2ND": "0x4380604e (cmp r3,#4)",
        "V2ND_CMP": "0x43806084 (cmp r3,#5)",
        "REQ_VSYNC_CUST_SND": "0x43805f60 (cmp r3,#6)",
        "VSYNC_CUST": "0x43805f9e (cmp r3,#7)",
        "VSYNC_CUST_CMP": "0x43805fdc (cmp r3,#8)",
        "REQ_FSPSUM_SND": "0x438060ba (cmp r3,#9)",
        "FSPSUM": "0x438060f0 (cmp r3,#0xa)",
        "FSPSUM_CMP": "0x43806126 (cmp r3,#0xb)",
    },
    "equivalentes_otras_fw": {
        "LRB_Snd_funcion": {"A6000": "0x43805ea8", "A7S": "0x437ac620",
                            "A6300": "0x437f6200"},
        "traza_LRB_antigua": {"A6000": "0x43902718", "A7S": "0x438f7114",
                              "A6300": "0x43986518"},
        "init_tabla_funciones": {"A6000": "0x43787d88", "A7S": "0x437a43c4"},
        "tabla_funciones_base": {"A6000": "0x43ff17b8", "A7S": "0x43ff65d4",
                                  "A6300": None},
        "cadena_LRB_ejemplo": {"A6000": "0x43caf219", "A7S": "0x43ca7108",
                               "A6300": "0x43dacf4f"},
    },
    "tabla_funciones_otras_fw": {
        "A7S": {"base": "0x43ff65d4", "n": 65, "idéntica": True,
                "excepción": "campo id de MSG_NONE: 0x10 (A6000) vs 0x43fd2020 (A7S)"},
        "A6300": {"base": None, "n": 0, "idéntica": False,
                  "nota": "0 apariciones de REPLY_/MSG_NONE/RAW_CONT_CAP_CANCEL/FUNC <= "},
    },
    "origenes_tabla": {
        "FUNC <= USER": 26, "FUNC <= BG  ": 3, "FUNC <= REL ": 7,
        "FUNC <= CAM ": 27, "???         ": 2,
    },
}

json.dump(out, open(os.path.join(D, "cam_func_mgr.json"), "w"), indent=1)
print("escrito analysis/s177_cam_func_mgr/cam_func_mgr.json")
print(json.dumps(out["contadores"], indent=1))
