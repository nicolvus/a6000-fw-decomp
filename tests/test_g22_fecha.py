"""G22-FECHA — página «Ajuste fecha/hora → Fecha/Hora»: el reloj del anfitrión llega al widget.

Qué se fija aquí (informe: `docs/gui/g22-fecha-hora.md`):

1. `live.msg_hora` manda al invitado la hora **de pared** del anfitrión («T época_local_hex»): época UTC + desfase
   de la zona, que es lo que el shim usa como base (`date_base`) y lo que devuelve en la orden 2 de `0x90013d`.
2. El shim responde `ViewBase::getModelInfo("@M018"/"model/CLOCK", info 0/1)` **sólo si la llamada real falla**
   (en el arnés `ModelClock` no existe) y con las mismas claves que rellena `ModelClock::onGetInfo`.
3. Contraste con los bytes del firmware 3.21: las claves/orden que usa `ModelClock::onGetInfo` (`libObj+0x4f1250`)
   son `0x100` (válida) y `0x101…0x106` (año, mes, día, hora, min, seg), y el widget `PAS_BtnDateTime`
   (`viewUnified2+0x2e2e10`) lee el año como u16 y lo acota a `0x833` (2099).

Los puntos marcados «bytes» se saltan si no está el firmware extraído en el árbol.
"""
from __future__ import annotations

import os
import struct
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
SHIM = ROOT / "scripts/gui/harness/shim/sonyshim.c"
# El firmware 3.21 extraído del arnés (stage) o el del paquete de firmas del repo.
LIBOB = (ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib/libObj.so",
         ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
                "/nflasha7_unpacked_unpacked/lib/libObj.so")
VIEWU6 = (ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib/viewUnified6.so",
          ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
                 "/nflasha7_unpacked_unpacked/lib/viewUnified6.so")
VIEWU2 = (ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib/viewUnified2.so",
          ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
                 "/nflasha7_unpacked_unpacked/lib/viewUnified2.so")


def binario(candidatos: tuple[Path, ...]) -> Path:
    for p in candidatos:
        if p.exists():
            return p
    pytest.skip("firmware 3.21 no extraído en este árbol")


def test_msg_hora_lleva_la_hora_de_pared_del_anfitrion() -> None:
    """«T <hex>»: la época que viaja es la UTC más el desfase de la zona, avanzada con el reloj monotónico del invitado."""
    sys.path.insert(0, str(HARNESS))
    import live

    tz_previo = os.environ.get("TZ")
    try:
        for zona, desfase in (("UTC0", 0), ("America/Argentina/Buenos_Aires", -3 * 3600), ("Asia/Tokyo", 9 * 3600)):
            os.environ["TZ"] = zona
            time.tzset()
            ahora = 1_700_000_000.0
            linea = live.msg_hora(ahora)
            assert linea.startswith(b"T ") and linea.endswith(b"\n"), linea
            enviado = int(linea[2:-1], 16)
            assert enviado == int(ahora) + desfase, (zona, hex(enviado))
            # el shim hace gmtime_r(date_local()): la hora de pared reconstruida tiene que ser la del anfitrión
            pared, reloj = time.gmtime(enviado), time.localtime(ahora)
            assert (pared.tm_hour, pared.tm_min, pared.tm_mday) == (reloj.tm_hour, reloj.tm_min, reloj.tm_mday)
    finally:
        if tz_previo is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = tz_previo
        time.tzset()


def test_msg_hora_sin_desfase_coincide_con_la_epoca_utc() -> None:
    sys.path.insert(0, str(HARNESS))
    import live

    tz_previo = os.environ.get("TZ")
    try:
        os.environ["TZ"] = "UTC0"
        time.tzset()
        assert int(live.msg_hora(1_700_000_000.0)[2:-1], 16) == 1_700_000_000
    finally:
        if tz_previo is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = tz_previo
        time.tzset()


def test_shim_responde_el_reloj_solo_cuando_el_modelo_falla() -> None:
    """Si `ModelClock` existiera, la llamada real devuelve 1 y el relleno no se ejecuta: es un respaldo, no un atajo ciego."""
    src = SHIM.read_text()
    assert '(!strcmp(name, "@M018") || !strcmp(name, "model/CLOCK"))' in src
    assert "(info == 0 || info == 1)" in src
    assert "static int reloj_params(void *list, int info)" in src
    # la condición cuelga de `!r` (fallo del modelo real) y de la fuente de hora del anfitrión
    assert src.index("if (!r && real && readable(name)") < src.index("reloj_params(list, info))")
    bloque = src[src.index("static int reloj_params"):src.index("/* ViewBase::getModelInfo(")]
    assert "date_local()" in bloque and "gmtime_r" in bloque
    assert '_ZN9ParamList3addEmP9ParamBase' in bloque and "0xf0fb0" in bloque  # Param<int>(int) del propio libObj
    assert "0xe50e8" in bloque and "ctbool(p," in bloque                      # 0x100 va como PrmBool (tipo 5), no Param<int>
    assert "(unsigned long)(0x101 + i)" in bloque                             # año..seg en orden, como el modelo
    assert "RELOJEMU" in src                                                  # se puede apagar (medir el «antes» en la misma sesión)


def test_claves_del_reloj_iguales_a_las_de_modelclock_en_los_bytes() -> None:
    """`ModelClock::onGetInfo` (libObj+0x4f1250) añade 0x100 y 0x101…0x106, en ese orden.

    Las palabras están comprobadas con `llvm-objdump -d --triple=thumbv7-none-eabi --start-address=0x4f20d8
    --stop-address=0x4f2130 libObj.so`: `mov.w r1,#0x100`, `movw r1,#0x101`, `mov.w r1,#0x102`, `movw r1,#0x103`,
    `mov.w r1,#0x104`, `movw r1,#0x105`, `mov.w r1,#0x106`, cada una seguida de `mov r2,rX` y `blx ParamList::add`.
    """
    b = binario(LIBOB).read_bytes()
    esperado = [(0x4F20DA, 0xF44F, 0x7180), (0x4F20E6, 0xF240, 0x1101), (0x4F20F2, 0xF44F, 0x7181),
                (0x4F20FE, 0xF240, 0x1103), (0x4F210A, 0xF44F, 0x7182), (0x4F2116, 0xF240, 0x1105),
                (0x4F2122, 0xF44F, 0x7183)]
    for off, h1, h2 in esperado:
        assert struct.unpack_from("<HH", b, off) == (h1, h2), hex(off)
    assert struct.unpack_from("<HH", b, 0x4F20E0) == (0xF7ED, 0xE66E)  # blx <ParamList::add@plt>


def test_widget_lee_el_anio_como_u16_y_lo_acota_a_2099() -> None:
    """`PAS_BtnDateTime::set...` (viewUnified2+0x2e2e10): año = ldrh.w del primer campo; límite 0x833 = 2099; día ≤ 0x1f; min ≤ 0x3c."""
    b = binario(VIEWU2).read_bytes()
    assert struct.unpack_from("<H", b, 0x2E2E10)[0] == 0xE92D          # push.w (entrada Thumb de la función)
    assert struct.unpack_from("<HH", b, 0x2E2E2A) == (0xF8B7, 0x9000)  # ldrh.w r9,[r7]      → año u16
    assert struct.unpack_from("<HH", b, 0x2E2E2E) == (0xF640, 0x0333)  # movw  r3,#0x833     → 2099
    assert struct.unpack_from("<HH", b, 0x2E2E40) == (0xF1B8, 0x0F1F)  # cmp.w r8,#0x1f      → día ≤ 31
    assert struct.unpack_from("<H", b, 0x2E2E46)[0] == 0x2E3C          # cmp   r6,#0x3c      → min ≤ 60


def test_la_vista_pide_0x100_como_prmbool_y_0x101_como_param_int() -> None:
    """`ViewDateSet` (viewUnified6+0x28ca6…0x28ccc) pide **tipo 5** para 0x100 y **tipo 1** para 0x101.

    Los trampolines locales del `.text` ponen el tipo y saltan al PLT de `ParamList::get`:
    `0x12260: push; movs r2,#5; pop; b.w 0xf51c` (get con tipo 5 → `PrmBool`) y
    `0x12276: push; movs r2,#1; pop; b.w 0xf51c` (tipo 1 → `Param<int>`). Con 0x100 creado como `Param<int>` la vista
    no rellena los campos y la página vuelve a `31-12-2037`: medido.
    """
    b = binario(VIEWU6).read_bytes()
    assert struct.unpack_from("<HH", b, 0x28CA8) == (0xF44F, 0x7180)  # mov.w  r1,#0x100
    assert struct.unpack_from("<HH", b, 0x28CAC) == (0xF7E9, 0xFAD8)  # bl     0x12260  (get con tipo 5)
    assert struct.unpack_from("<HH", b, 0x12262) == (0x2205, 0xAF00)  # movs   r2,#5
    assert struct.unpack_from("<HH", b, 0x1226A) == (0xF7FD, 0xB957)  # b.w    <ParamList::get@plt>
    assert struct.unpack_from("<HH", b, 0x28CBE) == (0xF240, 0x1101)  # movw   r1,#0x101
    assert struct.unpack_from("<HH", b, 0x28CC2) == (0xF7E9, 0xFAD8)  # bl     0x12276  (get con tipo 1)
    assert struct.unpack_from("<HH", b, 0x12278) == (0x2201, 0xAF00)  # movs   r2,#1


# Los dos extremos con los que `ViewDateSet` recorta la fecha, LEÍDOS del perfil (`bk.tbl`) y de la NVRAM de fábrica:
# `0x107004d` = fb 7e 3f d7 1f 00 00 00 → 2037-12-31 23:59:59 con el desempaquetado de `viewUnified6+0x29260`.
NVRAM = [2037, 12, 31, 23, 59, 59]


def recorta(actual: list[int], inicial: list[int], maximo: list[int] = NVRAM) -> list[int]:
    """Modelo del recorte de `viewUnified6+0x29582…0x295ec`: **satura al extremo contrario**.

    ```
    29588: cmp r1, r3        ; r1 = campo actual, r3 = campo del MÁXIMO (NVRAM)
    2958a: ble 0x29590
    2958c: str r2, [r4]      ; actual > máximo → toma el MÍNIMO (info 1)
    29590: cmp r1, r2
    29592: it lt
    29594: strlt r3, [r4]    ; actual < mínimo → toma el MÁXIMO (NVRAM)
    ```
    """
    return [i if a > n else n if a < i else a for a, i, n in zip(actual, inicial, maximo)]


def test_el_recorte_de_la_vista_satura_al_extremo_contrario() -> None:
    """Bytes del recorte y su efecto: por eso la info 1 tiene que ser la medianoche del día del anfitrión."""
    b = binario(VIEWU6).read_bytes()
    for off, hw in ((0x2958C, 0x6022), (0x29594, 0x6023), (0x295A0, 0x6062), (0x295A8, 0x6063),
                    (0x295E4, 0x6162), (0x295EC, 0x6163)):
        assert struct.unpack_from("<H", b, off)[0] == hw, hex(off)  # str / strlt cruzados, año y minuto
    actual = [2026, 11, 26, 2, 7, 53]  # medido: info 0 = 2026-11-26 02:07:53
    primera_t = [2026, 11, 26, 1, 50, 17]  # lo que entregaba la info 1 antes (primera «T»): el minuto 7 < 50
    assert recorta(actual, primera_t) == [2026, 11, 26, 2, 59, 53]  # el minuto salía 59 (medido en pantalla)
    medianoche = [2026, 11, 26, 0, 0, 0]  # lo que entrega ahora la info 1
    assert recorta(actual, medianoche) == actual
    # El defecto original (objeto a cero porque `reload` aborta) satura al máximo de la NVRAM; con la fecha inicial a
    # medianoche los campos de hora/min/seg no saturan (0 no es menor que 0) y sale exactamente el `31-12-2037 0:00`
    # que documenta la fila G22-E.
    assert recorta([0, 0, 0, 0, 0, 0], primera_t) == NVRAM
    assert recorta([0, 0, 0, 0, 0, 0], medianoche) == [2037, 12, 31, 0, 0, 0]
