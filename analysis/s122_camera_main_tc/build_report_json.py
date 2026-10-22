#!/usr/bin/env python3
"""S122 — compone `camera_main_tc.json` a partir de los JSON ya generados por los
escáneres del hito (`tc_map.json`, `refs_targeted.json`, `emitters.json`,
`diff_versions.json`, `dead_check.json`).

No vuelve a leer el firmware: solo agrega y ordena los hechos verificados.
Los datos de despacho, llamadores y vocabulario están codificados aquí porque
proceden de verificación manual con `disasm.py` / `callers.py` (Capstone).

Salida: camera_main_tc.json
Uso: build_report_json.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    tc = load("tc_map.json")
    em = load("emitters.json")
    diff = load("diff_versions.json")
    dead_check = load("dead_check.json")

    pub = collections.Counter(
        h["call"] for h in em["hits"] if h["class"] == "publisher"
    )
    publishers = [
        {"address": a, "sites": n}
        for a, n in sorted(pub.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    structural = {
        "publisher": 128,
        "printf": 127,
        "no_emit": 1,
        "total": len(em["hits"]),
        "candidate_publisher_sites": sum(
            1 for h in em["hits"] if h["kind"] in ("string", "prefix")
        ),
        "breakdown": {
            "publisher_string": 126,
            "publisher_prefix": 2,
            "printf_inner": 127,
            "no_emit_string_byte_table": 1,
        },
    }
    heuristic = dict(collections.Counter(h["class"] for h in em["hits"]))
    heuristic = {
        "publisher": heuristic.get("publisher", 0),
        "printf": heuristic.get("printf", 0),
        "other": heuristic.get("other", 0),
        "none": heuristic.get("none", 0),
        "total": len(em["hits"]),
    }

    anomalies = [
        {
            "site": "0x43876fcc",
            "idx": 95,
            "kind": "string",
            "heuristic": "printf",
            "structural": "publisher",
            "why": (
                "`add sb,pc` carga en `sb`, no en r0; su `ldr` más cercano de sb "
                "apunta a 0x43cb7343 y el destino se consume en 0x43876ffe "
                "(`mov r3,sb` -> `bl 0x43876c08`): sí publica. Su interior "
                "0x43876fce (`add sl,pc`) se consume en 0x43877004 -> `bl 0x43902718`."
            ),
        },
        {
            "site": "0x43879274",
            "idx": 121,
            "kind": "inner",
            "heuristic": "publisher",
            "structural": "printf",
            "why": (
                "hace `b 0x43879296` -> `bl 0x43902718`: imprime, pero no es la "
                "primera llamada de la ventana. Su pareja string 0x4387926a va a "
                "`bl 0x43878570`."
            ),
        },
    ]

    non_printf_inners = [0, 43, 45, 46, 60, 68, 72, 73, 74, 86, 87, 121, 124]
    emitters_block = {
        "printf_local": em["printers"]["printf"],
        "publishers": publishers,
        "publisher_prologue": {
            "bytes": "0xB408",
            "meaning": "push {r3}",
            "first_bl_offset": "p+0x1e",
            "first_bl_target": "0x435612d0",
            "first_bl_name": "osal_try_valloc_msg",
            "body": [
                "blx 0x439c5a04 (memset)",
                "bl 0x43561244",
                "bl 0x439c5004 (formateo tipo vsnprintf)",
                "bl 0x435612ec (osal_free_msg) en la ruta de error",
            ],
            "note": (
                "`push {r3}` no se detecta como inicio de función con la regla de "
                "prólogos del repo; por eso los 17 se listan por su dirección real."
            ),
        },
        "structural": structural,
        "heuristic": heuristic,
        "anomalies": anomalies,
        "non_printf_inners_reaching_printf": {
            "indices": non_printf_inners,
            "max_instructions": 251,
            "verified": (
                "los 13 alcanzan 0x43902718 dentro de la misma función; barrido con "
                "`bx lr` como tope -> 0 sin alcanzar"
            ),
        },
        "note": (
            "La cifra canónica es la estructural (128 publican / 127 imprimen / 1 no "
            "emite); la heurística de primera llamada directa se conserva como capa "
            "de contraste."
        ),
    }

    dispatch = {
        "function": "0x438730b0",
        "name": "ApolloSA_Main",
        "prologue": {
            "addr": "0x438730b0",
            "bytes": "2de9f04f",
            "asm": "push.w {r4,r5,r6,r7,r8,sb,sl,fp,lr}",
            "then": "sub sp,#0x7c",
        },
        "first_call": {"addr": "0x438730be", "target": "0x43872888"},
        "mode": {"addr": "0x438730c6", "asm": "uxtb.w sl,r5"},
        "range_check": {
            "cmp": "0x43873338",
            "bhi": "0x4387333a",
            "target_over": "0x438735a2",
        },
        "tbb": {
            "addr": "0x4387333e",
            "bytes": "dfe805f0",
            "table_addr": "0x43873342",
            "table": "05050914140d0f0d0f",
            "role": "chequeo de rango por modo, no despacho de operación",
            "cases": {
                "0,1": "0x4387334c",
                "2": "0x43873354",
                "3,4": "0x4387336a",
                "5": "0x4387335c",
                "6": "0x43873360",
                "7": "0x4387335c",
                "8": "0x43873360",
            },
            "common_bhi": "0x43873366",
            "invalid": {"2": "0x438735a8", "4": "0x438735a2"},
            "validated_fields": {
                "0,1": "(x-1)<=0xA",
                "2": "(x-1)<=1",
                "5,7": "x==0x95",
                "6,8": "(x-1)<=0x94",
                "source": "[r4,#0x2c]",
            },
        },
        "tbh": {
            "addr": "0x4387348e",
            "bytes": "dfe815f0",
            "table_addr": "0x43873492",
            "table": "090009000e00a300250015001d0015001d00",
            "cases": {
                "0,1": {"target": "0x438734a4", "action": "bl 0x43875878"},
                "2": {"target": "0x438734ae", "action": "bl 0x438e8204 (JudgeBdroRslt)"},
                "3": {"target": "0x438735d8", "action": "bl 0x43872c94 (núcleo)"},
                "4": {"target": "0x438734dc", "action": "bl 0x437d48e8 (calibración)"},
                "5,7": {"target": "0x438734bc", "action": "bl 0x438740c8 (VectTypeAtCoar)"},
                "6,8": {"target": "0x438734cc", "action": "bl 0x43874270 (FinData/OutData/VectTypeAtFine)"},
            },
        },
        "convergence": {
            "addr": "0x438735d8",
            "actions": [
                "mov r0,r5",
                "mov r1,r6",
                "mov r2,r4",
                "ldr r3,[sp,#0x6c]",
                "str r7,[sp]",
                "bl 0x43872c94 en 0x438735e2",
                "mov sb,r0",
                "b 0x438734e6",
            ],
            "bl_core_site": "0x438735e2",
            "note": "0x438735d8 no es un caso propio del tbh: es la convergencia de las ramas; el bl al núcleo está en 0x438735e2.",
        },
        "epilogue": {"addr": "0x4387359e", "asm": "pop.w {...,pc}"},
        "own_traces": {
            "sites": 14,
            "traces": 7,
            "addrs": [
                "0x43cb6ac7",
                "0x43cb6b10",
                "0x43cb6b57",
                "0x43cb6b8b",
                "0x43cb6bdc",
                "0x43cb6c0d",
                "0x43cb6c41",
            ],
        },
        "fin": {
            "entry": "0x43873644",
            "prologue": "0x43873646 (push {r0,r1,r2,r4,r5,lr})",
            "traces": ["0x43cb6cc5 (ApolloSA_Fin(start) %d)", "0x43cb6cee (ApolloSA_Fin(end))"],
        },
        "core": {
            "entry": "0x43872c94",
            "prologue": "0x43872c96 (push.w {r4,r5,r6,r7,r8,lr})",
            "traces": ["0x43cb6a93 (TC:APL:Err: MakerNote:GetTagPt %d)"],
            "filter": "modos 0-2, 6 y 8; el resto va a 0x43872fdc",
        },
    }

    callers = {
        "apollosa_main": [
            {
                "site": "0x437f1324",
                "context": "panorámica (ExecutePanoramaTC1ST, S105)",
                "evidence": "bl 0x438730b0 tras cmp r7,#2",
            },
            {
                "site": "0x438bdeac",
                "context": "[IMAGING_CAP], función 0x438bddf0",
                "evidence": "3 llamadores: 0x438be0de, 0x438be302, 0x43b1d74e",
            },
        ],
        "panorama_chain": {
            "entry": "0x437f1ac4 (ExecutePanoramaTC1ST)",
            "mid": "0x437f10d4",
            "cmp": "0x437f12f6 (cmp r7,#2)",
            "fin_call": "0x437f1314 -> 0x43873644",
            "main_call": "0x437f1324 -> 0x438730b0",
            "error_print": "0x437f1368 -> 0x43902718",
            "error_string": {
                "vaddr": "0x43cacf9c",
                "text": "[IMAGING_CAP]: ApolloSA_Main: err[0x%02x]",
                "ldr_add": ["0x437f1352", "0x437f135a"],
                "inner_add": ["0x437f1362", "0x437f1366"],
                "inner_vaddr": "0x43cacfab",
                "rectification": "S105 citaba 0x43cacf9b, byte NUL; el inicio real es 0x43cacf9c",
            },
        },
        "apl_clients": [
            {"function": "0x438765c8", "call_site": "0x43873378", "context": "modo 5/7", "trace": "TC:APL:Err: SA Preload %d (0x43cb700e)"},
            {"function": "0x438765fc", "call_site": "0x438733e6", "context": "", "trace": "TC:APL:Err: SA Acquire %d (0x43cb703a)"},
            {"function": "0x4387668c", "call_site": "0x43873418", "context": "", "trace": "SA Start %d %d (0x43cb7092)"},
            {"function": "0x43876a80", "call_site": "0x4387352c", "context": "", "trace": "TC:APL:Err: SA release2 %d (0x43cb714d)"},
            {"function": "0x43876ab4", "call_site": "0x4387343a", "context": "", "trace": "SA Prm Open2, SA Rslt Open, SA Vect Open"},
            {"function": "0x43876b74", "call_site": "0x438734e8", "context": "", "trace": "SA Prm Close2, SA Rslt Close, SA Vect Close"},
        ],
        "calibration": {"function": "0x437d48e8", "sites": 52, "labels": 26, "caller": "0x438734e0 (caso 4 del tbh)"},
        "judge_bdro_rslt": {"function": "0x438e8204", "caller": "0x438734b6 (caso 2 del tbh)", "sites": ["0x438e84f8", "0x438e850c"]},
        "smart_zoom": {"function": "0x43876ea4", "sites": 31, "caller": "0x4354af32 (función 0x4354a678)"},
        "ddt": {
            "sites": 18,
            "functions": ["0x43878620", "0x438786c4", "0x43879050", "0x43879104", "0x43879180", "0x43879204", "0x438792dc", "0x4387938e"],
            "no_direct_callers": ["0x438786c4", "0x43879204", "0x438792dc", "0x4387938e"],
        },
        "dist": {
            "sites": 13,
            "functions": ["0x437d713c", "0x437d7478", "0x437d765c"],
        },
    }

    diff_block = {"versions": {}}
    for ver, data in diff.items():
        rows = data["rows"]
        # distribución sobre las 127 trazas: una traza no localizada cuenta como 0 sitios
        by_n = collections.Counter(len(r.get("sites", [])) for r in rows)
        two = []
        for i, r in enumerate(rows):
            if len(r.get("sites", [])) >= 2:
                two.append(
                    {
                        "idx": i,
                        "vaddr": r["vaddr"],
                        "text": tc["strings"][i]["text"],
                        "sites": r["sites"],
                    }
                )
        lost = []
        for i, (s, r) in enumerate(zip(tc["strings"], rows)):
            total = len(s["sites"])
            # sitios de emision (publicador): punteros `string` + `prefix`
            publisher = sum(
                1 for ref in s.get("refs", []) if ref["kind"] in ("string", "prefix")
            )
            other = len(r.get("sites", []))
            if r.get("found") and total >= 1 and other == 0:
                lost.append(
                    {
                        "idx": i,
                        "vaddr": s["vaddr"],
                        "text": s["text"],
                        "a6000_publisher_sites": publisher,
                        "a6000_total_sites": total,
                        "other_sites": other,
                    }
                )
        not_found = [
            {"idx": i, "vaddr": r["vaddr"], "why": r.get("why")}
            for i, r in enumerate(rows)
            if not r.get("found")
        ]
        diff_block["versions"][ver] = {
            "bin": data["bin"],
            "token_camera_main_tc": data["token_camera_main_tc"],
            "texts_found": data["texts_found"],
            "texts_ref_pic": data["texts_ref_pic"],
            "pic_sites": data["pic_sites"],
            "texts_exact_literal": data["texts_exact_literal"],
            "sites_distribution": {str(k): v for k, v in sorted(by_n.items())},
            "two_sites": two,
            "lost_sites": lost,
            "not_found": not_found,
        }
    diff_block["conclusion"] = (
        "0 apariciones de la etiqueta [CAMERA_MAIN_TC]; 126/127 textos interiores "
        "presentes (falta idx 105, vacío); 119 textos con refs PIC / 123 sitios "
        "frente a 123/256 en la A6000; idéntico en A7S fw3.20 y A6300 fw2.01. "
        "La A6000 fw3.21 añade la instrumentación doble y tres trazas."
    )

    out = {
        "milestone": "S122",
        "module": "CAMERA_MAIN_TC",
        "firmware": {
            "model": "A6000",
            "version": "fw3.21",
            "bin": "analysis/rea-independent/input/av-cam.bin",
            "size": 11427236,
        },
        "base_vaddr": "0x43541000",
        "method": (
            "solo bytes: Capstone 5.0.7 + escáner PIC propio bajo la regla estricta "
            "canónica; sin REA/Ghidra, sin ejecutar firmware, sin cámara, sin red"
        ),
        "counts": {
            **tc["counts"],
            "publishers": len(publishers),
            "emitters_structural": structural,
            "emitters_heuristic": heuristic,
        },
        "rule": tc["rule"],
        "subblocks_content": tc["subblocks_content"],
        "subblocks_prefix": [
            {"name": b["name"], "n": b["n"], "lo": b["lo"], "hi": b["hi"]}
            for b in tc["subblocks"]
        ],
        "functions": tc["functions"],
        "emitters": emitters_block,
        "dispatch": dispatch,
        "callers": callers,
        "dead": {
            "count": len(tc["dead"]),
            "strings": tc["dead"],
            "evidence": {
                "absolute_pointers": 0,
                "addw_pc": 0,
                "movw_movt_pairs": 0,
                "in_a7s_a6300": 0,
                "source": "dead_check.json",
            },
            "note": "las cuatro son del camino de cancelación; ApolloSA_Cancel no existe como función en el binario",
        },
        "vocabulary": {
            "present": {
                "ApolloSA": 6,
                "SA ": 22,
                "DDT": 18,
                "TC:": 58,
                "Dist": 9,
                "Gmv": 4,
                "Gyro": 3,
                "Lmv": 2,
                "Raw": 2,
                "dist": 2,
                "PANORAMA": 1,
                "Exif": 1,
                "SMART ZOOM": 1,
                "zoom": 1,
                "still": 1,
                "Vect": 5,
                "Judge": 5,
                "Stit": 2,
            },
            "absent": [
                "shut", "silent", "electro", "mech", "sensor", "exposure", "drive",
                "readout", "jpeg", "movie", "stc", "bracket", "sweep", "interval",
            ],
            "shutter_line": "S51 A/B/C = NO se mantiene: ninguna traza distingue obturador mecánico de electrónico",
        },
        "differential": diff_block,
        "strings": [
            {
                "idx": i,
                "vaddr": s["vaddr"],
                "vaddr_string": s["vaddr_string"],
                "text": s["text"],
                "text_after_prefix": s["text_after_prefix"],
                "sites": s["sites"],
                "kinds": s["kinds"],
                "funcs": s["funcs"],
                "refs": s["refs"],
            }
            for i, s in enumerate(tc["strings"])
        ],
        "not_verified": [
            "Por qué idx 2, idx 32 e idx 108 pierden sus sitios en A7S/A6300 (¿emisión eliminada, movida o texto cambiado?); no se ha decompilado el código equivalente.",
            "Llamada por puntero a 0x438786c4 y a 0x43879204/0x438792dc/0x4387938e: sin llamadores bl/blx; la búsqueda de punteros absolutos no está cerrada.",
            "Significado de TC, DDT, DIST, STC, ARC, RC, Gmv y Lmv: el firmware no expande ninguna sigla.",
            "Estructura de los 17 publicadores en A7S/A6300: el diferencial se hizo por texto y referencia PIC, no por prólogos ni cuerpo.",
            "Etiqueta [CAMERA_MAIN_TC] en A7S fw3.21: no hay esa versión en el repo.",
            "Pipeline interno de calibración, DIST, DDT y SMART ZOOM más allá de sus trazas (SA/HW, buffers).",
            "Significado de r7 == 2 en 0x437f12f6: selecciona ApolloSA_Fin frente a ApolloSA_Main, no qué estado representa.",
            "Campos de APL_MEM_INFO, APL_IMG_INFO, APL_PANORAMA_INFO y JudgeBdroRslt (10 enteros): se conoce número y orden, no significado ni offset de origen.",
        ],
    }

    path = os.path.join(HERE, "camera_main_tc.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("escrito", path, "strings:", len(out["strings"]), "bytes:", os.path.getsize(path))


if __name__ == "__main__":
    main()
