"""Emula el código real de `libObj.so` (A6000 fw3.21 / CFW): despachador de escritura 0x689f44 → setter → conversor LIRO, y despachador de
lectura 0x68e9fc. Se sustituyen por modelos Python solo las fronteras (registro, MWF::ObjMsg/ObjIf, contenedores de lectura)."""

from __future__ import annotations

from pathlib import Path

from .armlib import Lib, Machine

BASE = 0x20000000
A = lambda x: (
    BASE + x
)  # dirección virtual = desplazamiento de fichero (segmento de código)


class LibObj:
    def __init__(self, so: Path, init_elems: tuple[int, int] = (0, 0)) -> None:
        self.m = Machine()
        m = self.m
        self.lib = Lib(m, so.read_bytes(), BASE)
        self.obj = m.alloc(0x2000)
        self.cont_addr = m.alloc(32)  # contenedor de lectura de Silent (id 0x6c)
        m.w32(self.obj + 0x54C, self.cont_addr)
        self.elem = {0: init_elems[0], 1: init_elems[1]}
        self.cmd = 0
        self.payload: dict[int, int] = {}
        self.msgs: dict[int, dict] = {}
        self.params: dict[int, int] = {}
        self.sent: list[dict] = []
        self.dest_ok = 1
        self.send_rc = 0
        self.errors: list[str] = []
        self.marks = 0
        self.read_out: dict[int, int] = {}
        self.numobj: dict[int, int] = {}
        nop = lambda mm: 0
        ov = m.overrides
        ov[A(0x131FD2) & ~1] = lambda mm: self.cmd
        ov[A(0x13200A) & ~1] = lambda mm: 0xD00D0000
        for f in (
            0x67A340,
            0x67A208,
            0x67A276,
            0x67A1F6,
            0x67A24E,
            0x67A290,
            0x42ABCC,
            0x42ABA8,
        ):
            ov[A(f) & ~1] = nop
        ov[A(0x42ABDC) & ~1] = self._find
        ov[A(0x42AC00) & ~1] = self._find
        ov[A(0x42067C) & ~1] = lambda mm: self.dest_ok
        ov[A(0x68D5A6) & ~1] = lambda mm: self.errors.append(
            f"err_log r1={mm.reg(1):#x}"
        )
        ov[A(0x68D432) & ~1] = lambda mm: self.errors.append("ok_log")
        ov[A(0x68E0CE) & ~1] = self._set_elem
        ov[A(0x68C39C) & ~1] = self._mark
        for f in (0x68C3AA, 0x68C33A):
            ov[A(f) & ~1] = self._get_elem
        h = m.handlers
        h["MWF::ObjMsg::ObjMsg(unsigned int, unsigned int)"] = self._msg_new
        h["MWF::ObjMsg::AddParam(unsigned int, MWF::Param const&)"] = self._add_param
        h[
            "MWF::ParamStd_Template<int, (MWF::Param::Type)7>::ParamStd_Template(int)"
        ] = lambda mm: self.params.__setitem__(mm.reg(0), mm.reg(1))
        h[
            "MWF::ParamStd_Template<unsigned int, (MWF::Param::Type)8>::ParamStd_Template(unsigned int)"
        ] = lambda mm: self.params.__setitem__(mm.reg(0), mm.reg(1))
        h["MWF::ObjIf::IssueCommandAsync(void*, MWF::ObjMsg*)"] = self._issue
        h["MWF::ObjMsg::GetMessageId() const"] = lambda mm: self.msgs[mm.reg(0)]["id"]
        h["MWF::ObjMsg::GetParam(unsigned int) const"] = lambda mm: self.msgs[
            mm.reg(0)
        ]["params"].get(mm.reg(1), 0)
        h["MWF::ParamStd_Template<int, (MWF::Param::Type)7>::GetValue() const"] = (
            lambda mm: self.params[mm.reg(0)]
        )
        h["ParamList::add(unsigned long, ParamBase*)"] = lambda mm: (
            self.read_out.__setitem__(mm.reg(1), self.numobj[mm.reg(2)])
        )
        for n, fn in list(h.items()):
            if n in self.lib.by_name:
                ov[self.lib.by_name[n] & ~1] = fn

    # --- modelos de frontera
    def _find(self, mm):
        k, out = mm.reg(1), mm.reg(2)
        if k in self.payload:
            mm.w32(out, self.payload[k])
            return 0
        return 1

    def _set_elem(self, mm):
        if mm.reg(1) <= 1:
            self.elem[mm.reg(1)] = mm.reg(2)

    def _mark(self, mm):
        self.marks += 1

    def _get_elem(self, mm):
        p = self.m.alloc(16)
        self.numobj[p] = self.elem[mm.reg(1)]
        return p

    def _msg_new(self, mm):
        self.msgs[mm.reg(0)] = {"cat": mm.reg(1), "id": mm.reg(2), "params": {}}

    def _add_param(self, mm):
        self.msgs[mm.reg(0)]["params"][mm.reg(1)] = mm.reg(2)

    def _issue(self, mm):
        msg = self.msgs[mm.reg(1)]
        self.sent.append(
            {
                "id": msg["id"],
                "params": {k: self.params[v] for k, v in msg["params"].items()},
            }
        )
        return self.send_rc

    # --- API
    def write(self, cmd: int, payload: dict[int, int]) -> dict | None:
        """Entrega un evento de escritura al despachador real; devuelve el mensaje enviado (o None)."""
        self.cmd, self.payload, self.sent, self.errors = cmd, payload, [], []
        self.m.call(A(0x689F44), self.obj)
        return self.sent[-1] if self.sent else None

    def to_liro(self, selector: int, sent: dict) -> bytes:
        """Conversor real del selector (0x9bbb5c → 0x99b004/0x99e968): mensaje → paquete de 9 bytes."""
        m = self.m
        msg = m.alloc(32)
        pv = m.alloc(16)
        self.params[pv] = next(iter(sent["params"].values()))
        self.msgs[msg] = {
            "cat": 0x3100,
            "id": sent["id"],
            "params": {next(iter(sent["params"])): pv},
        }
        buf = m.alloc(16)
        m.uc.mem_write(buf, b"\0" * 16)
        m.call(A(0x9BBB5C), selector, msg, buf, 0)
        return bytes(m.uc.mem_read(buf, 9))

    def read(self, rid: int) -> dict[int, int]:
        self.read_out = {}
        d = self.m.alloc(16)
        self.m.call(A(0x68E9FC), self.obj, rid, d)
        return dict(self.read_out)
