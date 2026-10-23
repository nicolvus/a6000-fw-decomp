#!/usr/bin/env python3
"""Test S383: verifica nombres ForLiro del obturador como strings rechazados en libObj.so A6000."""
from pathlib import Path

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")

def test_shutter_forliro_strings_present():
    """Los nombres ForLiro del obturador están en .rodata como strings."""
    data = PATH.read_bytes()
    # .rodata de libObj.so A6000: addr=0xbc9598, off=0xbc9598, size=0x2c8a1a
    rodata = data[0xbc9598:0xbc9598 + 0x2c8a1a]
    names = ["SetSilentShutterModeForLiro", "SetShutDriveForLiro",
             "SetFrontEShutterModeForLiro", "SetIrisDriveForLiro", "SetDriveModeForLiro"]
    for n in names:
        assert n.encode() in rodata, f"string '{n}' no encontrada en .rodata"

def test_non_supported_string_present():
    """Existe el sufijo NON SUPPORTED en los mensajes de rechazo."""
    data = PATH.read_bytes()
    rodata = data[0xbc9598:0xbc9598 + 0x2c8a1a]
    assert b"NON SUPPORTED" in rodata

def test_shutter_type_not_in_a6000():
    """SetShutterTypeForLiro NO está en A6000 (solo en A6300)."""
    data = PATH.read_bytes()
    dynstr = data[0x011768:0x011768 + 0x0231e5]
    assert b"SetShutterTypeForLiro" not in dynstr, "SetShutterTypeForLiro no debería estar en A6000"

if __name__ == "__main__":
    test_shutter_forliro_strings_present(); print("PASS test_shutter_forliro_strings_present")
    test_non_supported_string_present(); print("PASS test_non_supported_string_present")
    test_shutter_type_not_in_a6000(); print("PASS test_shutter_type_not_in_a6000")
    print("\nTodos los tests S383 PASS")
