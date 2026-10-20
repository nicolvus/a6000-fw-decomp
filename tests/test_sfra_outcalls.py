import sys

sys.path.insert(0, "scripts")
import sfra_outcalls as s  # noqa: E402

d = open("analysis/av-cam-analysis-view.elf", "rb").read()
o = s.outcalls(d)
assert 0x4390B3D0 in o and len(o) >= 10  # control positivo: hay llamadas salientes decodificadas
assert not [t for t in o if t in s.ANCHORS], "SFRA llama directamente a captura/CAIF/codificador"
print("ok")
