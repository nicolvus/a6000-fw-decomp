"""G116 (LUT-INT-2) — la app web (`site/lut`) genera el mismo `.LUT` que el firmware.

Se ejecuta el conversor real con Node sobre un `.cube` determinista y se compara byte a byte con `lut_sd_userland.referencia`
(la referencia del ARM emulado), además de validar el paquete con `lut_pkg.desempaqueta`. Sin navegador: el módulo es ES puro.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui")]
import lut_pkg as PK
import lut_sd_userland as U

SITIO = ROOT / "site/lut"
node = shutil.which("node")
needs_node = pytest.mark.skipif(node is None or not (SITIO / "lut.js").is_file(), reason="Node o app web ausente")


def cubo(n: int) -> str:
    filas = []
    for r in range(n):
        for g in range(n):
            for b in range(n):
                x, y, z = r / (n - 1), g / (n - 1), b / (n - 1)
                filas.append(f"{min(1, x * 1.1):.6f} {y * 0.9:.6f} {z * 0.8:.6f}")
    return f'TITLE "web-{n}"\nLUT_3D_SIZE {n}\n' + "\n".join(filas) + "\n"


def lee(contenido: bytes, tmp_path, node) -> dict:
    """Lo que la web ve en un `.LUT`: tabla, curva y un gris de la previsualización (Node)."""
    fichero = tmp_path / "lee.LUT"
    fichero.write_bytes(contenido)
    js = """
import {readFileSync} from "node:fs";
import {leeLut, aplicaColor} from "LUT_JS";
const r = leeLut(readFileSync(process.argv[2]));
if (!r) { console.log("null"); process.exit(1); }
const hex = (b) => Array.from(b).map((v) => v.toString(16).padStart(2, "0")).join("");
console.log(JSON.stringify({tabla: hex(r.tabla), curva: r.curva ? hex(new Uint8Array(r.curva.buffer, r.curva.byteOffset, r.curva.byteLength)) : null, gris: aplicaColor(0.5, 0.5, 0.5, r.nodos, r.curva)}));
""".replace("LUT_JS", (SITIO / "lut.js").as_uri())
    guion = tmp_path / "lee.mjs"
    guion.write_text(js, encoding="utf-8")
    out = subprocess.run([node, str(guion), str(fichero)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


@needs_node
@pytest.mark.parametrize("n", [2, 5, 33])
def test_la_web_produce_el_mismo_paquete_que_el_firmware(tmp_path, n):
    texto = cubo(n)
    entrada, salida = tmp_path / "a.cube", tmp_path / "LUT1.LUT"
    entrada.write_text(texto)
    subprocess.run([node, "lut_cli.mjs", str(entrada), str(salida)], cwd=SITIO, check=True, capture_output=True)
    b = salida.read_bytes()
    assert len(b) == PK.TAM1
    carga = PK.valida(b)
    assert carga == U.referencia(texto)                       # tabla idéntica a la del ARM (byte a byte)


@needs_node
def test_la_web_lee_un_paquete_v2_con_curva_tal_cual(tmp_path):
    """El `.LUT` final (v2 con curva, el que genera `lut_pkg.py`) se lee y se previsualiza sin reinterpretarlo."""
    texto = cubo(5)
    carga = U.referencia(texto)
    curva = [round(1023 * (i / 1023) ** 0.9) for i in range(1024)]
    pkg = PK.paquete(carga, curva)
    d = lee(pkg, tmp_path, node)
    assert bytes.fromhex(d["tabla"]) == carga
    assert bytes.fromhex(d["curva"]) == PK.np_u16(curva)
    v1 = lee(PK.paquete(carga), tmp_path, node)["gris"]                                   # misma tabla sin curva
    assert d["gris"] != v1 and sum(d["gris"]) > sum(v1)                                  # pow(x, 0.9) aclara, no oscurece
    assert lee(PK.paquete(carga, curva, usa_t=False), tmp_path, node)["curva"] is None   # usa_T = 0: se guarda y no se usa


@needs_node
def test_la_web_rechaza_un_cube_incompleto(tmp_path):
    entrada = tmp_path / "malo.cube"
    entrada.write_text("LUT_3D_SIZE 3\n0 0 0\n")
    r = subprocess.run([node, "lut_cli.mjs", str(entrada), str(tmp_path / "x.LUT")], check=False, cwd=SITIO, capture_output=True, text=True)
    assert r.returncode == 1 and "faltan filas" in r.stderr


@needs_node
def test_la_previsualizacion_es_la_cadena_del_repositorio(tmp_path):
    """El gris neutro no cambia con una tabla de identidad (cadena sRGB → YCbCr → LUT → RGB sin deltas)."""
    guion = tmp_path / "gris.mjs"
    js = """
import {convierte, leeLut, aplicaColor} from "LUT_JS";
const nl = String.fromCharCode(10);
const filas = [];
for (let r = 0; r < 2; r++) for (let g = 0; g < 2; g++) for (let b = 0; b < 2; b++) filas.push(r + " " + g + " " + b);
const c = convierte("LUT_3D_SIZE 2" + nl + filas.join(nl));
const {nodos} = leeLut(c.pkg);
console.log(JSON.stringify({n: c.n, grises: [0, 0.5, 1].map((v) => aplicaColor(v, v, v, nodos))}));
""".replace("LUT_JS", (SITIO / "lut.js").as_uri())
    guion.write_text(js, encoding="utf-8")
    r = subprocess.run([node, str(guion)], cwd=SITIO, check=True, capture_output=True, text=True)
    d = json.loads(r.stdout)
    assert d["n"] == 2
    for v, rgb in zip((0, 0.5, 1), d["grises"]):
        assert all(abs(c - v) < 2 / 255 for c in rgb), (v, rgb)
