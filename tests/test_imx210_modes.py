import sys, pathlib
root = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(root / "scripts"))
from imx210_modes import Img, matrix

def test_matrix():
    m = matrix(Img(str(root / "analysis/av-cam-analysis-view.elf")))
    assert m["modes"] == [0xb, 1, 5, 0x10, 7, 0x12, 3, 0xa, 0xf, 0x18, 0x1a, 0x19, 0x2f]
    assert len(m["rows"]) == 59
    r = {x["reg"]: x["values"] for x in m["rows"] if x["reg"] not in (0x12a,)}
    assert r[0x01][0] == 0x44 and r[0x01][2] == 0x41      # still vs vídeo: bit0 / bit2
    assert r[0x16][0] == 0x64 and r[0x16][3] == 0x18

if __name__ == "__main__":
    test_matrix(); print("ok")
