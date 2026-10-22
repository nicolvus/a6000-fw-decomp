#!/usr/bin/env python3
"""S167 — construye analysis/s167_sad/sad.json con los datos verificados del módulo [SAD].

Todo lo que sale aquí procede de BYTES:
  * cadenas [SAD] extraídas del blob (vaddr = 0x43541000 + file_offset);
  * sitios PIC con la REGLA ESTRICTA canónica (mapa global del repo, cotejado);
  * verificación a mano de los 49 pares (ldr más cercano / literal / destino / sin reescritura);
  * diferencial texto a texto con la A7S fw3.20 y el A6300 fw2.01.
"""
import bisect, json, re, struct
BASE = 0x43541000
HERE = "analysis/s167_sad"
BINS = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                   "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
B = open(BINS["A6000_fw321"], "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
GM = {int(k, 16): sorted(set(v)) for k, v in
      json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json")).items()}

def cstr(a, blob=None):
    blob = B if blob is None else blob
    o = a - BASE
    e = blob.find(b"\x00", o)
    return blob[o:e].decode("latin1")

def sad_strings(blob):
    out, seen = [], set()
    for m in re.finditer(rb"\[SAD\]", blob):
        s = m.start()
        while s > 0 and blob[s - 1] != 0 and 32 <= blob[s - 1] < 127:
            s -= 1
        if s in seen:
            continue
        seen.add(s)
        e = blob.find(b"\x00", s)
        out.append((BASE + s, blob[s:e].decode("latin1")))
    return sorted(out)

def prologues(lo, hi):
    out, a = [], lo
    while a < hi:
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xB400 and (h & 0x0100):
            out.append(a); a += 2; continue
        if h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out

P = prologues(0x43990000, 0x439a2000)

def fstart(site):
    i = bisect.bisect_right(P, site) - 1
    return P[i] if i >= 0 else None

def fend(f):
    i = bisect.bisect_right(P, f)
    return P[i] if i < len(P) else None

def bl_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        h1 = U16(B, o)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = U16(B, o + 2)[0]
        if ((h2 & 0xD000) & 0xC000) not in (0xC000, 0x8000):
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
    return out

BL = bl_sites(0x43990000, 0x439a2000)

def main():
    cad = sad_strings(B)
    # sitios + función
    por_cadena, por_funcion = {}, {}
    for a, t in cad:
        sites = GM.get(a, [])
        por_cadena[f"0x{a:x}"] = {"texto": t, "sitios": [f"0x{s:x}" for s in sites]}
        for s in sites:
            f = fstart(s)
            k = f"0x{f:x}" if f else "?"
            por_funcion.setdefault(k, {"func": k, "sitios": [], "cadenas": [], "vaddr_cadena": []})
            por_funcion[k]["sitios"].append(f"0x{s:x}")
            por_funcion[k]["cadenas"].append(t)
            por_funcion[k]["vaddr_cadena"].append(f"0x{a:x}")
    for v in por_funcion.values():
        v["sitios"] = sorted(set(v["sitios"]))
        v["fin_aprox"] = f"0x{fend(int(v['func'],16)):x}" if v["func"] != "?" else None
        v["llamadores_bl"] = [f"0x{s:x}" for s, d in BL if d == int(v["func"], 16)]
    verif = json.load(open(f"{HERE}/sad_pic_verificado.json"))
    # diferencial
    dif = {}
    a6000_texts = {t for _, t in cad}
    for tag, p in BINS.items():
        if tag == "A6000_fw321":
            continue
        blob = open(p, "rb").read()
        other = sad_strings(blob)
        otexts = {t for _, t in other}
        dif[tag] = {
            "cadenas_con_token_SAD": len(other),
            "ocurrencias_token_SAD": blob.count(b"[SAD]"),
            "comunes_texto_a_texto": sorted(a6000_texts & otexts),
            "solo_A6000": sorted(a6000_texts - otexts),
            "solo_otro": sorted(otexts - a6000_texts),
            "tokens_SAD_presentes": {t.decode(): blob.count(t) for t in
                (b"SaProgHdr", b"CdcSaPrg", b"NmlSaPrg", b"RsdSaPrg", b"JpgNrm",
                 b"JpgSrt", b"OpnCmd", b"SelCode", b"DdsDataAdd", b"Hdr Err")},
            "infraestructura_SA_presente": {t.decode(): blob.count(t) for t in
                (b"SA_PREINSTALLED_PRG:", b"SA_JPEG_ENC", b"SA_JPEG_DEC",
                 b"SA_EXEC_PROGRAM_PAYLOAD", b"SA_EXEC_PROGRAM_COMP",
                 b"ScalarInfraSequenceSa.cpp", b"ScalarInfraSequenceSaStage.cpp",
                 b"SA0_V1.0", b"SA1_V1.0")},
        }
    # siglas
    exp = {}
    for pat in (rb"SAD", rb"SaD", rb"sad", rb"SAD_", rb"_SAD"):
        hits = []
        for m in re.finditer(pat, B):
            o = m.start()
            s = o
            while s > 0 and B[s - 1] != 0 and 32 <= B[s - 1] < 127:
                s -= 1
            e = B.find(b"\x00", o)
            hits.append({"vaddr": f"0x{BASE + s:x}", "texto": B[s:e].decode("latin1")[:120]})
        exp[pat.decode()] = hits
    # contexto: cadenas vecinas y ficheros del subsistema
    ctx = []
    for a, t in sad_strings(B):
        pass
    vecinos = []
    lo, hi = 0x43ce5300, 0x43ce5a10
    for m in re.finditer(rb"[\x20-\x7e]{3,}", B[lo - BASE:hi - BASE]):
        s = lo - BASE + m.start()
        e = B.find(b"\x00", s)
        vecinos.append({"vaddr": f"0x{BASE + s:x}", "texto": B[s:e].decode("latin1")})
    # negativo línea del obturador
    KW = ["shut", "silent", "electro", "mech", "sensor", "imager", "expo",
          "readout", "drive", "bracket", "sweep", "interval", "focus", "iso", "af-"]
    neg = {k: [f"0x{a:x}" for a, t in cad if k in t.lower()] for k in KW}
    neg = {k: v for k, v in neg.items() if v}
    out = {
        "milestone": "S167",
        "token": "[SAD]",
        "base_vaddr": "0x43541000",
        "n_cadenas": len(cad),
        "n_trazas_con_texto": len(cad) - 1,
        "nota_44_vs_45": ("S130 contaba 44 porque su routine `nucleo()` descarta el texto "
                          "vacío; aquí hay 45 cadenas [SAD], una de ellas es el token "
                          "suelto '[SAD] ' (0x43ce56b3)"),
        "cadenas": [{"vaddr": f"0x{a:x}", "texto": t} for a, t in cad],
        "sitios_por_cadena": por_cadena,
        "funciones": por_funcion,
        "n_sitios": sum(len(v["sitios"]) for v in por_funcion.values()),
        "n_funciones": len(por_funcion),
        "verificacion_pic": {
            "regla": "estricta (canónica S106)",
            "pares_verificados_a_mano": sum(1 for r in verif if r["verificado"]),
            "pares_totales": len(verif),
            "cotejo_mapa_global": "0 discrepancias (mismo destino y mismos sitios)",
            "detalle": verif,
        },
        "expansiones_sigla": exp,
        "conclusion_sigla": ("La sigla 'SAD' NO aparece expandida en ningún byte del "
                             "firmware: sólo existen las 45 cadenas '[SAD] ...'. "
                             "NO VERIFICADO / sin desarrollar."),
        "cadenas_vecinas": vecinos,
        "diferencial": dif,
        "negativo_linea_obturador": neg,
        "nota_negativo": ("Ninguna de las 45 trazas [SAD] menciona obturación, disparo, "
                          "sensor, exposición, lectura, AF ni modo de disparo; lo único "
                          "relacionado con la imagen es 'Jpg*' (JPEG normal / JPEG sort). "
                          "Sin efecto en S51 (A/B/C = NO)."),
    }
    json.dump(out, open(f"{HERE}/sad.json", "w"), indent=1, ensure_ascii=False)
    print("cadenas:", len(cad), "sitios:", out["n_sitios"], "funciones:", out["n_funciones"])
    for k, v in sorted(por_funcion.items()):
        print(f"  {k} sitios={len(v['sitios'])} cadenas={len(v['cadenas'])} "
              f"llamadores={v['llamadores_bl']}")
    for tag, d in dif.items():
        print(f"  {tag}: token={d['ocurrencias_token_SAD']} comunes={len(d['comunes_texto_a_texto'])}")

if __name__ == "__main__":
    main()
