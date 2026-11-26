"""G22 — auditoría de CFW instalables (`scripts/gui/harness/audita_cfw.py`), sin QEMU por defecto.

Cubre detección de tipo y rechazo, ficheros de Sony quitados (FALLO), parches binarios no declarados
(AVISO), generación del informe JSON/Markdown y un marcador de arranque real que se omite si faltan
los artefactos del arnés o no se pide con `AUDITA_CFW_ARRANQUE=1`.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
sys.path.insert(0, str(HARNESS))

import audita_cfw as A


def arbol(base: Path, ficheros: dict[str, bytes]) -> Path:
    for rel, datos in ficheros.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(datos)
    return base


def overlay(base: Path, ficheros: dict[str, bytes]) -> Path:
    """Directorio con `cam/usr`: el /usr completo del CFW (como lo deja `pkg_usr.py`)."""
    arbol(base / "cam" / "usr", ficheros)
    return base


def sony(tmp: Path, ficheros: dict[str, bytes]) -> Path:
    return arbol(tmp / "sony", ficheros)


def checks(r: dict) -> dict[str, dict]:
    return {c["id"]: c for c in r["checks"]}


def test_detecta_tipo_y_rechaza_un_fichero_cualquiera(tmp_path: Path) -> None:
    basura = tmp_path / "basura.bin"
    basura.write_bytes(b"no es un firmware")
    with pytest.raises(A.EntradaError):
        A.detecta_tipo(basura)
    assert A.main([str(basura)]) == 2  # error claro, no un OK falso

    dat = tmp_path / "falso.dat"
    dat.write_bytes(A.DAT_MAGIC + b"\0" * 64)
    assert A.detecta_tipo(dat) == "dat"
    n15 = tmp_path / "nflasha15.bin"
    n15.write_bytes(b"TPZL" + b"\0" * 64)
    assert A.detecta_tipo(n15) == "nflasha15"
    paquete = tmp_path / "pkg"
    paquete.mkdir()
    (paquete / "nflasha15.bin").write_bytes(b"TPZL" + b"\0" * 64)
    assert A.detecta_tipo(paquete) == "paquete"
    assert A.detecta_tipo(overlay(tmp_path / "ov", {"lib/a.so": b"A"})) == "overlay"
    vacio = tmp_path / "vacio"
    vacio.mkdir()
    with pytest.raises(A.EntradaError):
        A.detecta_tipo(vacio)

    # Un .dat con cabecera pero sin FDAT se informa como FALLO, no como excepción.
    r = A.audita(dat, completo=True, arranque=False, salida=tmp_path / "out")
    assert r["veredicto"] == "FALLO"
    assert checks(r)["contenedor.fdat_presente"]["ok"] is False


def test_fichero_de_sony_quitado_es_fallo(tmp_path: Path) -> None:
    base = sony(tmp_path, {"lib/a.so": b"AAAA", "bin/tool": b"#!/bin/sh\n"})
    cfw = overlay(tmp_path, {"lib/a.so": b"AAAA"})  # falta bin/tool
    r = A.audita(cfw, completo=True, arranque=False, salida=tmp_path / "out", usr_sony=base)
    c = checks(r)
    assert c["usr.ficheros_quitados"]["ok"] is False
    assert "bin/tool" in c["usr.ficheros_quitados"]["detalle"]
    assert r["veredicto"] == "FALLO"
    assert A.main([str(cfw), "--sin-arranque", "--usr-sony", str(base), "--salida", str(tmp_path / "cli")]) == 1


def test_parche_binario_no_declarado_es_aviso(tmp_path: Path) -> None:
    base = sony(tmp_path, {"lib/data.bin": b"\0" * 16})
    cfw = overlay(tmp_path, {"lib/data.bin": b"\0\0\0\x01" + b"\0" * 12})  # cambia el byte 3
    r = A.audita(cfw, completo=True, arranque=False, salida=tmp_path / "out", usr_sony=base)
    c = checks(r)
    assert c["estructura.parches"]["ok"] is True
    assert c["estructura.parches"]["aviso"] is True
    assert "lib/data.bin" in c["estructura.parches"]["detalle"]
    assert r["veredicto"] == "AVISO"

    decl = tmp_path / "declara.json"
    decl.write_text(json.dumps({"parches": {"lib/data.bin": ["0x3-0x4"]}}))
    r2 = A.audita(cfw, completo=False, arranque=False, salida=tmp_path / "out2", usr_sony=base, declara=decl)
    assert checks(r2)["usr.cambios_declarados"]["aviso"] is False
    r3 = A.audita(cfw, completo=True, arranque=False, salida=tmp_path / "out3", usr_sony=base, declara=decl)
    assert checks(r3)["estructura.parches"]["aviso"] is False
    assert r3["veredicto"] == "OK"

    malo = tmp_path / "malo.json"
    malo.write_text(json.dumps({"parches": {"lib/data.bin": ["0x3-0x99"]}}))
    r4 = A.audita(cfw, completo=True, arranque=False, salida=tmp_path / "out4", usr_sony=base, declara=malo)
    assert checks(r4)["estructura.parches_rangos"]["ok"] is False
    assert r4["veredicto"] == "FALLO"


def test_informe_json_y_markdown(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base = sony(tmp_path, {"lib/a.so": b"AAAA", "share/x": b"texto"})
    cfw = overlay(tmp_path, {"lib/a.so": b"AAAA", "share/x": b"texto", "lib/nuevo.so": b"BBBB"})
    out = tmp_path / "informe"
    assert A.main([str(cfw), "--completo", "--sin-arranque", "--usr-sony", str(base),
                   "--salida", str(out), "--json"]) == 0
    impreso = json.loads(capsys.readouterr().out)
    assert impreso["veredicto"] in ("OK", "AVISO")
    j = json.loads(Path(impreso["json"]).read_text())
    for clave in ("ruta", "sha256", "version", "checks", "veredicto", "fecha", "coste_s"):
        assert clave in j
    assert j["checks"] and all({"id", "ok", "detalle", "evidencia"} <= set(c) for c in j["checks"])
    assert "lib/nuevo.so" in j["usr"]["anadidos"]
    md = Path(impreso["markdown"]).read_text()
    assert "# Auditoría CFW" in md and "| Etapa | Comprobación |" in md and j["veredicto"] in md
    assert Path(impreso["json"]).parent == out


def test_lote_genera_indice_json_y_tabla(tmp_path: Path) -> None:
    base = sony(tmp_path, {"lib/a.so": b"AAAA"})
    for n in ("uno", "dos"):
        overlay(tmp_path / n, {"lib/a.so": b"AAAA"})
    idx = A.audita_lote(tmp_path, completo=True, arranque=False, salida=tmp_path / "lote", declara=None, usr_sony=base,
                        teclas="", espera=10, puerto=None)
    assert len(idx["items"]) == 2
    assert all(it["veredicto"] == "OK" for it in idx["items"])
    assert Path(idx["json"]).is_file() and Path(idx["markdown"]).is_file()
    tabla = Path(idx["markdown"]).read_text()
    assert "| CFW | Versión |" in tabla and "uno" in tabla and "dos" in tabla


@pytest.mark.skipif(not A.arranque_disponible(), reason="faltan artefactos del arnés (vmlinuz/base.cpio.gz/stage/cam/usr/QEMU)")
@pytest.mark.skipif(os.environ.get("AUDITA_CFW_ARRANQUE") != "1",
                    reason="arranque real desactivado; ejecutar con AUDITA_CFW_ARRANQUE=1 (≈3 min, 1 QEMU)")
def test_arranque_real_del_arnes(tmp_path: Path) -> None:
    """Marcador: Sony de serie con perfil y puerto propios; captura la primera pantalla sin IMEXIT."""
    r = A.sesion_arranque(None, "audit-test-marcador", A.puerto_libre(), tmp_path, "cfw", "", 300)
    assert r["primera"] and not r["im_exit"] and not r["qemu_murio"], r.get("error")
    assert (tmp_path / "cfw-1-primera.png").is_file()
    assert not [q for q in A.qemu_activos() if "live/audit-test-marcador/" in q]


def test_etapa_arranque_orquesta_overlay_y_comparacion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = sony(tmp_path, {"lib/a.so": b"AAAA"})
    cfw = overlay(tmp_path / "cfw", {"lib/a.so": b"AAAB"})
    usr = {"dir_cfw": cfw / "cam/usr", "dir_sony": base, "anadidos": [], "cambiados": ["lib/a.so"], "quitados": []}
    base_png = tmp_path / "base-menu.png"
    base_png.write_bytes(b"png")

    def falsa_sesion(overlay, perfil, puerto, salida, etiqueta, teclas, espera, hueco_max=900.0, nuevo=False):
        assert (overlay / "cam/usr/lib/a.so").read_bytes() == b"AAAB"  # el overlay lleva solo lo cambiado
        for n, nombre in ((1, "primera"), (2, "menu"), (3, "disparo")):
            (salida / f"{etiqueta}-{n}-{nombre}.png").write_bytes(b"png")
        return {"perfil": perfil, "puerto": puerto, "pngs": {"primera": f"{etiqueta}-1-primera.png",
                "menu": f"{etiqueta}-2-menu.png", "disparo": f"{etiqueta}-3-disparo.png"},
                "metricas": {k: {"negro": False} for k in ("primera", "menu", "disparo")},
                "im_exit": False, "qemu_murio": False, "menu_abre": True, "error": "", "coste_s": 1.0,
                "live_log": str(salida / "x.log")}

    monkeypatch.setattr(A, "sesion_arranque", falsa_sesion)
    monkeypatch.setattr(A, "base_sony", lambda *a, **k: {"pngs": {"menu": str(base_png)}, "metricas": {}})
    monkeypatch.setattr(A, "compara_png", lambda *a, **k: {"comparable": True, "fraccion_distinta": 0.1,
                                                           "no_fondo": [500, 600]})
    checks: list[dict] = []
    A.etapa_arranque(usr, checks, tmp_path, "perfil-test", 8635, "", 10)
    c = {x["id"]: x for x in checks}
    assert c["arranque.primera_pantalla"]["ok"] is True
    assert c["arranque.menu_abre"]["ok"] is True
    assert c["arranque.menu_frente_sony"]["ok"] is True
    assert not [x for x in checks if x["ok"] is False]

    def sin_hueco(*a, **k):
        raise A.EntradaError("hay 2 qemu-system-arm y no se libera un hueco")

    monkeypatch.setattr(A, "sesion_arranque", sin_hueco)
    checks2: list[dict] = []
    A.etapa_arranque(usr, checks2, tmp_path, "perfil-test", 8635, "", 10)
    c2 = {x["id"]: x for x in checks2}
    assert c2["arranque.no_arrancado"]["ok"] is None and c2["arranque.no_arrancado"]["material"] is True
    assert A.veredicto(checks2) == "PARCIAL"  # falta de QEMU no es un fallo del CFW
