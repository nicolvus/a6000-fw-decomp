#!/usr/bin/env python3
"""S138 — ensambla `camera_main_fc.json` con los datos verificados del hito.

Todas las cifras proceden de los scripts de este directorio (bytes reales).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def main():
    strings = load("fc_strings.json")
    sites = load("fc_sites_verified.json")
    diff = load("fc_diff.json")
    refs = load("fc_refs_all.json")

    items = strings["a6000"]["items"]
    by_str = {}
    for s in sites:
        by_str.setdefault(s["expected"], []).append(s)

    FUNC_OF_SITE = {
        "0x437b7268": "0x437b7200", "0x437b72a6": "0x437b7200",
        "0x437b72ee": "0x437b7200", "0x437b7326": "0x437b7200",
        "0x437b7548": "0x437b74a4", "0x437b7570": "0x437b74a4",
        "0x437b77f4": "0x437b7778", "0x437b787c": "0x437b7844",
        "0x437b7db6": "0x437b7d6c", "0x437b7df6": "0x437b7d6c",
        "0x437b7fae": "0x437b7ea0", "0x437b8200": "0x437b81f0",
        "0x437b820e": "0x437b81f0",
    }
    FUNC_ROLE = {
        "0x437b7200": "calculo de area de cara/ojo (flags [ctx+0xde], [ctx+0xdf])",
        "0x437b74a4": "alta/activacion del temporizador OSAL",
        "0x437b7778": "baja del temporizador OSAL",
        "0x437b7844": "comprobacion APP MODE: face_on y obj_on simultaneos",
        "0x437b7d6c": "consulta OSAL de BatteryInfo",
        "0x437b7ea0": "ReplyForTouchShutter (invoca el callback guardado)",
        "0x437b81f0": "SetRequestReplyForTouchShutter (registra el callback)",
    }
    SIN_LLAMADOR = ["0x437b7598", "0x437b7778", "0x437b7ea0", "0x437b81f0"]

    strings_out = []
    for it in items:
        v = f"0x{it['vaddr']:x}"
        ss = by_str.get(v, [])
        strings_out.append({
            "vaddr": v,
            "text": it["text"],
            "core": it["text"].replace("[CAMERA_MAIN_FC]: ", ""),
            "n_sites": len(ss),
            "sites": [{"site": s["site"], "ldr": s["ldr"],
                       "function": FUNC_OF_SITE.get(s["site"]),
                       "verified_by_hand": s["ok"]} for s in ss],
        })

    funcs = {}
    for s in sites:
        f = FUNC_OF_SITE[s["site"]]
        funcs.setdefault(f, {"function": f, "role": FUNC_ROLE[f], "n_sites": 0,
                             "sites": [], "strings": [],
                             "incoming": {k: [f"0x{x:x}" for x in v]
                                          for k, v in refs.get(f, {}).items()}})
        funcs[f]["n_sites"] += 1
        funcs[f]["sites"].append(s["site"])
        if s["expected"] not in funcs[f]["strings"]:
            funcs[f]["strings"].append(s["expected"])

    out = {
        "hito": "S138",
        "modulo": "[CAMERA_MAIN_FC]",
        "base_vaddr": "0x43541000",
        "convention": "vaddr = 0x43541000 + file_offset",
        "firmware": "A6000 fw3.21 (analysis/rea-independent/input/av-cam.bin)",
        "regla_xref": "estricta (cada `add rX,pc` con el `ldr rX,[pc]` mas cercano; "
                      "ver analysis/s106_imaging_cap/scan_pic_refs_strict.py). "
                      "Los 13 sitios se han recalculado a mano con verify_sites.py",
        "counters": {
            "cadenas": len(items),
            "cadenas_distintas": len(set(i["text"] for i in items)),
            "sitios_pic": len(sites),
            "sitios_verificados_a_mano": sum(1 for s in sites if s["ok"]),
            "funciones_emisoras": len(funcs),
            "cadenas_sin_referencia": 0,
            "apariciones_del_token_en_a6000": strings["a6000"]["occurrences"],
            "apariciones_del_token_en_a7s": strings["a7s"]["occurrences"],
            "apariciones_del_token_en_a6300": strings["a6300"]["occurrences"],
        },
        "rango_cadenas": ["0x43ca6944", "0x43ca6aec"],
        "rango_codigo": ["0x437b7200", "0x437b821e"],
        "strings": strings_out,
        "funciones": sorted(funcs.values(), key=lambda x: x["function"]),
        "api_exportada": {
            "nota": "Tres de las funciones del modulo se alcanzan a traves de "
                    "thunks (colas de ramificacion) en 0x43aef72e-0x43aef736, que "
                    "exportan la API del subsistema FC",
            "thunks": [
                {"thunk": "0x43aef72e", "destino": "0x437b7ea0",
                 "nombre": "ReplyForTouchShutter", "llamador": "0x437b668c"},
                {"thunk": "0x43aef732", "destino": "0x437b7fe4",
                 "nombre": "copia del estado de areas de cara/ojo",
                 "llamador": "0x4378f6a6"},
                {"thunk": "0x43aef736", "destino": "0x437b81f0",
                 "nombre": "SetRequestReplyForTouchShutter",
                 "llamador": "0x4380a4c8 (b.w) <- 0x43808058"},
            ],
            "cola_a_0x437b7598": {"sitio": "0x43aef9ca",
                                  "nota": "cola de ramificacion (b.w) desde la funcion "
                                          "que termina en 0x43aef9ca"},
        },
        "sin_referencia_entrada": {
            "funciones": ["0x437b7778"],
            "metodo": "barrido inverso de ramas (bl/b.w/blx/b de 16 bits) sobre toda "
                      "la imagen, con las cuatro combinaciones de los bits J1/J2; "
                      "ademas punteros absolutos de 32 bits y materializaciones PIC "
                      "`ldr`+`add`",
            "nota": "La funcion 0x437b7778 (traza 'osal_free_timer') no tiene ninguna "
                    "referencia entrante en av-cam.bin",
        },
        "impresor": {
            "funcion": "0x437b7158",
            "nota": "logger privado del modulo (OSAL): osal_try_valloc_msg 0x435612d0, "
                    "envio 0x43561244, formato 0x439c5004, osal_free_msg 0x435612ec, "
                    "osal_snd_msg 0x4356120c. Llamada: r0=3 (nivel), r1=5 (modulo), "
                    "r2=1 (mascara), r3=puntero a la cadena",
        },
        "sigla_FC": {
            "base_textual": "namespace C++ `Camera::FC` (28 cadenas de asercion, "
                            "p. ej. `Camera::FC::FCTop::ExecApiNotifyStartTouch` "
                            "0x43cefa06) y arbol de ficheros `FC/**/*.cpp` "
                            "(99 ficheros, 0x43cef12a-0x43cf707a)",
            "no_desarrollada": "No hay base textual para expandir la sigla mas alla "
                               "del namespace `Camera::FC`",
            "biblioteca_camera_fc": {
                "presente_en": ["A6000 fw3.21", "A7S fw3.20", "A6300 fw2.01"],
                "ocurrencias_camera_fc_por_firmware": {
                    "a6000": 45, "a7s": 45, "a6300": 45},
                "ocurrencias_FC_slash_por_firmware": {
                    "a6000": 101, "a7s": 101, "a6300": 101},
                "codigo": "aprox. 0x439d0000-0x439fffff",
            },
        },
        "diferencial": {
            "a7s_fw320": {"token": 0, "cadenas_completas": 0, "nucleos_de_texto": 0,
                          "fragmentos_de_codigo": "0/8"},
            "a6300_fw201": {"token": 0, "cadenas_completas": 0, "nucleos_de_texto": 0,
                            "fragmentos_de_codigo": "0/8"},
            "detalle": diff,
        },
        "relacion_disparo_tactil": {
            "participa_en_la_cadena_0x3011": False,
            "motivo": "Ninguna funcion de la cadena documentada (0x4379d838 RelMgr, "
                      "0x4379e6a8, 0x4379eba0 -> 0x3011, 0x43809ed8 CamUser, "
                      "0x437df640 CaptureStart, 0x437df338, 0x437eabfc, 0x437e4de4) "
                      "llama a la zona [CAMERA_MAIN_FC] (0x437b6000-0x437b8400) ni a "
                      "la biblioteca Camera::FC (0x439d0000-0x43a00000), ni a sus "
                      "thunks (0x43aef72e/0x43aef732/0x43aef736)",
            "api_propia": "El modulo si implementa una API de respuesta de disparo "
                          "tactil: ReplyForTouchShutter (0x437b7ea0) y "
                          "SetRequestReplyForTouchShutter (0x437b81f0), con el "
                          "callback en la ranura global 0x43eb3bf0 (invocado con "
                          "`blx r1` en 0x437b7fa2). Se alcanzan por los thunks "
                          "0x43aef72e y 0x43aef736",
            "quien_la_usa": "El wrapper de captura `wrapper/Face.cpp` (0x4380a384, "
                            "0x4380a424; traza 'wrapper/Face.cpp' en 0x4380a33a, "
                            "0x4380a3d2, 0x4380a472) llama a la biblioteca "
                            "Camera::FC (`FC/Api/fc_api_tracking.cpp` 0x43cefa43, via "
                            "0x439d95bc/0x439d953c) y el dispatcher de captura "
                            "(funcion 0x43807f4c) llama a 0x4380a4c4 -> thunk "
                            "0x43aef736 -> SetRequestReplyForTouchShutter",
            "veredicto": "La API de disparo tactil del modulo FC existe y esta "
                         "cableada, pero por un camino distinto del documentado "
                         "(0x3011): no participa en la cadena RelMgr -> 0x3011 -> "
                         "CamUser -> CaptureStart",
        },
        "no_verificado": [
            "El fichero fuente que implementa el modulo [CAMERA_MAIN_FC] (ninguna "
            "de las 9 trazas cita un .cpp)",
            "La funcion 0x437b7778 (traza 'osal_free_timer') no tiene ninguna "
            "referencia entrante en av-cam.bin: no se puede afirmar si es codigo "
            "muerto o se invoca desde otro binario del paquete de firmware",
            "El significado del flag `lc` (byte [ctx+0xdf]) y su relacion exacta "
            "con el modulo [CAMERA_MAIN_LC] (S127)",
            "El destinatario de los mensajes OSAL del modulo (temporizador y "
            "BatteryInfo)",
            "La semántica de face_on ([ctx+0x49c]) y obj_on ([ctx+0x49e])",
            "Si la API ReplyForTouchShutter debía enlazar con la cadena 0x3011",
        ],
    }
    dest = os.path.join(HERE, "camera_main_fc.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("->", dest)
    print(json.dumps(out["counters"], indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
