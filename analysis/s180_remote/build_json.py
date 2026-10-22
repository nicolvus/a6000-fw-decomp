#!/usr/bin/env python3
"""S180 - construir analysis/s180_remote/remote.json (datos estructurados del hito)."""
import json, os, re

HERE = "analysis/s180_remote"
strs = json.load(open(f"{HERE}/strings_raw.json"))
pics = json.load(open(f"{HERE}/pic_sites.json"))
fmap = json.load(open(f"{HERE}/func_map.json"))
ver = json.load(open(f"{HERE}/pic_verified.json"))
log = json.load(open(f"{HERE}/log_calls.json"))
lev = json.load(open(f"{HERE}/levels_accy.json"))
vfy = json.load(open(f"{HERE}/verify.json"))
lines = {r["dest"]: r["line"] for r in log}
# valor verificado a mano (el barrido automatico toma la escritura compartida por
# dos ramas que acaban en el mismo `bl`): 0x43566ad6 `movs r2,#0xc0`
#                                          0x43566ad8 `str  r2,[sp]`
OVERRIDE_LINEAS = {"0x43c25f3d": 192}
lines.update(OVERRIDE_LINEAS)
lv = {r["vaddr"]: r for r in lev}

# --- funcion -> traza (sitios) ---------------------------------------------
func_traces = {}
for f, items in fmap["remote_funcs"].items():
    func_traces[f] = [
        {"site": it["site"], "dest": it["dest"], "text": it["text"],
         "linea_fuente": lines.get(it["dest"])} for it in items]

strings = []
for r in pics["strings"]:
    va = hex(r["vaddr"])
    strings.append({
        "vaddr": r["vaddr"],
        "text": r["text"],
        "nivel": r["level"],
        "prefijo_len": r["prefix_len"],
        "nucleo": r["core"],
        "n_pic_sites": r["n_pic"],
        "pic_sites": [hex(s) for s in r["pic_sites"]],
        "funciones": sorted({f for f, items in fmap["remote_funcs"].items()
                             for it in items if it["dest"] == va}),
        "linea_fuente": lines.get(va),
        "id_modulo": lv.get(va, {}).get("r0_id_modulo"),
        "nivel_log": lv.get(va, {}).get("r2_nivel"),
        "logger": lv.get(va, {}).get("logger"),
        "gemelo_externo": pics["twins"]["A6000"][[x["vaddr"] for x in pics["strings"]].index(r["vaddr"])]["external"],
        "nucleo_presente_A7S": len(pics["twins"]["A7S"][[x["vaddr"] for x in pics["strings"]].index(r["vaddr"])]["external"]) > 0,
        "nucleo_presente_A6300": len(pics["twins"]["A6300"][[x["vaddr"] for x in pics["strings"]].index(r["vaddr"])]["external"]) > 0,
    })

out = {
    "hito": "S180",
    "titulo": "el modulo [REMOTE] (32 trazas) de la A6000 fw3.21",
    "model": "A6000",
    "firmware": "fw3.21",
    "binary": "analysis/rea-independent/input/av-cam.bin",
    "vaddr_base": "0x43541000",
    "xref_rule": "PIC estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py); mapa global analysis/s106_imaging_cap/pic_refs_strict_global.json",
    "counters": {
        "token_REMOTE_A6000": strs["A6000"].__len__(),
        "token_REMOTE_A7S": len(strs["A7S"]),
        "token_REMOTE_A6300": len(strs["A6300"]),
        "cadenas": len(strings),
        "rango": [min(r["vaddr"] for r in pics["strings"]), max(r["vaddr"] for r in pics["strings"])],
        "sitios_pic": sum(r["n_pic"] for r in pics["strings"]),
        "funciones": len(fmap["remote_funcs"]),
        "cadenas_muertas": 0,
        "pares_pic_verificados_a_mano": len(ver),
        "fallos_verificacion": sum(1 for v in ver if not v["ok"]),
        "reuso_de_registro": sum(1 for v in ver if v["kill"]),
        "punteros_absolutos_4B": {k: sum(x["count"] for x in v) for k, v in vfy["abs_ptrs"].items()},
        "gemelos_nucleo_externo": {k: sum(1 for x in v if x["externos"])
                                   for k, v in vfy["twins"].items()},
        "nota_gemelos": "las 6 coincidencias externas de la A6000 son literales de OTROS "
                        "sub-bloques [ACCY] ([HELLO] comparte RetrySendCmd/SendCmd Buffer Busy/"
                        "NotifyUartTimedOut; [HOUSING] comparte RestoreInfo; "
                        "NotifyAttached/NotifyDetached son genericos repetidos), "
                        "no el 'original' de una traza reescrita",
    },
    "que_es": {
        "veredicto": "subsistema de MANDO A DISTANCIA (control remoto por UART) de la A6000 fw3.21",
        "clase_rtti": "AccyUmDeviceRemote",
        "clase_rtti_vaddr": "0x43c26340",
        "clase_base_rtti": "AccyUmDeviceBase",
        "clase_base_rtti_vaddr": "0x43c2536d",
        "vtable_clase": "0x43fb9114",
        "vtable_metodos": {
            "0": "0x43566ec1 -> NotifyAttached  (0x43566ec0)",
            "1": "0x43566a55 -> NotifyApiRequest (0x43566a54)",
            "2": "0x43566e5d -> NotifyUartResponse (0x43566e5c)",
            "3": "0x43566d8d -> NotifyUartTimedOut (0x43566d8c)",
            "4": "0x43566999 -> CallForTransaction (0x43566998)",
            "5": "0x43566291 -> NotifyUartCommand (0x43566290)",
            "6": "0x435665f9 -> ExecUartCommand (0x435665f8)",
            "7": "0x43566d45 -> NotifyDetached (0x43566d44)",
        },
        "nota_base_textual": "REMOTE se desarrolla en la clase RTTI AccyUmDeviceRemote; ACCY y UM NO tienen base textual en los bytes",
    },
    "logging": {
        "logger_propio_del_subbloque": "0x435661e4",
        "firma": "(u16 id_modulo=93, u16 ?, u16 nivel, const char *fmt, ...)",
        "id_modulo": 93,
        "niveles": {"1": "ERR", "2": "WARN", "3": "DEBUG", "4": "INFO"},
        "mensaje": "[ACCY][<NIVEL>][REMOTE]:<linea_fuente>:<mensaje>",
        "primer_vararg": "numero de linea del fichero fuente",
        "loggers_por_subbloque_ACCY": {
            "REMOTE": "0x435661e4", "HELLO": "0x435659dc", "BASE": "0x43565768",
            "UART": "0x435639e8", "FACTORY": "0x43564410", "MAIN": "0x43562c94",
            "HW": "0x435627e0", "SENSER": "0x43563700", "UTILITY": "0x4356405c",
            "HOUSING": "0x43564a08", "AVOUT": "0x43565458", "AVR": "0x435655d0",
            "JIRO": "0x43565f20", "NULL": "0x435660a0"},
        "doble_emision_al_logger_global_0x43902718": False,
        "lineas_fuente": sorted({r["line"] for r in log if r["line"]}),
    },
    "estructura_de_datos": {
        "tipo": "objeto AccyUmDeviceRemote (clase C++ con RTTI)",
        "campos_por_offset": {
            "+0x04": "contador (incrementado en RestoreInfo)",
            "+0x0C": "Spinal (byte con signo) - estado del disparador/collar",
            "+0x10": "marca de tiempo de la transaccion (32 bit)",
            "+0x14": "flag 'buffer listo' (0 = buffer error)",
            "+0x18": "contador de reintentos de la transaccion",
            "+0x1C": "longitud del comando pendiente",
            "+0x20": "buffer del comando pendiente (6 bytes ASCII)",
            "+0x24": "contador de reintentos en ASCII",
            "+0x30": "maximo de reintentos (word)",
            "+0x34": "estado del ZOOM (word)",
            "+0x38": "velocidad del ZOOM (word)",
            "+0x3C": "flag GF  (guide frame)",
            "+0x3D": "flag SS  (start/stop)",
            "+0x3E": "flag Freeze",
            "+0x3F": "flag Photo",
            "+0x40": "estado de Tally solicitado",
            "+0x41": "estado de Tally actual",
            "+0x42": "estado de control / ocupado (busy)",
        },
        "saveinfo_blob": {
            "tamano": 3,
            "byte0_bits": {"0": "GF", "1": "SS", "2": "Freeze", "3": "Photo", "4-5": "Zoom (2 bits)"},
            "byte1": "Tally",
            "byte2": "reservado (0)",
            "guardado_en": "0x435664d0 (SaveInfo) / restaurado_en 0x43566580 (RestoreInfo)",
        },
        "tabla_codigos_tecla": {
            "0x0A000009": "GUIDE FRAME",
            "0x0A00000D": "START STOP",
            "0x0A000008": "PHOTO FREEZE",
            "0x0A00000C": "PHOTO REC",
            "0x0A000011": "ZOOM",
            "0x0A00000A": "codigo adicional presente en el pool (0x43566d24), uso NO VERIFICADO",
            "pool_A6000": ["0x435667f0", "0x435667f4", "0x435667f8", "0x435667fc", "0x43566800"],
            "pool_A7S": ["0x43564874", "0x43564878", "0x4356487c", "0x43564880", "0x43564884"],
            "pool_A6300": ["0x4355f040", "0x4355f044", "0x4355f048", "0x4355f04c", "0x4355f050"],
            "eventos_key_OFF": {"GUIDE FRAME": "0x06000600", "START STOP": "0x06000700",
                                "PHOTO FREEZE": "0x06000800", "PHOTO REC": "0x06000900",
                                "ZOOM": "0x06000A00 (zoom=1) / 0x06000B00 (zoom=2)"},
        },
        "protocolo_uart": {
            "trama_emitida": "6 bytes ASCII '%' '7' '6' <estado> '0' '*' + NUL (TallyControlCmd 0x4356692c)",
            "trama_recibida": "'#' '7' <categoria '0'-'5'> <d1> <d2> <d3>",
            "categoria_tbb": {"tbb": "0x435662f4", "entradas": 6},
            "comando_tbb": {"tbb": "0x43566638", "entradas": 4,
                            "0": "GUIDE FRAME", "1": "START STOP", "2": "PHOTO FREEZE", "3": "PHOTO REC"},
            "tally_tbb": {"tbb": "0x43566960", "entradas": 4,
                          "0": "'0' (default)", "1": "'1'", "2": "'2'", "3": "'3'"},
        },
    },
    "strings": strings,
    "funciones": func_traces,
    "diferencial": {
        "token_REMOTE": {"A6000_fw321": 32, "A7S_fw320": 0, "A6300_fw201": 0},
        "token_ACCY": {"A6000_fw321": 106, "A7S_fw320": 0, "A6300_fw201": 0},
        "nucleo_sin_prefijo_presente": {"A6000_fw321": "32/32 (dentro de la propia cadena)",
                                        "A7S_fw320": "0/32", "A6300_fw201": "0/32"},
        "clase_RTTI_AccyUmDeviceRemote": {"A6000_fw321": "0x43c26340",
                                          "A7S_fw320": "0x43c25aed",
                                          "A6300_fw201": "0x43d0ca6c"},
        "vtable_AccyUmDeviceRemote": {"A6000_fw321": "0x43fb9114",
                                      "A7S_fw320": "0x43fb2e14",
                                      "A6300_fw201": "0x4416fd74"},
        "tabla_codigos_tecla_5_codigos": {"A6000_fw321": "si", "A7S_fw320": "si (0x43564874)",
                                          "A6300_fw201": "si (0x4355f040)"},
        "traza_equivalente_otra_etiqueta": "ninguna: en A7S/A6300 no hay traza [ACCY] en absoluto",
        "veredicto": "ETIQUETADO/LOGGING: el codigo del mando remoto EXISTE en los tres firmware "
                     "(misma clase RTTI, misma vtable de 8 metodos, misma tabla de 5 codigos de tecla); "
                     "lo propio de la A6000 fw3.21 son las 32 trazas [REMOTE] (y todo el set [ACCY])",
    },
    "negativo_obturador": vfy["negativo"],
    "shutter_line": {
        "veredicto": "NEGATIVO ACOTADO: el modulo [REMOTE] no habla de obturacion, sensor, "
                     "exposicion ni parametros del obturador",
        "terminos_con_coincidencia": {k: v for k, v in vfy["negativo"].items() if v},
        "nota": "'frame' = GUIDE FRAME (guia de encuadre), 'rec' = PHOTO REC (grabacion), "
                "'speed' = velocidad del ZOOM, 'time' = timeout de UART; ninguno es el obturador",
    },
    "no_verificado": [
        "nombre del fichero fuente del sub-bloque [REMOTE] (NO VERIFICADO: el bloque ACCY no referencia ningun nombre de fichero)",
        "significado de la sigla ACCY y de UM (NO VERIFICADO: sin base textual)",
        "significado de 'Spinal' (literal sin explicar en los bytes)",
        "significado de GF / SS / Tally / JIRO / AVR / LANC / AISATSU (literales sin explicar)",
        "tabla de nombres de tecla 0x0A0000xx -> accion de camara (no localizada)",
        "cola OSAL de destino del mensaje NotifyInput (0x007A0020) y su consumidor",
        "codigo 0x0A00000A (pool 0x43566d24): su uso NO VERIFICADO",
        "por que el bloque ACCY tiene trazas solo en la A6000 fw3.21 (NO VERIFICADO)",
    ],
}
os.makedirs(HERE, exist_ok=True)
json.dump(out, open(f"{HERE}/remote.json", "w"), indent=1, ensure_ascii=False)
print("->", f"{HERE}/remote.json")
print("cadenas:", len(strings), "funciones:", len(func_traces))
