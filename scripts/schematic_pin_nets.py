"""Empareja etiquetas de pin (IC5700) con redes por coordenada en una hoja vectorial del manual Sony.
Uso: python3 -I scripts/schematic_pin_nets.py PDF PAGINA
Limitación: empareja por fila (y) y columna; cableado cruzado requiere inspección visual."""
import re, subprocess, sys, xml.etree.ElementTree as ET

def words(pdf, page):
    xml = subprocess.run(["pdftotext", "-bbox", "-f", str(page), "-l", str(page), pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    xml = re.sub(r'<!DOCTYPE[^>]*>', '', xml).replace('xmlns="http://www.w3.org/1999/xhtml"', '')
    return [(float(w.get("xMin")), float(w.get("yMin")), w.text or "") for w in ET.fromstring(xml).iter("word")]

def rows(ws, tol=2.0):
    out = {}
    for x, y, t in ws:
        out.setdefault(round(y / tol), []).append((x, t))
    return {k: sorted(v) for k, v in sorted(out.items())}

if __name__ == "__main__":
    for k, r in rows(words(sys.argv[1], int(sys.argv[2]))).items():
        print(" | ".join(f"{t}@{x:.0f}" for x, t in r))
