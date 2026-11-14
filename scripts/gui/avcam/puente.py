#!/usr/bin/env python3
"""Puente LIRO VM ↔ invitado (paso 2 de la emulación de av-cam): lo que im.elf manda a las colas de kernel de av-cam llega a la LIRO VM
y lo que av-cam envía vuelve al invitado, donde el shim (`AVQ=`) lo entrega a la cola de im.elf que corresponda.

Invitado → anfitrión: «\\x01AVQ qid tam cabecera cuerpo» (hex). Anfitrión → invitado: «Q qid cabecera cuerpo» (hex), una línea.
La LIRO VM corre en un hilo con el tiempo virtual atado al reloj real (`vm.limite`); cada mensaje entrante la hace avanzar y todo lo que av-cam
emite hacia colas ajenas se reenvía (salvo las de `NO_REENVIAR`: entrada, reloj y servicios que el shim ya atiende).
"""
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ae as A
import liro_vm as L

# colas de salida de av-cam que el invitado no debe recibir: teclas (las pone el anfitrión), servicios del núcleo y trazas
NO_REENVIAR = {0x7A0020, 0x910040, 0x910041, 0x910042, 0x924127, 0x8F0139, 0x8F013A, 0x920021}


def colas_avcam() -> list[int]:
    """Colas de recepción de av-cam (registradas con callback o con tarea en espera): los mensajes del invitado a ellas son para la LIRO VM."""
    vm = arranca()[0]
    q = set(vm.qcb) | {x.espera[1] for x in vm.tasks.values() if x.estado == "espera" and x.espera[:1] == ("rcv",)}
    return sorted(q)


def arranca() -> tuple[L.Vm, float]:
    vm = L.carga(L.AVCAM, L.BK)
    L.crea_tarea(vm, 1, "entry_pre", 0x43541044, 0, 0).estado = "lista"
    L.planifica(vm, 20_000_000)
    L.crea_tarea(vm, 2, "entry_main", 0x43541058, 0, 0).estado = "lista"
    L.planifica(vm, 200_000_000)
    return vm, vm.t


class Puente:
    def __init__(self, enviar, registro: Path | None = None, ae: A.Emisor | None = None) -> None:
        """enviar(línea: bytes): manda una línea al invitado. registro: JSONL con todo lo que entra y sale (evidencia).
        ae: emisor opcional del AE (ae.py, atajo: av-cam no lo genera); arranca con la primera orden de ObjCamera a CamMgr (0x30001)."""
        self.enviar, self.registro, self.ae = enviar, registro, ae
        if ae:
            ae.enviar = self._envia_ae
        self.cerrojo = threading.RLock()
        self.vm, t0 = arranca()
        self.vm.limite, self.t_real0, self.t_virt0 = t0, time.monotonic(), t0
        self.visto = len(self.vm.salida_ext)  # lo emitido durante el arranque se guarda aparte: solo se reenvía en un arranque en frío del invitado
        self.n_in = self.n_out = 0
        threading.Thread(target=self._reloj, daemon=True).start()

    def _envia_ae(self, linea: bytes) -> None:
        q, cab, datos = linea.decode().split()[1:]
        self._anota(sale=f"0x{q}", tarea="ae.py", cab=cab, datos=datos)
        self.enviar(linea)

    def reenvia_arranque(self) -> None:
        """Arranque en frío del invitado: av-cam ya arrancó (en la cámara lo hace antes que im.elf) y sus avisos esperan en las colas del kernel; el shim los
        retiene hasta que im.elf registre cada cola."""
        with self.cerrojo:
            for _t, tarea, _api, q, datos, cab in self.vm.salida_ext[:self.visto]:
                if q not in NO_REENVIAR:
                    self._anota(arranque=f"{q:#x}", tarea=tarea, cab=cab, datos=datos)
                    self.enviar(f"Q {q:x} {cab} {datos}\n".encode())

    def _anota(self, **kw: object) -> None:
        if self.registro:
            with self.registro.open("a") as f:
                f.write(json.dumps({"t": round(self.vm.t, 2), **kw}) + "\n")

    def _reloj(self) -> None:
        while True:
            time.sleep(0.02)
            with self.cerrojo:
                self._avanza()

    def _avanza(self) -> None:
        self.vm.limite = self.t_virt0 + (time.monotonic() - self.t_real0) * 1000
        L.planifica(self.vm, 20_000_000)
        self._saca()

    def _saca(self) -> None:
        vm = self.vm
        nuevos, self.visto = vm.salida_ext[self.visto:], len(vm.salida_ext)
        for t, tarea, _api, q, datos, cab in nuevos:
            self._anota(sale=f"{q:#x}", tarea=tarea, cab=cab, datos=datos)
            if q in NO_REENVIAR:
                continue
            self.n_out += 1
            self.enviar(f"Q {q:x} {cab} {datos}\n".encode())

    def desde_invitado(self, linea: str) -> None:
        """«qid tam cabecera cuerpo» → mensaje a una cola de av-cam."""
        qs, tams, cab, cuerpo = linea.split()
        q, tam = int(qs, 16), int(tams, 16)
        with self.cerrojo:
            vm = self.vm
            m = vm.malloc(max(tam, 0x40) + 12 + 0x20) + 12
            vm.uc.mem_write(m - 12, bytes.fromhex(cab))
            vm.uc.mem_write(m, bytes.fromhex(cuerpo)[:tam])
            vm.msz[m] = tam
            self.n_in += 1
            self._anota(entra=f"{q:#x}", cab=cab, datos=cuerpo)
            if self.ae and q == 0x30001:
                self.ae.arranca()
            L.entrega(vm, q, m)
            self._avanza()


if __name__ == "__main__":  # autoprueba: arranque y lista de colas de av-cam
    cs = colas_avcam()
    print(len(cs), "colas:", ",".join(f"{c:x}" for c in cs))
