import importlib.util
import pathlib

root = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("tc", root / "scripts" / "thumb_callers.py")
tc = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(tc)  # type: ignore[union-attr]

d = (root / "analysis" / "av-cam-analysis-view.elf").read_bytes()
calls: dict[int, list[int]] = {}
for src, dst in tc.bl_targets(d):
    calls.setdefault(dst, []).append(src)
# el codificador directo solo se llama desde la secuencia FUN_4354d740 (Sequence_HSRecGolfshot.cpp)
for fn in (0x4379B180, 0x4379B058, 0x4379AAF4):
    assert calls[fn] and all(0x4354D740 <= a < 0x4354EB00 for a in calls[fn]), hex(fn)
# RCVDataSet (0x43798ccc): HS (0x4354e62e) y rutas de película 0x43815xxx
assert sorted(calls[0x43798CCC]) == [0x4354E62E, 0x43815A12, 0x43815B22]
print("ok")
