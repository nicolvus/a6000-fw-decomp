#!/usr/bin/env python3
"""DIAGNÓSTICO (G75 T70, E2E-3): réplica fuera de línea de un `avcam.jsonl` (con AVCAM_RELOJ=1 si se quiere el Master del modelo) que registra los factores de bloqueo de RelLock.

uso: AVCAM_RELOJ=1 rel_diag.py avcam.jsonl T_FIN_MS
Engancha `0x43aea1cc` (pone el bit r1 de `[RelLock+4]`: liberado) y `0x43aea1da` (lo borra: activo) y `0x4381d088` (`RelLock::IsAllowed`); imprime el instante virtual, el bit, el llamador (lr)
y, al final, la máscara. Tiene el mismo ritmo que `replica.py` (≈15 s por pasada); no modifica nada del arnés."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import liro_vm as L
import puente
from unicorn import UC_HOOK_BLOCK, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2

SET, CLR, ISALLOWED, RANURA = 0x43AEA1CC, 0x43AEA1DA, 0x4381D088, 0x43B04DCC  # RANURA: guarda r2 en la ranura r1 (this+0x48+4·r1) de RelLock
src, t_fin = sys.argv[1], float(sys.argv[2])
vm, _ = puente.arranca(None)
rd = lambda a, n=4: int.from_bytes(bytes(vm.uc.mem_read(a, n)), "little")
eventos = []


def gancho(uc, addr, size, _):
    r0, r1, lr = (uc.reg_read(x) for x in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_LR))
    if addr == RANURA:
        eventos.append((round(vm.t, 1), "ranura", f"[{r1}]={uc.reg_read(UC_ARM_REG_R2):#x}", lr))
    elif addr == ISALLOWED:
        eventos.append((round(vm.t, 1), "IsAllowed", f"this={r0:#x} tecla={r1} estado={uc.reg_read(UC_ARM_REG_R2)} mask={rd(r0 + 4):#x}", lr))
    else:
        eventos.append((round(vm.t, 1), "libera" if addr == SET else "ACTIVA", f"bit {r1} obj={r0:#x}", lr))


VENT = tuple(float(x) for x in os.environ.get("REL_VENTANA", "0,0").split(","))  # (t0, t1): con t1>0 registra las entradas de función (push) de esa ventana
entradas = {}
if VENT[1]:
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    _md, _bin = Cs(CS_ARCH_ARM, CS_MODE_THUMB), Path(__file__).resolve().parents[3] / "analysis/rea-independent/input/av-cam.bin"
    _d = _bin.read_bytes()

    cnt = [0, 1e9, 0]

    def blk(uc, addr, size, _):
        cnt[0] += 1; cnt[1] = min(cnt[1], vm.t); cnt[2] = max(cnt[2], vm.t)
        if VENT[0] <= vm.t <= VENT[1] and addr not in entradas:
            i = next(_md.disasm(_d[addr - 0x43541000 : addr - 0x43541000 + 4], addr & ~1), None)
            if i and i.mnemonic.startswith("push") and "lr" in i.op_str:
                entradas[addr] = round(vm.t, 1)
    vm.uc.hook_add(UC_HOOK_BLOCK, blk, None, 0x43541000, 0x43FE0000)
for a in (SET, CLR, ISALLOWED, RANURA):
    vm.uc.hook_add(UC_HOOK_CODE, gancho, None, a & ~1, a | 1)


def retorno(uc, addr, size, _):  # valor devuelto por las dos llamadas a IsAllowed de `0x4379e6a8` (0x4379e7e8 y 0x4379e818)
    eventos.append((round(vm.t, 1), "retorno", f"IsAllowed -> {uc.reg_read(UC_ARM_REG_R0)}", addr))


for a in (0x4379E7E8, 0x4379E818, 0x4379E86C, 0x4379E852):  # el 3.º y 4.º marcan la rama: permitido (0x3011) / bloqueado (0x3012)
    vm.uc.hook_add(UC_HOOK_CODE, retorno, None, a, a + 1)
if os.environ.get("REL_VIGILA"):  # «dir:tam» (hex): anota cada escritura del rango con el pc, el valor y el llamador
    _d, _t = (int(x, 16) for x in os.environ["REL_VIGILA"].split(":"))
    vm.uc.hook_add(UC_HOOK_MEM_WRITE, lambda uc, acc, a, sz, val, _: eventos.append((round(vm.t, 1), "escribe", f"[{a:#x}]={val & 0xFFFFFFFF:#x} pc={uc.reg_read(UC_ARM_REG_PC):#x}", uc.reg_read(UC_ARM_REG_LR))), None, _d, _d + _t - 1)


def registros():
    """Con REL_INYECTA=T_MS: tras el instante T_MS entrega además una copia de la `0x404b` del jsonl con id `0x404a` (evento 0xf de RelMgr: DIAGNÓSTICO, el emisor real no está localizado)."""
    todos = [json.loads(x) for x in open(src)]
    ini = os.environ.get("REL_INYECTA")
    if ini:
        c = next(r for r in todos if r.get("entra") == "0x40193" and r["datos"][4:8] == "4b40")
        todos.append({**c, "t": float(ini), "datos": c["datos"][:4] + "4a40" + c["datos"][8:]})
        todos.sort(key=lambda r: r["t"])
    return todos


ESC = os.environ.get("REL_ESCRIBE")  # «T_MS:dir:valor,...» (hex dir/valor): escribe 4 B en la VM al llegar a T_MS (prueba del encabezado del anillo, T85)
pend = sorted((float(a), int(b, 16), int(c, 16)) for a, b, c in (x.split(":") for x in ESC.split(","))) if ESC else []


def escribe_hasta():  # el tiempo es el virtual de la VM (vm.t), no el `t` del jsonl
    while pend and pend[0][0] <= vm.t:
        _, a, v = pend.pop(0)
        vm.uc.mem_write(a, v.to_bytes(4, "little"))
        eventos.append((round(vm.t, 1), "escribe!", f"[{a:#x}]={v:#x} (hdr0={rd(0x82D90000):#x})", 0))




def f1(uc, addr, size, _):  # entrada de 0x43b04bac (factor 1): anillo, encabezado compartido y contador
    r0, r1 = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)
    ctl = rd(r0)
    eventos.append((round(vm.t, 1), "factor1", f"ring={r0:#x} ctl={ctl:#x} [ctl]={[hex(rd(ctl + 4 * i)) for i in range(4)]} ring+4={rd(r0 + 4):#x} +8={rd(r0 + 8):#x} +c={rd(r0 + 0xC, 1):#x} +d={rd(r0 + 0xD, 1):#x} n={r1}", uc.reg_read(UC_ARM_REG_LR)))


vm.uc.hook_add(UC_HOOK_CODE, f1, None, 0x43B04BAC, 0x43B04BAD)
for _a in filter(None, os.environ.get("REL_PCS", "").split(",")):  # direcciones Thumb (hex) cuya ejecución se anota
    vm.uc.hook_add(UC_HOOK_CODE, lambda uc, a, sz, _: eventos.append((round(vm.t, 1), "pc", f"{a:#x} r0={uc.reg_read(UC_ARM_REG_R0):#x}", uc.reg_read(UC_ARM_REG_LR))), None, int(_a, 16) & ~1, int(_a, 16) | 1)
for r in registros():
    if "entra" not in r:
        continue
    if r["t"] > t_fin:
        break
    vm.limite = r["t"]
    L.planifica(vm, int(os.environ.get("REL_PASO", 20_000_000)))
    escribe_hasta()
    d = bytes.fromhex(r["datos"])
    m = vm.malloc(max(len(d), 0x40) + 12 + 0x20) + 12
    vm.uc.mem_write(m - 12, bytes.fromhex(r["cab"]))
    vm.uc.mem_write(m, d)
    vm.msz[m] = len(d)
    L.entrega(vm, int(r["entra"], 16), m)
vm.limite = t_fin
L.planifica(vm, 4 * int(os.environ.get("REL_PASO", 20_000_000)))
ult = {}
for t, k, txt, lr in eventos:
    if k == "IsAllowed" or ult.get((k, txt)) is None or t > 12000:
        print(f"{t:9.1f} {k:9s} {txt} lr={lr:#x}")
    ult[(k, txt)] = t
print("salidas a 0x30001 tras 17400:", [(round(x[0]), x[4][:12]) for x in vm.salida_ext if x[3] == 0x30001 and x[0] > 17400][:8])
print("últimas salidas:", [(round(x[0]), hex(x[3]), str(x[4])[:24]) for x in vm.salida_ext][-12:])
print("a 0x30001/0x3011:", [(round(x[0]), hex(x[3]), str(x[4])[:24]) for x in vm.salida_ext if x[3] in (0x30001, 0x3009) or "1130" in str(x[4])[:8]][-10:])
print("vm.t final", round(vm.t), "salidas no-AE tras el último IsAllowed:", [(round(x[0]), hex(x[3]), str(x[4])[:20]) for x in vm.salida_ext if x[3] != 0x20002 and x[0] > 23000][:20])
print("máscara final", hex(rd(0x43EA03EC)), "modo", hex(rd(0x43F68C92, 2)), "[0x43ede338]", hex(rd(0x43EDE338)))
for a, t in entradas.items():
    print(f"entrada {a:#x} t={t}")
print("bloques", cnt if VENT[1] else "")
