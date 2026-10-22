#!/usr/bin/env python3
"""S167 — genera `analysis/s167_sad/sad.json` (datos estructurados del módulo `[SAD]`).

Consume `sad_raw.json` (escáner) y `sad_pic_verified.json` (verificación PIC a mano)
y añade: mapa función→traza, sub-bloques, diferencial y el bloque de hallazgos.
"""
import json
import os
import re
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A63 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))

B = open(BIN, "rb").read()


def cstr(a, blob=None):
    blob = B if blob is None else blob
    o = a - BASE
    if o < 0 or o >= len(blob):
        return None
    e = blob.find(b"\x00", o)
    return blob[o:e].decode("latin1")


def sub_bloque(texto):
    """Clasificación por contenido del mensaje (sin inventar semántica)."""
    if "Same Unit Handle Get" in texto or "same hndl get_cnt" in texto \
            or "alloc_cnt" in texto or "SameHandleGetCnt" in texto \
            or "Alloc all Cnt" in texto or "Dmm Same Handle Get Num" in texto:
        return "HANDLE_ALLOC"
    if "Hdr Err" in texto:
        return "SA_HDR_ERR"
    if "DbgPrt CmdRcv" in texto:
        return "DBGPRT_CMD"
    if "CfgStatePrt" in texto or "ZmCfg" in texto or "SaCfg" in texto:
        return "CFG_STATE"
    if "FifoStatePrt" in texto or "FifoDataPrt" in texto or "Fifo" in texto \
            or "OpnCmd" in texto or "JpgNrm" in texto or "JpgSrt" in texto:
        return "FIFO"
    if "CalcTime" in texto:
        return "CALCTIME"
    if "SaProgHdr" in texto or "PrgID" in texto:
        return "SA_PROG_HDR"
    if "DdsDataAdd" in texto:
        return "DDS_DATA_ADD"
    if "data1=other" in texto or "SelCodeErr" in texto:
        return "SELCODE"
    return "OTROS"


def main():
    raw = json.load(open(os.path.join(HERE, "sad_raw.json")))
    ver = json.load(open(os.path.join(HERE, "sad_pic_verified.json")))

    cad = raw["cadenas"]
    con_contenido = [c for c in cad if c["texto"].strip() != "[SAD]"]
    solo_prefijo = [c for c in cad if c["texto"].strip() == "[SAD]"]

    # --- mapa función → traza
    mapa_func = {}
    for k, v in sorted(raw["funciones"].items()):
        # deduplicar por cadena: una traza con N sitios aparece N veces en la
        # lista de sitios pero es UNA sola traza de la función.
        vistos = set()
        trazas = []
        for a, t in zip(v["vaddr_cadena"], v["cadenas"]):
            if a in vistos:
                continue
            vistos.add(a)
            trazas.append({"vaddr": a, "texto": t, "sub_bloque": sub_bloque(t)})
        mapa_func[k] = {
            "func": v["func"],
            "n_sitios_pic": len(v["sitios"]),
            "sitios_pic": v["sitios"],
            "llamadores_bl": v["llamadores_bl"],
            "n_trazas": len(trazas),
            "trazas": trazas,
        }

    # --- sub-bloques
    bloques = {}
    for c in con_contenido:
        bloques.setdefault(sub_bloque(c["texto"]), []).append(
            {"vaddr": hex(c["vaddr"]), "texto": c["texto"]})
    for k in bloques:
        bloques[k].sort(key=lambda x: int(x["vaddr"], 16))

    # --- diferencial
    dif = {}
    for name, path in (("A7S_fw320", A7S), ("A6300_fw201", A63)):
        blob = open(path, "rb").read()
        occ = [m.start() for m in re.finditer(re.escape(b"[SAD]"), blob)]
        dif[name] = {
            "ocurrencias_token": len(occ),
            "cadenas_[SAD]": 0,
            "nucleos_texto_comunes_con_a6000": raw["diferencial"][name]["comunes"],
            "nota": ("0 apariciones del token [SAD]: la etiqueta y sus 44 mensajes "
                     "no existen en este firmware"),
        }

    # --- verificación PIC
    pic = {
        "regla": ver["regla"],
        "n_sitios_verificados_a_mano": ver["n_sitios_verificados"],
        "n_ok": ver["n_ok"],
        "n_fallo": ver["n_fallo"],
        "cotejo_con_mapa_global_repo": {
            "n_discrepancias": raw["cotejo_mapa_global"]["n_discrepancias"],
            "detalle": raw["cotejo_mapa_global"]["discrepancias"],
        },
    }

    out = {
        "milestone": "S167",
        "token": "[SAD]",
        "que_es": {
            "lectura": ("Módulo de depuración/diagnóstico del subsistema 'SA' "
                        "(acelerador escalar): volcado del estado de configuracion, "
                        "de la FIFO de JPEG, de los tiempos de calculo y de las "
                        "cabeceras de programa SA (SaProgHdr), mas la gestion de "
                        "handles de unidad/DMM."),
            "base_textual": ("NO VERIFICADO / sigla sin expandir: no existe ninguna "
                              "cadena en el firmware que exponga 'SAD' como sigla "
                              "(RTTI, nombres de fichero, simbolos). Se deja sin "
                              "desarrollar."),
            "indicios_de_la_sigla": [
                "SA es el acelerador escalar del firmware: `SA_PREINSTALLED_PRG:` "
                "(0x43ce561f), `SA_JPEG_ENC` (0x43ce5634), `SA_JPEG_DEC` (0x43ce5640), "
                "`SA0_V1.0SA5_V1.0` (0x43ce5402), `ZMA0V1.0SA5_V1.0` (0x43ce5435)",
                "las trazas [SAD] estan intercaladas en .rodata entre esas cadenas de "
                "SA (0x43ce546b-0x43ce59c1)",
                "el codigo emisor esta en la misma zona que el gestor de programas "
                "preinstalados SA (0x4399ede0 referencia SA_PREINSTALLED_PRG:)",
                "`exec_sadone` (RTTI, 0x43ce7004) pertenece a NS_SCALAR_INFRA "
                "(ScalarInfraSequenceSaStageAuto::exec_sa_done), NO al modulo [SAD]",
            ],
        },
        "cadenas": [
            {"vaddr": hex(c["vaddr"]), "texto": c["texto"],
             "sub_bloque": sub_bloque(c["texto"]),
             "sitios_pic": raw["sitios_por_cadena"][hex(c["vaddr"])]}
            for c in cad
        ],
        "n_cadenas_totales": len(cad),
        "n_cadenas_con_contenido": len(con_contenido),
        "n_cadenas_solo_prefijo": len(solo_prefijo),
        "solo_prefijo": [hex(c["vaddr"]) for c in solo_prefijo],
        "n_sitios_pic_totales": sum(len(v) for v in raw["sitios_por_cadena"].values()),
        "n_cadenas_sin_referencia": 0,
        "mapa_funcion_traza": mapa_func,
        "n_funciones_emisoras": len(mapa_func),
        "sub_bloques": bloques,
        "ficheros_fuente": {
            "nota": ("Las 5 funciones emisoras NO imprimen `file=%s`; el modulo no "
                     "embebe ningun nombre de fichero propio. La zona de codigo "
                     "(0x43990000-0x439a1600) pertenece al bloque ScalarInfra "
                     "(NS_SCALAR_INFRA): sus ficheros vecinos son "
                     "`ScalarInfraAsyncMain.cpp` (0x43ce59fd), `ScalarInfraSequenceSa.cpp` "
                     "(0x43ce6c15) y `ScalarInfraSequenceSaStage.cpp` (0x43ce6e16), "
                     "referenciados desde 0x439a18d6 / 0x439a4024 / 0x439a47a0."),
            "ficheros_vecinos": {
                "ScalarInfraAsyncMain.cpp": hex(0x43ce59fd),
                "ScalarInfraSequenceSa.cpp": hex(0x43ce6c15),
                "ScalarInfraSequenceSaStage.cpp": hex(0x43ce6e16),
            },
            "fichero_propio_del_modulo": "NO VERIFICADO (no embebido)",
        },
        "rtti_relacionado": {
            "NS_SCALAR_INFRA41ScalarInfraSequenceSaStageAutoexec_sadoneE": hex(0x43ce7004),
            "nota": ("Unico RTTI con 'sad' en el binario. Pertenece a "
                     "NS_SCALAR_INFRA (etapa Sa del ScalarInfra), NO es el modulo [SAD]."),
        },
        "comando_entrante": {
            "id_mensaje_u16": "0x9548",
            "id_mensaje_u16_vaddr": hex(0x439a119e),
            "despachador": hex(0x439a119c),
            "llamador": hex(0x4399b5ac),
            "dispatcher_padre": hex(0x4399b074),
            "registro_del_dispatcher_padre": hex(0x43fd2a88),
            "nota": ("En 0x439a119e `movw r3,#0x9548` + `ldrh r2,[r0,#2]` + `cmp r2,r3` "
                     "comprueba que el mensaje recibido lleva el id 0x9548. El byte "
                     "[r0+4] debe ser 1 y el byte [r0+5] selecciona 6 subcomandos "
                     "mediante la tabla `tbh` de 0x439a11d0 (casos 1..6)."),
            "subcomandos_tbh": {
                "tabla": hex(0x439a11d0),
                "caso_1_cfg_state": hex(0x439a11dc),
                "caso_2_fifo_state": hex(0x439a126c),
                "caso_3_fifo_data": hex(0x439a13f2),
                "caso_4_dds_data_add": hex(0x439a14ae),
                "caso_5_sa_prog_hdr": hex(0x439a14c0),
                "caso_6_dmm_handle": hex(0x439a1536),
            },
        },
        "verificacion_pic": pic,
        "diferencial": dif,
        "diferencial_estructural": {
            "hallazgo": ("La tabla de bytes que en la A7S/A6300 ocupa el hueco entre "
                         "`ZMA0V1.0SA5_V1.0` y `SA_PREINSTALLED_PRG:` esta INTERCALADA "
                         "en la A6000 con las 44 cadenas [SAD]: la cabecera de 27 B y "
                         "la tabla de 25 indices (0x03..0x1b) sobreviven intactas, "
                         "pero las trazas se han insertado en dos huecos, partiendo "
                         "el bloque en 3 (A: 3 cadenas, B: 3 cadenas, C: 39 cadenas)."),
            "tabla_A7S": hex(0x43cda6ef),
            "tabla_A6300": hex(0x43df89bc),
            "cabecera_27B_identica_en_los_tres": {
                "A6000": hex(0x43ce5445),
                "A7S": hex(0x43cda6ef),
                "A6300": hex(0x43df89bc),
                "bytes": ("000101010001010204088383830483838307070707070707070707"),
            },
            "tabla_indices_25_identica": {
                "A6000": hex(0x43ce54bc),
                "A7S": hex(0x43cda716),
                "bytes_no_0x1c": [hex(x) for x in range(0x03, 0x1C)],
            },
            "bloques_de_cadenas_SAD": {
                "A_handles": [hex(0x43ce546b), hex(0x43ce54bb), 3],
                "B_hdr_err": [hex(0x43ce55bc), hex(0x43ce5618), 3],
                "C_dbgprt": [hex(0x43ce564c), hex(0x43ce59d1), 39],
            },
        },
        "interes_para_la_linea_del_obturador": {
            "menciona_obturacion": False,
            "negativo_verificado": {
                "shutter": 0, "silent": 0, "obtur": 0, "expos": 0, "imager": 0,
                "sensor": 0, "readout": 0, "drive": 0, "brack": 0, "sweep": 0,
                "interval": 0, "still": 0, "movie": 0, "focus": 0, "aperture": 0,
                "iso": 0,
            },
            "unicas_apariciones_de_jpg": ["JpgNrm", "JpgSrt", "JpgNrmIndex", "JpgSrtIndex"],
            "nota": ("El modulo no habla de obturacion, exposicion ni sensor. Solo "
                     "aparece 'Jpg' en 4 mensajes, pero como indice de cola FIFO "
                     "(JpgNrm/JpgSrt = indices normal/sort de JPEG), no como captura. "
                     "Sin efecto en S51 (A/B/C = NO)."),
        },
        "verif_adicional": {
            "canal_de_log_propio": {
                "impresor": hex(0x439a10f0),
                "id_mensaje": "0x93 (147)",
                "tamano_mensaje": "0x9a",
                "reserva": "osal_try_valloc_msg 0x435612d0",
                "nota": ("impresor propio del modulo, distinto del logger global "
                         "0x435ab880 que usan [SFRA]/[SFRS]"),
            },
            "direcciones_de_datos_de_los_emisores": {
                "tabla_handles_255_u16": {
                    "vaddr": hex(0x43f84bfe),
                    "como": ("ldr r3,[pc,#0xb8] en 0x43998574 + add r3,pc en "
                             "0x4399857a; fin = base+0x1fe"),
                },
                "tabla_handles_32_u16": {
                    "vaddr": hex(0x43f85932),
                    "como": ("ldr r3,[pc,#0x98] en 0x43998598 + add r3,pc en "
                             "0x4399859a; fin = base+0x40"),
                },
                "contador_u32_alloc_cnt": {
                    "vaddr": hex(0x43f31368),
                    "como": "ldr r3,[pc,#0x80] en 0x439985b6 + add r3,pc en 0x439985b8",
                },
                "contador_u16_same_hndl_get_cnt": {
                    "vaddr": hex(0x43f84bfc),
                    "como": "ldr r3,[pc,#0x70] en 0x439985ca + add r3,pc en 0x439985d0",
                },
            },
            "tabla_de_versiones_sa": {
                "vaddr_ini": hex(0x43ce5402),
                "entradas": ["SA0_V1.0|SA5_V1.0", "ZMA1V1.0|SA5_V1.0",
                             "SA1_V1.0|SA5_V1.0", "ZMA0V1.0|SA5_V1.0"],
                "comparacion_16_bytes": hex(0x43993128),
                "globales_runtime": [hex(0x43f2ef7c), hex(0x43f2ef6e),
                                     hex(0x43f2ef5c), hex(0x43f2ef8c)],
            },
            "anclas_de_codigo_para_el_diferencial": {
                "nota": ("sitios PIC de las mismas cadenas del driver SA en los tres "
                         "firmwares: el bloque de codigo es el mismo modulo pero "
                         "distinto codigo (crece en la fw3.21 de la A6000)"),
                "[SIO]osal_valloc_msg": {"A6000": hex(0x43990414), "A7S": hex(0x4397df30),
                                         "A6300": hex(0x43a24b68)},
                "SA_PREINSTALLED_PRG:": {"A6000": hex(0x4399ee6a), "A7S": hex(0x4398c8cc),
                                          "A6300": hex(0x43a2accc)},
                "ScalarInfraAsyncMain.cpp": {"A6000": hex(0x439a18d6), "A7S": hex(0x4398f122),
                                             "A6300": hex(0x43a387fa)},
            },
            "cadena_PEG_DEC_muerta": {
                "vaddr": hex(0x43ce5644),
                "texto": "PEG_DEC",
                "nota": ("subcadena de 'SA_JPEG_DEC' (0x43ce5640) + 4. 0 referencias PIC "
                         "y 0 punteros embebidos de 4 B: es una cadena MUERTA. El "
                         "ldr r3,[pc,#0x3e4] de 0x439a11ac apunta al pool 0x439a1594 "
                         "(W=0x344494) y con el add r3,pc de 0x439a11b4 el destino es "
                         "0x43ce564c ('[SAD] DbgPrt CmdRcv'), NO 0x43ce5644."),
            },
        },
        "abierto_no_verificado": [
            "sigla 'SAD' sin expansion textual: NO VERIFICADO (no se inventa)",
            "fichero fuente propio del modulo: NO VERIFICADO (no embebido en el binario)",
            "significado de CdcSaPrg/NmlSaPrg/RsdSaPrg: NO VERIFICADO (3 tipos de "
            "cabecera de programa SA; solo se sabe que validan y dan error)",
            "que representa exactamente la 'unit' y el 'Dmm' (handle): NO VERIFICADO",
            "el binario A7S/A6300 tiene el mismo codigo sin la etiqueta [SAD]: "
            "NO VERIFICADO (no se ha localizado codigo equivalente alli)",
        ],
    }
    dest = os.path.join(HERE, "sad.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("escrito", dest)
    print("cadenas:", out["n_cadenas_totales"],
          "contenido:", out["n_cadenas_con_contenido"],
          "sitios:", out["n_sitios_pic_totales"],
          "funciones:", out["n_funciones_emisoras"])
    print("PIC verificados:", pic["n_sitios_verificados_a_mano"],
          "ok:", pic["n_ok"], "fallos:", pic["n_fallo"],
          "discrepancias vs mapa global:", pic["cotejo_con_mapa_global_repo"]["n_discrepancias"])


if __name__ == "__main__":
    main()
