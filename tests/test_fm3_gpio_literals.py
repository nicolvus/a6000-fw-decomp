import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "scripts"))
from fm3_gpio_literals import decode_bitband, describe_alias

def test_aliases_from_task():
    assert decode_bitband(0x42668234) == (0x40033410, 13)  # PDOR4 b13 = P4D
    assert decode_bitband(0x42668238) == (0x40033410, 14)  # P4E
    assert decode_bitband(0x4266811C) == (0x40033408, 7)   # PDOR2 b7 = P27

def test_names():
    assert describe_alias(0x42668238).endswith("PDOR4[14]")
    assert describe_alias(0x42664234).endswith("DDR4[13]")
    assert describe_alias(0x42660234).endswith("PFR4[13]")

if __name__ == "__main__":
    test_aliases_from_task(); test_names(); print("ok")
