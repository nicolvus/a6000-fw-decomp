"""S167 — verificación INDEPENDIENTE del módulo [SAD] contra los bytes del firmware.

Complementa `tests/test_s167_sad.py`: aquí se rehace, desde cero y sin usar
`analysis/s167_sad/sad.json`, la regla PIC estricta y se comprueban los datos
que el informe `analysis/s167_sad/sad.md` afirma:

  * las 45 cadenas [SAD] y sus direcciones exactas;
  * los 49 sitios de emisión y las 5 funciones emisoras (prólogo Thumb);
  * la verificación a mano de los 49 pares PIC (ldr más cercano, literal del
    pool, destino y ausencia de reescritura del registro);
  * el despachador de 6 subcomandos (tbh) del volcado de estado;
  * la tabla de versiones SA y los programas preinstalados;
  * el diferencial con la A7S fw3.20 y el A6300 fw2.01.

Si una dirección cambia en el firmware, el test falla.
"""
import bisect
import json
import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7S = (ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
GLOBAL_MAP = ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json"

B = BIN.read_bytes()
A7 = A7S.read_bytes()
A63 = A6300.read_bytes()
GM = {int(k, 16): sorted(set(v)) for k, v in json.loads(GLOBAL_MAP.read_text()).items()}


def u16(a):
    return struct.unpack_from("<H", B, a - BASE)[0]


def u32(a):
    return struct.unpack_from("<I", B, a - BASE)[0]


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


def pic_ldr_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        h = u16(a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(a + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= len(B) - 4:
            out.append((a, reg, u32(lit), lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        h = u16(a)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def writes_to_reg(lo, hi, reg):
    out = []
    a = lo
    while a < hi:
        h = u16(a)
        if ((h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg) or \
           ((h & 0xFF7F) == 0xF85F and ((u16(a + 2) >> 12) & 0xF) == reg) or \
           ((h & 0xF800) == 0x6800 and ((h >> 8) & 7) == reg) or \
           ((h & 0xF800) == 0x9800 and ((h >> 8) & 7) == reg) or \
           (0x2000 <= (h & 0xF800) <= 0x3800 and ((h >> 8) & 7) == reg) or \
           ((h & 0xFC00) == 0x4000 and ((h & 7) | ((h >> 4) & 8)) == reg) or \
           ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15 and
            ((((h >> 7) & 1) << 3) | (h & 7)) == reg) or \
           ((h & 0xFE00) == 0x6000 and ((h >> 8) & 7) == reg) or \
           ((h & 0xFE00) == 0x7000 and ((h >> 8) & 7) == reg) or \
           ((h & 0xFE00) == 0x8000 and ((h >> 8) & 7) == reg) or \
           ((h & 0xF800) == 0x5000 and ((h >> 8) & 7) == reg) or \
           ((h & 0xFE00) == 0x5200 and ((h >> 8) & 7) == reg):
            out.append(a)
        a += 2
    return out


class TestS167SadIndependiente(unittest.TestCase):

    # ------------------------------------------------------------- cadenas
    def test_45_cadenas_sad_en_la_a6000(self):
        cad = sad_strings(B)
        self.assertEqual(len(cad), 45)
        self.assertEqual(cad[0][0], 0x43ce546b)
        self.assertEqual(cad[-1][0], 0x43ce59c1)
        # 44 con texto + 1 token suelto
        self.assertEqual(len([t for _, t in cad if t != "[SAD] "]), 44)
        self.assertEqual(cstr(0x43ce56b3), "[SAD] ")

    def test_tres_bloques_en_rodata(self):
        cad = sad_strings(B)
        self.assertEqual(cad[2][0], 0x43ce54a5)
        self.assertEqual(cad[3][0], 0x43ce55bc)
        # hueco de 0x100 bytes entre el bloque A y el B
        self.assertEqual(cad[3][0] - (cad[2][0] + len(cad[2][1]) + 1), 0x100)
        # entre el bloque B y el C hay las 3 cadenas de programa SA
        self.assertEqual(cad[6][0], 0x43ce564c)
        self.assertEqual(cstr(0x43ce561f), "SA_PREINSTALLED_PRG:")
        self.assertEqual(cstr(0x43ce5634), "SA_JPEG_ENC")
        self.assertEqual(cstr(0x43ce5640), "SA_JPEG_DEC")

    def test_tabla_del_driver_SA_intercalada_por_las_trazas_SAD(self):
        """La cabecera de 27 B y la tabla de 25 indices de la tabla del driver SA
        sobreviven intactas en la A6000, pero las 44 cadenas [SAD] se han
        intercalado en dos huecos (por eso el bloque se parte en 3)."""
        cabecera = bytes.fromhex(
            "000101010001010204088383830483838307070707070707070707")
        self.assertEqual(len(cabecera), 27)
        # cabecera IDENTICA en los tres firmware
        self.assertEqual(B[0x43ce5445 - BASE:0x43ce5445 - BASE + 27], cabecera)
        self.assertEqual(A7[0x43cda6ef - BASE:0x43cda6ef - BASE + 27], cabecera)
        self.assertEqual(A63[0x43df89bc - BASE:0x43df89bc - BASE + 27], cabecera)
        # tabla de 25 indices (0x03..0x1b) embebida en un mar de 0x1c: IDENTICA
        seq6 = [x for x in B[0x43ce54bc - BASE:0x43ce55bc - BASE] if x != 0x1C]
        seq7 = [x for x in A7[0x43cda716 - BASE:0x43cda816 - BASE] if x != 0x1C]
        self.assertEqual(seq6, seq7)
        self.assertEqual(seq6, list(range(0x03, 0x1C)))
        # las cadenas [SAD] estan en los dos huecos
        self.assertTrue(cstr(0x43ce546b).startswith("[SAD] "))   # bloque A
        self.assertTrue(cstr(0x43ce55bc).startswith("[SAD] "))   # bloque B
        self.assertTrue(cstr(0x43ce564c).startswith("[SAD] "))   # bloque C
        # y los otros dos firmware no tienen ninguna en ese tramo
        self.assertNotIn(b"[SAD]", A7[0x43cda6ef - BASE:0x43cda81c - BASE])
        self.assertNotIn(b"[SAD]", A63[0x43df89bc - BASE:0x43df8960 - BASE])

    # ------------------------------------------------- sitios y emisores
    def test_49_sitios_en_5_funciones(self):
        cad = sad_strings(B)
        n_sitios = 0
        for a, _ in cad:
            n_sitios += len(GM.get(a, []))
        self.assertEqual(n_sitios, 49)
        prols = []
        a = 0x43990000
        while a < 0x439a2000:
            h = u16(a)
            if (h & 0xFE00) == 0xB400 and (h & 0x0100):
                prols.append(a)
            elif h == 0xE92D and (u16(a + 2) & 0x4000):
                prols.append(a)
            a += 2
        fcount = {}
        for a, _ in cad:
            for s in GM.get(a, []):
                i = bisect.bisect_right(prols, s) - 1
                fcount[prols[i]] = fcount.get(prols[i], 0) + 1
        self.assertEqual(fcount, {0x43998578: 3, 0x4399d464: 1, 0x4399d528: 1,
                                  0x4399d618: 1, 0x439a119c: 43})

    def test_prologos_de_los_emisores(self):
        self.assertEqual(B[0x43998578 - BASE:0x43998578 - BASE + 4].hex(), "30b57b44")
        self.assertEqual(B[0x4399d464 - BASE:0x4399d464 - BASE + 4].hex(), "2de9f04f")
        self.assertEqual(B[0x4399d528 - BASE:0x4399d528 - BASE + 4].hex(), "2de9f04f")
        self.assertEqual(B[0x4399d618 - BASE:0x4399d618 - BASE + 4].hex(), "2de9f043")
        self.assertEqual(B[0x439a119c - BASE:0x439a119c - BASE + 4].hex(), "7fb549f2")

    # ---------------------------------------------- verificación a mano PIC
    def test_49_pares_pic_verificados(self):
        lo, hi = 0x43990000, 0x439a2000
        ldrs = pic_ldr_sites(lo, hi)
        by = {}
        for a, reg, w, lit in ldrs:
            by.setdefault(reg, []).append((a, w, lit))
        for v in by.values():
            v.sort()
        keys = {r: [x[0] for x in v] for r, v in by.items()}
        adds = dict(pic_add_sites(lo, hi))
        n = 0
        for a, _ in sad_strings(B):
            for s in GM.get(a, []):
                reg = adds[s]
                v = by[reg]
                i = bisect.bisect_left(keys[reg], s) - 1
                la, w, lit = v[i]
                self.assertLessEqual(s - la, 4096, f"ventana en {s:#x}")
                self.assertEqual(w, u32(lit), f"literal en {s:#x}")
                self.assertEqual((w + (s + 4)) & 0xFFFFFFFF, a, f"destino en {s:#x}")
                self.assertEqual(writes_to_reg(la + 2, s, reg), [],
                                 f"r{reg} reescrito entre {la:#x} y {s:#x}")
                n += 1
        self.assertEqual(n, 49)

    def test_reimplementacion_del_escaner_estricto_coincide_con_el_repo(self):
        """El PIC estricto reimplementado aquí reproduce el mapa global canónico."""
        lo, hi = 0x43541000, 0x44017000
        ldrs = pic_ldr_sites(lo, hi)
        by = {}
        for a, reg, w, lit in ldrs:
            by.setdefault(reg, []).append((a, w))
        for v in by.values():
            v.sort()
        keys = {r: [x[0] for x in v] for r, v in by.items()}
        starts = set()
        prev = False
        for i, c in enumerate(B):
            cur = 32 <= c < 127
            if cur and not prev:
                starts.add(BASE + i)
            prev = cur
        res = {}
        for s, reg in pic_add_sites(lo, hi):
            v = by.get(reg)
            if not v:
                continue
            ks = keys[reg]
            i = bisect.bisect_left(ks, s) - 1
            if i < 0:
                continue
            la, w = v[i]
            if s - la > 4096:
                continue
            tgt = (w + (s + 4)) & 0xFFFFFFFF
            if tgt in starts:
                res.setdefault(tgt, []).append(s)
        self.assertEqual(len(res), 17525)
        self.assertEqual({k: sorted(set(v)) for k, v in res.items()},
                         {k: sorted(set(v)) for k, v in GM.items()})

    # ------------------------------------------------------ despachador
    def test_despachador_de_6_subcomandos(self):
        self.assertEqual(B[0x439a119e - BASE:0x439a11a2 - BASE].hex(), "49f24853")
        self.assertEqual(B[0x439a11cc - BASE:0x439a11d0 - BASE].hex(), "dfe813f0")
        tabla = B[0x439a11d0 - BASE:0x439a11d0 - BASE + 12]
        self.assertEqual(tabla.hex(), "06004e0011016f017801b301")
        casos = [0x439a11d0 + 2 * int.from_bytes(tabla[i:i + 2], "little")
                 for i in range(0, 12, 2)]
        self.assertEqual(casos, [0x439a11dc, 0x439a126c, 0x439a13f2,
                                 0x439a14ae, 0x439a14c0, 0x439a1536])

    def test_ramas_de_error_del_despachador(self):
        """bhi -> '[SAD] data1=other' (0x43ce59af); bne -> '[SAD] SelCodeErr'."""
        self.assertEqual(GM.get(0x43ce59af, []), [0x439a1576])
        self.assertEqual(GM.get(0x43ce59c1, []), [0x439a1582])
        # la rama bhi salta a 0x439a156e (antes del literal de data1=other)
        self.assertEqual(B[0x439a11c8 - BASE:0x439a11cc - BASE].hex(), "00f2d181")
        # la rama bne salta a 0x439a157a (antes del literal de SelCodeErr)
        self.assertEqual(B[0x439a11be - BASE:0x439a11c2 - BASE].hex(), "40f0dc81")

    def test_tabla_de_versiones_sa(self):
        tabla = B[0x43ce5402 - BASE:0x43ce5402 - BASE + 68]
        self.assertEqual(tabla.hex(),
                         "5341305f56312e305341355f56312e30005a4d413156312e30"
                         "5341355f56312e30005341315f56312e305341355f56312e30"
                         "005a4d413056312e305341355f56312e3000")

    def test_programas_preinstalados_sa(self):
        self.assertEqual(GM.get(0x43ce561f, []), [0x4399ee6a])
        self.assertEqual(GM.get(0x43ce5634, []), [0x4399eefa])
        self.assertEqual(GM.get(0x43ce5640, []), [0x4399ef0e])

    def test_rtti_y_ficheros_del_subsistema(self):
        self.assertEqual(cstr(0x43ce59d2),
                         "N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE")
        self.assertEqual(cstr(0x43ce6bea),
                         "N15NS_SCALAR_INFRA21ScalarInfraSequenceSaE")
        self.assertEqual(cstr(0x43ce7004),
                         "N15NS_SCALAR_INFRA41ScalarInfraSequenceSaStageAutoexec_sadoneE")
        self.assertEqual(cstr(0x43ce6c15), "ScalarInfraSequenceSa.cpp")
        self.assertEqual(cstr(0x43ce6e16), "ScalarInfraSequenceSaStage.cpp")
        self.assertEqual(len(GM.get(0x43ce6c15, [])), 10)
        self.assertEqual(len(GM.get(0x43ce6e16, [])), 6)

    def test_sigla_sad_sin_expansion(self):
        for m in re.finditer(rb"SAD", B):
            o = m.start()
            s = o
            while s > 0 and B[s - 1] != 0 and 32 <= B[s - 1] < 127:
                s -= 1
            e = B.find(b"\x00", o)
            self.assertTrue(cstr(BASE + s).startswith("[SAD]"),
                            f"SAD fuera de traza: {cstr(BASE + s)!r}")

    # ------------------------------------------------------- diferencial
    def test_cero_token_en_a7s_y_a6300(self):
        self.assertEqual(A7.count(b"[SAD]"), 0)
        self.assertEqual(A63.count(b"[SAD]"), 0)

    def test_infraestructura_sa_en_los_tres(self):
        for tok in (b"SA_PREINSTALLED_PRG:", b"SA_JPEG_ENC", b"SA_JPEG_DEC",
                    b"SA_EXEC_PROGRAM_PAYLOAD", b"SA_EXEC_PROGRAM_COMP",
                    b"ScalarInfraSequenceSa.cpp", b"ScalarInfraSequenceSaStage.cpp",
                    b"SA0_V1.0", b"SA1_V1.0"):
            self.assertEqual(B.count(tok), 1, tok)
            self.assertEqual(A7.count(tok), 1, tok)
            self.assertEqual(A63.count(tok), 1, tok)

    def test_tokens_exclusivos_de_la_a6000(self):
        for tok in (b"SaProgHdr", b"CdcSaPrg", b"NmlSaPrg", b"RsdSaPrg", b"JpgNrm",
                    b"JpgSrt", b"OpnCmd", b"SelCode", b"DdsDataAdd", b"Hdr Err",
                    b"DbgPrt"):
            self.assertGreater(B.count(tok), 0, tok)
            self.assertEqual(A7.count(tok), 0, tok)
            self.assertEqual(A63.count(tok), 0, tok)

    def test_anclas_de_codigo_para_el_diferencial(self):
        """Las mismas cadenas del driver SA existen en los tres firmwares, en
        direcciones distintas (el bloque de código también es distinto)."""
        anclas = {
            "A6000": (B, {"[SIO]osal_valloc_msg": 0x43ce5398,
                          "SA_PREINSTALLED_PRG:": 0x43ce561f,
                          "SA_JPEG_ENC": 0x43ce5634,
                          "SA_JPEG_DEC": 0x43ce5640,
                          "ScalarInfraSequenceSa.cpp": 0x43ce6c15}),
            "A7S": (A7, {"[SIO]osal_valloc_msg": 0x43cda642,
                         "SA_PREINSTALLED_PRG:": 0x43cda81c,
                         "SA_JPEG_ENC": 0x43cda831,
                         "SA_JPEG_DEC": 0x43cda83d,
                         "ScalarInfraSequenceSa.cpp": 0x43cdbac0}),
            "A6300": (A63, {"[SIO]osal_valloc_msg": 0x43df880b,
                            "SA_PREINSTALLED_PRG:": 0x43df8959,
                            "SA_JPEG_ENC": 0x43df896e,
                            "SA_JPEG_DEC": 0x43df897a,
                            "ScalarInfraSequenceSa.cpp": 0x43df9f42}),
        }
        for tag, (blob, tabla) in anclas.items():
            for txt, addr in tabla.items():
                o = blob.find(txt.encode())
                self.assertGreater(o, 0, f"{tag}: {txt}")
                self.assertEqual(BASE + o, addr, f"{tag}: {txt}")

    # ----------------------------------------------- línea del obturador
    def test_negativo_linea_del_obturador(self):
        for k in ("shut", "silent", "electro", "mech", "sensor", "imager", "expo",
                  "readout", "drive", "bracket", "sweep", "interval", "focus", "iso"):
            for a, t in sad_strings(B):
                self.assertNotIn(k, t.lower(), f"{k!r} en {a:#x}")


if __name__ == "__main__":
    unittest.main()
