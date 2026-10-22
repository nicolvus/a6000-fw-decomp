#!/usr/bin/env python3
"""S139 — el módulo `[ENCSEQCTRL]` (46 trazas) del firmware A6000 fw3.21.

Qué hace:
  1. extrae las 46 cadenas que contienen `[ENCSEQCTRL]` (con su inicio real de cadena);
  2. clasifica los sub-bloques ([O/U Crank], [state], [Begin]/[Term], MSGID_*, ...);
  3. toma los sitios PIC de la regla **estricta** ya calculados en
     `analysis/s106_imaging_cap/pic_refs_strict_global.json` (destino → sitios `add rX,pc`);
  4. atribuye cada sitio a su función (prólogo Thumb `push {..,lr}` más cercano por detrás);
  5. calcula los llamadores `bl` directos de cada función (decodificación manual del
     patrón `bl`/`b.w` de 32 bits, como en S137, sin desensamblado lineal);
  6. busca punteros absolutos de 4 B a las cadenas;
  7. localiza los nombres de clase y los ficheros fuente del subsistema `McAvc*`;
  8. compara texto a texto con la A7S fw3.20 y el A6300 fw2.01.

Salida: analysis/s139_encseqctrl/encseqctrl_raw.json
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
A63 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GLOBAL = os.path.join(ROOT, "analysis", "s106_imaging_cap", "pic_refs_strict_global.json")

CODE_LO, CODE_HI = 0x43541000, 0x43A00000
TOKEN = "[ENCSEQCTRL]"

# Nombres de clase y ficheros fuente del subsistema (del bloque RTTI de la zona).
CLASSES = [
    "McAvcEncSeqCtrl", "McAvcEncVideoSeqCtrlIf", "McAvcEncVideoSeqCtrlStateBase",
    "McAvcEncVideoSeqCtrlBase", "McAvcEncVideo24PSeqCtrl", "McAvcEncVideo30P25PSeqCtrl",
    "McAvcEncVideo60I50ISeqCtrl", "McAvcEncVideo60P50PSeqCtrl", "McAvcEncSeqCtrlParam",
    "McAvcEncAudioSeqCtrlIf", "McAvcEncAudioSeqCtrlState", "McAvcEncAudioSeqCtrlStateOuCrank",
    "McAvcEncAudioSeqCtrlStateEncoding", "McAvcEncAudioSeqCtrlStateNotInit",
    "McAvcEncAudioSeqCtrlStateOuCrankEncoding", "McAvcEncAudioSeqCtrlStateOuCrankReady",
    "McAvcEncAudioSeqCtrlStateReady", "McAvcEncAudioSeqCtrlStateStub",
    "McAvcEncAudioSeqCtrlStateWaitClose", "McAvcEncAudioSeqCtrlStateWaitEnc",
    "McAvcEncAudioSeqCtrlStateWaitOpen", "McAvcEncAudioSeqCtrlStateWaitReady",
    "McAvcEncModeMgr", "McAvcEncModeReady", "McAvcEncModeEncErr", "McAvcEncModeEncMovie",
    "McAvcEncModeEncStill", "McAvcEncModeInActive", "McAvcEncMode",
    "McAvcEncVfm", "McAvcEncLpcmBufIf",
]
SOURCES = [
    "seqCtrl/mcAvcEncSeqCtrl.cpp", "mcAvcEncModeMgr.cpp", "mcAvcEncModeReady.cpp",
    "mcAvcEncModeEncErr.cpp", "seqCtrl/audio/mcAvcEncAudioSeqCtrlState.cpp",
    "seqCtrl/audio/mcAvcEncAudioSeqCtrlStateNotInit.cpp",
    "seqCtrl/audio/mcAvcEncAudioSeqCtrlStateOuCrankEncoding.cpp",
    "seqCtrl/audio/mcAvcEncAudioSeqCtrlStateOuCrankReady.cpp",
    "seqctrl/mcAvcDecSeqCtrl.cpp",
]


def strings_with(b, token):
    """[(inicio_cadena, offset_del_token, texto)] para cada ocurrencia de `token`."""
    out = []
    for m in re.finditer(re.escape(token.encode()), b):
        s = m.start()
        while s > 0 and b[s - 1] != 0 and 32 <= b[s - 1] < 127:
            s -= 1
        e = b.find(b"\0", m.start())
        out.append((BASE + s, BASE + m.start(), b[s:e].decode("latin1")))
    return out


def prologues(b, lo, hi):
    """Direcciones de prólogos de función Thumb (`push {..,lr}`)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = struct.unpack_from("<H", b, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", b, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def callers(b, targets):
    """{destino: [sitios]} con decodificación manual del patrón `bl`/`b.w` de 32 bits."""
    out = {t: [] for t in targets}
    tset = set(targets)
    for a in range(CODE_LO, CODE_HI - 4, 2):
        h1 = struct.unpack_from("<H", b, a - BASE)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", b, a - BASE + 2)[0]
        if (h2 & 0xD000) not in (0x9000, 0xD000):
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        tgt = (a + 4 + imm) & 0xFFFFFFFF
        if tgt in tset:
            out[tgt].append(a)
    return out


def abs_pointers(b, va):
    pat = struct.pack("<I", va)
    return [BASE + m.start() for m in re.finditer(re.escape(pat), b)]


def sub_block(text):
    """Sub-bloque funcional de una traza [ENCSEQCTRL] (mutuamente excluyente)."""
    t = text[len(TOKEN):]
    if "[O/U Crank]" in t or "OuCrank" in t:
        return "O_U_CRANK"
    if "[state]" in t or "State:0x%x->0x%x" in t:
        return "STATE"
    if "m_beginEncCompTime" in t:
        return "TIMING_WARNING"
    if "Chip Mode" in t:
        return "CHIP_MODE"
    if "syshsCnt" in t or "HighSpeed" in t:
        return "SYSHS"
    if "PIN SUPPLY" in t or "Pin Supply" in t:
        return "PIN_SUPPLY"
    if "OU StopInfo" in t:
        return "OU_STOP"
    if "abcd[%d]" in t:
        return "FRAME_DEBUG"
    if "ReviseNum" in t:
        return "REVISE_NUM"
    if "termEncodeVfc" in t or "TermEnc TimeInfo" in t:
        return "TERM_VFC"
    if "BeginEnc TimeInfo" in t:
        return "BEGIN_TIMEINFO"
    if "CheckSendFirstRefTimer" in t:
        return "REF_TIMER"
    if "Invalid replyId" in t:
        return "REPLY_ID"
    if "AVSC_CID_MPRNTFY" in t:
        return "SA_CONFIRM"
    if "MSGID_AVC_ENC_VIDEO" in t:
        return "MSGID_COMP"
    if "ProcAvcMsg" in t:
        return "PROCAVCMSG"
    if "semaphore" in t:
        return "SEMAPHORE"
    if "File:%s" in t or "Func:%s()" in t:
        return "LOG_MACRO"
    return "GENERAL"


def fmt_free(text):
    """Texto sin especificadores de formato (para comparar entre firmwares)."""
    return re.sub(r"%[-#0-9.lh]*[a-zA-Z]", "%", text)


def diff(path, a6000_texts, token=TOKEN):
    b = open(os.path.join(ROOT, path), "rb").read()
    tb = token.encode()
    occ = [m.start() for m in re.finditer(re.escape(tb), b)]
    texts = set()
    for m in re.finditer(re.escape(tb), b):
        s = m.start()
        while s > 0 and b[s - 1] != 0 and 32 <= b[s - 1] < 127:
            s -= 1
        e = b.find(b"\0", m.start())
        texts.add(b[s:e].decode("latin1"))
    a = set(a6000_texts)
    return {
        "ocurrencias_token": len(occ),
        "textos": len(texts),
        "comunes": len(a & texts),
        "solo_a6000": sorted(a - texts),
        "solo_modelo": sorted(texts - a),
    }


def main():
    b = open(os.path.join(ROOT, BIN), "rb").read()
    g = json.load(open(GLOBAL))

    occ = strings_with(b, TOKEN)
    starts = sorted({s for s, _, _ in occ})
    strs = []
    for s in starts:
        text = [t for ss, _, t in occ if ss == s][0]
        strs.append({"vaddr": hex(s), "sub_bloque": sub_block(text), "texto": text})

    sites = {hex(s): [hex(x) for x in g.get(hex(s), [])] for s in starts}

    P = prologues(b, CODE_LO, CODE_HI)

    def fstart(site):
        i = bisect.bisect_right(P, site) - 1
        return P[i] if i >= 0 else None

    funcs = {}
    for s in starts:
        for x in g.get(hex(s), []):
            f = fstart(x)
            e = funcs.setdefault(hex(f), {"sitios": [], "cadenas": [], "detalle": []})
            e["sitios"].append(hex(x))
            e["cadenas"].append(hex(s))
            e["detalle"].append({"sitio": hex(x), "cadena": hex(s),
                                 "texto": [t for ss, _, t in occ if ss == s][0]})
    for v in funcs.values():
        v["sitios"] = sorted(set(v["sitios"]), key=lambda x: int(x, 16))
        v["cadenas"] = sorted(set(v["cadenas"]), key=lambda x: int(x, 16))
        v["detalle"] = sorted(v["detalle"], key=lambda d: int(d["sitio"], 16))

    tgt = [int(k, 16) for k in funcs]
    cm = callers(b, tgt)
    for k, v in funcs.items():
        v["llamadores_bl"] = [hex(x) for x in cm[int(k, 16)]]

    abs_str = {}
    for s in starts:
        p = abs_pointers(b, s)
        if p:
            abs_str[hex(s)] = [hex(x) for x in p]

    # nombres de clase y ficheros fuente del subsistema
    rtti = {}
    for name in CLASSES:
        offs = [m.start() for m in re.finditer(re.escape(name.encode()), b)]
        if offs:
            rtti[name] = [hex(BASE + o) for o in offs[:6]]
    sources = {}
    for name in SOURCES:
        o = b.find(name.encode())
        if o >= 0:
            sources[name] = hex(BASE + o)

    texts = [t for _, _, t in occ]
    out = {
        "token": TOKEN,
        "ocurrencias": len(occ),
        "cadenas": strs,
        "sitios": sites,
        "funciones": funcs,
        "punteros_4B_a_cadenas": abs_str,
        "totales": {
            "cadenas": len(starts),
            "referenciadas": sum(1 for s in starts if g.get(hex(s))),
            "sin_referencia": [hex(s) for s in starts if not g.get(hex(s))],
            "sitios": sum(len(v) for v in sites.values()),
            "funciones": len(funcs),
        },
        "sub_bloques": {},
        "rtti_clases": rtti,
        "ficheros_fuente": sources,
        "diferencial": {
            "A7S_fw320": diff(A7S, texts),
            "A6300_fw201": diff(A63, texts),
        },
    }
    for s in strs:
        out["sub_bloques"].setdefault(s["sub_bloque"], []).append(s["vaddr"])

    with open(os.path.join(HERE, "encseqctrl_raw.json"), "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(out["totales"], ensure_ascii=False, indent=1))
    print("sub_bloques:", {k: len(v) for k, v in sorted(out["sub_bloques"].items())})
    for k, v in out["diferencial"].items():
        print(k, "oc:", v["ocurrencias_token"], "textos:", v["textos"],
              "comunes:", v["comunes"], "solo_a6000:", len(v["solo_a6000"]),
              "solo_modelo:", len(v["solo_modelo"]))


if __name__ == "__main__":
    main()
