"""Búsqueda de accesos a memoria por desplazamiento en un av-cam (Thumb, Capstone con detalle)."""
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_MEM

sys.path.insert(0, str(Path(__file__).parent))
import pic


def decode_all(blob: bytes, start: int = 0, end: int | None = None):
    """Barrido lineal Thumb con skipdata: resincroniza sobre datos. Devuelve instrucciones con detalle."""
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.detail = True
    cs.skipdata = True
    end = end or len(blob)
    return cs.disasm(blob[start:end], pic.BASE + start)


def mem_accesses(blob: bytes, disps: set[int], mnems: tuple[str, ...] = ("str", "ldr")):
    """Lista de (dirección, texto) de loads/stores con alguno de los desplazamientos pedidos."""
    out = []
    for i in decode_all(blob):
        if not i.mnemonic.startswith(mnems):
            continue
        for op in i.operands:
            if op.type == ARM_OP_MEM and op.mem.disp in disps:
                out.append((i.address, f"{i.mnemonic} {i.op_str}"))
                break
    return out
