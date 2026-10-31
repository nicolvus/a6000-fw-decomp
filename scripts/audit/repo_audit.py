"""Auditoría mecánica del repositorio: escribe knowledge/audit/estado.json (memoria temporal)."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import warnings
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "knowledge" / "audit" / "estado.json"
MEMORIA = ROOT / "knowledge" / "audit" / "memoria.json"
ESTADO_VIVOS = ("docs/STATE.md", "knowledge/CURRENT.md", "knowledge/PROGRESS.md")
ESTADO_DOCS = ("docs/STATE.md", "knowledge/CURRENT.md", "knowledge/PROGRESS.md", "CONTEXT.md", "knowledge/agents/NEEDS-HUMAN.md")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ESTADOS = {"ABIERTO", "PARCIAL", "NO_VERIFICADO", "BLOQUEADO", "DIFERIDO", "CERRADO", "DESCARTADO"}


def estado_valido(estado: str) -> bool:
    """Acepta el estado base y sus calificadores habituales ('CON LÍMITE', '(…)').

    El documento usa variantes como «CERRADO CON LÍMITE» o «ABIERTO (en prueba)»;
    el estado base sigue siendo uno de ESTADOS.
    """
    return any(
        estado == base or estado.startswith((base + " CON ", base + " ("))
        for base in ESTADOS
    )
MAX_JSON = 30_000_000
CAP = 60  # shortcut: lista truncada por categoría, subir si se necesita el detalle completo


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def tracked() -> list[str]:
    return [p for p in git("ls-files", "-z").split("\0") if p]


def clip(items: list) -> dict:
    return {"total": len(items), "muestra": items[:CAP]}


def check_git(files: list[str]) -> dict:
    sync = git("rev-list", "--left-right", "--count", "HEAD...origin/main").split()
    big = sorted(((ROOT / f).stat().st_size, f) for f in files if (ROOT / f).is_file())[-8:]
    return {
        "head": git("rev-parse", "--short", "HEAD").strip(),
        "adelante_atras_origin": [int(sync[0]), int(sync[1])],
        "versionados": len(files),
        "modificados_sin_commit": [ln for ln in git("status", "--porcelain").splitlines()],
        "versionados_e_ignorados": clip(git("ls-files", "-ci", "--exclude-standard").split("\n")[:-1]),
        "mayores": [{"bytes": s, "ruta": f} for s, f in reversed(big)],
        "binarios_versionados": clip([f for f in files if re.search(r"\.(so|bin|elf|zip|apk|pdf)$", f)]),
    }


def md_links(files: list[str]) -> dict:
    rotos, ignorados = [], []
    tset = set(files)
    for f in files:
        if not f.endswith(".md"):
            continue
        base = (ROOT / f).parent
        text = (ROOT / f).read_text(errors="replace")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        for m in LINK.finditer(text):
            t = m.group(1).split("#")[0]
            if not t or re.match(r"[a-z]+:", t) or t.startswith(("<", "/")) or not re.search(r"[/.]", t):
                continue  # shortcut: ignora destinos sin / ni punto (ruido de código entre corchetes)
            p = (base / t.split("?")[0]).resolve()
            try:
                rel = p.relative_to(ROOT).as_posix()
            except ValueError:
                rotos.append({"en": f, "enlace": t, "motivo": "fuera del repo"})
                continue
            if rel in tset:
                continue
            if p.exists():
                if not p.is_dir():
                    ignorados.append({"en": f, "enlace": t})
                continue
            rotos.append({"en": f, "enlace": t, "motivo": "no existe"})
    return {"rotos": clip(rotos), "existen_pero_no_versionados": clip(ignorados)}


SKIP_REFS = ("references/", "analysis/", "work/")
# Copias históricas y bitácora: sus cifras son de la fecha en que se escribieron, no se cruzan con la colección actual.
HISTORICAL = ("docs/history/", "knowledge/history/", "knowledge/PROGRESS.md")
REF = re.compile(r"`((?:tests|analysis|docs|scripts|knowledge|reports|tools|site)/[A-Za-z0-9_./\-]+\.[A-Za-z0-9]+)`")
RUNTIME = re.compile(r"\.(sock|dis|frames)$|/run/|node_modules|\.json/\.c$|\.jsonl$")


def path_refs(files: list[str]) -> dict:
    """Rutas entre comillas inversas en Markdown (fuera de references/analysis/work) que no existen."""
    tset, rotas = set(files), []
    for f in files:
        if not f.endswith(".md") or f.startswith(SKIP_REFS):
            continue
        for m in REF.finditer((ROOT / f).read_text(errors="replace")):
            r = m.group(1)
            if r not in tset and not (ROOT / r).exists() and not RUNTIME.search(r):
                rotas.append({"en": f, "ruta": r})
    return clip(rotas)


def collected_counts() -> dict[str, int]:
    py = ROOT / ".venv" / "bin" / "python"
    out = subprocess.run([str(py), "-m", "pytest", "tests", "--collect-only", "-q"], check=False, cwd=ROOT, capture_output=True, text=True).stdout
    return dict(Counter(ln.split("::")[0] for ln in out.splitlines() if ln.startswith("tests/") and "::" in ln))


CLAIM = re.compile(r"(\d+)\s+(?:tests|pruebas)[^`\n]{0,40}`(tests/[\w/]+\.py)`|`(tests/[\w/]+\.py)`\s*\((\d+)\s+(?:tests|pruebas)")


def test_claims(files: list[str], counts: dict[str, int]) -> dict:
    """Cifras «N tests» junto a un archivo de prueba que difieren de lo colectado."""
    dif = []
    for f in files:
        if not f.endswith(".md") or f.startswith(SKIP_REFS + HISTORICAL):
            continue
        for m in CLAIM.finditer((ROOT / f).read_text(errors="replace")):
            n, path = (int(m.group(1)), m.group(2)) if m.group(1) else (int(m.group(4)), m.group(3))
            real = counts.get(path)
            if real is not None and real != n:
                dif.append({"en": f, "archivo": path, "dice": n, "real": real})
    return clip(dif)


def json_py(files: list[str]) -> dict:
    warnings.simplefilter("ignore")  # los .py ajenos emiten SyntaxWarning al analizarse
    mal_json, mal_py = [], []
    for f in files:
        p = ROOT / f
        if not p.is_file():
            continue
        if f.endswith(".json") and p.stat().st_size < MAX_JSON:
            try:
                json.loads(p.read_text())
            except Exception as e:  # noqa: BLE001
                mal_json.append({"ruta": f, "error": str(e)[:80]})
        elif f.endswith(".py"):
            try:
                ast.parse(p.read_text())
            except Exception as e:  # noqa: BLE001
                mal_py.append({"ruta": f, "error": str(e)[:80]})
    return {"json_invalido": clip(mal_json), "python_invalido": clip(mal_py)}


def tests_cobertura(files: list[str]) -> dict:
    tests = {Path(f).name for f in files if f.startswith("tests/") and f.endswith(".py")}
    sin_prueba = []
    for f in files:
        if re.match(r"analysis/s403_pendientes/[^/]+\.py$", f):
            stem = Path(f).stem
            if not any(stem in t for t in tests):
                sin_prueba.append(f)
    sin_prueba_scripts = [
        f
        for f in files
        if re.match(r"scripts/[^/]+\.py$", f) and not any(Path(f).stem in t for t in tests)
    ]
    return {
        "archivos_de_prueba": len(tests),
        "s403_sin_prueba": clip(sin_prueba),
        "scripts_raiz_sin_prueba_por_nombre": clip(sin_prueba_scripts),
    }


def pendientes() -> dict:
    text = (ROOT / "docs" / "PENDIENTES.md").read_text()
    filas = []
    seccion = ""
    for ln in text.splitlines():
        if ln.startswith("## "):
            seccion = ln[3:].strip()
        m = re.match(r"\|\s*([A-Z]\d+[a-z]?|—)\s*\|\s*([^|]+?)\s*\|", ln)
        if m:
            filas.append({"id": m.group(1), "campo2": m.group(2), "seccion": seccion})
    abiertas = [
        f for f in filas if f["seccion"].startswith(("A.", "B.", "D.", "E.")) and f["id"] != "—"
    ]
    estados_mal = [f for f in abiertas if not estado_valido(f["campo2"])]
    ids = [f["id"] for f in filas if f["id"] != "—"]
    dup = [i for i, n in Counter(ids).items() if n > 1]
    return {
        "filas": len(filas),
        "abiertas_por_estado": dict(Counter(f["campo2"] for f in abiertas)),
        "estados_no_validos": estados_mal,
        "ids_duplicados": dup,
        "ids_abiertos": [f["id"] for f in abiertas],
    }


def memoria(estado: dict, files: list[str]) -> dict:
    """Memoria temporal: pendientes por ID, fechas de los documentos de estado y comprobaciones de coherencia."""
    text = (ROOT / "docs" / "PENDIENTES.md").read_text()
    abiertas, cerradas, seccion = {}, [], ""
    for ln in text.splitlines():
        if ln.startswith("## "):
            seccion = ln[3:].strip()
        m = re.match(r"\|\s*([A-Z]\d+[a-z]?)\s*\|\s*([^|]+?)\s*\|", ln)
        if m:
            (cerradas.append(m.group(1)) if seccion.startswith("Cerradas") else abiertas.__setitem__(m.group(1), m.group(2)))
    fechas = {d: git("log", "-1", "--format=%cs", "--", d).strip() for d in ESTADO_DOCS}
    # El último cambio registrado en PENDIENTES debe constar en los documentos de estado vivos.
    ultima = re.findall(r"^\| (\d\d-\d\d-\d{4}) \|", text.split("## Registro de cambios")[-1], re.M)[-1]
    menciona = {d: ultima in (ROOT / d).read_text() for d in ESTADO_VIVOS}
    readme = (ROOT / "README.md").read_text()
    enlaces_pend = [e for e in estado["enlaces_md"]["rotos"]["muestra"] if e["en"] == "docs/PENDIENTES.md"]
    coherencia = {
        "head_igual_a_origin": estado["git"]["adelante_atras_origin"] == [0, 0],
        "ids_pendientes_unicos": not estado["pendientes"]["ids_duplicados"],
        "estados_validos": not estado["pendientes"]["estados_no_validos"],
        "enlaces_de_pendientes_validos": not enlaces_pend,
        "docs_de_estado_mencionan_ultimo_cambio": all(menciona.values()),
        "readme_cita_cierres_recientes": all(i in readme for i in ("E26", "3.25", "T040")),
        "sin_json_ni_python_invalido": not (estado["json_py"]["json_invalido"]["total"] or estado["json_py"]["python_invalido"]["total"]),
        "sin_rutas_citadas_inexistentes": estado["rutas_citadas_inexistentes"]["total"] == 0,
        "volcados_sha256_ok": not estado["volcados_sha256"]["falla"],
    }
    return {
        "head": estado["git"]["head"],
        "pruebas_colectadas": estado["pruebas_colectadas"],
        "pendientes_abiertos": abiertas,
        "pendientes_cerrados": cerradas,
        "documentos_de_estado": {d: {"ultimo_commit": fechas[d], "menciona_ultimo_cambio": menciona.get(d)} for d in ESTADO_DOCS},
        "coherencia": coherencia,
        "incoherencias": [k for k, v in coherencia.items() if not v],
    }


def cifras() -> dict:
    """Cifras de pruebas citadas en documentos clave (para cruzar con la colección real)."""
    pat = re.compile(r"(\d[\d ]{2,6})\s+(?:aprobadas|pruebas|passed)")
    out = {}
    for rel in ("README.md", "docs/PENDIENTES.md", "docs/STATE.md", "knowledge/CURRENT.md"):
        t = (ROOT / rel).read_text(errors="replace")
        out[rel] = sorted({m.group(1).strip() for m in pat.finditer(t)})[-12:]
    return out


def site_status(files: list[str]) -> dict:
    st = json.loads((ROOT / "site" / "status.json").read_text())
    reales = [f for f in files if re.match(r"docs/capture/s\d+[-_a-zA-Z0-9]*\.md$", f)]
    return {
        "status_documented_count": st.get("documented_count"),
        "status_latest": st.get("latest"),
        "informes_s_en_docs_capture": len(reales),
    }


def sha_dumps() -> dict:
    res = {"ok": 0, "falla": [], "sin_archivo": 0}
    for sums in (ROOT / "analysis" / "camera-dumps").glob("*/SHA256SUMS"):
        for ln in sums.read_text().splitlines():
            parts = ln.split(None, 1)
            if len(parts) != 2:
                continue
            h, name = parts[0], parts[1].lstrip("* ")
            if name == "SHA256SUMS":
                continue  # autorreferencia con hash de archivo vacío
            p = sums.parent / name
            if not p.is_file():
                res["sin_archivo"] += 1
                continue
            import hashlib

            d = hashlib.sha256()
            with p.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    d.update(chunk)
            if d.hexdigest() == h:
                res["ok"] += 1
            else:
                res["falla"].append(str(p.relative_to(ROOT)))
    return res


def main() -> int:
    files = tracked()
    counts = collected_counts()
    estado = {
        "git": check_git(files),
        "enlaces_md": md_links(files),
        "json_py": json_py(files),
        "rutas_citadas_inexistentes": path_refs(files),
        "cifras_de_pruebas_discrepantes": test_claims(files, counts),
        "pruebas_colectadas": sum(counts.values()),
        "pruebas": tests_cobertura(files),
        "pendientes": pendientes(),
        "cifras_citadas": cifras(),
        "site": site_status(files),
        "volcados_sha256": sha_dumps(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(estado, indent=1, ensure_ascii=False) + "\n")
    mem = memoria(estado, files)
    MEMORIA.write_text(json.dumps(mem, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"incoherencias": mem["incoherencias"], "abiertos": len(mem["pendientes_abiertos"]), "cerrados": len(mem["pendientes_cerrados"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
