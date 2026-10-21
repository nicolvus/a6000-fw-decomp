"""S72-11: expansiones candidatas de siglas por iniciales de frases en las cadenas de av-cam.bin (heurística)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
S = ["ADF", "IDT", "VDF", "VEF", "SFRS", "SFRA", "WSX", "ACCY", "AUGI", "SAD", "APL", "ZIT", "FDT", "VAT", "PRC", "VAE", "VOT", "BSFS", "ENCOUCSTAT", "CLK_CTRL", "VPH", "SSBI"]
texts = {m.group().decode() for m in re.finditer(rb"[\x20-\x7e]{6,80}", data)}
for sg in S:
    k = len(sg.replace("_", ""))
    hits = set()
    for t in texts:
        words = re.findall(r"[A-Za-z][a-z]+|[A-Z]{2,}", t)
        for i in range(len(words) - k + 1):
            if "".join(w[0].upper() for w in words[i:i + k]) == sg.replace("_", "") and len({w.lower() for w in words[i:i + k]}) == k:
                hits.add(" ".join(words[i:i + k]))
    good = [h for h in hits if all(len(w) > 2 for w in h.split())][:5]
    print(sg, good)
