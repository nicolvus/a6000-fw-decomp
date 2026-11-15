import importlib.util
import pathlib

s = importlib.util.spec_from_file_location("f", pathlib.Path(__file__).parents[1] / "scripts" / "imx210_fps_limits.py")
f = importlib.util.module_from_spec(s)
s.loader.exec_module(f)  # type: ignore[union-attr]
m = {r["mode"]: r for r in f.table()}
assert len(m) == 13
assert (m[0x12]["cols"], m[0x12]["lines"], m[0x12]["hmax"], m[0x12]["vmax60"], m[0x12]["vmax50"]) == (2000, 570, 693, 650, 750)
assert abs(m[0x12]["fps60"] - 120.0) < 0.2 and round(m[0x0A]["fps60"]) == 260
assert m[0x05]["lines"] == 1124 and m[0x05]["fps_max"] < 70  # 1080p120 imposible: 1124 líneas a 12,82 us no llegan a 70 fps
assert m[0x12]["mpx_s"] < 150  # 2000x570x120 = 137 Mpx/s, cabe en el tope del codificador (134,6 Mpx/s de 1996x1124x60)
assert max(r["fps_max"] for r in m.values() if r["lines"] >= 1000) < 120
print("ok")
