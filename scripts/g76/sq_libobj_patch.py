#!/usr/bin/env python3
"""G76 VFR-F2 — ajuste «S&Q» de la carpeta CFW: una cueva en `libObj` 3.21 manda lo mismo que el modelo MOVIE_REC_O_U_CRANK de Sony al activarse.

Mensajes (como `0x60040c`, `0x604800` y `0x60051c`, con las conversiones de UI `0x5f7e2c`/`0x5f7f16`):
  - ObjCamera (objeto 8, asíncrono): ObjMsg(0x3100, MSGID_SET_O_U_CRANK_MODE_CMD 0x75e4) + PARAMID_O_U_CRANK_MODE 0x971a (OFF 0x205 / ON 0x206)
    + PARAMID_O_U_CRANK_FRAME_RATE 0x971b (VALUEID por índice de UI: 0x207…0x20d, 0x3e2 = 120/100);
  - MovieRecorder (objeto 0xa, síncrono como 0x604800): ObjMsg(0x3300, 0x1005) + 0xc001 (modo 0/1) + 0xc002 (código 0…7; el índice 8 = 120/100 → 0, como Sony);
  - Effect (objeto 9, asíncrono): ObjMsg(0x3900, 0x3015) + 0x1013 (bool = modo).
Gancho: el `bl 0x67a340` de entrada de 0x683e60 (función de ModelStillRec que la UI ejecuta al salir del menú, medido en el arnés: `IssueCommandAsync`
ra = libObj+0x683efd), mismo patrón que g68. La cueva guarda r0-r3/sp (0x67a340 recibe un 5.º argumento en [sp]), lee el ajuste y solo envía si cambió
respecto al último enviado (celda en la cola del .bss, `CTR + 8` de g61), así que Off manda OFF una vez y el resto de las veces no manda nada (= fábrica).
Cueva: +0x900…+0xC00 de la función muerta 0x2648d8 (g61 usa +0x000…+0x500, g68 +0x600…+0x800).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61")]
import cfw_ajustes as cfw
import intervalo_patch as g61
from e25_24.thumb import bl

SRC = g61.SRC
HOOK = (0x683E78, bytes.fromhex("f6f762fa"))     # bl 0x67a340
DESTINO = 0x67A340
CAVE, CAVE_FIN = 0x2648D8 + 0x900, 0x2648D8 + 0xC00
CELDA = g61.CTR + 8
PLT_BOOL, PLT_DTOR_B, PLT_MSGOUT, PLT_SYNC = 0xDF460, 0xE2504, 0xDE4CC, 0xDEC0C   # ParamStd<bool>, su dtor, ObjMsg() vacío, IssueCommandSync
CAM_VID = (0x207, 0x208, 0x209, 0x20A, 0x20B, 0x20C, 0x20D, 0x207, 0x3E2)        # 0x5f7e2c por índice de UI 0…8
MR_COD = (0, 1, 2, 3, 4, 5, 6, 7, 0)                                              # 0x5f7f16 (8 → 0)
MSG_CAM, P_MODO, P_FR, ON, OFF = 0x75E4, 0x971A, 0x971B, 0x206, 0x205


def asm() -> str:
    a = cfw.POR_ID["sq"]
    P = g61
    return f"""
        push.w {{r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}}
        sub sp, #0x40
        {cfw.leer_asm(a, "tq", g61.BLX_BACKUP)}
        mov r4, r0
        adr.w r0, lit
        ldr r1, [r0]
        add r0, r1
        adds r0, #8
        mov r8, r0
        ldr r1, [r0]
        cmp r1, r4
        beq.w sal
        str r4, [r0]
        subs r5, r4, #1
        it lo
        movlo r5, #0
        cmp r4, #0
        ite ne
        movne r6, #{ON:#x}
        moveq r6, #{OFF:#x}
        adr.w r0, tcam
        ldrh.w r7, [r0, r5, lsl #1]
        add r0, sp, #0
        mov.w r1, #0x3100
        movw r2, #{MSG_CAM:#x}
        @@blx {P.PLT_MSG:#x}
        add r0, sp, #0x10
        mov r1, r6
        @@blx {P.PLT_INT:#x}
        add r0, sp, #0
        movw r1, #{P_MODO:#x}
        add r2, sp, #0x10
        @@blx {P.PLT_ADD:#x}
        add r0, sp, #0x10
        @@blx {P.PLT_DTOR_P:#x}
        add r0, sp, #0x10
        mov r1, r7
        @@blx {P.PLT_INT:#x}
        add r0, sp, #0
        movw r1, #{P_FR:#x}
        add r2, sp, #0x10
        @@blx {P.PLT_ADD:#x}
        add r0, sp, #0x10
        @@blx {P.PLT_DTOR_P:#x}
        movs r0, #8
        @@bl {P.OBJ_DE:#x}
        add r1, sp, #0
        @@blx {P.PLT_ISSUE:#x}
        add r0, sp, #0
        @@blx {P.PLT_DTOR_M:#x}
        adr.w r0, tmr
        ldrb r7, [r0, r5]
        cmp r4, #0
        ite ne
        movne r6, #1
        moveq r6, #0
        add r0, sp, #0x30
        @@blx {PLT_MSGOUT:#x}
        add r0, sp, #0
        mov.w r1, #0x3300
        movw r2, #0x1005
        @@blx {P.PLT_MSG:#x}
        add r0, sp, #0x10
        mov r1, r6
        @@blx {P.PLT_INT:#x}
        add r0, sp, #0
        movw r1, #0xc001
        add r2, sp, #0x10
        @@blx {P.PLT_ADD:#x}
        add r0, sp, #0x10
        @@blx {P.PLT_DTOR_P:#x}
        add r0, sp, #0x10
        mov r1, r7
        @@blx {P.PLT_INT:#x}
        add r0, sp, #0
        movw r1, #0xc002
        add r2, sp, #0x10
        @@blx {P.PLT_ADD:#x}
        add r0, sp, #0x10
        @@blx {P.PLT_DTOR_P:#x}
        movs r0, #0xa
        @@bl {P.OBJ_DE:#x}
        add r1, sp, #0
        add r2, sp, #0x30
        @@blx {PLT_SYNC:#x}
        add r0, sp, #0
        @@blx {P.PLT_DTOR_M:#x}
        add r0, sp, #0x30
        @@blx {P.PLT_DTOR_M:#x}
        add r0, sp, #0
        mov.w r1, #0x3900
        movw r2, #0x3015
        @@blx {P.PLT_MSG:#x}
        add r0, sp, #0x10
        mov r1, r6
        @@blx {PLT_BOOL:#x}
        add r0, sp, #0
        movw r1, #0x1013
        add r2, sp, #0x10
        @@blx {P.PLT_ADD:#x}
        add r0, sp, #0x10
        @@blx {PLT_DTOR_B:#x}
        movs r0, #9
        @@bl {P.OBJ_DE:#x}
        add r1, sp, #0
        @@blx {P.PLT_ISSUE:#x}
        add r0, sp, #0
        @@blx {P.PLT_DTOR_M:#x}
    sal:
        add sp, #0x40
        pop.w {{r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}}
        @@b.w {DESTINO:#x}
        .align 2
    tcam:
        {"".join(f".short {v:#x}{chr(10)}        " for v in CAM_VID)}
    tmr:
        {"".join(f".byte {v}{chr(10)}        " for v in MR_COD)}
        .align 2
    lit:
        .word @DELTA@
    """


def apply_bytes(data: bytes) -> bytes:
    a, old = HOOK
    if data[a:a + 4] != old:
        raise ValueError(f"gancho {a:#x} distinto del original")
    code = g61._ens(asm(), CAVE)
    assert CAVE + len(code) <= CAVE_FIN, hex(CAVE + len(code))
    out = bytearray(data)
    out[CAVE:CAVE + len(code)] = code
    out[a:a + 4] = bl(a, CAVE)
    return bytes(out)
