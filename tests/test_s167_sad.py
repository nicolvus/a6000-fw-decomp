#!/usr/bin/env python3
"""S167 — tests del módulo `[SAD]` (44 trazas) del firmware A6000 fw3.21.

Todos los tests leen **bytes reales** de los tres firmware y comprueban
direcciones concretas: si una dirección cambia, el test falla.

Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import os
import re
import struct

import pytest

BASE = 0x43541000
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = "analysis/s167_sad"

U16 = struct.Struct("<H")
U32 = struct.Struct("<I")

B = open(A6000, "rb").read()
A7S_B = open(A7S, "rb").read()
A63_B = open(A6300, "rb").read()


def cstr(vaddr, blob=None):
    blob = B if blob is None else blob
    o = vaddr - BASE
    assert 0 <= o < len(blob), f"vaddr {vaddr:#x} fuera del blob"
    e = blob.find(b"\x00", o)
    assert e >= 0, f"sin NUL en {vaddr:#x}"
    return blob[o:e].decode("latin1")


def u16(vaddr, blob=None):
    blob = B if blob is None else blob
    return U16.unpack_from(blob, vaddr - BASE)[0]


def u32(vaddr, blob=None):
    blob = B if blob is None else blob
    return U32.unpack_from(blob, vaddr - BASE)[0]


def bytes_at(vaddr, n):
    return B[vaddr - BASE: vaddr - BASE + n]


# ------------------------------------------------------------------ cadenas
CADENAS = [
    (0x43ce546b, "[SAD] Same Unit Handle Get"),
    (0x43ce5486, "[SAD] same hndl get_cnt=0x%08x"),
    (0x43ce54a5, "[SAD] alloc_cnt=0x%08x"),
    (0x43ce55bc, "[SAD] !!! CdcSaPrg Hdr Err !!!"),
    (0x43ce55db, "[SAD] !!! NmlSaPrg Hdr Err !!!"),
    (0x43ce55fa, "[SAD] !!! RsdSaPrg Hdr Err !!!"),
    (0x43ce564c, "[SAD] DbgPrt CmdRcv"),
    (0x43ce5660, "[SAD] CfgStatePrt"),
    (0x43ce5672, "[SAD]      D3,D2,D1,D0"),
    (0x43ce5689, "[SAD] ----------------"),
    (0x43ce56a0, "[SAD] ZmCfg=0x%08x"),
    (0x43ce56b3, "[SAD] "),
    (0x43ce56ba, "[SAD] SaCfg=0x%08x"),
    (0x43ce56cd, "[SAD] = FifoStatePrt ="),
    (0x43ce56e4, "[SAD] D3:dummy,D2:WrtPtr,D1:RdPtr,D0:NumQue"),
    (0x43ce5710, "[SAD] OpnCmd=0x%08x"),
    (0x43ce5724, "[SAD] JpgNrm=0x%08x"),
    (0x43ce5738, "[SAD] JpgSrt=0x%08x"),
    (0x43ce574c, "[SAD] = FifoDataPrt ="),
    (0x43ce5762, "[SAD] JpgNrmIndex=0x%02x"),
    (0x43ce577b, "[SAD] JpgSrtIndex=0x%02x"),
    (0x43ce5794, "[SAD] OpnCmdIndex=0x%02x"),
    (0x43ce57ad, "[SAD] FifoSize=0x%02x"),
    (0x43ce57c3, "[SAD]     D3,D2,D1,D0"),
    (0x43ce57d9, "[SAD] ---------------"),
    (0x43ce57ef, "[SAD] Fifo=0x%08x"),
    (0x43ce5801, "[SAD] = CalcTimePrt ="),
    (0x43ce5817, "[SAD] (ave):(max) (dummy):(count)"),
    (0x43ce5839, "[SAD] --------------------------"),
    (0x43ce585a, "[SAD] Data=0x%08x 0x%08x"),
    (0x43ce5873, "[SAD] = End =="),
    (0x43ce5882, "[SAD] = CalcTimeSum Prt(sum:4byte)="),
    (0x43ce58a6, "[SAD] Data=0x%08x"),
    (0x43ce58b8, "[SAD] = End ="),
    (0x43ce58c6, "[SAD] DdsDataAdd=0x%08x"),
    (0x43ce58de, "[SAD] !!! SaProgHdr Err !!!"),
    (0x43ce58fa, "[SAD] PrgID=0x%02x"),
    (0x43ce590d, "[SAD] Add=0x%08x"),
    (0x43ce591e, "[SAD] Data=0x%08x 0x%08x 0x%08x 0x%08x"),
    (0x43ce5945, "[SAD] SaProgHdr OK"),
    (0x43ce5958, "[SAD] Dmm Same Handle Get Num"),
    (0x43ce5976, "[SAD] SameHandleGetCnt=0x%08x"),
    (0x43ce5994, "[SAD] Alloc all Cnt=0x%08x"),
    (0x43ce59af, "[SAD] data1=other"),
    (0x43ce59c1, "[SAD] SelCodeErr"),
]


@pytest.mark.parametrize("vaddr,texto", CADENAS)
def test_cadena_sad_exacta(vaddr, texto):
    """Cada cadena [SAD] está exactamente en su dirección, con su texto exacto."""
    assert cstr(vaddr) == texto


def test_total_cadenas_sad():
    """45 cadenas empiezan por [SAD]; 44 con mensaje (una es solo el prefijo)."""
    starts = set()
    for m in re.finditer(rb"\[SAD\]", B):
        s = m.start()
        while s > 0 and B[s - 1] != 0 and 32 <= B[s - 1] < 127:
            s -= 1
        starts.add(s)
    assert len(starts) == 45
    # la 45.ª (0x43ce56b3) es el prefijo sin texto
    solo_prefijo = [BASE + s for s in starts
                    if B[s:B.find(b"\x00", s)] == b"[SAD] "]
    assert solo_prefijo == [0x43ce56b3]
    assert len(starts) - len(solo_prefijo) == 44


def test_rango_bloque_sad():
    """Las 45 cadenas ocupan 3 bloques separados, no uno contiguo."""
    addrs = sorted(a for a, _ in CADENAS)
    assert addrs[0] == 0x43ce546b
    assert addrs[-1] == 0x43ce59c1
    # bloque A: 3 cadenas, hueco de 256 B (tabla de indices), bloque B: 3 cadenas,
    # hueco de 51 B (cola + 3 cadenas SA), bloque C: 39 cadenas
    assert addrs[0] == 0x43ce546b and addrs[2] == 0x43ce54a5
    assert addrs[3] == 0x43ce55bc and addrs[5] == 0x43ce55fa
    assert addrs[6] == 0x43ce564c and addrs[-1] == 0x43ce59c1
    # el hueco A->B (256 B) no contiene ninguna cadena [SAD]
    hueco = B[0x43ce54bc - BASE:0x43ce55bc - BASE]
    assert b"[SAD]" not in hueco
    # el hueco B->C (51 B) contiene la cola de tabla y las 3 cadenas SA, no [SAD]
    hueco2 = B[0x43ce5619 - BASE:0x43ce564c - BASE]
    assert b"[SAD]" not in hueco2
    assert b"SA_PREINSTALLED_PRG:" in hueco2
    # dentro del rango total no hay otros prefijos de modulo intercalados
    for m in re.finditer(rb"\[[A-Z][A-Z0-9_]{1,24}\]", B[0x43ce546b - BASE:0x43ce59c1 - BASE]):
        assert m.group() == b"[SAD]"


# ------------------------------------------------------- referencias PIC
def test_mapa_pic_global_tiene_las_45_cadenas():
    """El mapa PIC canónico del repo referencia las 45 cadenas [SAD]."""
    gm = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
    total = 0
    for a, _ in CADENAS:
        assert hex(a) in gm, f"{a:#x} sin referencia PIC"
        total += len(gm[hex(a)])
    assert total == 49


def test_sitios_pic_de_cadenas_clave():
    """Sitios PIC exactos de las cadenas con más de una referencia y de las de 1."""
    gm = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
    esperado = {
        0x43ce546b: [0x43998602],
        0x43ce55bc: [0x4399d4d2],
        0x43ce55db: [0x4399d5d8],
        0x43ce55fa: [0x4399d6ac],
        0x43ce564c: [0x439a11b4],
        0x43ce5689: [0x439a1208, 0x439a1290],
        0x43ce56b3: [0x439a1230, 0x439a1328, 0x439a13b4],
        0x43ce57d9: [0x439a13d0, 0x439a1474],
        0x43ce59c1: [0x439a1582],
    }
    for a, sitios in esperado.items():
        assert sorted(gm[hex(a)]) == sorted(sitios), hex(a)


def test_par_pic_verificado_a_mano_del_despachador():
    """Verificación manual (4 comprobaciones) de 3 pares PIC del despachador.

    (a) el `ldr rX,[pc,#imm]` más cercano por detrás es el emparejado;
    (b) el literal del pool es el que se lee;
    (c) destino == literal + (add + 4);
    (d) el registro no se reescribe entre `ldr` y `add`.
    """
    # (sitio, ldr, pool, literal, destino, registro)
    casos = [
        (0x439a11b4, 0x439a11ac, 0x439a1594, 0x344494, 0x43ce564c, 3),
        (0x439a11e4, 0x439a11dc, 0x439a1598, 0x344478, 0x43ce5660, 3),
        (0x439a1582, 0x439a157a, 0x439a163c, 0x34443b, 0x43ce59c1, 3),
    ]
    for sitio, ldr, pool, lit, destino, reg in casos:
        # (b) el pool contiene el literal
        assert u32(pool) == lit, hex(pool)
        # (c) destino = literal + (add + 4)
        assert (lit + sitio + 4) & 0xFFFFFFFF == destino
        # el destino es el inicio de la cadena [SAD] esperada
        assert cstr(destino).startswith("[SAD] ")
        # (a) el `ldr` del mismo registro más cercano por detrás es el emparejado
        assert u16(ldr) & 0xF800 == 0x4800, "el ldr debe ser de 16 bits"
        assert (u16(ldr) >> 8) & 7 == reg
        # el desplazamiento del `ldr` apunta exactamente al pool
        imm = (u16(ldr) & 0xFF) * 4
        assert ((ldr + 4) & ~3) + imm == pool
        # (d) sin reescritura de r3 entre `ldr` y `add` (r3 solo se carga por ldr)
        entre = bytes_at(ldr + 2, sitio - ldr - 2)
        # comprobación explícita: ningún `ldr r3,[..]` entre ldr y add
        escrituras = 0
        for i in range(0, len(entre) - 1, 2):
            h = U16.unpack_from(entre, i)[0]
            if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == 3:
                escrituras += 1
            elif (h & 0xFF7F) == 0xF85F and ((U16.unpack_from(entre, i + 2)[0] >> 12) & 0xF) == 3:
                escrituras += 1
        assert escrituras == 0, "r3 se reescribe entre ldr y add"


def test_despachador_id_mensaje_0x9548():
    """0x439a119c compara el id de mensaje recibido contra 0x9548."""
    # movw r3, #0x9548  ->  Thumb2 11110 i 10 0100 imm4 | 0 imm3 Rd imm8
    assert bytes_at(0x439a119e, 4) == bytes.fromhex("49f24853")
    # ldrh r2, [r0, #2] -> 0x8842 (halfword, little-endian en memoria: 42 88)
    assert bytes_at(0x439a11a2, 2) == bytes.fromhex("4288")
    # cmp r2, r3 -> 0x9a42
    assert bytes_at(0x439a11a6, 2) == bytes.fromhex("9a42")


def test_tabla_tbh_6_subcomandos():
    """La tabla tbh de 0x439a11d0 tiene 6 entradas con los destinos esperados."""
    base = 0x439a11d0
    esperado = [0x439a11dc, 0x439a126c, 0x439a13f2, 0x439a14ae, 0x439a14c0, 0x439a1536]
    for i, dest in enumerate(esperado):
        off = u16(base + 2 * i)
        assert base + 2 * off == dest, f"caso {i+1}"


# ------------------------------------------------- funciones emisoras
def test_prologo_funcion_gestor_de_handle():
    """0x43998578: push {r4,r5,lr} y barrido de tabla u16 invalidando con 0xFFFF."""
    assert bytes_at(0x43998578, 2) == bytes.fromhex("30b5")   # push {r4,r5,lr}
    # strh r2,[r3,#-0x2] con r2 = 0xFFFF (mov.w r2,#-1 = 0x4ff0ff32 en 0x4399858a)
    assert bytes_at(0x4399858a, 4) == bytes.fromhex("4ff0ff32")
    assert bytes_at(0x4399858e, 4) == bytes.fromhex("23f8022c")


def test_validadores_pragma_sa():
    """Los tres validadores de cabecera tienen el push.w de 9 registros."""
    for a in (0x4399d464, 0x4399d528, 0x4399d618):
        assert bytes_at(a, 4)[:2] in (b"\x2d\xe9",), hex(a)


def test_dispatcher_padre_registrado_en_tabla():
    """0x4399b074 aparece con bit Thumb en la entrada de handler 0x43fd2a88."""
    assert u32(0x43fd2a88) == 0x4399b075
    assert u32(0x43fd2a8c) == 0x18
    assert u32(0x43fd2a90) == 0x1000
    assert u32(0x43fd2a94) == 0
    assert u32(0x43fd2a98) == 0xFFFFFFFF


# ------------------------------------------------------------ diferencial
def test_a7s_no_tiene_token_sad():
    """La A7S fw3.20 no contiene ni una sola aparicion del token [SAD]."""
    assert len(re.findall(rb"\[SAD\]", A7S_B)) == 0
    assert len(re.findall(rb"\[SAD\]", A63_B)) == 0


@pytest.mark.parametrize("texto", [
    b"DbgPrt CmdRcv", b"CfgStatePrt", b"FifoStatePrt", b"FifoDataPrt",
    b"CalcTimePrt", b"CalcTimeSum", b"SaProgHdr", b"CdcSaPrg", b"NmlSaPrg",
    b"RsdSaPrg", b"Same Unit Handle Get", b"Dmm Same Handle Get Num",
    b"Alloc all Cnt", b"SelCodeErr", b"DdsDataAdd", b"JpgNrm", b"JpgSrt",
    b"ZmCfg", b"SaCfg", b"OpnCmd", b"FifoSize", b"alloc_cnt",
])
def test_contenido_sad_ausente_en_a7s_y_a6300(texto):
    """El contenido del modulo [SAD] no existe (ni sin etiqueta) en los otros dos."""
    assert texto not in A7S_B
    assert texto not in A63_B


@pytest.mark.parametrize("vaddr,texto", [
    (0x43ce561f, "SA_PREINSTALLED_PRG:"),
    (0x43ce5634, "SA_JPEG_ENC"),
    (0x43ce5640, "SA_JPEG_DEC"),
    (0x43ce5402, "SA0_V1.0SA5_V1.0"),
    (0x43ce5435, "ZMA0V1.0SA5_V1.0"),
])
def test_cadenas_sa_comunes_presentes_en_los_tres(vaddr, texto):
    """Las cadenas del subsistema SA que SI existen en los tres firmwares."""
    assert cstr(vaddr) == texto
    assert texto.encode() in A7S_B
    assert texto.encode() in A63_B


def test_tabla_de_datos_intercalada_por_las_trazas_sad():
    """La cabecera de 27 B y la tabla de 25 indices sobreviven intactas en la A6000,
    pero las cadenas [SAD] se han intercalado en dos huecos (3 bloques)."""
    cabecera = bytes.fromhex(
        "000101010001010204088383830483838307070707070707070707")
    assert len(cabecera) == 27
    # cabecera IDENTICA en los tres firmware
    assert bytes_at(0x43ce5445, 27) == cabecera            # A6000
    assert A7S_B[0x43cda6ef - BASE:0x43cda6ef - BASE + 27] == cabecera   # A7S
    assert A63_B[0x43df89bc - BASE:0x43df89bc - BASE + 27] == cabecera   # A6300
    # la tabla de 25 indices (0x03..0x1b) embebida en un mar de 0x1c es IDENTICA
    seq6 = [x for x in B[0x43ce54bc - BASE:0x43ce55bc - BASE] if x != 0x1C]
    seq7 = [x for x in A7S_B[0x43cda716 - BASE:0x43cda816 - BASE] if x != 0x1C]
    assert seq6 == seq7 == list(range(0x03, 0x1C))
    # y las cadenas [SAD] están intercaladas en los dos huecos
    assert cstr(0x43ce546b).startswith("[SAD] ")     # bloque A, antes de la tabla
    assert cstr(0x43ce55bc).startswith("[SAD] ")     # bloque B, tras la tabla
    assert cstr(0x43ce564c).startswith("[SAD] ")     # bloque C, tras las cadenas SA
    # la A7S/A6300 no tienen ninguna cadena [SAD] en ese tramo
    assert b"[SAD]" not in A7S_B[0x43cda6ef - BASE:0x43cda81c - BASE]
    assert b"[SAD]" not in A63_B[0x43df89bc - BASE:0x43df8960 - BASE]


# ------------------------------------------------- negativo obturador
@pytest.mark.parametrize("termino", [
    b"shutter", b"silent", b"obtur", b"expos", b"imager", b"sensor",
    b"readout", b"drive", b"brack", b"sweep", b"interval", b"still",
    b"movie", b"focus", b"aperture", b"iso",
])
def test_negativo_linea_obturador(termino):
    """Ninguna de las 45 cadenas [SAD] menciona obturacion/exposicion/sensor."""
    bloque = B[0x43ce546b - BASE:0x43ce59c1 - BASE]
    assert termino not in bloque.lower()


def test_unicas_apariciones_de_jpg():
    """Solo 4 cadenas contienen 'Jpg' y son indices de cola FIFO."""
    con_jpg = [(a, t) for a, t in CADENAS if "Jpg" in t]
    assert len(con_jpg) == 4
    assert {a for a, _ in con_jpg} == {0x43ce5724, 0x43ce5738, 0x43ce5762, 0x43ce577b}
    for _, t in con_jpg:
        assert t.startswith("[SAD] Jpg")


# ----------------------------------------------------- expansion de sigla
def test_sin_expansion_textual_de_sad():
    """No existe en el firmware ninguna cadena que exponga 'SAD' como sigla
    (RTTI, nombres de fichero o simbolos): la sigla queda SIN DESARROLLAR."""
    # 45 apariciones de 'SAD' y todas son las propias trazas [SAD]
    assert len(re.findall(rb"SAD", B)) == 45
    for m in re.finditer(rb"SAD", B):
        s = m.start()
        assert B[s - 1:s] == b"[", hex(BASE + s)
    # ni SAD_ ni _SAD ni Sad<algo>
    assert not re.search(rb"SAD_", B)
    assert not re.search(rb"_SAD", B)
    assert not re.search(rb"Sad[A-Za-z]", B)
    # el unico RTTI con 'sad' es exec_sadone de NS_SCALAR_INFRA (no es [SAD])
    assert b"N15NS_SCALAR_INFRA41ScalarInfraSequenceSaStageAutoexec_sadoneE" in B
    assert cstr(0x43ce7004).startswith("N15NS_SCALAR_INFRA")


def test_rtti_y_ficheros_vecinos_del_bloque_scalarinfra():
    """Las cadenas [SAD] son contiguas a las del bloque NS_SCALAR_INFRA."""
    assert cstr(0x43ce59d2) == "N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE"
    assert cstr(0x43ce59fd) == "ScalarInfraAsyncMain.cpp"
    assert cstr(0x43ce6c15) == "ScalarInfraSequenceSa.cpp"
    assert cstr(0x43ce6e16) == "ScalarInfraSequenceSaStage.cpp"


# ---------------------------------------------------------- artefactos
def test_cadena_peg_dec_muerta():
    """'PEG_DEC' (0x43ce5644) es una subcadena muerta: 0 referencias PIC y 0
    punteros embebidos. El ldr de 0x439a11ac NO apunta a ella."""
    assert cstr(0x43ce5640) == "SA_JPEG_DEC"
    assert cstr(0x43ce5644) == "PEG_DEC"
    gm = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
    assert hex(0x43ce5644) not in gm
    import struct as _s
    assert _s.pack("<I", 0x43ce5644) not in B
    # el ldr de 0x439a11ac resuelve a '[SAD] DbgPrt CmdRcv' (0x43ce564c)
    pool = 0x439a1594
    w = u32(pool)
    assert (w + (0x439a11b4 + 4)) & 0xFFFFFFFF == 0x43ce564c
    assert cstr(0x43ce564c) == "[SAD] DbgPrt CmdRcv"


def test_impresor_propio_del_modulo():
    """El impresor 0x439a10f0 es propio de [SAD]: id 0x93, tamaño 0x9a y
    reserva con osal_try_valloc_msg 0x435612d0."""
    # movs r2, #0x9a  (tamaño del mensaje)  -> 9a 22
    assert bytes_at(0x439a110a, 2) == bytes.fromhex("9a22")
    # bl 0x435612d0 -> osal_try_valloc_msg   -> c0 f7 df f0
    assert bytes_at(0x439a110e, 4) == bytes.fromhex("c0f7dff0")
    # el llamador pasa r0 = 0x93 (id de mensaje) -> 93 20
    assert bytes_at(0x439a11ae, 2) == bytes.fromhex("9320")


def test_json_estructurado_consistente():
    """sad.json reflects the same figures as the bytes."""
    j = json.load(open(os.path.join(HERE, "sad.json")))
    assert j["n_cadenas_totales"] == 45
    assert j["n_cadenas_con_contenido"] == 44
    assert j["n_sitios_pic_totales"] == 49
    assert j["n_funciones_emisoras"] == 5
    assert j["n_cadenas_sin_referencia"] == 0
    assert j["verificacion_pic"]["n_sitios_verificados_a_mano"] == 49
    assert j["verificacion_pic"]["n_ok"] == 49
    assert j["verificacion_pic"]["n_fallo"] == 0
    assert j["verificacion_pic"]["cotejo_con_mapa_global_repo"]["n_discrepancias"] == 0
    assert j["diferencial"]["A7S_fw320"]["ocurrencias_token"] == 0
    assert j["diferencial"]["A6300_fw201"]["ocurrencias_token"] == 0
    assert j["interes_para_la_linea_del_obturador"]["menciona_obturacion"] is False
    # el mapa funcion->traza cubre las 45 cadenas
    assert sum(len(v["trazas"]) for v in j["mapa_funcion_traza"].values()) == 45
    # cada cadena del JSON tiene su texto real en el binario
    for c in j["cadenas"]:
        assert cstr(int(c["vaddr"], 16)) == c["texto"]
