#!/usr/bin/env python3
"""S132 — el módulo `[CLK_CTRL]` (66 trazas) de la fw3.21 de la A6000.

Sólo análisis de bytes. No ejecuta firmware ni usa REA/Ghidra.

Salida: analysis/s132_clk_ctrl/clk_ctrl.json

Convención: vaddr = 0x43541000 + file_offset (verificada en S106).

Regla de referencias: **estricta** (canónica del repo,
analysis/s106_imaging_cap/scan_pic_refs_strict.py).  El mapa global ya existe
en analysis/s106_imaging_cap/pic_refs_strict_global.json; aquí sólo se consulta.
"""
import bisect
import json
import os
import re
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
GLOBAL_REFS = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))

U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

# emisores de traza del módulo (llamadas `bl` a las que se pasa el formato)
PRINTERS = (0x4359f690, 0x435a0c68, 0x4359ec38)

# ---------------------------------------------------------------- sub-bloques
SUBBLOCKS = [
    ("DDL_CALL", lambda t: t.startswith("[CLK_CTRL]: Call:ddl_clkctrl_")),
    ("STATE", lambda t: t.startswith("[CLK_CTRL]: State:")),
    ("LOCK", lambda t: "lock_sync_signal subsystem" in t
                     or "unlock_sync_signal subsystem" in t),
    ("TASK", lambda t: "Tsk ClkCtrl Initial" in t or "Main routine start" in t),
    ("CHANGE_CLK", lambda t: ("CHANGE_CLK" in t or "ClkChgExec" in t
                              or "DelayChgExec" in t or "STATE_CHANGE_CLK" in t
                              or "change_vfc" in t
                              or "tsk state = %d(%d:NORMAL" in t)),
    ("SUBSYS_OPEN_CLOSE", lambda t: ("subsytem" in t or "Busy!!" in t
                                     or "request open" in t)),
    ("VPH_HTP", lambda t: ("vph stat" in t or "subVFC" in t or "10Count" in t
                           or "Send HTP" in t or "Now:0x" in t)),
    ("MSG_MASTER_SLAVE", lambda t: ("Message from Master" in t
                                    or "Message to Slave" in t
                                    or "targetVfc" in t or "m_vfc" in t
                                    or "SndMsgPublic" in t
                                    or "unknown message" in t)),
    ("OSAL_ERR", lambda t: ("osal" in t or "OSAL_SEM_ERR" in t)),
    ("SET_DELAY_SYNC", lambda t: ("set sync signal" in t
                                  or "set sysv delay subsystem" in t
                                  or "CLKCTRL_ERR_BUSY" in t
                                  or "Delay is no change" in t
                                  or "MAX OVER" in t
                                  or "State Error" in t
                                  or "clk_now=%d, ret=%d" in t)),
]


def classify(text):
    for name, fn in SUBBLOCKS:
        if fn(text):
            return name
    return "OTROS"


# ---------------------------------------------------------------- utilidades
def prologues(data, lo, hi):
    """Prólogos de función Thumb: `push {..,lr}` (16 bits) o `push.w` (32)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = U16(data, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def _disasm(data, lo, hi):
    """[(addr, mnemonic, op_str)] con capstone (Thumb)."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    off = lo - BASE
    return [(i.address, i.mnemonic, i.op_str)
            for i in md.disasm(data[off:off + (hi - lo)], lo)]


_MOVS = re.compile(r"^r(\d+)$")
_IMM = re.compile(r"^r(\d+), #(0x[0-9a-f]+|\d+)$")


_DEST = re.compile(r"^r(\d+)(?:,|\s|$)")
_WRITERS = ("movs", "mov", "movw", "mov.w", "add", "adds", "sub", "subs",
            "ldr", "ldrb", "ldrh", "ldr.w", "and", "ands", "orr", "eor",
            "uxtb", "uxth", "mul", "mvn", "rsb", "rsbs", "lsl", "lsls",
            "lsr", "lsrs", "bic", "rev", "ror")


def line_arg(data, site, func_start=None, n_specs=None):
    """Valor del argumento `L=%d` de una traza: el inmediato almacenado en el
    hueco de pila más alto justo antes de la llamada al emisor de traza.

    Se evalúa hacia adelante desde el prólogo de la función para no arrastrar
    valores de registro de otra función.
    """
    n_specs = n_specs or {}
    lo = func_start if func_start else site - 0x60
    ins = _disasm(data, lo, site + 0x40)
    idx = next((k for k, (a, m, o) in enumerate(ins) if a == site), None)
    if idx is None:
        return None
    call = None
    for k in range(idx, len(ins)):
        a, m, o = ins[k]
        if m == "bl" and o.startswith("#0x"):
            if int(o[1:], 16) in PRINTERS:
                call = k
                break
    if call is None:
        return None
    reg_val = {}
    stack = {}
    for k in range(0, call):
        a, m, o = ins[k]
        if m == "str" and o.startswith("r") and "[sp" in o:
            rm = re.match(r"^r(\d+), \[sp(?:,\s*#(0x[0-9a-f]+|\d+))?\]", o)
            if rm:
                reg = int(rm.group(1))
                off = int(rm.group(2), 0) if rm.group(2) else 0
                if reg in reg_val:
                    stack[off] = reg_val[reg]
            continue
        if m.startswith("stm") and "[sp" in o and "{" in o:
            rm = re.match(r"^stm\w* sp, \{(.*)\}$", o)
            if rm:
                regs = [x.strip() for x in rm.group(1).split(",")]
                for j, rg in enumerate(regs):
                    rn = re.match(r"^r(\d+)$", rg)
                    if rn and int(rn.group(1)) in reg_val:
                        stack[4 * j] = reg_val[int(rn.group(1))]
            continue
        dm = _DEST.match(o)
        if dm and m.split(".")[0] in _WRITERS:
            reg = int(dm.group(1))
            mm = _IMM.match(o)
            if mm:
                reg_val[reg] = int(mm.group(2), 0)
            else:
                reg_val.pop(reg, None)
    if not stack:
        return None
    # el argumento `L=%d` es el último vararg: está en el hueco de pila
    # 4*(n_args-1), donde n_args = número de conversiones del formato
    n = n_specs.get(site, 0)
    if n:
        return stack.get(4 * (n - 1))
    return stack[max(stack)]


def main():
    data = open(BIN, "rb").read()
    refs = json.load(open(GLOBAL_REFS))
    a7s = open(A7S, "rb").read()
    a6300 = open(A6300, "rb").read()

    # ---------------------------------------------------------- cadenas
    strs = []
    for m in re.finditer(rb"\[CLK_CTRL\][\x20-\x7e]*", data):
        t = m.group().decode("latin1")
        strs.append({
            "vaddr": hex(BASE + m.start()),
            "offset": hex(m.start()),
            "text": t,
            "nucleo": t[len("[CLK_CTRL]: "):] if t.startswith("[CLK_CTRL]: ") else t,
            "subbloque": classify(t),
        })

    # ---------------------------------------------------------- referencias
    starts = prologues(data, BASE, BASE + len(data))
    for s in strs:
        a = int(s["vaddr"], 16)
        sites = refs.get(s["vaddr"], [])
        s["n_sitios"] = len(sites)
        s["sitios"] = [hex(x) for x in sorted(sites)]
        funcs = []
        for x in sites:
            i = bisect.bisect_right(starts, x) - 1
            funcs.append(hex(starts[i]) if i >= 0 else None)
        s["funciones"] = sorted(set(f for f in funcs if f))
        if re.search(r"L\s*=\s*%d", s["text"]):
            vals = []
            nsp = {}
            for x in sorted(sites):
                nsp[x] = len(re.findall(r"%[-+ #0-9.]*[a-zA-Z]", s["text"]))
            for x in sorted(sites):
                i = bisect.bisect_right(starts, x) - 1
                fs = starts[i] if i >= 0 else None
                vals.append(line_arg(data, x, fs, nsp))
            vals = [v for v in vals if v is not None]
            s["L"] = sorted(set(vals))
        else:
            s["L"] = []

    # ---------------------------------------------------------- funciones
    by_func = {}
    for s in strs:
        for f in s["funciones"]:
            by_func.setdefault(f, []).append(s["vaddr"])
    funcs = []
    for f in sorted(by_func, key=lambda x: int(x, 16)):
        funcs.append({
            "func": f,
            "n_cadenas": len(by_func[f]),
            "cadenas": sorted(by_func[f]),
        })

    # ---------------------------------------------------------- diferencial
    def core(t):
        return t[len("[CLK_CTRL]: "):].encode("latin1")

    n7 = n6 = 0
    for s in strs:
        c = core(s["text"])
        s["en_a7s"] = c in a7s
        s["en_a6300"] = c in a6300
        n7 += s["en_a7s"]
        n6 += s["en_a6300"]

    # API DDL: tabla de nombres "N)ddl_clkctrl_..." (A6000 y otros firmwares)
    api_re = re.compile(r"^(\d+)\)(.*)$")

    def api_table(buf):
        """Tabla de entradas numeradas "N)nombre" que siguen a "CALL CB3"."""
        i = buf.find(b"CALL CB3")
        if i < 0:
            return []
        blk = buf[i:i + 0x400]
        out = []
        for tok in blk.split(b"\x00"):
            m = api_re.match(tok.decode("latin1"))
            if not m:
                continue
            n = int(m.group(1))
            txt = m.group(2).strip()
            if out and n <= out[-1][0]:
                break
            out.append((n, txt))
        return out

    api6 = api_table(data)
    api7 = api_table(a7s)
    api6300 = api_table(a6300)

    # mapa id de API -> función implementadora (verificado desensamblando
    # el despachador DDL de 0x435a0880)
    API_IMPL = {
        0: ("ddl_clkctrl_open_clk", 0x4359f174),
        1: ("ddl_clkctrl_close_clk", 0x4359f12c),
        2: ("ddl_clkctrl_open_dly", 0x4359f0e4),
        3: ("ddl_clkctrl_close_dly", 0x4359f09c),
        4: ("ddl_clkctrl_set_sync_signal", 0x4359ef88),
        5: ("ddl_clkctrl_set_sysv_delay", 0x4359ef2c),
        6: ("ddl_clkctrl_lock_sync_signal", 0x4359eed0),
        7: ("ddl_clkctrl_unlock_sync_signal", 0x4359ee78),
        8: ("ddl_clkctrl_set_sysv_initial_delay", 0x4359f048),
        9: ("ddl_clkctrl_set_sync_initial_signal", 0x4359f000),
        10: ("ddl_clkctrl_printf_info", 0x43a486b6),
        11: ("set_sync_signal + bucle de cambio de retardo (0x4359ecc0)", None),
        12: ("set_sync_signal + bucle de cambio de retardo (0x4359ecc0)", None),
        13: ("set_sync_signal + lock_sync_signal", None),
        14: ("lock_sync_signal", None),
    }

    # subsistema (id de reloj) que usa cada consumidor de la API, con su
    # fichero/funcionalidad (verificado desensamblando los llamadores)
    CONSUMERS = [
        {"func": "0x4378dfde", "subsistema": "0x03", "modulo": "CAMERA_MAIN_SYNC",
         "nota": "abre/cierra el reloj, bloquea (lock) y desbloquea la señal de sync "
                "alrededor de las secuencias de exposición/lectura"},
        {"func": "0x4368b3e4", "subsistema": "0x0a", "modulo": "VDF",
         "nota": "VdfDisplayCmdSetPanelOut (VdfDisplayCmdSetPanelOut.cpp)"},
        {"func": "0x436afba0", "subsistema": "0x0d", "modulo": "VEF",
         "nota": "módulo de efectos del finder"},
        {"func": "0x4366bd38", "subsistema": "0xc2", "modulo": "SYSV / TP_R",
         "nota": "sincronización vertical del sistema"},
        {"func": "0x4362840e", "subsistema": "0x57", "modulo": "MC (shell)",
         "nota": "comando de depuración: 24P/25P/30P/50I/50P/60I/60P"},
        {"func": "0x43628e98", "subsistema": "0x57", "modulo": "MC",
         "nota": "McMsgAvscDec::ClockChange(FRAME_RATE) (mcMsgAvscDec.cpp)"},
        {"func": "0x43617f22", "subsistema": "0x57", "modulo": "MC",
         "nota": "comandos de shell clk_open / clk_chg / clk_close"},
        {"func": "0x43a79c60", "subsistema": "0x57", "modulo": "MC",
         "nota": "McUtilMulti"},
        {"func": "0x43622d82", "subsistema": "dinámico (ldrh [r0,#4])", "modulo": "MC",
         "nota": "McAvcDecCmdParamCheck::CheckActDecParam1st "
                 "(seqctrl/mcAvcDecCmdParamCheck.cpp)"},
        {"func": "0x43a4928a", "subsistema": "0x10b", "modulo": "(no identificado)",
         "nota": "id de subsistema 0x10b"},
        {"func": "0x43a84942", "subsistema": "dinámico (ldrh [r0,#4])",
         "modulo": "(no identificado)", "nota": ""},
        {"func": "0x437947cc", "subsistema": "-", "modulo": "CAMERA_MAIN",
         "nota": "init_cam_clkctrl (init_cam_SetCamParam_main.cpp): fija "
                 "CLKTYPE y sysv_delay inicial"},
        {"func": "0x43ae8c66", "subsistema": "-", "modulo": "(no identificado)",
         "nota": "único consumidor de ddl_clkctrl_get_clk_chg_enable"},
    ]

    # tokens comparados entre firmwares
    tokens = {}
    for tok in (b"[CLK_CTRL]", b"ddl_clkctrl_", b"ClkCtrl", b"CLKTYPE",
                b"SYSV_DELAY", b"init_cam_clkctrl", b"targetVfc",
                b"STATE_CHANGE_CLK", b"ClkChgExec", b"DelayChgExec",
                b"change_vfc", b"subVFC", b"[CLKCTRL]"):
        tokens[tok.decode("latin1")] = {
            "a6000": len(re.findall(re.escape(tok), data)),
            "a7s": len(re.findall(re.escape(tok), a7s)),
            "a6300": len(re.findall(re.escape(tok), a6300)),
        }

    out = {
        "milestone": "S132",
        "modulo": "[CLK_CTRL]",
        "base": hex(BASE),
        "bin": BIN,
        "regla_referencias": "estricta (scan_pic_refs_strict.py) sobre el mapa global",
        "conteo": {
            "cadenas": len(strs),
            "cadenas_referenciadas": sum(1 for s in strs if s["n_sitios"] > 0),
            "cadenas_sin_referencia": sum(1 for s in strs if s["n_sitios"] == 0),
            "sitios": sum(s["n_sitios"] for s in strs),
            "funciones": len(funcs),
        },
        "subbloques": {},
        "cadenas": strs,
        "funciones": funcs,
        "api_ddl_despachador": "0x435a0880 (CALL CB3)",
        "api_ddl_mapa": {str(k): {"nombre": v[0], "impl": hex(v[1]) if v[1] else None}
                         for k, v in API_IMPL.items()},
        "consumidores": CONSUMERS,
        "diferencial": {
            "nucleo_en_a7s": n7,
            "nucleo_en_a6300": n6,
            "cadenas_totales": len(strs),
            "api_ddl_a6000": api6,
            "api_ddl_a7s": api7,
            "api_ddl_a6300": api6300,
            "tokens": tokens,
        },
    }
    for s in strs:
        out["subbloques"].setdefault(s["subbloque"], []).append(s["vaddr"])
    out["conteo_subbloques"] = {k: len(v) for k, v in sorted(out["subbloques"].items())}

    dest = os.path.join(HERE, "clk_ctrl.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("cadenas:", len(strs), "sitios:", out["conteo"]["sitios"],
          "funciones:", len(funcs))
    print("referenciadas:", out["conteo"]["cadenas_referenciadas"],
          "sin referencia:", out["conteo"]["cadenas_sin_referencia"])
    print("subbloques:", out["conteo_subbloques"])
    print("diferencial A7S/A6300 (núcleo presente):", n7, n6)
    print("escrito", dest)


if __name__ == "__main__":
    main()
