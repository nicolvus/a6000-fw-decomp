#!/usr/bin/env python3
"""LIRO VM: ejecuta av-cam.bin (LIRO, fw 3.21) en Unicorn con la API que le da liro.ko (paso 1 de la emulación de av-cam).

uso: liro_vm.py [--avcam av-cam.bin] [--bk bk.tbl] [--pasos N] [--informe salida.json]

Cómo lo carga la cámara (liro.ko, VERIFICADO, docs/capture/s20-mailbox40193-osal-architecture.md y avcam-liro-vm.md):
  blob en VA 0x43541000; cabecera +4 «LIRO», +8 versión 4, +0xc entry(pre), +0x10 entry(main), +0x14 → descriptor;
  memcpy(descriptor+0x24, tabla, 0x344): 209 punteros (μITRON 4 + OSAL + Backup + arch_*), orden de .init.data de liro.ko;
  entry(pre)(0) en un kthread, luego entry(main) en otro.
Aquí cada puntero de la tabla apunta a una trampa (TRAP_BASE + 4·i) que atiende Python; las tareas μITRON son contextos de
Unicorn con planificador cooperativo (se cambia en cada llamada bloqueante o tras un cupo de instrucciones) y tiempo virtual.
El hardware no está emulado: toda lectura/escritura fuera de lo mapeado crea una página a cero y queda registrada (MMIO).
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
from dataclasses import dataclass, field
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_FETCH_UNMAPPED,
    UC_HOOK_MEM_READ,
    UC_HOOK_MEM_READ_UNMAPPED,
    UC_HOOK_MEM_WRITE_UNMAPPED,
    UC_MODE_ARM,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_C1_C0_2,
    UC_ARM_REG_CPSR,
    UC_ARM_REG_FPEXC,
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
    UC_CPU_ARM_CORTEX_A15,
)

REPO = Path(__file__).resolve().parents[3]
AVCAM = REPO / "analysis/rea-independent/input/av-cam.bin"
LIRO_KO = REPO / "analysis/camera-extract/usr/kmod/liro.ko"
BK = REPO / "analysis/gui/g22/harness/overlay/cam/usr/share/bk.tbl"
REGLAS = Path(__file__).with_name("mmio_reglas.json")

BASE, IMG_LO, IMG_SZ = 0x43541000, 0x43540000, 0x00D00000   # imagen + .data/.bss (hasta 0x44240000)
TRAP_BASE, NAPI = 0xFFF00000, 209
TASK_EXIT = TRAP_BASE + 4 * NAPI                              # retorno de una tarea / entrada → fin
HEAP, HEAP_SZ = 0x50000000, 0x0C000000
STACKS, STACK_SZ = 0x60000000, 0x10000
STACK_MAP = 0x04000000                                        # 1024 pilas de 64 KiB
E_OK, E_TMOUT, E_NOEXS, E_PAR = 0, -50, -42, -17
TMO_POL, TMO_FEVR = 0, -1
QUANTUM = 200_000                                             # instrucciones por turno antes de ceder


def api_names() -> list[str]:
    """Orden de la tabla: relocalizaciones de .init.data de liro.ko (offset/4 → símbolo); huecos = None."""
    import subprocess
    out = subprocess.run(["readelf", "-rW", str(LIRO_KO)], capture_output=True, text=True, check=True).stdout
    names: list[str] = [""] * NAPI
    sec = False
    for ln in out.splitlines():
        if "'.rel.init.data'" in ln:
            sec = True
            continue
        if sec and ln.startswith("Relocation section"):
            break
        p = ln.split()
        if sec and len(p) >= 5 and all(c in "0123456789abcdef" for c in p[0]):
            names[int(p[0], 16) // 4] = p[4]
    return names


@dataclass
class Task:
    tid: int
    name: str
    entry: int
    pri: int
    ctx: object = None
    estado: str = "dormida"          # dormida | lista | espera | fin
    espera: tuple = ()               # (tipo, objeto, …)
    despertar: float | None = None   # tiempo virtual (ms) de fin de espera
    ret: int | None = None           # r0 al reanudar tras una espera (None = no tocar r0)
    act: int = 0                     # activaciones encoladas (act_tsk)
    pasos: int = 0


@dataclass
class Vm:
    uc: Uc
    names: list[str]
    bk: dict[int, bytes]
    tasks: dict[int, Task] = field(default_factory=dict)
    sems: dict[int, list] = field(default_factory=dict)     # id → [cuenta, máx]
    flgs: dict[int, int] = field(default_factory=dict)
    mbxs: dict[int, collections.deque] = field(default_factory=dict)
    mbfs: dict[int, collections.deque] = field(default_factory=dict)
    slots: dict[int, int] = field(default_factory=dict)
    libres: list[int] = field(default_factory=list)
    nslots: int = 0
    ncb: int = 0
    queues: dict[int, collections.deque] = field(default_factory=dict)   # colas OSAL locales (por qid)
    qcb: dict[int, tuple] = field(default_factory=dict)                   # qid → (callback, arg)
    cycs: dict[int, list] = field(default_factory=dict)                   # id → [handler, periodo, prox, activo, exinf]
    inh: dict[int, int] = field(default_factory=dict)                     # interrupción → manejador (def_inh)
    t: float = 0.0
    heap: int = HEAP
    cur: Task | None = None
    calls: collections.Counter = field(default_factory=collections.Counter)
    mmio: dict[int, list] = field(default_factory=dict)                   # página → [lecturas, escrituras, primer pc]
    log: list[str] = field(default_factory=list)
    salida_ext: list = field(default_factory=list)                        # mensajes a colas que no son de av-cam
    pcs: collections.Counter = field(default_factory=collections.Counter)  # PC al agotar el cupo (dónde gira una tarea)
    ultimas: collections.deque = field(default_factory=lambda: collections.deque(maxlen=40))  # últimas llamadas a la API
    next_id: int = 0x100
    dmm_n: int = 0
    dyn_n: int = 0
    pendientes_cb: list = field(default_factory=list)  # callbacks de cola por ejecutar (tareas efímeras)
    trampa: int | None = None
    fallo: str = ""

    # --- memoria y registros
    def r(self, n: int) -> int:
        return self.uc.reg_read([UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3][n])

    def arg(self, n: int) -> int:
        if n < 4:
            return self.r(n)
        sp = self.uc.reg_read(UC_ARM_REG_SP)
        return struct.unpack("<I", self.uc.mem_read(sp + 4 * (n - 4), 4))[0]

    def rd(self, a: int, n: int = 4) -> int:
        return int.from_bytes(self.uc.mem_read(a, n), "little")

    def wr(self, a: int, v: int, n: int = 4) -> None:
        self.uc.mem_write(a, (v & ((1 << 8 * n) - 1)).to_bytes(n, "little"))

    def cstr(self, a: int, n: int = 200) -> str:
        try:
            b = bytes(self.uc.mem_read(a, n))
        except UcError:
            return f"<{a:#x}>"
        return b.split(b"\0")[0].decode("latin-1")

    def malloc(self, n: int) -> int:
        a = self.heap
        self.heap = (self.heap + n + 15) & ~15
        if self.heap > HEAP + HEAP_SZ:
            raise MemoryError("montón agotado")
        return a

    def nuevo_id(self) -> int:
        self.next_id += 1
        return self.next_id


def carga(avcam: Path, bkp: Path) -> Vm:
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_A15)  # BIONZ X: Cortex-A (NEON/VFPv4); la CPU por omisión de Unicorn no trae VFP
    uc.mem_map(IMG_LO, IMG_SZ)
    img = avcam.read_bytes()
    uc.mem_write(BASE, img)
    assert img[4:8] == b"ORIL" and struct.unpack_from("<I", img, 8)[0] == 4, "cabecera LIRO inesperada"
    uc.mem_map(TRAP_BASE, 0x1000)
    uc.mem_write(TRAP_BASE, b"\x1e\xff\x2f\xe1" * (NAPI + 1))  # bx lr (nunca se ejecuta: la trampa para antes)
    uc.mem_map(HEAP, HEAP_SZ)
    uc.mem_map(STACKS, STACK_MAP)
    uc.mem_map(0x80000000, 0x04000000)  # shortcut: RAM física (gl_common/ISP, p. ej. 0x82d90000) como memoria llana; el mapa real está en DmmConfig.bin (ausente)
    names = api_names()
    desc = struct.unpack_from("<I", img, 0x14)[0]
    uc.mem_write(desc + 0x24, b"".join(struct.pack("<I", TRAP_BASE + 4 * i if names[i] else 0) for i in range(NAPI)))
    bk: dict[int, bytes] = {}
    if bkp.exists():
        d, o = bkp.read_bytes(), 0
        while o + 8 <= len(d):
            i, n = struct.unpack_from("<II", d, o)
            bk[i] = d[o + 8:o + 8 + n]
            o += 8 + n + (-n % 4)
    vm = Vm(uc, names, bk)

    def h_code(uc: Uc, addr: int, size: int, _: object) -> None:
        vm.trampa = (addr - TRAP_BASE) // 4
        uc.emu_stop()
    uc.hook_add(UC_HOOK_CODE, h_code, None, TRAP_BASE, TRAP_BASE + 4 * NAPI + 3)

    def h_unmapped(uc: Uc, acc: int, addr: int, size: int, val: int, _: object) -> bool:
        pc = uc.reg_read(UC_ARM_REG_PC)
        if acc == UC_HOOK_MEM_FETCH_UNMAPPED or addr < 0xE0000000:  # solo la zona de periféricos se crea a demanda; lo demás es un fallo
            vm.fallo = f"acceso inválido {addr:#x} desde pc={pc:#x}"
            return False
        pg = addr & ~0xFFF
        uc.mem_map(pg, 0x1000)
        vm.mmio[pg] = [0, 0, pc]
        return True
    uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, h_unmapped)
    # registros con regla: la página se mapea ya y cada lectura aplica (valor & ~y) | o antes de leerse
    for rg in json.loads(REGLAS.read_text())["reglas"]:
        dr, o, y = int(rg["dir"], 16), int(rg.get("o", "0"), 16), int(rg.get("y", "0"), 16)
        pg = dr & ~0xFFF
        if pg not in vm.mmio:
            uc.mem_map(pg, 0x1000)
            vm.mmio[pg] = [0, 0, 0]

        def h_regla(uc: Uc, acc: int, addr: int, size: int, val: int, r: tuple) -> None:
            v = int.from_bytes(uc.mem_read(r[0], 4), "little")
            uc.mem_write(r[0], ((v & ~r[2]) | r[1]).to_bytes(4, "little"))
        uc.hook_add(UC_HOOK_MEM_READ, h_regla, (dr, o, y), dr, dr + 3)
    # patrones: mismo registro (desplazamiento dentro de la página) en todos los bloques de un rango
    for pt in json.loads(REGLAS.read_text()).get("patrones", []):
        lo, hi, desp = int(pt["rango"][0], 16), int(pt["rango"][1], 16), int(pt["desp"], 16)
        o, y = int(pt.get("o", "0"), 16), int(pt.get("y", "0"), 16)

        def h_patron(uc: Uc, acc: int, addr: int, size: int, val: int, r: tuple) -> None:
            if addr & 0xFFF == r[0]:
                v = int.from_bytes(uc.mem_read(addr, 4), "little")
                uc.mem_write(addr, ((v & ~r[2]) | r[1]).to_bytes(4, "little"))
        uc.hook_add(UC_HOOK_MEM_READ, h_patron, (desp, o, y), lo, hi - 1)
    return vm


def crea_tarea(vm: Vm, tid: int, name: str, entry: int, pri: int, r0: int = 0) -> Task:
    previo = vm.uc.context_save()
    t = Task(tid, name, entry, pri)
    if tid not in vm.slots:  # una pila por tarea (reiniciarla la reutiliza); las efímeras (cb/cyc) devuelven la suya al terminar
        vm.slots[tid] = vm.libres.pop() if vm.libres else vm.nslots + 1
        vm.nslots = max(vm.nslots, vm.slots[tid])
    sp = STACKS + STACK_MAP - STACK_SZ * vm.slots[tid]
    uc = vm.uc
    uc.reg_write(UC_ARM_REG_SP, sp)
    uc.reg_write(UC_ARM_REG_LR, TASK_EXIT)
    uc.reg_write(UC_ARM_REG_R0, r0)
    uc.reg_write(UC_ARM_REG_PC, entry)  # Unicorn fija el modo Thumb con el bit 0 del PC
    uc.reg_write(UC_ARM_REG_C1_C0_2, uc.reg_read(UC_ARM_REG_C1_C0_2) | (0xF << 20))  # CPACR: cp10/cp11 habilitados
    uc.reg_write(UC_ARM_REG_FPEXC, 0x40000000)                                        # FPEXC.EN: VFP/NEON activos (como en el kernel)
    t.ctx = uc.context_save()
    uc.context_restore(previo)
    vm.tasks[tid] = t
    return t


# --- API: cada función devuelve el r0 o None si la tarea queda bloqueada (el valor llega al despertar)
def api(vm: Vm, i: int) -> int | None:
    n, a = vm.names[i], vm.arg
    vm.calls[n] += 1
    t = vm.cur
    assert t is not None
    vm.ultimas.append(f"{t.name if t else '?'} {n}({', '.join(hex(vm.r(k)) for k in range(4))}) lr={vm.uc.reg_read(UC_ARM_REG_LR):#x}")
    if n in ("CRE_TSK", "cre_tsk", "acre_tsk", "CRE_CYC", "cre_cyc", "acre_cyc", "CRE_SEM", "CRE_FLG", "CRE_MBX") and vm.calls[n] <= 3:
        crudo = [vm.r(k) for k in range(4)]
        pk = crudo[1] if n.isupper() or n.startswith("cre") else crudo[0]
        try:
            pal = [vm.rd(pk + 4 * k) for k in range(8)]
        except UcError:
            pal = []
        vm.log.append(f"CRUDO {n} r0-r3={[hex(x) for x in crudo]} pk={[hex(x) for x in pal]}")
    assert t is not None

    def bloquea(tipo: tuple, tmo: int) -> int | None:
        if tmo == TMO_POL:
            return E_TMOUT
        t.estado, t.espera = "espera", tipo
        t.despertar = None if tmo == TMO_FEVR else vm.t + tmo
        return None

    if n in ("cre_tsk", "CRE_TSK", "acre_tsk"):
        if n == "acre_tsk":
            tid, pk = vm.nuevo_id(), a(0)
        else:
            tid, pk = a(0), a(1) + (0x44 if n == "CRE_TSK" else 0)  # CRE_TSK recibe el bloque de control de liro.ko: T_CTSK en +0x44 (0x2328)
        # T_CTSK (μITRON 4): tskatr, exinf, task, itskpri, stksz, stk[, nombre]
        atr, exinf, entry, pri = (vm.rd(pk + 4 * k) for k in range(4))
        nombre = vm.cstr(vm.rd(pk + 24)) if 0x43540000 <= vm.rd(pk + 24) < 0x44300000 else f"tsk{tid:#x}"
        nt = crea_tarea(vm, tid, nombre, entry, pri, exinf)
        nt.pk = pk  # type: ignore[attr-defined]  # T_CTSK: exinf/task se releen al activar (av-cam los rellena después de crear)
        if atr & 2:  # TA_ACT
            nt.estado = "lista"
        vm.log.append(f"{vm.t:9.1f} {t.name}: {n} id={tid:#x} entry={entry:#x} pri={pri} '{nombre}'")
        return tid if n == "acre_tsk" else E_OK
    if n in ("act_tsk", "sta_tsk"):
        tid = a(0) or t.tid
        nt = vm.tasks.get(tid)  # type: ignore[assignment]
        if not nt:
            return E_NOEXS
        if nt.estado in ("dormida", "fin"):
            pk = getattr(nt, "pk", 0)
            if pk:
                nt.entry = vm.rd(pk + 8) or nt.entry
            vm_reset(vm, nt, a(1) if n == "sta_tsk" else (vm.rd(pk + 4) if pk else 0)).estado = "lista"
            vm.log.append(f"{vm.t:9.1f} {t.name}: {n} {nt.name}")
        else:
            nt.act += 1
        return E_OK
    if n in ("ext_tsk", "exd_tsk"):
        t.estado = "fin"
        return None
    if n in ("get_tid",):
        vm.wr(a(0), t.tid)
        return E_OK
    if n in ("dly_tsk", "tslp_tsk"):
        tmo = a(0)
        if n == "tslp_tsk" and t.act:
            t.act -= 1
            return E_OK
        return bloquea(("dormir",), tmo if tmo < 0x80000000 else TMO_FEVR) if not (n == "dly_tsk" and tmo == 0) else E_OK
    if n == "wup_tsk":
        nt = vm.tasks.get(a(0) or t.tid)  # type: ignore[assignment]
        if nt and nt.estado == "espera" and nt.espera[0] == "dormir":
            despierta(vm, nt, E_OK)
        elif nt:
            nt.act += 1
        return E_OK
    if n in ("cre_sem", "CRE_SEM", "acre_sem"):
        sid, pk = (vm.nuevo_id(), a(0)) if n == "acre_sem" else (a(0), a(1) + (8 if n == "CRE_SEM" else 0))  # shortcut: +8 por analogía con CRE_CYC, sin verificar
        vm.sems[sid] = [vm.rd(pk + 4), vm.rd(pk + 8)]
        return sid if n == "acre_sem" else E_OK
    if n == "sig_sem":
        s = vm.sems.setdefault(a(0), [0, 1 << 30])
        w = [x for x in vm.tasks.values() if x.estado == "espera" and x.espera == ("sem", a(0))]
        if w:
            despierta(vm, w[0], E_OK)
        else:
            s[0] += 1
        return E_OK
    if n == "twai_sem":
        s = vm.sems.setdefault(a(0), [0, 1 << 30])
        if s[0] > 0:
            s[0] -= 1
            return E_OK
        return bloquea(("sem", a(0)), sgn(a(1)))
    if n in ("cre_flg", "CRE_FLG", "acre_flg"):
        fid, pk = (vm.nuevo_id(), a(0)) if n == "acre_flg" else (a(0), a(1) + (8 if n == "CRE_FLG" else 0))  # shortcut: +8 por analogía con CRE_CYC, sin verificar
        vm.flgs[fid] = vm.rd(pk + 4)
        return fid if n == "acre_flg" else E_OK
    if n == "set_flg":
        vm.flgs[a(0)] = vm.flgs.get(a(0), 0) | a(1)
        for x in list(vm.tasks.values()):
            if x.estado == "espera" and x.espera[:2] == ("flg", a(0)):
                patron, modo, p_ret = x.espera[2:]
                if cumple(vm.flgs[a(0)], patron, modo):
                    vm.wr(p_ret, vm.flgs[a(0)])
                    if modo & 4:  # TWF_CLR
                        vm.flgs[a(0)] = 0
                    despierta(vm, x, E_OK)
        return E_OK
    if n == "clr_flg":
        vm.flgs[a(0)] = vm.flgs.get(a(0), 0) & a(1)
        return E_OK
    if n == "twai_flg":
        fid, patron, modo, p_ret, tmo = a(0), a(1), a(2), a(3), sgn(a(4))
        v = vm.flgs.get(fid, 0)
        if cumple(v, patron, modo):
            vm.wr(p_ret, v)
            if modo & 4:
                vm.flgs[fid] = 0
            return E_OK
        return bloquea(("flg", fid, patron, modo, p_ret), tmo)
    if n in ("cre_mbx", "CRE_MBX", "acre_mbx", "cre_mbf", "CRE_MBF", "acre_mbf", "cre_mpf", "CRE_MPF", "acre_mpf",
             "cre_mpl", "CRE_MPL", "acre_mpl"):
        oid = vm.nuevo_id() if n.startswith("acre") else a(0)
        vm.mbxs.setdefault(oid, collections.deque())
        return oid if n.startswith("acre") else E_OK
    if n == "snd_mbx":
        w = [x for x in vm.tasks.values() if x.estado == "espera" and x.espera[:2] == ("mbx", a(0))]
        if w:
            vm.wr(w[0].espera[2], a(1))
            despierta(vm, w[0], E_OK)
        else:
            vm.mbxs.setdefault(a(0), collections.deque()).append(a(1))
        return E_OK
    if n == "trcv_mbx":
        buz = vm.mbxs.setdefault(a(0), collections.deque())
        if buz:
            vm.wr(a(1), buz.popleft())
            return E_OK
        return bloquea(("mbx", a(0), a(1)), sgn(a(2)))
    if n == "tsnd_mbf":  # (id, msg, tam, tmo): µITRON 4 mensaje de tamaño variable; shortcut: sin límite de tamaño del búfer
        dato = bytes(vm.uc.mem_read(a(1), a(2)))
        w = [x for x in vm.tasks.values() if x.estado == "espera" and x.espera[:2] == ("mbf", a(0))]
        if w:
            vm.uc.mem_write(w[0].espera[2], dato)
            despierta(vm, w[0], len(dato))
        else:
            vm.mbfs.setdefault(a(0), collections.deque()).append(dato)
        return E_OK
    if n == "trcv_mbf":  # (id, &buf, tmo) → tamaño recibido
        buz = vm.mbfs.setdefault(a(0), collections.deque())
        if buz:
            dato = buz.popleft()
            vm.uc.mem_write(a(1), dato)
            return len(dato)
        return bloquea(("mbf", a(0), a(1)), sgn(a(2)))
    if n == "rel_mpf":
        return E_OK
    if n in ("tget_mpf", "tget_mpl"):
        sz = 0x1000 if n == "tget_mpf" else a(1)
        vm.wr(a(2) if n == "tget_mpl" else a(1), vm.malloc(sz))
        return E_OK
    if n in ("cre_cyc", "CRE_CYC", "acre_cyc"):
        cid, pk = (vm.nuevo_id(), a(0)) if n == "acre_cyc" else (a(0), a(1) + (8 if n == "CRE_CYC" else 0))  # T_CCYC en +8 (0x6860)
        atr, exinf, h, per = (vm.rd(pk + 4 * k) for k in range(4))
        vm.cycs[cid] = [h, max(per, 1), vm.t + per, bool(atr & 2), exinf]
        vm.log.append(f"{vm.t:9.1f} {t.name}: {n} id={cid:#x} h={h:#x} periodo={per} ms")
        return cid if n == "acre_cyc" else E_OK
    if n == "sta_cyc":
        if a(0) in vm.cycs:
            vm.cycs[a(0)][3], vm.cycs[a(0)][2] = True, vm.t + vm.cycs[a(0)][1]
        return E_OK
    if n == "stp_cyc":
        if a(0) in vm.cycs:
            vm.cycs[a(0)][3] = False
        return E_OK
    if n == "def_inh":
        vm.inh[a(0)] = vm.rd(a(1) + 4) if a(1) else 0
        vm.log.append(f"{vm.t:9.1f} {t.name}: def_inh int={a(0):#x} manejador={vm.inh[a(0)]:#x}")
        return E_OK
    if n == "get_tim":
        ms = int(vm.t)
        vm.wr(a(0), ms & 0xFFFFFFFF)
        vm.wr(a(0) + 4, ms >> 32)
        return E_OK
    if n in ("liro_malloc",):
        return vm.malloc(a(0))
    if n in ("liro_free", "malloc_reset", "osal_free_stack"):
        return E_OK
    if n == "memcpy":
        vm.uc.mem_write(a(0), bytes(vm.uc.mem_read(a(1), a(2))))
        return a(0)
    if n in ("prints", "printch"):
        texto = vm.cstr(a(0)) if n == "prints" else chr(a(0) & 0xFF)
        vm.log.append(f"{vm.t:9.1f} {t.name}: «{texto.rstrip()}»")
        return E_OK
    if n.startswith("arch_"):
        return a(0)  # shortcut: identidad VA/PA/caché, hasta conocer el mapa de memoria del BIONZ que usa av-cam
    # --- OSAL
    # firmas del OSAL de kernel (osal_uipc.ko, VERIFICADO por desensamblado): reg_cb(qid, ?, cb, arg), valloc(qid, &msg, tam, tmo),
    # rcv(qid, &msg, tmo), snd(qid, msg), free(qid, msg); el mensaje lleva cabecera de 12 B delante (refcuenta en msg−6)
    if n in ("osal_reg_msg_queue_cb", "osal_reg_sync_msg_queue_cb"):
        vm.qcb[a(0)] = (a(2), a(3))
        vm.log.append(f"{vm.t:9.1f} {t.name}: {n} qid={a(0):#x} cb={a(2):#x} arg={a(3):#x}")
        return E_OK
    if n == "osal_valloc_msg_wait":
        m = vm.malloc(min(a(2), 0x800) + 12) + 12  # cabecera de 12 B delante (msg−4 = cola de respuesta, 0x43b51726)
        vm.wr(a(1), m)
        return E_OK
    if n in ("osal_snd_msg", "osal_snd_sync_msg", "osal_snd_sync_direct"):
        q, m = a(0), a(1)
        if q == 0x910041 and m:  # sleep(ms) del núcleo (0x43591e20: ms en m+0x18); sin esto la tarea gira sobre el reloj
            return bloquea(("sleep",), max(vm.rd(m + 0x18), 1))
        datos = bytes(vm.uc.mem_read(m, 0x30)) if m else b""
        if servicio_kernel(vm, q, m, t):
            if n == "osal_snd_msg" and m:  # asíncrono: la respuesta vuelve en el mismo búfer a la cola de msg−4
                entrega(vm, vm.rd(m - 4), m)
            return E_OK
        if q in vm.queues or q in vm.qcb:
            entrega(vm, q, m)
        else:
            vm.salida_ext.append((vm.t, t.name, n, q, datos.hex()))
        return E_OK
    if n == "liro_osal_rcv_msg_tmo":
        cola = vm.queues.setdefault(a(0), collections.deque())
        if cola:
            vm.wr(a(1), cola.popleft())
            return E_OK
        return bloquea(("rcv", a(0), a(1)), sgn(a(2)))
    if n in ("osal_create_thread", "osal_create_waitable_thread"):
        tid = vm.nuevo_id()
        nt = crea_tarea(vm, tid, vm.cstr(a(0)) if a(0) > 0x10000 else f"osal{tid:#x}", a(1), 0, a(2))
        nt.estado = "lista"
        vm.log.append(f"{vm.t:9.1f} {t.name}: {n} '{nt.name}' entry={a(1):#x}")
        return tid
    if n == "osal_dynamic_id":  # (n, grupo, &qid): cola dinámica nueva del grupo (osal_uipc.ko); el número exacto no importa mientras sea único
        vm.dyn_n += 1
        nq = (a(1) << 16) | (0x700 + vm.dyn_n)
        vm.queues.setdefault(nq, collections.deque())
        vm.wr(a(2), nq)
        return E_OK
    if n in ("osal_thread_id",):
        return t.tid
    if n in ("osal_subsystem_id",):
        return 0x3  # shortcut: id de subsistema de av-cam sin verificar; fijarlo con osal_uipc.ko
    # --- Backup (NVRAM del volcado real)
    if n == "Backup_read":
        d = vm.bk.get(a(0))
        if d is None:
            vm.log.append(f"{vm.t:9.1f} {t.name}: Backup_read {a(0):#x} AUSENTE")
            return -1
        vm.uc.mem_write(a(1), d)
        return len(d)
    if n == "Backup_read_4Byte":
        d = vm.bk.get(a(0), b"\0" * 4)
        return int.from_bytes(d[:4].ljust(4, b"\0"), "little")
    if n in ("Backup_get_datasize",):
        return len(vm.bk.get(a(0), b""))
    if n.startswith("Backup_write"):
        vm.log.append(f"{vm.t:9.1f} {t.name}: {n} {a(0):#x}")
        return E_OK
    # sin modelo propio: E_OK y queda en el recuento (informe) para implementarla cuando haga falta
    return E_OK


DMM_UNIDAD = 0x00200000  # shortcut: 2 MiB por unidad; el tamaño real sale de DmmConfig.bin (no está en el firmware extraído)


def servicio_kernel(vm: Vm, q: int, m: int, t: Task) -> bool:
    """Servicios que en la cámara dan los módulos del kernel; True si el mensaje queda atendido."""
    if q == 0x61003C and m:  # dmm.ko: av-cam 0x4394d74c pide AllocUnitNew {u16 1, s16 err, u32 tipo}; lee err +2, manejador +4, dirección +0x10
        orden = vm.rd(m, 2)
        vm.wr(m, orden | 0x8000, 2)  # la respuesta lleva el id de la orden con 0x8000 (av-cam: «ERR_DMM_DIFFERENT_COMP msg_id 5, my_id 0x8001»)
        if orden in (1, 5):
            vm.dmm_n += 1
            base = vm.malloc(DMM_UNIDAD)
            vm.wr(m + 2, 0, 2)
            vm.wr(m + 4, vm.dmm_n, 2)
            vm.wr(m + 0x10, base)
            vm.wr(m + 8, base)  # INFERENCIA: el envoltorio 0x43a833fa lee dirección en +8 y tamaño en +0xc (→ *r1, *r2), 0x435c5126 los usa para su reserva lineal
            vm.wr(m + 0xC, DMM_UNIDAD)
            vm.wr(m + 6, 0x1111, 2)  # INFERENCIA: 0x43620b12 exige 0x1111 en la respuesta (+6) para la petición con +0x14=0x1111
            vm.log.append(f"{vm.t:9.1f} {t.name}: DMM orden {orden} ({'AllocUnitNew' if orden == 1 else 'OpenUnit'}) → {base:#x} (unidad {vm.dmm_n})")
        else:
            vm.wr(m + 2, 0, 2)
            vm.log.append(f"{vm.t:9.1f} {t.name}: DMM orden {orden} sin modelar (responde 0)")
        return True
    if q == 0x910042 and m and vm.rd(m) == 0x20:  # reloj del núcleo: µs (64 bit) en m[6..7], como el shim de la UI
        vm.t += 0.01  # shortcut: cada lectura del reloj cuesta 10 µs virtuales, para que los sondeos de tiempo (esperas activas) terminen
        us = int(vm.t * 1000)
        vm.wr(m + 24, us & 0xFFFFFFFF)
        vm.wr(m + 28, us >> 32)
        return True
    if q in (0x8F013A, 0x8F0139) and m:  # registro (logger): el texto va en el cuerpo
        b = bytes(vm.uc.mem_read(m, 0x120))
        txt = max((x for x in b.split(b"\0") if len(x) >= 4), key=len, default=b"")
        if txt and all(32 <= c < 127 or c in (9, 10) for c in txt):
            vm.log.append(f"{vm.t:9.1f} {t.name}: LOG {txt.decode('latin-1').strip()}")
        return True
    return False


def entrega(vm: Vm, q: int, m: int) -> None:
    """Entrega m a la cola q: a la tarea que la espera, al callback registrado (cb(msg, arg), __default_cb de osal_uipc.ko) o a la cola."""
    w = [x for x in vm.tasks.values() if x.estado == "espera" and x.espera[:2] == ("rcv", q)]
    if w:
        vm.wr(w[0].espera[2], m)
        despierta(vm, w[0], E_OK)
        return
    if q in vm.qcb:
        cb, arg = vm.qcb[q]
        viejo = vm.cur
        vm.ncb += 1
        h = crea_tarea(vm, 0x20000 + vm.ncb, f"cb{q:#x}", cb, -1, m)
        vm.uc.context_restore(h.ctx)
        vm.uc.reg_write(UC_ARM_REG_R1, arg)
        h.ctx = vm.uc.context_save()
        h.estado = "lista"
        vm.pendientes_cb.append(h)
        vm.cur = viejo
        return
    vm.queues.setdefault(q, collections.deque()).append(m)


def sgn(v: int) -> int:
    return v - (1 << 32) if v & 0x80000000 else v


def cumple(v: int, patron: int, modo: int) -> bool:
    return (v & patron) == patron if modo & 1 else bool(v & patron)  # TWF_ANDW=0? μITRON4: TWF_ANDW=0, TWF_ORW=1


def despierta(vm: Vm, x: Task, ret: int) -> None:
    x.estado, x.espera, x.despertar, x.ret = "lista", (), None, ret


def vm_reset(vm: Vm, t: Task, r0: int) -> Task:
    """Vuelve a crear el contexto de t (act_tsk/sta_tsk de una tarea dormida) sin perder el contexto de la tarea en curso."""
    ctx = vm.uc.context_save()
    nt = crea_tarea(vm, t.tid, t.name, t.entry, t.pri, r0)
    nt.act = t.act
    nt.pk = getattr(t, "pk", 0)  # type: ignore[attr-defined]
    vm.uc.context_restore(ctx)
    return nt


def corre(vm: Vm, t: Task, cupo: int) -> None:
    """Ejecuta t hasta trampa, bloqueo o fin de cupo."""
    uc = vm.uc
    uc.context_restore(t.ctx)
    if t.ret is not None:
        uc.reg_write(UC_ARM_REG_R0, t.ret & 0xFFFFFFFF)
    vm.cur = t
    restante = cupo
    while restante > 0 and t.estado == "lista":
        pc = uc.reg_read(UC_ARM_REG_PC) | (1 if uc.reg_read(UC_ARM_REG_CPSR) & 0x20 else 0)
        vm.trampa = None
        try:
            uc.emu_start(pc, 0xFFFFFFFF, count=restante)
        except UcError as e:
            t.estado = "fin"
            sp = uc.reg_read(UC_ARM_REG_SP)
            pila = [w for w in struct.unpack("<128I", uc.mem_read(sp, 512)) if 0x43541000 <= w < 0x43fa0000 and w & 1]
            vm.log.append(f"{vm.t:9.1f} {t.name}: ERROR {e} pc={uc.reg_read(UC_ARM_REG_PC):#x} lr={uc.reg_read(UC_ARM_REG_LR):#x} {vm.fallo} "
                          f"r0-r7={[hex(uc.reg_read(UC_ARM_REG_R0 + k)) for k in range(8)]} pila≈{[hex(w) for w in pila[:12]]}")
            break
        restante = 0 if vm.trampa is None else restante - 1
        if vm.trampa is None:
            vm.pcs[(t.name, uc.reg_read(UC_ARM_REG_PC))] += 1
            break
        if vm.trampa == NAPI:  # la entrada de la tarea volvió
            t.estado = "fin"
            break
        r = api(vm, vm.trampa)
        lr = uc.reg_read(UC_ARM_REG_LR)
        uc.reg_write(UC_ARM_REG_PC, lr)  # Unicorn toma el modo Thumb del bit 0
        if r is not None:
            uc.reg_write(UC_ARM_REG_R0, r & 0xFFFFFFFF)
        t.ret = None if r is not None else 0
    t.pasos += cupo - max(restante, 0)
    t.ctx = uc.context_save()


def planifica(vm: Vm, pasos_max: int) -> None:
    total = 0
    while total < pasos_max:
        for cid, c in vm.cycs.items():  # manejadores cíclicos: se ejecutan hasta volver, en una tarea efímera
            if c[3] and c[2] <= vm.t and c[0]:
                c[2] += c[1]
                h = crea_tarea(vm, 0x10000 + cid, f"cyc{cid:#x}", c[0], -1, c[4])
                h.estado = "lista"
                corre(vm, h, QUANTUM)
                if h.estado == "espera":
                    vm.log.append(f"{vm.t:9.1f} cyc{cid:#x}: el manejador se bloqueó (no permitido en μITRON)")
                del vm.tasks[h.tid]
                vm.libres.append(vm.slots.pop(h.tid))
                total += QUANTUM // 10
        while vm.pendientes_cb:  # callbacks de cola: se ejecutan hasta volver (contexto de kernel en la cámara)
            h = vm.pendientes_cb.pop(0)
            corre(vm, h, QUANTUM)
            if h.estado == "espera":
                vm.log.append(f"{vm.t:9.1f} {h.name}: el callback quedó bloqueado")
            vm.tasks.pop(h.tid, None)
            vm.libres.append(vm.slots.pop(h.tid))
            total += QUANTUM // 10
        listas = sorted((x for x in vm.tasks.values() if x.estado == "lista"), key=lambda x: (x.pri, x.tid))
        if not listas:
            prox = [x.despertar for x in vm.tasks.values() if x.estado == "espera" and x.despertar is not None]
            prox += [c[2] for c in vm.cycs.values() if c[3] and c[0]]
            if not prox:
                vm.log.append(f"{vm.t:9.1f} sin tareas listas ni esperas con plazo: reposo")
                return
            vm.t = min(prox)
            for x in vm.tasks.values():
                if x.estado == "espera" and x.despertar is not None and x.despertar <= vm.t:
                    despierta(vm, x, E_OK if x.espera == ("sleep",) else E_TMOUT)
            continue
        for x in listas:
            corre(vm, x, QUANTUM)
            total += QUANTUM
        vm.t += 1.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--avcam", type=Path, default=AVCAM)
    ap.add_argument("--bk", type=Path, default=BK)
    ap.add_argument("--pasos", type=int, default=50_000_000)
    ap.add_argument("--informe", type=Path)
    a = ap.parse_args()
    vm = carga(a.avcam, a.bk)
    pre = crea_tarea(vm, 1, "entry_pre", 0x43541044, 0, 0)
    pre.estado = "lista"
    planifica(vm, a.pasos // 10)
    main_t = crea_tarea(vm, 2, "entry_main", 0x43541058, 0, 0)
    main_t.estado = "lista"
    planifica(vm, a.pasos)
    inf = {
        "tiempo_virtual_ms": vm.t,
        "tareas": {f"{x.tid:#x}": {"nombre": x.name, "estado": x.estado, "espera": [hex(v) if isinstance(v, int) else v for v in x.espera],
                                    "pc": hex(vm.uc.context_restore(x.ctx) or vm.uc.reg_read(UC_ARM_REG_PC)), "pasos": x.pasos}
                   for x in vm.tasks.values()},
        "llamadas": dict(vm.calls.most_common()),
        "colas_registradas": {f"{q:#x}": f"cb={cb[0]:#x} arg={cb[1]:#x}" for q, cb in vm.qcb.items()},
        "mensajes_fuera": [list(m) for m in vm.salida_ext[:200]],
        "mmio_paginas": {f"{p:#x}": f"pc={v[2]:#x}" for p, v in sorted(vm.mmio.items())},
        "interrupciones": {f"{k:#x}": hex(v) for k, v in vm.inh.items()},
        "giros": [f"{n} pc={pc:#x} ×{c}" for (n, pc), c in vm.pcs.most_common(20)],
        "ultimas_llamadas": list(vm.ultimas),
        "registro": vm.log[-400:],
    }
    txt = json.dumps(inf, indent=1, ensure_ascii=False)
    if a.informe:
        a.informe.write_text(txt)
    print(json.dumps({k: (v if isinstance(v, float) else len(v)) for k, v in inf.items()}, ensure_ascii=False))  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
