"""Tests for S134 — la aritmética de los parámetros del imager (shut/svd/shd/spl/sint/gs)."""

import json
import pathlib
import struct

import pytest
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def _data():
    with open(ROOT / BIN, "rb") as fh:
        return fh.read()


def _insn(data, vaddr, ctx=None):
    """Insn en `vaddr`. Con `ctx` se desensambla desde el inicio del contexto (para que
    capstone reconstruya los bloques IT)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ini = ctx if ctx else vaddr
    for ins in md.disasm(data[ini - BASE_VADDR:ini - BASE_VADDR + 0x400], ini):
        if ins.address == vaddr:
            return f"{ins.mnemonic} {ins.op_str}"
        if ins.address > vaddr:
            break
    return ""


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


class TestValidador:
    def test_la_funcion_de_validacion(self):
        data = _data()
        # prologo push.w {r4-r8, sb, sl, lr}: empieza por 0xE92D
        assert _u16(data, 0x4381106C) == 0xE92D

    def test_el_gs_es_el_flag_svd_igual_a_9(self):
        data = _data()
        ctx = 0x4381106C
        assert _insn(data, 0x4381118E, ctx) == "ldr.w r3, [r4, #0x1fc]"
        assert _insn(data, 0x43811192, ctx) == "cmp r3, #9"
        assert _insn(data, 0x43811196, ctx) == "subs r3, #8"
        assert _insn(data, 0x4381119A, ctx) == "movs r3, #0"
        assert _insn(data, 0x4381119C, ctx) == "strb.w r3, [sp, #0x21]"

    def test_la_formula_del_svd_esperado(self):
        data = _data()
        ctx = 0x4381106C
        assert _insn(data, 0x438110BE, ctx) == "ldr.w r0, [r4, #0x1f8]"   # shut
        assert _insn(data, 0x438110C2, ctx) == "cmp r0, #0"
        assert _insn(data, 0x438110CA, ctx) == "ldr.w r6, [r4, #0x1fc]"   # svd
        assert _insn(data, 0x438110CE, ctx) == "ldrh.w sb, [sl, #0xcc]"   # VdNum
        assert _insn(data, 0x438110D6, ctx) == "movne r6, r0"             # svd != 9 -> shut
        assert _insn(data, 0x438110D8, ctx) == "moveq r6, #1"             # svd == 9 -> 1
        assert _insn(data, 0x438110DA, ctx) == "cmp.w sb, #1"
        assert _insn(data, 0x438110E0, ctx) == "ldrb.w r0, [sl, #0x14e]"  # svr_num
        assert _insn(data, 0x438110E4, ctx) == "muls r0, r6, r0"          # shut * svr_num
        assert _insn(data, 0x438110F0, ctx) == "subs r0, #1"              # -1
        assert _insn(data, 0x438110F4, ctx) == "tst.w r0, #0x8000"        # desbordamiento

    def test_la_division_es_sin_signo(self):
        data = _data()
        assert _insn(data, 0x4355FAF0).startswith("subs r2, r1, #1")
        assert _insn(data, 0x4355FB06) == "clz r3, r0"
        assert _insn(data, 0x4355FB0A) == "clz r2, r1"

    def test_el_accesor_del_estado_es_un_singleton(self):
        data = _data()
        assert _insn(data, 0x4378F9B4) == "ldr r0, [pc, #4]"
        assert _insn(data, 0x4378F9B6) == "add r0, pc"
        assert _insn(data, 0x4378F9B8) == "bx lr"
        # el global resuelto
        w = _u32(data, 0x4378F9BC)
        assert (w + 0x4378F9BA) & 0xFFFFFFFF == 0x43E99208


class TestTrazas:
    def test_las_tres_trazas_de_validacion(self):
        data = _data()
        base = BASE_VADDR

        def cstr(va):
            off = va - base
            end = off
            while end < len(data) and data[end] != 0:
                end += 1
            return data[off:end].decode("latin1")

        assert cstr(0x43CB11D2) == (
            "[CAMERA_MAIN_SYNC]: Imager param error shut:%d, svr_num:%d, VdNum:%d")
        assert cstr(0x43CB1217) == (
            "[CAMERA_MAIN_SYNC]: Imager svd error. shut:%d, svd:%d -> %d")
        assert cstr(0x43CB1253) == (
            "[CAMERA_MAIN_SYNC]: shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d")

    def test_las_referencias_pic_de_las_trazas(self):
        with open(ROOT / "analysis" / "s106_imaging_cap" /
                  "pic_refs_strict_global.json", encoding="utf-8") as fh:
            refs = json.load(fh)
        for destino, sitio in (("0x43cb11d2", 0x4381110E),
                               ("0x43cb1217", 0x43811162),
                               ("0x43cb1253", 0x438111D4)):
            assert sitio in refs[destino], destino


class TestSinTabla:
    def test_no_hay_una_tabla_de_svd_por_drive_mode(self):
        """El svd esperado sale de una formula, no de una tabla indexada por el modo."""
        data = _data()
        # la unica lectura indexada del bloque es la del estado singleton (no una tabla)
        ctx = 0x4381106C
        assert _insn(data, 0x438110B4, ctx) == "ldr r3, [r0, #0x24]"
        assert _insn(data, 0x438110B8, ctx) == "ldm r3, {r0, r1, r2, r3}"
        assert _insn(data, 0x438110BA, ctx) == "stm.w r6, {r0, r1, r2, r3}"
