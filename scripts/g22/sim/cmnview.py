"""Emula el elemento `Normal` real de `cmn_view_processDataMgr.so` (setValue/getValue) con modelos Python de ParamList/PrmNumber y de
`CmnViewModelIfWrapper::{requestModelExecute,getModelInfo}` (que redirigen a los callbacks del integrador)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .armlib import Lib, Machine

BASE = 0x10000000


class CmnView:
    def __init__(
        self,
        so: Path,
        pid: int,
        on_request: Callable[[str, int, dict[int, int]], None],
        on_info: Callable[[str, int], dict[int, int] | None],
    ) -> None:
        self.m = Machine()
        m = self.m
        self.lib = Lib(m, so.read_bytes(), BASE)
        self.lists: dict[int, dict[int, int]] = {}
        self.prm: dict[int, tuple[str, int]] = {}
        self.on_request, self.on_info = on_request, on_info
        h = m.handlers
        h["operator new(unsigned int)"] = lambda mm: mm.alloc(mm.reg(0))
        h["operator delete(void*)"] = lambda mm: 0
        h["ParamList::ParamList()"] = self._pl_new
        h["ParamList::~ParamList()"] = lambda mm: 0
        h["ParamList::add(unsigned long, ParamBase*)"] = self._pl_add
        h["PrmNumber::PrmNumber(int)"] = lambda mm: self._prm(mm, "num")
        h["PrmBool::PrmBool(bool)"] = lambda mm: self._prm(mm, "bool")
        h["PrmNumber::GET(ParamList const*, unsigned long)"] = self._pl_get
        h["PrmNumber::getNumber() const"] = lambda mm: self.prm[mm.reg(0)][1]
        h[
            "CmnViewModelIfWrapper::requestModelExecute(char const*, unsigned long, ParamList*)"
        ] = self._req
        h[
            "CmnViewModelIfWrapper::getModelInfo(char const*, int, ParamList*, ParamList const*)"
        ] = self._info
        h["__cxa_guard_acquire"] = lambda mm: 1
        h["__cxa_guard_release"] = lambda mm: 0
        h["__aeabi_atexit"] = lambda mm: 0
        h["__cxa_atexit"] = lambda mm: 0
        for (
            n,
            fn,
        ) in (
            h.items()
        ):  # clases definidas (inline) en la propia .so: se sustituyen por el modelo
            if n in self.lib.by_name:
                m.overrides[self.lib.by_name[n] & ~1] = fn
        # instancia Normal real: constructor + setProcessId
        self.obj = m.alloc(0x100)
        f = self.lib.by_name
        m.call(
            f["CmnViewProcessDataElementNormal::CmnViewProcessDataElementNormal()"],
            self.obj,
        )
        m.call(
            f[
                "CmnViewProcessDataElementNormal::initProcessDataElement(ViewBaseProduct*, int)"
            ],
            self.obj,
            m.alloc(0x100),
            pid,
        )

    # --- modelos
    def _pl_new(self, mm):
        self.lists[mm.reg(0)] = {}

    def _prm(self, mm, kind):
        self.prm[mm.reg(0)] = (kind, mm.reg(1))

    def _pl_add(self, mm):
        self.lists[mm.reg(0)][mm.reg(1)] = mm.reg(2)

    def _pl_get(self, mm):
        return self.lists.get(mm.reg(0), {}).get(mm.reg(1), 0)

    def _req(self, mm):
        name, ev, lst = mm.cstr(mm.reg(0)), mm.reg(1), mm.reg(2)
        self.on_request(
            name, ev, {k: self.prm[p][1] for k, p in self.lists.get(lst, {}).items()}
        )

    def _info(self, mm):
        name, mid, out = mm.cstr(mm.reg(0)), mm.reg(1), mm.reg(2)
        d = self.on_info(name, mid)
        if d is None:
            return 0
        for k, v in d.items():
            p = mm.alloc(16)
            self.prm[p] = ("num", v)
            self.lists.setdefault(out, {})[k] = p
        return 1

    # --- API del elemento
    def set_value(self, idx: int) -> int:
        return self.m.call(
            self.lib.by_name["CmnViewProcessDataElementNormal::setValue(int)"],
            self.obj,
            idx,
        )

    def get_value(self) -> int | None:
        out = self.m.alloc(16)
        self.m.w32(out, 0xFFFFFFFF)
        ok = (
            self.m.call(
                self.lib.by_name["CmnViewProcessDataElementNormal::getValue(int&)"],
                self.obj,
                out,
            )
            & 0xFF
        )
        return self.m.u32(out) if ok else None
