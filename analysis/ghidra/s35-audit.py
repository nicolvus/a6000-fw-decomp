"""Audita integridad y exports S35 sin ejecutar firmware."""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
BLOB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
EXPECTED = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main():
    blob = BLOB.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == EXPECTED
    paths = [OUT / "silent-liro.gpr", *sorted((OUT / "silent-liro.rep").rglob("*"))]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in paths if p.is_file() and not p.name.endswith(".lock")}
    manifest = OUT / "s35-integrity.json"
    if "--baseline" in sys.argv:
        assert not manifest.exists()
        manifest.write_text(json.dumps(hashes, indent=2) + "\n")
        print("PASS SHA y baseline proyecto")
        return
    assert hashes == json.loads(manifest.read_text())
    exports = list(OUT.glob("s35-objects*.json"))
    assert exports, "Faltan exports S35"
    for path in exports:
        data = json.loads(path.read_text())
        assert data["source_sha256"] == EXPECTED
        for row in data["functions"]:
            if "entry" in row:
                assert row["status"] == "decompiled", row["query"]
    def word(address):
        return struct.unpack_from("<I", blob, address - 0x43541000)[0]

    objects = [(0x44023400, 0x43E7EF80), (0x44024D10, 0x43E7EE00),
               (0x44021914, 0x43E7EE44), (0x4402603C, 0x43E7EED4)]
    for slot, target in objects:
        assert word(slot) == target
    vtables = [(0x44021C18, 0x43FCBF80, 0x43AD828C),
               (0x44026C8C, 0x43FCBE70, 0x43AD79AE),
               (0x4402430C, 0x43FCBFC0, 0x436D30E8),
               (0x44026090, 0x43FCBFF0, 0x436D32A4),
               (0x4401EFD8, 0x43FCBEE8, 0x436D26E4),
               (0x44026ACC, 0x43FCBD78, 0x436D23E0)]
    for slot, table, method in vtables:
        assert word(slot) + 8 == table
        assert word(table + 8) == method | 1
    scan = json.loads((OUT / "s35-causes-scan.json").read_text())
    assert scan["source_sha256"] == EXPECTED
    masks = [r for r in scan["immediate_hits"] if "3380000" in r["instruction"]]
    assert len(masks) == 1 and masks[0]["site"] == "436cf958"
    rows = {r["query"]: r for p in exports for r in json.loads(p.read_text())["functions"]}
    for address, offset in [("436d30c8", "0xa1610"), ("436d3284", "0xa1710"),
                            ("436d26c4", "0xa1210"), ("436d23c0", "0xa1310")]:
        assert offset in rows[address]["pseudo_code"]
    result = {"source_sha256": EXPECTED, "project_unchanged": True,
              "slots_verified": len(objects), "vtables_verified": len(vtables),
              "exports": len(exports), "scan_immediates": len(scan["immediate_hits"]),
              "status": "PASS"}
    (OUT / "s35-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    print("| Estado | Resultado S35 |")
    print("|---|---|")
    print("| VERIFICADO | Ofmt/Ifmt, vtables y +8; lectura/RMW SGC 0xfc0a… |")
    print("| PARCIAL | Factores DFE sin correspondencia física con APL |")
    print("| INFERENCIA | Activación SGC compatible con flujo mayor; no prueba completion |")
    print("| NO_VERIFICADO | Bit 0x00200000, cadena APL→IRQ→EC/LM y fin exposición |")
    print("| FRONTERA ESTATICA AGOTADA | Vía de cuatro objetos; falta routing/traza pasiva |")
    print("| PRÓXIMO PASO EXACTO | Proveedor DMM 0x43561524, tabla+0x2e4 y lector YC |")


if __name__ == "__main__":
    main()
