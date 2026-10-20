import importlib.util
import pathlib

root = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("sx", root / "scripts" / "string_xrefs.py")
sx = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(sx)  # type: ignore[union-attr]

d = (root / "analysis" / "av-cam-analysis-view.elf").read_bytes()
r = sx.xrefs(d, {0x43C9B376, 0x43C9B335, 0x43E99320})
assert r[0x43C9B376] == [0x4372858A]  # "[IMAGING_CAP]: EnterCapturingLv"
assert r[0x43C9B335] == [0x437284DA]  # "[IMAGING_CAP]: EnterCapturing"
assert 0x4378EA7C in r[0x43E99320]  # petición de modo de imagen (SetSequenceMode_img)
print("ok")
