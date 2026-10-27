"""E24-05e / E24-05h-5 (offline): qué espacios de memoria leen T022/T023 y productores BIONZ de pkt[1] y pkt[2..3] del 0x0c.

Solo lee `av-cam.bin` y el texto de los scripts de cámara; no los ejecuta ni toca la cámara.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "e24_05d"))
from bz import Bz

VIRT2PHYS = 0x40000000  # físico = virtual de av-cam + 0x40000000 (T022, camera_darwin_buffers.py)
BIONZ_DRAM = (0x80000000, 0xC0000000)  # updater_full_dump.py: RAM física de BIONZ leída por tramos
DARWIN_SRAM = (0x20000000, 0x20010000)  # mapa del FM3 de Darwin (S, ADC, temporizadores)
DARWIN_PERIPH = (0x40000000, 0x40100000)
T022_PACKET = bytes.fromhex("00020016bd130000000053 0e00400000000000900000".replace(" ", ""))


def ins(b: Bz, a: int) -> str:
    i = b.dis(a, 4)[0]
    return f"{i.mnemonic} {i.op_str}"


def lit(b: Bz, a: int) -> int:
    k = int(b.dis(a, 4)[0].op_str.split("#")[-1].rstrip("]"), 0)
    return b.u32(((a + 4) & ~3) + k)


def pcrel(b: Bz, ld: int, add: int) -> int:
    return (lit(b, ld) + add + 4) & 0xFFFFFFFF


def espacios() -> dict:
    """Rangos físicos que leen realmente los scripts de cámara y si alguno toca el mapa de Darwin."""
    sc = ROOT / "scripts"
    t = (sc / "camera_darwin_buffers.py").read_text()
    m = re.search(r"BASE, SIZE = (0x[0-9a-f]+), (0x[0-9a-f]+)", t)
    assert m, "BASE, SIZE no encontrados en camera_darwin_buffers.py"
    base, size = int(m.group(1), 16), int(m.group(2), 16)
    bufs = [int(x, 16) for x in re.findall(r"\((0x8[0-9a-f]{7}), \d+\)", t)]
    lecturas, darwin = {}, []
    for f in sorted(sc.glob("*.py")) + sorted(sc.glob("*.sh")):
        s = f.read_text()
        if "/dev/mem" not in s or not f.name.startswith(("camera", "senser")):
            continue
        phys = sorted({int(x, 16) for x in re.findall(r"0x(8[0-9a-f]{7})\b", s)})
        lecturas[f.name] = {"lee": "if=/dev/mem" in s, "escribe": "of=/dev/mem" in s, "fisicas": [f"{p:#x}" for p in (phys[:1] + phys[-1:])]}
        if re.search(r"0x20[0-9a-f]{6}\b", s):
            darwin.append(f.name)
    return {
        "T022_T023": {"ventana": [f"{base:#x}", f"{base + size:#x}"], "buffers": [f"{x:#x}" for x in bufs],
                      "en_DRAM_BIONZ": BIONZ_DRAM[0] <= base and base + size <= BIONZ_DRAM[1],
                      "solape_SRAM_Darwin": base < DARWIN_SRAM[1] and base + size > DARWIN_SRAM[0],
                      "solape_perifericos_Darwin": base < DARWIN_PERIPH[1] and base + size > DARWIN_PERIPH[0]},
        "scripts_que_usan_dev_mem": lecturas,
        "scripts_con_literales_0x20xxxxxx": darwin,
        "volcado_actualizador": {"RAM": [f"{BIONZ_DRAM[0]:#x}", f"{BIONZ_DRAM[1]:#x}"], "SFR": "0xf0000000"},
    }


def paquete(b: Bz) -> dict:
    """Constructor de `pkt` (0x43841070) y fuentes de pkt[1] y pkt[2..3], verificados por instrucciones."""
    g = pcrel
    got = (lit(b, 0x4383FBC8) + 0x4383FBCA + 4) & 0xFFFFFFFF
    cls, flag = g(b, 0x43841360, 0x43841364), g(b, 0x43841350, 0x43841354)
    est = [b.u32(got + lit(b, 0x4383FBD8)), b.u32(got + lit(b, 0x4383FBDE))]
    esperado = {
        0x43841088: "ldr r4, [sp, #0xc8]",  # pkt = 5.º argumento
        0x43841344: "strb r3, [r4]", 0x43841392: "strb r3, [r4, #1]", 0x43841396: "strb r2, [r4, #1]",
        0x438413A4: "strb r3, [r4, #1]", 0x438413B4: "strb r3, [r4, #1]",
        0x438413B6: "ldrh.w r0, [sl, #0x162]", 0x438413BA: "bl #0x4382fe08", 0x438413C4: "strb r3, [r4, #2]",
        0x438413CC: "strb r3, [r4, #2]", 0x438413D4: "strb r3, [r4, #3]", 0x438413DA: "strb r3, [r4, #4]",
        0x4384144A: "strb r3, [r4, #8]", 0x4382FE16: "cmp.w r0, #0xb00", 0x4382FE28: "ldrb.w r3, [r3, #0x102]",
        0x4382FE2C: "and r3, r3, #8", 0x437F8800: "adds r2, #0x40", 0x437F8816: "bl #0x43841070",
        0x437F87FE: "ldr r3, [r2, #0x20]",
        0x438D01EC: "ldrh r1, [r1, #0x10]", 0x438D01F2: "strh.w r1, [r2, #0x48]"}  # 0x438d0064 reescribe pkt[8..9]
    chk = {f"{a:#x}": ins(b, a) == e for a, e in esperado.items()}
    p = T022_PACKET
    return {
        "bytes": chk,
        "pkt_es_carga_mas_0x40": chk["0x437f8800"] and chk["0x437f87fe"],
        "globales_pkt1": {"clase_0x43eedecc": f"{cls:#x}", "flag_0x43f9b503": f"{flag:#x}"},
        "estructuras_sl": [f"{x:#x}" for x in est], "got": f"{got:#x}",
        "sl_0x162_fisicas": [f"{x + 0x162 + VIRT2PHYS:#x}" for x in est],
        "T022": {"pkt1": p[1], "pkt23": int.from_bytes(p[2:4], "little"), "pkt45": int.from_bytes(p[4:6], "little"),
                 "pkt_a_b": int.from_bytes(p[10:12], "little"), "pkt8": p[8],
                 "pkt23_supera_umbral_0xb00": int.from_bytes(p[2:4], "little") >= 0xB00,
                 "pkt8_inicial_0xa0_en_0x43841070": ins(b, 0x43841448) == "movs r3, #0xa0"},
    }


def direcciones(pk: dict) -> list[dict]:
    cls, flag = (int(v, 16) for v in pk["globales_pkt1"].values())
    sl = [int(x, 16) for x in pk["estructuras_sl"]]
    f = lambda v, n, nom, estado, pers, via: {"nombre": nom, "virt": f"{v:#x}", "fisica": f"{v + VIRT2PHYS:#x}", "bytes": n,
                                               "estado": estado, "persiste_tras_disparo": pers, "via": via}
    return [
        f(0x43F91E32, 22, "pkt 0x0c completo", "MEDIDO en T022", "sí, hasta el siguiente envío/reintento del 0x0c", "T022"),
        f(cls, 4, "clase de captura (pkt[1] clase 1/3)", "dirección por bytes; lectura no probada", "sí (copia estable)", "T022"),
        f(flag, 1, "flag de captura (pkt[1] bit 6)", "dirección por bytes; lectura no probada", "sí (copia estable)", "T022"),
        f(sl[0] + 0x162, 2, "[sl+0x162] estructura 1 (origen de pkt[2..3])", "dirección por bytes; lectura no probada", "no se sabe (AE la reescribe)", "T022"),
        f(sl[1] + 0x162, 2, "[sl+0x162] estructura 2 (origen de pkt[2..3])", "dirección por bytes; lectura no probada", "no se sabe (AE la reescribe)", "T022"),
    ]


def main() -> dict:
    b = Bz()
    pk = paquete(b)
    return {"A_espacios": espacios(), "B_paquete": pk, "C_direcciones": direcciones(pk)}


if __name__ == "__main__":
    out = main()
    d = ROOT / "analysis" / "e24-05h-5"
    d.mkdir(parents=True, exist_ok=True)
    (d / "protocolo.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str)[:3000])
