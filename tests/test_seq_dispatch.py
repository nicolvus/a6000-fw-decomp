import importlib.util
import pathlib

root = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("sd", root / "scripts" / "seq_dispatch.py")
sd = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(sd)  # type: ignore[union-attr]

d = (root / "analysis" / "av-cam-analysis-view.elf").read_bytes()
t = sd.table(d)
assert t["got_base"] == "0x4401eee4"
assert t["cases"]["0xa"]["func"] == "0x4354c6d0" and t["cases"]["0xa"]["got_offset"] == "0x3594"
assert t["cases"]["0x9"]["func"] == "0x4354d740"
assert sd.word(d, 0x4380F098) == 0x3594  # literal GOT cargado por 0x4380ee0c
print("ok")
