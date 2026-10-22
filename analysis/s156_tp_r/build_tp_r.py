#!/usr/bin/env python3
"""S156 — genera analysis/s156_tp_r/tp_r.json con los datos verificados del módulo [TP_R].

Todo sale de bytes:
  - cadenas con el token [TP_R] / [TP R] en los tres firmwares,
  - referencias PIC (regla estricta canónica) y función que las contiene,
  - GID de las colas OSAL,
  - pertenencia a la familia de loggers de S151,
  - diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01.
"""
import bisect
import json
import re
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from diffscan import BASE, FILES, Img  # noqa: E402
from common import U16, U32, cstr, pic_ldr_sites, pic_add_sites  # noqa: E402

A6 = Img(FILES["A6000"])

# ---------------------------------------------------------------- cadenas
TOKENS = ("[TP_R]", "[TP R]")
targets = []
for a, s in A6.strings():
    if any(t in s for t in TOKENS):
        targets.append((a, s))
targets.sort()

smap = A6.strict_map()

# función que contiene un sitio (prólogo Thumb más cercano hacia atrás)
def func_start(addr):
    o = addr - BASE
    a = o - (o % 2)
    while a >= max(0, o - 0x4000):
        h1 = U16(A6.B, a)[0]
        if (h1 & 0xFE00) == 0xB400 and (h1 & 0x00FF) != 0:
            return BASE + a
        if a + 4 <= A6.N and h1 == 0xE92D:
            return BASE + a
        a -= 2
    return None


strings = []
for a, s in targets:
    refs = smap.get(a, [])
    absp = A6.abs_ptrs(a)
    strings.append({
        "addr": f"0x{a:x}",
        "text": s,
        "token": "[TP_R]" if "[TP_R]" in s else "[TP R]",
        "pic_refs": [f"0x{r:x}" for r in refs],
        "funcs": sorted({f"0x{func_start(r):x}" for r in refs}),
        "abs_ptrs": [f"0x{x:x}" for x in absp],
        "viva": bool(refs) or bool(absp),
    })
# ------------------------------------------------- función → traza
by_func = {}
for st in strings:
    for site in st["pic_refs"]:
        fs = f"0x{func_start(int(site, 16)):x}"
        by_func.setdefault(fs, []).append({"site": site, "text": st["text"],
                                            "cadena": st["addr"]})

# ------------------------------------------------------- otros binarios
diff = {}
for which in ("A7S", "A6300"):
    img = Img(FILES[which])
    sm = img.strict_map()
    lst = []
    for a, s in img.strings():
        if any(t in s for t in TOKENS):
            lst.append({
                "addr": f"0x{a:x}",
                "text": s,
                "pic_refs": [f"0x{r:x}" for r in sm.get(a, [])],
                "abs_ptrs": [f"0x{x:x}" for x in img.abs_ptrs(a)],
                "viva": bool(sm.get(a)) or bool(img.abs_ptrs(a)),
            })
    diff[which] = {"n_cadenas": len(lst), "cadenas": lst}

# núcleo de texto (sin etiqueta) -> ¿aparece en A7S/A6300 con otra etiqueta?
cores = {}
for st in strings:
    t = st["text"]
    core = t.split("]: ", 1)[1] if "]: " in t else t
    cores.setdefault(core, []).append(st["addr"])
core_diff = {}
for which in ("A7S", "A6300"):
    img = Img(FILES[which])
    found = {}
    for core in cores:
        cb = core.encode()
        hits = []
        for m in re.finditer(re.escape(cb), img.B):
            o = m.start()
            s = o
            while s > 0 and 32 <= img.B[s - 1] < 127:
                s -= 1
            e = img.B.find(b"\x00", o)
            hits.append({"addr": f"0x{BASE + s:x}",
                         "text": img.B[s:e].decode("ascii", "replace")})
        if hits:
            found[core] = hits
    core_diff[which] = found

# ------------------------------------------------------- GID de colas
def ldr_value(addr):
    o = addr - BASE
    h = U16(A6.B, o)[0]
    h2 = U16(A6.B, o + 2)[0]
    if (h & 0xF800) == 0x4800:
        lit = ((addr + 4) & ~3) + ((h & 0xFF) * 4)
    else:
        lit = ((addr + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    return U32(A6.B, lit - BASE)[0]


gids = {
    "cola_de_log_del_firmware_0x4366c300": f"0x{ldr_value(0x4366c314):08x}",
    "cola_auxiliar_0x4366c388": f"0x{ldr_value(0x4366c38c):08x}",
    "cola_propia_del_modulo_TP_osal_rcv_msg": f"0x{ldr_value(0x4366c85c):08x}",
    "cola_propia_del_modulo_TP_reg_sync_cb": f"0x{ldr_value(0x4366cc2a):08x}",
    "cola_en_boot_init_tp": f"0x{ldr_value(0x4366cbf0):08x}",
    "cola_en_boot_exit_tp": f"0x{ldr_value(0x4366c774):08x}",
}

# ------------------------------------------- familia de loggers (S151)
def fam(B):
    out = []
    n = len(B)
    for a in range(0, n - 48, 2):
        if B[a] == 0x08 and B[a + 1] == 0xB4:
            for k in range(a + 4, min(a + 40, n - 2), 2):
                if B[k] == 0x9A and B[k + 1] == 0x22:
                    out.append(BASE + a)
                    break
    return out


def fam_estricta(B):
    out = []
    n = len(B)
    for a in range(0, n - 8, 2):
        if (B[a] == 0x08 and B[a + 1] == 0xB4
                and B[a + 2] == 0x9A and B[a + 3] == 0x22):
            out.append(BASE + a)
    return out


fam_counts = {}
for which in ("A6000", "A7S", "A6300"):
    B = open(FILES[which], "rb").read()
    fam_counts[which] = {
        "laxa_push_r3_movs_r2_0x9a": len(fam(B)),
        "estricta_push_r3_seguido_de_movs_r2_0x9a": len(fam_estricta(B)),
    }

out = {
    "hito": "S156",
    "modulo": "[TP_R]",
    "codigo_del_modulo": {
        "extento": ["0x4366c2a4", "0x4366cd38"],
        "funciones": ["0x4366c2a4", "0x4366c2bc", "0x4366c300", "0x4366c388",
                      "0x4366c410", "0x4366c456", "0x4366c498", "0x4366c540",
                      "0x4366c568", "0x4366c624", "0x4366c6e8", "0x4366c840",
                      "0x4366c8fc", "0x4366c924", "0x4366c978", "0x4366ca92",
                      "0x4366cadc", "0x4366caf4"],
        "tabla_de_comandos_ddl": "0x43fe3f28",
        "nombre_registrado": "tp",
        "comandos": ["start", "set_mode", "print_xy", "dds_on", "dds_off"],
        "boot_init": {"funcion": "0x4366caf4", "llamada_desde": "0x43a464dc",
                      "id_de_arranque": 135, "parametro": 280},
        "boot_exit": {"funcion": "0x4366c6e8", "llamada_desde": "0x43a4670c",
                      "id_de_parada": 134},
    },
    "base_vaddr": f"0x{BASE:x}",
    "binario": FILES["A6000"],
    "regla_referencias": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py)",
    "cadenas": strings,
    "contadores": {
        "n_cadenas_TP_R": sum(1 for s in strings if s["token"] == "[TP_R]"),
        "n_cadenas_TP_espacio": sum(1 for s in strings if s["token"] == "[TP R]"),
        "n_cadenas_totales": len(strings),
        "n_vivas": sum(1 for s in strings if s["viva"]),
        "n_muertas": sum(1 for s in strings if not s["viva"]),
        "n_sitios_pic": sum(len(s["pic_refs"]) for s in strings),
        "n_funciones": len(by_func),
    },
    "mapa_funcion_traza": by_func,
    "colas_osal_gid": gids,
    "familia_loggers_s151": {
        "reporter_TP": "0x4366c300",
        "miembro_de_la_familia_laxa": True,
        "prologo": "0x4366c300 push {r3}; 0x4366c302 movs r3,#0; push.w {...}; 0x4366c318 movs r2,#0x9a",
        "contadores": fam_counts,
    },
    "diferencial": {
        "A7S": diff["A7S"],
        "A6300": diff["A6300"],
        "nucleos_por_etiqueta": core_diff,
    },
}

with open("analysis/s156_tp_r/tp_r.json", "w") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print(json.dumps(out["contadores"], indent=1))
print("funciones:", json.dumps({k: len(v) for k, v in by_func.items()}, indent=1))
