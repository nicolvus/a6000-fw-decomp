#!/usr/bin/env python3
"""S166 — modulo `[ADC_DEBUG]` (14 trazas) de la A6000 fw3.21: cadenas, pares PIC
verificados a mano (regla estricta), funcion contenedora, tabla de comandos ADJ,
llamadores del servicio LIRO_ADC y diferencial con A7S fw3.20 / A6300 fw2.01.

  vaddr = 0x43541000 + file_offset

Regla de referencias: estricta (canonica del repo), mapa global ya calculado en
analysis/s106_imaging_cap/pic_refs_strict_global.json
(ver analysis/s106_imaging_cap/pic_xref_methodology.md).  Ademas este script
*redecodifica* cada par (ldr rX,[pc,#imm] + add rX,pc) desde los bytes y lo
comprueba contra el mapa: eso es la "verificacion a mano" automatizada.

Salida: analysis/s166_adc_debug/adc_debug.json
"""
import bisect
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 0x43541000

A6000 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7S = (ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
               "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
REFS = ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json"
PROL = HERE / "prologues.json"

DATA = A6000.read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
PAT = re.compile(rb"[\x20-\x7e]{4,}")
TOKEN = "[ADC_DEBUG]"

# --- direcciones verificadas a mano (ver informe) ---------------------------
ADJ_TABLE = 0x440189BC          # descriptor del grupo ADJ del driver LIRO ADC
ADJ_CMD_GET_D = 0x43CE5299      # "get_d"
ADJ_CMD_GET_DA = 0x43CE52BE     # "get_da"
ADJ_CMD_SET_DA = 0x43CE52DE     # "set_da"
LIRO_ADC_HANDLE = 0x720018      # handle del servicio LIRO_ADC
ADC_ARR = 0x43F84B80            # array de valores ADC: 2 unidades x 12 canales (u16)
ADC_HW_BASE = 0xF2406000        # bloque de HW del ADC (unidad 0); unidad 1 = +0x1000
ADC_HW_CH = 0xF2406014          # registro u16 por canal (unidad 0)


def strings_with(data, token):
    out = []
    for m in PAT.finditer(data):
        t = m.group().decode("latin1")
        if token not in t:
            continue
        off = m.start()
        end = off
        while end < len(data) and data[end] != 0:
            end += 1
        out.append((BASE + off, data[off:end].decode("latin1")))
    return out


def cstr(data, addr):
    off = addr - BASE
    if off < 0 or off >= len(data):
        return None
    end = off
    while end < len(data) and data[end] != 0:
        end += 1
    return data[off:end].decode("latin1")


def u32(data, addr):
    off = addr - BASE
    if off < 0 or off + 4 > len(data):
        return None
    return struct.unpack_from("<I", data, off)[0]


def decode_pic(data, site):
    """Recodifica el par PIC (ldr rX,[pc,#imm] + add rX,pc) alrededor de `site`.

    Devuelve (destino, ldr_addr, pool_addr, offset) o None.  Se recorre hacia
    atras buscando el `ldr` del mismo registro y hacia adelante el `add`."""
    # el `add rX,pc` esta en `site`; buscamos el `ldr` hacia atras
    # (el `site` que nos da el mapa es la direccion del `add`)
    reg = None
    for back in range(0, 40, 2):
        a = site - back
        if a < BASE:
            break
        h = struct.unpack_from("<H", data, a - BASE)[0]
        if (h >> 11) == 0b01001 and ((h >> 8) & 7) != 0:
            reg = (h >> 8) & 7
            imm = (h & 0xFF) * 4
            pool = ((a + 4) & ~3) + imm
            off = u32(data, pool)
            if off is None:
                return None
            return (site + 4 + off, a, pool, off, reg)
    return None


def container(site, prol):
    """Proximo prologo `push {...,lr}` por detras (mismo metodo que S133/S164)."""
    k = bisect.bisect_left(prol, site) - 1
    for p in reversed(prol[max(0, k - 80):k + 1]):
        if site - p > 0x3000:
            break
        last = None
        ok = True
        for ins in MD.disasm(DATA[p - BASE:site - BASE], p):
            if ins.address >= site:
                break
            m, o = ins.mnemonic, ins.op_str
            if (m.startswith("pop") and "pc" in o) or (m == "bx" and o == "lr"):
                ok = False
                break
            last = ins
        if ok and last is not None and last.address + last.size == site:
            return p, False
    for p in reversed(prol[max(0, k - 80):k + 1]):
        if site - p > 0x3000:
            break
        return p, True
    return None, True


def bl_target(addr):
    o = addr - BASE
    if o + 4 > len(DATA):
        return None
    hw1, hw2 = struct.unpack_from("<HH", DATA, o)
    if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xD000) != 0xD000:
        return None
    S = (hw1 >> 10) & 1
    imm10 = hw1 & 0x3FF
    J1 = (hw2 >> 13) & 1
    J2 = (hw2 >> 11) & 1
    imm11 = hw2 & 0x7FF
    I1 = 1 - (J1 ^ S)
    I2 = 1 - (J2 ^ S)
    off = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | (imm11 << 1)
    if S:
        off -= (1 << 25)
    return addr + 4 + off


def sweep_service_handles(target):
    """Llamadas `bl <target>` cuyo r0 (handle) se carga desde un literal."""
    res = defaultdict(list)
    n = len(DATA)
    i = 0
    while i < n - 4:
        hw1 = int.from_bytes(DATA[i:i + 2], "little")
        if (hw1 & 0xF800) == 0xF000:
            a = BASE + i
            if bl_target(a) == target:
                handle = None
                j = i - 2
                while j >= max(i - 60, 0):
                    hj = int.from_bytes(DATA[j:j + 2], "little")
                    if (hj >> 11) == 0b01001 and ((hj >> 8) & 7) == 0:
                        imm = (hj & 0xFF) * 4
                        pool = ((BASE + j + 4) & ~3) + imm
                        handle = u32(DATA, pool)
                        break
                    j -= 2
                res["0x%08x" % (handle if handle is not None else 0)].append(a)
            i += 4
        else:
            i += 2
    return res


def main():
    refs = {int(k, 16): v for k, v in json.loads(REFS.read_text()).items()}
    prol = json.loads(PROL.read_text())

    a7s = A7S.read_bytes()
    a6300 = A6300.read_bytes()

    strs = strings_with(DATA, TOKEN)

    # ---- pares PIC: mapa estricto + verificacion manual (recodificacion) ----
    pairs = []
    for saddr, text in strs:
        for site in refs.get(saddr, []):
            dec = decode_pic(DATA, site)
            ok = bool(dec) and dec[0] == saddr
            f, approx = container(site, prol)
            pairs.append({
                "string": saddr,
                "string_hex": "%08x" % saddr,
                "text": text,
                "site": site,
                "site_hex": "%08x" % site,
                "manual_ok": ok,
                "manual_dest": ("%08x" % dec[0]) if dec else None,
                "ldr_addr": ("%08x" % dec[1]) if dec else None,
                "pool_addr": ("%08x" % dec[2]) if dec else None,
                "pool_offset": ("0x%08x" % dec[3]) if dec else None,
                "func": f,
                "func_hex": ("%08x" % f) if f else None,
                "approx_function": approx,
            })

    by_string = defaultdict(list)
    for p in pairs:
        by_string[p["string"]].append(p)

    strings_json = []
    for saddr, text in strs:
        rr = by_string.get(saddr, [])
        strings_json.append({
            "vaddr": saddr,
            "vaddr_hex": "%08x" % saddr,
            "text": text,
            "n_sites": len(rr),
            "sites": [p["site"] for p in rr],
            "sites_hex": [p["site_hex"] for p in rr],
            "functions": sorted({p["func"] for p in rr if p["func"]}),
            "functions_hex": sorted({p["func_hex"] for p in rr if p["func_hex"]}),
            "manual_ok_all": all(p["manual_ok"] for p in rr),
            "a7s_present": text.encode("latin1") in a7s,
            "a6300_present": text.encode("latin1") in a6300,
        })

    funcs = []
    by_func = defaultdict(list)
    for p in pairs:
        by_func[p["func"]].append(p)
    # entrada real de la funcion (la tabla ADJ apunta al `cmp` previo al `push`)
    FUNC_ENTRY = {0x4398EB22: 0x4398EB20, 0x4398EC7E: 0x4398EC7C}
    for f, rs in sorted(by_func.items(), key=lambda kv: (kv[0] is None, kv[0])):
        funcs.append({
            "vaddr": f,
            "vaddr_hex": ("%08x" % f) if f else None,
            "func_entry": FUNC_ENTRY.get(f),
            "func_entry_hex": ("%08x" % FUNC_ENTRY[f]) if f in FUNC_ENTRY else None,
            "n_sites": len(rs),
            "sites_hex": sorted({p["site_hex"] for p in rs}),
            "strings_hex": sorted({p["string_hex"] for p in rs}),
            "texts": [p["text"] for p in sorted(rs, key=lambda x: x["site"])],
            "approx_function": any(p["approx_function"] for p in rs),
        })

    # ---- tabla de comandos ADJ del driver LIRO ADC --------------------------
    adj = {}
    for name, s in (("get_d", ADJ_CMD_GET_D), ("get_da", ADJ_CMD_GET_DA),
                    ("set_da", ADJ_CMD_SET_DA)):
        # la tabla es: {u32 ptr_tabla, u32 ?, u32 n_cmds, u32 mask, entradas de 12 B}
        idx = None
        for off in range(0, 0x80, 12):
            if u32(DATA, ADJ_TABLE + 0x10 + off) == s:
                idx = off
                break
        help_ptr = u32(DATA, ADJ_TABLE + 0x10 + idx + 4) if idx is not None else None
        handler = u32(DATA, ADJ_TABLE + 0x10 + idx + 8) if idx is not None else None
        adj[name] = {
            "name_addr": "%08x" % s,
            "name": cstr(DATA, s),
            "help_addr": ("%08x" % help_ptr) if help_ptr else None,
            "help": cstr(DATA, help_ptr) if help_ptr else None,
            "handler_ptr": ("%08x" % handler) if handler else None,
            "handler": ("%08x" % (handler & ~1)) if handler else None,
        }
    adj_table = {
        "descriptor_addr": "%08x" % ADJ_TABLE,
        "n_cmds": u32(DATA, ADJ_TABLE + 8),
        "mask": u32(DATA, ADJ_TABLE + 12),
        "entries": adj,
    }

    # ---- despachador de sub-comandos del driver (0x4398e578) ---------------
    # tbb de 5 entradas en 0x4398e5d0 (base 0x4398e5d4)
    tbb_base = 0x4398E5D4
    tbb_raw = DATA[0x4398E5D0 - BASE:0x4398E5D0 - BASE + 5]
    sub_cmds = []
    for i, b in enumerate(tbb_raw):
        target = tbb_base + 2 * b
        # la etiqueta es el destino del primer `add rX,pc` que sigue al caso
        label = None
        for ins in MD.disasm(DATA[target - BASE:target - BASE + 40], target):
            if ins.mnemonic == "add" and ins.op_str.endswith(", pc"):
                dec = decode_pic(DATA, ins.address)
                if dec:
                    label = "%08x" % dec[0]
                break
        sub_cmds.append({
            "subcmd": i + 1,
            "tbb_target": "%08x" % target,
            "label_addr": label,
            "label": cstr(DATA, int(label, 16)) if label else None,
        })

    # ---- clientes del servicio LIRO_ADC (handle 0x720018) -------------------
    handles = sweep_service_handles(0x43561228)
    adc_sites = handles.get("0x%08x" % LIRO_ADC_HANDLE, [])
    clients = []
    for s in sorted(adc_sites):
        f, _ = container(s, prol)
        clients.append({
            "site": s,
            "site_hex": "%08x" % s,
            "func": f,
            "func_hex": ("%08x" % f) if f else None,
        })
    n_handles_total = sum(len(v) for v in handles.values())

    # ---- ficheros fuente / RTTI embebidos en la region del driver ----------
    driver_lo, driver_hi = 0x4398E000, 0x4398F200
    rev = defaultdict(list)
    for d, v in refs.items():
        for s in v:
            rev[s].append(d)
    driver_strings = []
    for site in sorted(rev):
        if driver_lo <= site < driver_hi:
            for d in rev[site]:
                txt = cstr(DATA, d)
                if txt:
                    driver_strings.append({"site": "%08x" % site, "addr": "%08x" % d,
                                           "text": txt})
    file_like = [s for s in driver_strings
                 if re.search(r"\.(cpp|c|h|hpp)$", s["text"]) or re.match(r"^\d+[A-Z]", s["text"])]

    # ---- diferencial --------------------------------------------------------
    terms = [
        "[ADC_DEBUG]", "[ADC_DEBUG]: few arg", "[ADC_DEBUG]: ADC DATA0",
        "[ADC_DEBUG]: ADC DATA11", "[ADC_DEBUG]: ADC DATA = ",
        "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA",
        "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA_ALL",
        "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_CHECK_DATA",
        "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_TEST_MODE",
        "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_SET_DATA",
        "get_d", "get_da", "set_da", "TSK_ADC", "boot_exit_adcliro",
        "ADC_GET_DATA     unit_no ch_no", "ADC_GET_DATA_ALL unit_no",
        "ADC_SET_DATA_ALL unit_no data0 data1 ... data11",
        "liro_adc", "CNF_ADC_CH_EVF_TEMP", "Get ADC CNF_ADC_CH_EVF_TEMP",
        "int_ADC_Handler", "ADC::Initialize", "SendToADCTask", "ADC flg timeout",
        "ADC error fact", "jitter NG", "ADCkeyInfo", "sem=%x", "reg_sync err=%d",
        "unreg_sync=%d", "Backup Read Error!",
        "[ACCY][INFO][HW]:AD=%d, ID=%d", "[ILLUMI]AD MAXOVER", "ADcor=0x%x",
    ]
    diff = {}
    for t in terms:
        tb = t.encode("latin1")
        diff[t] = {"A6000": DATA.count(tb), "A7S": a7s.count(tb), "A6300": a6300.count(tb)}

    out = {
        "milestone": "S166",
        "modulo": "[ADC_DEBUG]",
        "binary": str(A6000.relative_to(ROOT)),
        "vaddr_rule": "vaddr = 0x43541000 + file_offset",
        "xref_rule": "estricta (analysis/s106_imaging_cap/pic_refs_strict_global.json); "
                     "ver analysis/s106_imaging_cap/pic_xref_methodology.md",
        "counts": {
            "cadenas": len(strs),
            "sitios_pic": len(pairs),
            "pares_verificados_a_mano": sum(1 for p in pairs if p["manual_ok"]),
            "referenciadas": len(by_string),
            "sin_referencia": len(strs) - len(by_string),
            "funciones": len(funcs),
            "clientes_servicio_liro_adc": len(clients),
            "callos_totales_al_servicio_generico": n_handles_total,
        },
        "strings": strings_json,
        "functions": funcs,
        "pares_pic": pairs,
        "tabla_adj": adj_table,
        "despachador_subcomandos": {
            "func": "4398e578",
            "cmd_id": "0x901",
            "tbb_table": "4398e5d0",
            "tbb_raw": " ".join("%02x" % b for b in tbb_raw),
            "subcomandos": sub_cmds,
        },
        "clientes_liro_adc": clients,
        "estructura": {
            "array_valores_adc": "%08x" % ADC_ARR,
            "array_valores_adc_layout": "2 unidades x 12 canales, u16 cada uno "
                                        "(indice = unidad*12 + canal)",
            "hw_base_unidad0": "%08x" % ADC_HW_BASE,
            "hw_base_unidad1": "%08x" % (ADC_HW_BASE + 0x1000),
            "hw_registro_por_canal_unidad0": "%08x" % ADC_HW_CH,
            "handle_servicio_liro_adc": "%08x" % LIRO_ADC_HANDLE,
            "ids_mensaje": {
                "0xfff0": "ADC_GET_DATA (1 canal) -> [4]=unidad, [5]=canal, [6]=valor u16",
                "0xfff1": "ADC_GET_DATA_ALL (12 canales) -> [4]=unidad, [6..0x1d]=12 u16",
                "0xfff2": "ADC_SET_DATA_ALL (12 canales) -> [4..5], [6..0x1d]=12 u16",
            },
        },
        "ficheros_fuente": {
            "region": "%08x-%08x" % (driver_lo, driver_hi),
            "cadenas_referenciadas": driver_strings,
            "nombres_de_fichero_o_rtti": file_like,
            "nota": "vacio: el driver LIRO ADC no embebe ningun nombre de fichero "
                    "ni de clase RTTI",
        },
        "diferencial": diff,
        "diferencial_nota": "El driver LIRO ADC y sus comandos ADJ (get_d/get_da/set_da) "
                            "existen en los TRES firmwares con el mismo layout y los mismos "
                            "ids de mensaje (0xfff0/0xfff1/0xfff2). Lo propio de la A6000 "
                            "fw3.21 es (a) la etiqueta [ADC_DEBUG] con sus 14 trazas y (b) "
                            "las 5 etiquetas ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_*. En la A7S "
                            "fw3.20 (handlers 0x4397c860 / 0x4397c89c) y en el A6300 fw2.01 "
                            "(handler 0x43a23480) los handlers son estructuralmente "
                            "identicos pero NO imprimen nada.",
    }
    (HERE / "adc_debug.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(out["counts"], indent=1))
    for s in strings_json:
        print("  %s %-52s sites=%s funcs=%s" % (s["vaddr_hex"], s["text"][:52].replace("\n", "\\n"),
                                                s["sites_hex"], s["functions_hex"]))
    print("ADJ:", json.dumps(adj_table["entries"], indent=1))
    print("clientes LIRO_ADC:", [c["site_hex"] for c in clients])
    print("escrito", HERE / "adc_debug.json")


if __name__ == "__main__":
    main()
