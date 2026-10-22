#!/usr/bin/env python3
"""S167 — añade al `sad.json` los datos de la verificación independiente (sub-agente 2).

No altera ninguna clave existente: sólo añade claves nuevas con prefijo `verif_indep_*`.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "sad.json")
d = json.load(open(P))

d["verif_indep_bloques_rodata"] = {
    "descripcion": ("Las 45 cadenas [SAD] no son un bloque contiguo: hay 3 bloques "
                    "separados por 0x100 bytes de relleno y por las 3 cadenas de "
                    "programa SA intercaladas."),
    "bloque_A_handles": {"vaddr_ini": "0x43ce546b", "vaddr_fin": "0x43ce54b8", "n": 3},
    "bloque_B_hdr_err": {"vaddr_ini": "0x43ce55bc", "vaddr_fin": "0x43ce5618", "n": 3},
    "intercalado_SA": {"vaddr_ini": "0x43ce561f", "vaddr_fin": "0x43ce564b",
                       "cadenas": ["SA_PREINSTALLED_PRG:", "SA_JPEG_ENC", "SA_JPEG_DEC"]},
    "bloque_C_dbgprt": {"vaddr_ini": "0x43ce564c", "vaddr_fin": "0x43ce59d1", "n": 39},
}

d["verif_indep_log_channel"] = {
    "impresor_propio": {"vaddr": "0x439a10f0",
                        "id_mensaje_osal": "0x93 (147)",
                        "tamano_mensaje": "0x9a",
                        "nota": ("las 45 trazas [SAD] se emiten con este impresor, que "
                                 "reserva con osal_try_valloc_msg 0x435612d0")},
    "logger_global_de_NS_SCALAR_INFRA": {"vaddr": "0x435ab880",
                                         "lo_usan": ["[SFRA]", "[SFRS]"]},
    "conclusion": ("[SAD] usa un canal de log propio, distinto del de [SFRA]/[SFRS]: "
                   "es un modulo independiente del mismo subsistema."),
}

d["verif_indep_tabla_versiones_sa"] = {
    "tabla": {"vaddr_ini": "0x43ce5402", "bytes": 68,
              "entradas": ["SA0_V1.0|SA5_V1.0", "ZMA1V1.0|SA5_V1.0",
                           "SA1_V1.0|SA5_V1.0", "ZMA0V1.0|SA5_V1.0"]},
    "globales_runtime": ["0x43f2ef58", "0x43f2ef68", "0x43f2ef78"],
    "bucle_de_comparacion": ("cmp/ldrb 16 bytes en 0x43993128-0x4399315e: compara la "
                             "version en ejecucion con el literal de .rodata"),
}

d["verif_indep_direcciones_de_datos"] = {
    "tablas_de_handles": {"0x43f85932": "32 entradas u16",
                          "0x43f84bfe": "255 entradas u16"},
    "contadores": ["0x43f84bfc", "0x43f84bf4", "0x43f31368", "0x43f31364"],
    "byte_informar_una_sola_vez": {"vaddr": "0x43e211c8",
                                    "compartido_por": ["0x4399d464", "0x4399d528",
                                                       "0x4399d618"]},
    "puntero_embebido": {"sitio": "0x439a11ac",
                         "destino": "0x43ce5644",
                         "nota": ("'PEG_DEC' = 'SA_JPEG_DEC'+4: el despachador compara "
                                  "el nombre del programa recibido con SA_JPEG_DEC")},
}

d["verif_indep_ficheros"] = {
    "fichero_propio_del_modulo": "NO VERIFICADO",
    "comprobacion": ("En 0x43990000-0x439a1800 ningun sitio PIC (regla estricta Y regla "
                     "ancha) apunta a un nombre .cpp/.h ni a un nombre de clase RTTI; "
                     "las 65 cadenas referenciadas son [SIO](3), [SAD](45), la tabla de "
                     "versiones SA(4), los nombres de programa SA(3) y literales sueltos."),
    "ficheros_de_la_capa_de_secuencia": {
        "ScalarInfraSequenceSa.cpp": {"vaddr": "0x43ce6c15", "n_sitios": 10},
        "ScalarInfraSequenceSaStage.cpp": {"vaddr": "0x43ce6e16", "n_sitios": 6},
        "ScalarInfraAsyncMain.cpp": {"vaddr": "0x43ce59fd", "n_sitios": 3}},
}

d["verif_indep_anclas_diferencial"] = {
    "nota": ("anclas de CODIGO (no de cadenas) para el diferencial: el bloque driver SA "
             "existe en los tres firmwares, pero en la A6000 fw3.21 es otro codigo "
             "(crece ~0x2CE bytes y anade el volcado [SAD])."),
    "sitio_de_[SIO]osal_valloc_msg": {"A6000": "0x43990414", "A7S": "0x4397df30",
                                      "A6300": "0x43a24b68"},
    "sitio_de_SA_PREINSTALLED_PRG": {"A6000": "0x4399ee6a", "A7S": "0x4398c8cc",
                                     "A6300": "0x43a2accc"},
    "sitio_de_ScalarInfraAsyncMain.cpp": {"A6000": "0x439a18d6", "A7S": "0x4398f122",
                                           "A6300": "0x43a387fa"},
    "delta_A6000_menos_A7S": {"0x124e4": "primera ancla", "0x1259e": "segunda ancla",
                               "0x127b4": "tercera ancla"},
    "codigo_distinto_en_la_A7S": ["0x4398ecd0 (equivale a 0x439a11b4)",
                                  "0x43986100 (equivale a 0x43998578)"],
}

d["verif_indep_pares_pic"] = {
    "regla": "estricta (canonica S106)",
    "pares_verificados_a_mano": 49, "pares_totales": 49, "fallos": 0,
    "comprobaciones": ["ldr mas cercano del mismo registro (ventana 4 KB)",
                        "literal del pool correcto",
                        "destino = literal + (add + 4) == inicio de cadena",
                        "registro no reescrito entre ldr y add"],
    "cotejo_mapa_global_repo": {"n_discrepancias": 0,
                                "destinos": 17525},
}

json.dump(d, open(P, "w"), indent=1, ensure_ascii=False)
print("sad.json actualizado; claves:", len(d))
