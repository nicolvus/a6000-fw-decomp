import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("t", pathlib.Path(__file__).parents[1] / "scripts" / "imx210_param_tables.py")
t = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(t)  # type: ignore[union-attr]

d = t._read()
st = t.ctor_stack_args(d)
assert st[0x18] == 0x43BC16DC and st[0x24] == 0x43BC1D58 and len(st) == 14
m = {r["mode"]: r for r in t.per_mode(d)}
assert len(m) == 13
assert (m[0x0B]["row72_camcore"][7], m[0x0B]["row72_camcore"][15]) == (6000, 4000) == (m[0x2F]["row72_camcore"][7], m[0x2F]["row72_camcore"][15])
assert (m[0x05]["row72_camcore"][7], m[0x05]["row72_camcore"][15]) == (1996, 1124)
for k in (0x01, 0x05, 0x0F):  # periodo de cuadro NTSC: a*b = 900900 = 54.054 MHz / 59.94 Hz
    a, b = m[k]["ab12_variant0"][:2]
    assert a * b == 900900, hex(k)
assert m[0x0B]["ab12_variant0"][0] * m[0x0B]["ab12_variant0"][1] == 3608064
print("ok")
