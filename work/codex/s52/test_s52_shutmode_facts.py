"""Comprobaciones estáticas S52; se ejecuta aislado con ``python3 -I``."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 0x43541000
A7S = ROOT / "work/claude/input/a7s-av-cam.bin"
A6000 = ROOT / "work/claude/input/a6000-av-cam.bin"


def at(blob: bytes, va: int, size: int) -> bytes:
    return blob[va - BASE : va - BASE + size]


def main() -> None:
    a7s, a6000 = A7S.read_bytes(), A6000.read_bytes()
    assert hashlib.sha256(a7s).hexdigest() == "b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e"
    assert hashlib.sha256(a6000).hexdigest() == "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

    # A7S: ldr.w [r7,#0x404]; cmp #2; bne: clase Silent -> destino clase 0.
    assert at(a7s, 0x438649F0, 12) == bytes.fromhex("d7f80424022a02d1704a7a44")
    # El llamador prepara ModeRsvParam con +4d0/+4d4/+4d5 y llama al constructor.
    assert at(a7s, 0x43828240, 20) == bytes.fromhex("0dab94f8d41494f8d524d0f8d00490f77bfbcaf6")
    # Constructor: param+9 se guarda en el byte +4 de su salida, no en SetExposure.
    assert at(a7s, 0x437B8958, 16) == bytes.fromhex("206081ea050582ea0606fff79dffa571")
    # SetExposure IMX235 selecciona ShutMode desde param+9 y su TBB sigue el límite <=4.
    assert at(a7s, 0x436F4198, 20) == bytes.fromhex("9af8096093f82d2093f82e7093f82f30ff2a18bf")
    assert at(a7s, 0x436F423E, 10) == bytes.fromhex("042e5cd8dfe806f0030b")
    # IMX210 también toma param+9 y admite el rango 0..4 antes de su TBB.
    assert at(a6000, 0x436D70BE, 10) == bytes.fromhex("b9f1040f00f2e480dfe8")

    # La literal de la ruta Silent resuelve al destino de clase concreto.
    assert int.from_bytes(at(a7s, 0x43864BBC, 4), "little") + 0x438649FE == 0x43F06BC8
    # Las vtables contienen exactamente los SetExposure recuperados.
    assert int.from_bytes(at(a7s, 0x43FCE078, 4), "little") == 0x436F4169
    assert int.from_bytes(at(a6000, 0x43FCC0B8, 4), "little") == 0x436D6F6D
    emulation = json.loads((ROOT / "work/codex/s52_shutmode_emulation.json").read_text())
    assert len(emulation["runs"]) == 30
    assert all(run["error"] is None for run in emulation["runs"])
    a7s_zero = next(run for run in emulation["runs"] if run["sensor"] == "imx235" and run["shutmode"] == 0)
    assert a7s_zero["calls"][0]["target"] == 0x436F2D10

    # S52/XCHECK: tipo Silent 2 activa la bandera A7S +0x748; la A6000
    # conserva el desplazamiento homólogo +0x740 pero no esta asignación.
    assert at(a7s, 0x43813E94, 16) == bytes.fromhex("8af7b6fe0228c4f88c0702d10123c4f8")

    # Constructor CAIF A7S: tipo 2 codifica modo 2 en +0xd y bit 5 en +0x12.
    assert at(a7s, 0x43863258, 20) == bytes.fromhex("d6f86c27022a08bf022300e0022397f88c139b01")
    assert at(a7s, 0x4386329A, 20) == bytes.fromhex("d6f86c27a2f102014a4242eb010298f800105201")
    # La clase 0/3 toma la ruta que escribe 2 en el byte +1 del paquete.
    assert at(a7s, 0x4386315C, 24) == bytes.fromhex("032b00d053b9dff878357b441b78012b01d1413300e00223")
    assert at(a6000, 0x4384137C, 20) == bytes.fromhex("032b0ad1dff884357b441b78012b01d1413300e0")

    # Clase 0 no alcanza la rama que envía el mensaje 0x22 (tipo 3).
    assert at(a7s, 0x438627D2, 20) == bytes.fromhex("274b7b441b68012b06d0032b0ed1244b7b441b78")

    # VD_Pre guarda el tipo obtenido por el conversor en el offset +0x7e8.
    assert at(a7s, 0x437B6F6C, 20) == bytes.fromhex("d9f80030d3f85002e7f746fe07f5ba512c31c7f8")


if __name__ == "__main__":
    main()
