"""Recupera clases C++ (RTTI Itanium) y vtables de un ELF ARM32 vía relocaciones dinámicas, solo con stdlib.

Uso: python3 -I scripts/rtti_vtables.py lib.so salida.json
Salida: clases {typeinfo, nombre, bases, vtables[{addr, offset_to_top, metodos}]} e índice función→(clase, slot).
Autocomprobación: todo _ZTI/_ZTV exportado debe coincidir con lo recuperado; si no, aborta."""
import json
import struct
import subprocess
import sys

R_ABS32, R_RELATIVE = 2, 23
TI_KINDS = {
    "_ZTVN10__cxxabiv117__class_type_infoE": "class",
    "_ZTVN10__cxxabiv120__si_class_type_infoE": "si",
    "_ZTVN10__cxxabiv121__vmi_class_type_infoE": "vmi",
}


class Elf:
    def __init__(self, path: str):
        self.d = open(path, "rb").read()
        shoff, = struct.unpack_from("<I", self.d, 0x20)
        shnum, shstrndx = struct.unpack_from("<HH", self.d, 0x30)
        raw = [struct.unpack_from("<10I", self.d, shoff + i * 40) for i in range(shnum)]
        stroff = raw[shstrndx][4]
        self.secs = {}
        for s in raw:
            name = self.d[stroff + s[0]:self.d.index(b"\0", stroff + s[0])].decode()
            self.secs[name] = {"type": s[1], "addr": s[3], "off": s[4], "size": s[5], "link": s[6]}
        self.text = self.secs[".text"]
        self._syms()
        self._relocs()

    def off(self, va: int) -> int | None:
        for s in self.secs.values():
            if s["addr"] and s["type"] != 8 and s["addr"] <= va < s["addr"] + s["size"]:  # 8 = NOBITS
                return va - s["addr"] + s["off"]
        return None

    def u32(self, va: int) -> int:
        return struct.unpack_from("<I", self.d, self.off(va))[0]

    def cstr(self, va: int) -> str:
        o = self.off(va)
        return self.d[o:self.d.index(b"\0", o)].decode("latin-1")

    def _syms(self):
        ds, dstr = self.secs[".dynsym"], self.secs[".dynstr"]
        self.syms = []
        for i in range(ds["size"] // 16):
            nm, val, _, _, _, shndx = struct.unpack_from("<IIIBBH", self.d, ds["off"] + i * 16)
            name = self.d[dstr["off"] + nm:self.d.index(b"\0", dstr["off"] + nm)].decode()
            self.syms.append((name, val if shndx else None))

    def _relocs(self):
        self.rel = {}  # va -> (target_va | None, symbol_name | None)
        for sec in (".rel.dyn",):
            r = self.secs[sec]
            for i in range(r["size"] // 8):
                where, info = struct.unpack_from("<II", self.d, r["off"] + i * 8)
                typ, sym = info & 0xFF, info >> 8
                if typ == R_RELATIVE:
                    self.rel[where] = (self.u32(where), None)
                elif typ == R_ABS32:
                    name, val = self.syms[sym]
                    add = self.u32(where)
                    self.rel[where] = ((val + add) if val is not None else None, name)

    def is_code(self, va: int | None) -> bool:
        t = self.text
        return va is not None and t["addr"] <= (va & ~1) < t["addr"] + t["size"]


def demangle(names: list[str]) -> list[str]:
    out = subprocess.run(["c++filt"], input="\n".join("_ZTS" + n for n in names), capture_output=True,
                         text=True, check=True).stdout.splitlines()
    return [o.removeprefix("typeinfo name for ") for o in out]


def recover(e: Elf) -> dict:
    tis = {}
    for where, (_, sym) in e.rel.items():
        kind = TI_KINDS.get(sym or "")
        if not kind:
            continue
        name_va = e.rel.get(where + 4, (None,))[0]
        if name_va is None:
            continue
        bases = []
        if kind == "si":
            bases = [e.rel.get(where + 8, (None,))[0]]
        elif kind == "vmi":
            n = e.u32(where + 12)
            bases = [e.rel.get(where + 16 + 8 * k, (None,))[0] for k in range(n)]
        tis[where] = {"kind": kind, "mangled": e.cstr(name_va), "bases": [b for b in bases if b]}
    for ti, nm in zip(tis.values(), demangle([t["mangled"] for t in tis.values()])):
        ti["name"] = nm

    vtables = []
    for where, (target, _) in e.rel.items():
        if target not in tis or (where - 4) in e.rel:  # offset_to_top nunca está relocado
            continue
        top = struct.unpack("<i", struct.pack("<I", e.u32(where - 4)))[0]
        if top > 0:
            continue
        methods, slot = [], where + 4
        while slot in e.rel:
            tgt, sym = e.rel[slot]
            if e.is_code(tgt):
                methods.append({"entry": hex(tgt & ~1), "thumb": bool(tgt & 1), "sym": sym})
            elif sym in ("__cxa_pure_virtual", "__cxa_deleted_virtual"):
                methods.append({"entry": None, "sym": sym})
            else:
                break
            slot += 4
        vtables.append({"addr_point": where + 4, "typeinfo": target, "offset_to_top": top, "methods": methods})

    classes = {}
    for va, ti in tis.items():
        classes[hex(va)] = {"name": ti["name"], "kind": ti["kind"],
                            "bases": [tis[b]["name"] if b in tis else hex(b) for b in ti["bases"]], "vtables": []}
    by_fn = {}
    for vt in vtables:
        c = classes[hex(vt["typeinfo"])]
        c["vtables"].append({"addr_point": hex(vt["addr_point"]), "offset_to_top": vt["offset_to_top"],
                             "methods": vt["methods"]})
        for i, m in enumerate(vt["methods"]):
            if m["entry"]:
                by_fn.setdefault(m["entry"], []).append({"class": c["name"], "vtable": hex(vt["addr_point"]),
                                                         "slot": i * 4})
    return {"classes": classes, "methods_by_entry": by_fn}


def self_check(e: Elf, res: dict) -> None:
    rec_ti = set(res["classes"])
    vt_points = {v["addr_point"] for c in res["classes"].values() for v in c["vtables"]}
    for name, val in e.syms:
        if val is None:
            continue
        if name.startswith("_ZTI"):
            assert hex(val) in rec_ti, f"typeinfo exportado no recuperado: {name}"
        if name.startswith("_ZTV"):
            assert hex(val + 8) in vt_points, f"vtable exportada no recuperada: {name}"


if __name__ == "__main__":
    elf = Elf(sys.argv[1])
    result = recover(elf)
    self_check(elf, result)
    n_vt = sum(len(c["vtables"]) for c in result["classes"].values())
    print(f"clases={len(result['classes'])} vtables={n_vt} metodos_unicos={len(result['methods_by_entry'])}")
    json.dump(result, open(sys.argv[2], "w"), indent=1)
