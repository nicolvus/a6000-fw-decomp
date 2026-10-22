"""Tests for S137 — el token `[CTRLCORE]` (núcleo de control del códec) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware, recalculan el mapa de
referencias PIC de forma independiente y comprueban direcciones, textos, guardas y
ramas concretas. Si cambia una dirección, un texto o un recuento, el test falla.
"""

import bisect
import json
import pathlib
import struct

import pytest

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
JSON_PATH = "analysis/s137_ctrlcore/ctrlcore.json"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = b"[CTRLCORE]"


# --------------------------------------------------------------- utilidades
_DATA_CACHE = {}
_PIC_CACHE = {}


def _data(path=BIN_PATH):
    if path not in _DATA_CACHE:
        with open(ROOT / path, "rb") as fh:
            _DATA_CACHE[path] = fh.read()
    return _DATA_CACHE[path]


def _json():
    with open(ROOT / JSON_PATH) as fh:
        return json.load(fh)


def _u16(data, vaddr):
    off = vaddr - BASE_VADDR
    assert 0 <= off <= len(data) - 2, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack("<H", data[off:off + 2])[0]


def _u32(data, vaddr):
    off = vaddr - BASE_VADDR
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack("<I", data[off:off + 4])[0]


def _cstr(data, vaddr, maxlen=300):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _occurrences(data):
    """[(vaddr_token, vaddr_cadena, texto)] de cada token `[CTRLCORE]`."""
    out = []
    start = 0
    while True:
        i = data.find(TOKEN, start)
        if i < 0:
            break
        s = i
        while s > 0 and 32 <= data[s - 1] < 127:
            s -= 1
        out.append((BASE_VADDR + i, BASE_VADDR + s, _cstr(data, BASE_VADDR + s)))
        start = i + 1
    return out


def _branch_target(data, vaddr):
    """Destino de un `b.w`/`bl` de 32 bits que empieza en `vaddr`."""
    h1 = _u16(data, vaddr)
    h2 = _u16(data, vaddr + 2)
    assert (h1 & 0xF800) == 0xF000, f"{hex(vaddr)} no es B.W/BL de 32 bits"
    assert (h2 & 0xC000) in (0x8000, 0xC000), f"{hex(vaddr)} no es B.W/BL"
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    i1 = (~(j1 ^ s)) & 1
    i2 = (~(j2 ^ s)) & 1
    imm11 = h2 & 0x7FF
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        imm -= 1 << 25
    return (vaddr + 4 + imm) & 0xFFFFFFFF


def _pic_ref(data, add_site):
    """Destino del `add rX,pc` de `add_site` (regla estricta, mismo registro)."""
    h = _u16(data, add_site)
    assert (h & 0xFF00) == 0x4400, f"{hex(add_site)} no es `add rX,pc`"
    assert ((h >> 3) & 0xF) == 15, f"{hex(add_site)} no usa PC como origen"
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    for la in range(add_site - 2, add_site - 4096, -2):
        lh = _u16(data, la)
        if (lh & 0xF800) == 0x4800:
            lreg = (lh >> 8) & 7
            lit = ((la + 4) & ~3) + ((lh & 0xFF) * 4)
        elif (lh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, la + 2)
            lreg = (h2 >> 12) & 0xF
            lit = ((la + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        else:
            continue
        if lreg != reg:
            continue
        return (_u32(data, lit) + (add_site + 4)) & 0xFFFFFFFF
    return None


def _pic_index(data):
    """{destino: [sitios `add rX,pc`]} de toda la imagen (recálculo independiente)."""
    key = id(data)
    if key in _PIC_CACHE:
        return _PIC_CACHE[key]
    n = len(data)
    ldrs = []
    for a in range(BASE_VADDR, BASE_VADDR + n - 8, 2):
        o = a - BASE_VADDR
        h = struct.unpack("<H", data[o:o + 2])[0]
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack("<H", data[o + 2:o + 4])[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        else:
            continue
        o2 = lit - BASE_VADDR
        if 0 <= o2 <= n - 4:
            ldrs.append((a, reg, struct.unpack("<I", data[o2:o2 + 4])[0]))
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    keys = {}
    for reg, v in by_reg.items():
        v.sort()
        keys[reg] = [x[0] for x in v]
    out = {}
    for a in range(BASE_VADDR, BASE_VADDR + n - 4, 2):
        o = a - BASE_VADDR
        h = struct.unpack("<H", data[o:o + 2])[0]
        if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        out.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    _PIC_CACHE[key] = out
    return out


FUNCIONES = {
    0x435A1B64: [0x435A18B8, 0x435A18D6, 0x435A190E, 0x435A1952],
    0x435A1BAC: [0x435A18C4],
    0x435A1BE0: [0x435A191A],
    0x435A1C14: [0x435A192C],
    0x435A1C5C: [0x435A177C],
    0x435A1D1C: [0x435A172E],
    0x435A1DE0: [0x435A16AC],
    0x435A1F18: [0x435A14C2],
    0x435A20B0: [0x435A14A2],
    0x435A2200: [0x435A1482],
    0x435A2354: [0x435A1684],
    0x435A23B4: [0x435A16C4, 0x435A16F0],
    0x43629C4C: [0x43620044],
    0x43920BCC: [0x4391AD28, 0x4391AD46, 0x4391AD7C, 0x4391ADA0],
    0x43920C2C: [0x4391AD32],
    0x43920C9C: [0x4391AD86],
}


# ------------------------------------------------------------------- cadenas
class TestCadenas:
    def test_conteo_y_rango(self):
        data = _data()
        occ = _occurrences(data)
        assert len(occ) == 55, f"Se esperaban 55 cadenas [CTRLCORE], hay {len(occ)}"
        assert occ[0][1] == 0x43C3B82D
        assert occ[-1][1] == 0x43CDB492
        assert occ[0][2].startswith("[ERR][CDIAG][CTRLCORE]")

    def test_reparto_por_contenedor(self):
        occ = _occurrences(_data())
        cd = [o for o in occ if "[CDIAG]" in o[2]]
        mc = [o for o in occ if "[MCSENS]" in o[2]]
        am = [o for o in occ if "[AMSENS]" in o[2]]
        assert (len(cd), len(mc), len(am)) == (51, 1, 3)
        assert len(cd) + len(mc) + len(am) == 55
        assert sum(1 for o in cd if o[2].startswith("[ERR]")) == 2

    def test_textos_concretos(self):
        data = _data()
        esperadas = {
            0x43C3B82D: "[ERR][CDIAG][CTRLCORE]p_prm is NULL file[%s] func[%s] line[%d]",
            0x43C3B87B: "[ERR][CDIAG][CTRLCORE]p_prm is NULL",
            0x43C3B89F: "[CDIAG][CTRLCORE]Exec DbgDiagAvc HD REC!!",
            0x43C3B91D: "[CDIAG][CTRLCORE]Exec DbgDiagAvc SD DEC!!(NotSupport)",
            0x43C3B953: "[CDIAG][CTRLCORE]No Support EXEC MODE!!",
            0x43C3B9A9: "[CDIAG][CTRLCORE]Exec ConfirmDoneCodec HD REC!!",
            0x43C3BA86: "[CDIAG][CTRLCORE]Exec CmpData HD REC!!",
            0x43C3BB74: "[CDIAG][CTRLCORE]Exec CmpData JPEG ENCDEC!!",
            0x43C3BBA0: "[CDIAG][CTRLCORE]ExecCmd !! [0x%04X] mode[0x%02X] func[0x%02X]",
            0x43C3BC80: "[CDIAG][CTRLCORE]Exec RunCodec JPG ENC!!",
            0x43C3BF7D: "[CDIAG][CTRLCORE][SET_DIAG_MODE] mode[0x%02X] func[0x%02X]",
            0x43C3BFEE: ("[CDIAG][CTRLCORE]memIdx[%d] fileId[%02d:%02d] "
                         "unitHandle[0x%04X] unitType[0x%08X] size[0x%08X]"),
            0x43C3C0EB: "[CDIAG][CTRLCORE]Exec SetData JPG ENCDEC!!",
            0x43C73649: "[ERR][MCSENS][CTRLCORE]p_prm is NULL file[%s] func[%s] line[%d]",
            0x43CDB41A: "[ERR][AMSENS][CTRLCORE]p_prm is NULL file[%s] func[%s] line[%d]",
            0x43CDB46D: "[ERR][AMSENS][CTRLCORE]p_prm is NULL",
            0x43CDB492: "[AMSENS][CTRLCORE][AVCE][PARAM] adr[0x%08X] size[%d]",
        }
        for vaddr, texto in esperadas.items():
            assert _cstr(data, vaddr) == texto, f"vaddr {hex(vaddr)}"

    def test_ficheros_fuente_y_firmas(self):
        data = _data()
        ficheros = {
            0x43C3B86C: "cdCtrlCore.cpp",
            0x43C73689: "mcSensCtrlCore.cpp",
            0x43CDB45A: "amSensCtrlCore.cpp",
            0x43C454E8: "mcAvCtrlCore.cpp",
            0x43C3B1A8: "cdCtrlIf.cpp",
        }
        for vaddr, texto in ficheros.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)
        firmas = {
            0x43C3B7A9: ("CDIAGER CdCtrlCore::SetCompNormal(OsalResponsePacket*, "
                         "__uint32_t)"),
            0x43C3C19C: ("CDIAGER CdCtrlCore::SetCompDeleteData(OsalResponsePacket*, "
                         "__uint32_t)"),
            0x43C3C162: "CDIAGER CdCtrlCore::SetData(const __uint8_t*, __uint32_t)",
            0x43C7369C: ("MCSENSERR McSensCtrlCore::SetCompNormal(OsalResponsePacket*, "
                         "__uint32_t)"),
            0x43CDB4C7: ("AMSENSERR AmSensCtrlCore::SetCompNormal(OsalResponsePacket*, "
                         "__uint32_t)"),
            0x43C3B647: "CDIAGER CdCtrlIf::ExecCmd(CdCtrlIf::MSG_SENS_COMMAND*)",
            0x43C3B688: ("CDIAGER CdCtrlIf::ExecSensComp(__uint32_t, OsalResponsePacket*, "
                         "__uint32_t)"),
        }
        for vaddr, texto in firmas.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_sin_menciones_del_obturador(self):
        texto = " ".join(o[2] for o in _occurrences(_data())).lower()
        for palabra in ("shutter", "silent", "efcs", "curtain", "mechan",
                        "imager", "sensor", "readout", "exposure"):
            assert palabra not in texto, palabra


# --------------------------------------------------------------- sitios PIC
class TestSitios:
    def test_mapa_independiente_coincide_con_el_json(self):
        data = _data()
        occ = _occurrences(data)
        idx = _pic_index(data)
        js = _json()
        mapa = {int(k, 16): [int(x, 16) for x in v] for k, v in js["sitios"].items()}
        assert len(mapa) == 55
        assert sum(len(v) for v in mapa.values()) == 74
        total = 0
        for _tok, vaddr, texto in occ:
            refs = idx.get(vaddr, [])
            assert refs == mapa[vaddr], hex(vaddr)
            assert len(refs) == len(set(refs))
            for site in refs:
                # el sitio es un `add rX,pc` real y resuelve a esta cadena
                assert (_u16(data, site) & 0xFF00) == 0x4400
                assert _pic_ref(data, site) == vaddr
                assert _cstr(data, vaddr).startswith(
                    js["cadenas"][[int(c["vaddr"], 16) for c in js["cadenas"]].index(vaddr)]["texto"][:20]
                )
            total += len(refs)
        assert total == 74, total

    def test_sitios_concretos(self):
        idx = _pic_index(_data())
        assert idx[0x43C3B82D] == [0x435A1B72, 0x435A1C22]
        assert idx[0x43C3B87B] == [0x435A1BB2, 0x435A1BE6]
        assert idx[0x43C3B89F] == [0x435A1CA2]
        assert idx[0x43C3B953] == [
            0x435A1CEE, 0x435A1EDC, 0x435A2072,
            0x435A21B8, 0x435A230A, 0x435A2782,
        ]
        assert idx[0x43C3BA86] == [0x435A1E3A]
        assert len(idx[0x43C3BFEE]) == 7
        assert idx[0x43CDB492] == [0x43920C6A, 0x43920CDA]

    def test_ninguna_cadena_muerta(self):
        data = _data()
        idx = _pic_index(data)
        for _tok, vaddr, _texto in _occurrences(data):
            assert idx.get(vaddr), hex(vaddr)
            assert data.find(struct.pack("<I", vaddr)) == -1, hex(vaddr)


# -------------------------------------------------------------- funciones
class TestFunciones:
    def test_16_funciones_y_reparto(self):
        js = _json()
        assert len(js["funciones"]) == 16
        assert set(js["funciones"]) == {hex(f) for f in FUNCIONES}
        assert sum(f["n_sitios"] for f in js["funciones"].values()) == 74
        # 67 pares funcion-cadena: una misma cadena puede aparecer en 2 sitios
        assert sum(f["n_cadenas"] for f in js["funciones"].values()) == 67
        assert len({c for f in js["funciones"].values() for c in f["cadenas"]}) == 55

    @pytest.mark.parametrize("func", sorted(FUNCIONES))
    def test_prologo_push(self, func):
        data = _data()
        h = _u16(data, func)
        es_push = (h & 0xFF00) == 0xB500 or h in (0xE92D, 0xB5F0) or (h & 0xFFF0) == 0xB5F0
        assert es_push, f"{hex(func)}: {hex(h)} no es un push Thumb"

    @pytest.mark.parametrize("func,llamadores", sorted(FUNCIONES.items()))
    def test_llamadores_bl(self, func, llamadores):
        data = _data()
        for site in llamadores:
            assert _branch_target(data, site) == func, hex(site)

    def test_firma_de_la_propia_funcion_dentro_del_cuerpo(self):
        idx = _pic_index(_data())
        dentro = {
            0x43C3B6DF: [0x435A1CF0],   # DbgDiagAvc
            0x43C3B72A: [0x435A1EDE],   # CmpData
            0x43C3C123: [0x435A2074],   # RunCodec
            0x43C3B768: [0x435A21BA],   # RelMemArea
            0x43C3B7EC: [0x435A230C],   # SetMemArea
            0x43C3C19C: [0x435A1C26],   # SetCompDeleteData
            0x43C3C162: [0x435A23E6, 0x435A2784],  # SetData
        }
        for firma, sites in dentro.items():
            assert idx.get(firma, [])[:len(sites)] == sites or sites == idx.get(firma), firma

    def test_guarda_de_SetCompNormal_pasa_firma_y_linea(self):
        data = _data()
        # push {r3,lr}; cbnz r1; ldr r0,[pc,#0x34]; movw r3,#0x2bd
        assert _u16(data, 0x435A1B64) == 0xB508
        assert _u16(data, 0x435A1B6A) == 0xF240
        assert _u16(data, 0x435A1B6C) == 0x23BD
        assert _pic_ref(data, 0x435A1B72) == 0x43C3B82D
        # el nombre del fichero y la firma se pasan como `file` y `func`
        assert _pic_ref(data, 0x435A1B74) == 0x43C3B86C
        assert _pic_ref(data, 0x435A1B76) == 0x43C3B7A9
        # trama de respuesta: tipo 8, +0x01 = 1, +0x0c = 1, +0x10 = [obj+0x1480+0x18]
        assert _u16(data, 0x435A1B84) == 0x2308          # movs r3,#8
        assert _u16(data, 0x435A1B8E) == 0x60CA          # str r2,[r1,#0xc]
        assert _u16(data, 0x435A1B92) == 0x6982          # ldr r2,[r0,#0x18]
        assert _u16(data, 0x435A1B9A) == 0x740A          # strb r2,[r1,#0x10]
        # variante SetCompDeleteData: movw r3,#0x34f y tipo 0x20
        assert _u16(data, 0x435A1C1A) == 0xF240
        assert _u16(data, 0x435A1C1C) == 0x334F
        assert _u16(data, 0x435A1C30) == 0x2320
        # variantes sin nombre
        assert _u16(data, 0x435A1BBC) == 0xF500          # add.w r0,r0,#0x1480 (tipo 2)
        assert _u16(data, 0x435A1BBE) == 0x50A4

    def test_guardas_de_McSens_y_AmSens(self):
        data = _data()
        assert _u16(data, 0x43629C52) == 0x2313          # movs r3,#0x13
        assert _u16(data, 0x43920BD2) == 0x2326          # movs r3,#0x26
        assert _u16(data, 0x43920C2C) == 0xB573          # push {r0,r1,r4,r5,r6,lr}
        assert _u16(data, 0x43920C42) == 0x2302          # movs r3,#2 (tipo)
        assert _u16(data, 0x43920C46) == 0x700B          # strb r3,[r1] (1 = 2-1)
        assert _u16(data, 0x43920C54) == 0x2112          # movs r1,#0x12
        assert _branch_target(data, 0x43920C5C) == 0x43A3A9B4
        assert _u16(data, 0x43920C9C) == 0xB573
        assert _branch_target(data, 0x43920CCC) == 0x43A3A9B4


# ------------------------------------------------------------- despachadores
class TestDespachadores:
    def test_guardas_linea(self):
        data = _data()
        assert _u16(data, 0x435A142A) == 0x23C2          # movs r3,#0xc2
        assert _u16(data, 0x435A15F4) == 0x2341          # movs r3,#0x41
        assert _u16(data, 0x435A17F4) == 0xF240          # movw r3,#0x12d
        assert _u16(data, 0x435A17F6) == 0x132D
        # guarda genérica y log de "no soportado"
        assert _cstr(data, 0x43C3B176) == "[%s] -- file[%s] func[%s] line[%d]"
        assert _cstr(data, 0x43C3B238) == (
            "[ERR][CDIAG][CTRLIF]NOT SUPPORTED -- COMMAND ID [0x%08X] [%s]")

    def test_exec_cmd_ramas(self):
        data = _data()
        assert _branch_target(data, 0x435A1482) == 0x435A2200  # id 2  -> SetMemArea
        assert _branch_target(data, 0x435A14A2) == 0x435A20B0  # id 3  -> RelMemArea
        assert _branch_target(data, 0x435A14C2) == 0x435A1F18  # 0x11  -> RunCodec
        # camino "no soportado": log con la firma de ExecCmd y retorno 1
        assert _pic_ref(data, 0x435A14CC) == 0x43C3B238
        assert _pic_ref(data, 0x435A14CE) == 0x43C3B647
        assert _u16(data, 0x435A14D4) == 0x2001          # movs r0,#1

    def test_exec_sens_cmd_comparaciones(self):
        data = _data()
        assert _u16(data, 0x435A1626) == 0x2D21          # cmp r5,#0x21
        assert _u16(data, 0x435A165C) == 0x2D41          # cmp r5,#0x41
        assert _u16(data, 0x435A1660) == 0x2DD1          # cmp r5,#0xd1
        assert _u16(data, 0x435A1654) == 0x2D32          # cmp r5,#0x32
        assert _u16(data, 0x435A164A) == 0x2D33          # cmp r5,#0x33

    def test_exec_sens_cmd_ramas(self):
        data = _data()
        assert _branch_target(data, 0x435A1684) == 0x435A2354  # 1 -> SetDiagMode
        assert _branch_target(data, 0x435A1698) == 0x435A157C  # 2/3/0x11 -> trama
        assert _branch_target(data, 0x435A16AC) == 0x435A1DE0  # 0x12 -> CmpData
        assert _branch_target(data, 0x435A172E) == 0x435A1D1C  # 0x41 -> ConfirmDoneCodec
        assert _branch_target(data, 0x435A177C) == 0x435A1C5C  # 0xd1 -> DbgDiagAvc
        assert _branch_target(data, 0x435A16C4) == 0x435A23B4  # 0x21 sub 1
        assert _branch_target(data, 0x435A16F0) == 0x435A23B4  # 0x22 sub 1
        assert _branch_target(data, 0x435A173C) == 0x43A48D16  # 0x32
        assert _branch_target(data, 0x435A1752) == 0x43A48CF2  # 0x33

    def test_trama_de_12_bytes(self):
        data = _data()
        # 0x435a157c: marco de 12 B en pila; id en +0, mode en +2, func en +3
        assert _u16(data, 0x435A1586) == 0x220C          # movs r2,#0xc
        assert _u16(data, 0x435A1590) == 0xF8AD          # strh.w r6,[sp,#0xc] (id)
        assert _u16(data, 0x435A1592) == 0x600C
        assert _u16(data, 0x435A1594) == 0x7823          # ldrb r3,[r4]
        assert _u16(data, 0x435A159C) == 0xF88D          # strb.w r3,[sp,#0xe] (mode)
        assert _u16(data, 0x435A159E) == 0x300E
        assert _u16(data, 0x435A15A0) == 0x7863          # ldrb r3,[r4,#1]
        assert _u16(data, 0x435A15A2) == 0xF88D          # strb.w r3,[sp,#0xf] (func)
        assert _u16(data, 0x435A15A4) == 0x300F

    def test_exec_sens_comp_compone_respuestas(self):
        data = _data()
        assert _branch_target(data, 0x435A18B8) == 0x435A1B64  # SetCompNormal
        assert _branch_target(data, 0x435A18C4) == 0x435A1BAC
        assert _branch_target(data, 0x435A191A) == 0x435A1BE0
        assert _branch_target(data, 0x435A192C) == 0x435A1C14  # SetCompDeleteData
        # los nombres SENS_* de la tabla de respuestas (prefijo [CDIAG][CTRLIF])
        for vaddr, nombre in {
            0x43C3B518: "SENS_SET_DIAG_MODE",
            0x43C3B540: "SENS_SET_DATA_AREA",
            0x43C3B568: "SENS_REL_DATA_AREA",
            0x43C3B590: "SENS_RUN_CODEC",
            0x43C3B5B4: "SENS_CMP_DATA",
            0x43C3B601: "SENS_SET_DATA",
            0x43C3B624: "SENS_GET_DATA",
            0x43C3B497: "SENS_CNFM_SET_DATA_AREA",
            0x43C3B4C4: "SENS_CNFM_REL_DATA_AREA",
            0x43C3B5D7: "SENS_CNFM_DONE_CODEC",
            0x43C3B4F1: "SENS_DBG_DIAG_AVC",
        }.items():
            assert _cstr(data, vaddr) == f"[CDIAG][CTRLIF]{nombre} [%s]", hex(vaddr)


# --------------------------------------------------------------- diferencial
class TestDiferencial:
    def test_a7s_tiene_las_mismas_55_cadenas(self):
        path = ROOT / A7S_BIN
        if not path.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(path, "rb") as fh:
            a7s = fh.read()
        assert a7s.count(TOKEN) == 55
        texto_a6 = {o[2] for o in _occurrences(_data())}
        texto_a7 = {o[2] for o in _occurrences(a7s)}
        assert texto_a6 == texto_a7
        assert len(texto_a7) == 55

    def test_a6300_anade_4k_y_cdext(self):
        path = ROOT / A6300_BIN
        if not path.exists():
            pytest.skip("blob de la A6300 no disponible")
        with open(path, "rb") as fh:
            a6300 = fh.read()
        assert a6300.count(TOKEN) == 90
        texto_a6 = {o[2] for o in _occurrences(_data())}
        texto_a63 = {o[2] for o in _occurrences(a6300)}
        nuevos = texto_a63 - texto_a6
        assert len(nuevos) == 35, len(nuevos)
        assert len([t for t in nuevos if "4K" in t]) == 14
        assert len([t for t in nuevos if "[CDEXT]" in t]) == 21
        assert "[CDIAG][CTRLCORE]Exec RunCodec 4K REC!!" in nuevos
        assert "[CDEXT][CTRLCORE]StartVideoCodecDiag !!" in nuevos
        assert not (texto_a6 - texto_a63)


# --------------------------------------------------------------------- JSON
class TestJsonDelHito:
    def test_cifras_y_estructura(self):
        js = _json()
        assert js["token"] == "[CTRLCORE]"
        assert js["base_vaddr"] == "0x43541000"
        assert js["cifras"]["cadenas"] == 55
        assert js["cifras"]["sitios_pic"] == 74
        assert js["cifras"]["funciones"] == 16
        assert js["verificacion_pic"]["confirmados"] == 74
        assert js["verificacion_pic"]["texto_ok"] == 74
        assert js["modulos"] == {"[CDIAG]": 51, "[MCSENS]": 1, "[AMSENS]": 3}
        assert len(js["cadenas"]) == 55
        assert len(js["funciones"]) == 16
        assert set(js["despachadores"]) == {
            "CdCtrlIf::ExecCmd",
            "CdCtrlIf::ExecSensCmd",
            "CdCtrlIf::ExecSensComp",
        }
        assert js["despachadores"]["CdCtrlIf::ExecCmd"]["vaddr"] == "0x435a1424"
        assert js["despachadores"]["CdCtrlIf::ExecSensCmd"]["guard_linea"] == 65
        assert js["despachadores"]["CdCtrlIf::ExecSensComp"]["guard_linea"] == 301

    def test_no_verificado(self):
        js = _json()
        assert len(js["no_verificado"]) == 4
        assert any("0x439b4244" in s for s in js["no_verificado"])
        assert any("0x435a1bac" in s for s in js["no_verificado"])
        assert js["punteros_4B_a_cadenas"]
        assert all(v == [] for v in js["punteros_4B_a_cadenas"].values())
