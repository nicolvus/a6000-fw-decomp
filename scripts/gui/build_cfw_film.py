#!/usr/bin/env python3
"""G97 — CFW «Film»: SOLO Silent Shooting (tres estados del 3.80 + Silent calibrado R87) y el menú «Film» con los 38 looks de G97. Nada más del CFW:
sin Picture Profile, sin LUT de la SD, sin el resto de ajustes. NO instala nada.

Encadena lo existente:
  1. `build_silent_menu_test` (nodo Silent pid 0x12, página, textos) y `silent_descriptor`;
  2. `build_pp_menu` con la especificación sustituida por la carpeta «Film» (8 filas de ≤ 7 opciones, ajustes CFW de 1 B) + el userland de
     `film_userland` en `viewUnified2.so` (`DT_INIT` → `films_hilo`, datos de los 38 looks en el mismo segmento);
  3. `libObj.so` = 3.21 + eco de Silent (`patch_libobj_eco`), sin el parche PP;
  4. BIONZ = el de `base-380.tar` (3.38 + tres estados con Silent manda sobre EFCS) + `patch_silent_r5` (R87) + `film_patch` (LUT + curva tras la gamma);
  5. `build_nflasha15` + `build_package_nflasha15` (Darwin v3, sin `nflasha5`).
Desde el 3.92 (G104) el av-cam acepta el código ISO 0x2f (409600: topes, tabla de EXIF y códigos 0x4b…0x50, `iso_avcam_patch`) y la pantalla ISO
llega a 204800 (`iso_ui_patch.N_CFW`; 256000…409600 hechas pero `libObj` las devuelve a 204800, G104 §8.7: filas de `viewUnified4` y `WrapperIso` de `viewUnified2`; `iso_libobj_patch`; `iso_ui_recursos`: textos e iconos de la A7S).
Desde el 3.92 (G103) `CautionConfig.so` lleva además «Extra fine» en Calidad (`quality_exfine_patch`, G39: 8 B).
Con `--pp` (G102, 3.92+): además el Picture Profile del CFW completo (menú PP con cada ajuste en una sola fila y todas sus opciones, las mismas listas completas de PP/Gamma/Color Mode/valores en el menú Fn y PP en la
rueda, `libObj` con S-Log/S-Gamut y eco PP, núcleo con `build_base_pp.bionz_cfw` debajo de las películas).
Uso: build_cfw_film.py SALIDA [--version 3.87] [--looks analysis/lut/g97/looks.npz] [--pp]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in ("scripts/gui", "scripts", "scripts/lut", "scripts/g22"):
    sys.path.insert(0, str(ROOT / d))
import build_base_pp
import build_cfw_completo as C
import build_nflasha15
import build_package_nflasha15
import build_pp_menu
import build_silent_menu_test
import exfine_size_patch
import film_patch
import film_userland as FU
import iso_avcam_patch
import iso_libobj_patch
import iso_ui_patch
import iso_ui_recursos
import patch_libobj_ppeco
import patch_silent_r5
import pp_menu_spec as M
import quality_exfine_patch

LOOKS = ROOT / "analysis/lut/g97/looks.npz"


AYUDA_PP = "Picture Profile: choose from the full list of values."


FUNCIONES = frozenset({"film", "pp", "exfine", "iso"})   # G105: base = Silent (tres estados + Silent calibrado + Darwin v3); cada función se suma aparte
BISECCION = frozenset({"film_ui", "film_nucleo", "iso_ui", "iso_nucleo"})   # G106: solo la parte userland o solo la capa del núcleo de film/iso (aislar fallos en cámara)
NUCLEO_FILM, NUCLEO_ISO, UI_FILM, UI_ISO = {"film", "film_nucleo"}, {"iso", "iso_nucleo"}, {"film", "film_ui"}, {"iso", "iso_ui"}
POR_DEFECTO = frozenset({"film", "exfine", "iso"})     # el CFW Film 3.92 (con `--pp` además «pp»)


def bionz_de(funciones=POR_DEFECTO):
    """Núcleo: 3.38 + tres estados (base-380) → PP del 3.81 con Silent calibrado (`pp`) o solo Silent calibrado (R87) → + películas (`film`) → + ISO (`iso`)."""
    def f(original: bytes) -> bytes:
        d = build_base_pp.bionz_cfw(original) if "pp" in funciones else patch_silent_r5.apply_bytes(original)
        d = film_patch.apply_bytes(d) if NUCLEO_FILM & set(funciones) else d
        return iso_avcam_patch.apply_bytes(d) if NUCLEO_ISO & set(funciones) else d
    return f


bionz = bionz_de(POR_DEFECTO)
bionz_pp = bionz_de(POR_DEFECTO | {"pp"})


def menu_silent(stage: Path, dest: Path) -> None:
    """Solo Silent (sin carpetas nuevas): el `CautionConfig.so` y los textos de `build_silent_menu_test` (ya en `stage`) y el `viewUnified2.so` que hace
    `build_pp_menu.main(..., silent=True)` sin ajustes: entrada Silent antes del EFCS, descriptor de tres estados y EFCS en gris con Silent."""
    import add_menu_entry
    import pid_space
    import silent_descriptor
    orig = C.DEV_A / C.USR
    (dest / "lib").mkdir(parents=True, exist_ok=True)
    (dest / "share/app").mkdir(parents=True, exist_ok=True)
    vu2 = add_menu_entry.patch((orig / "lib/viewUnified2.so").read_bytes(), [C.SILENT_DELTA])
    vu2 = silent_descriptor.patch(vu2, silent_descriptor.TABLA_D_VU2, silent_descriptor.DESC_EFCS_VU2)
    (dest / "lib/viewUnified2.so").write_bytes(pid_space.patch(vu2, [], gris_efcs=True))
    shutil.copy(stage / C.USR / "lib/CautionConfig.so", dest / "lib/CautionConfig.so")
    parcheados = ["lib/CautionConfig.so", "lib/viewUnified2.so"]
    for f in (stage / C.USR / "share/app").glob("string_*.uxc"):
        if f.read_bytes() != (orig / "share/app" / f.name).read_bytes():
            shutil.copy(f, dest / "share/app" / f.name)
            parcheados.append(f"share/app/{f.name}")
    man = {"idiomas": sorted(p.rsplit("/", 1)[1] for p in parcheados if p.startswith("share/")),
           "parcheados": {p: C.sha((dest / p).read_bytes()) for p in parcheados}}
    (dest / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))


def menu_film(pp: bool = False, maximo: int = 99, film: bool = True) -> dict:
    """Sin `pp`: la especificación del menú pasa a ser solo la carpeta «Film» (los ajustes guardan 1 B en el Backup; sin Picture Profile).
    Con `pp` (G102): carpeta «Picture Profile» (configurar del 3.81; cada ajuste en UNA fila con todas sus opciones salvo `maximo` < 99) + carpeta «Film»;
    en el menú Fn «Film» y las listas completas de PP;
    en la rueda «Film» (9) y «Picture Profile» (10). Devuelve los argumentos con nombre de `build_pp_menu.main`."""
    aj = FU.ajustes()
    todas = FU.ajuste_todas()
    if pp:
        kw = build_pp_menu.configurar(gam=True, col=True, acc=False, fn_pp=True, maximo=maximo)
        fn_pp = list(build_pp_menu.FN_TREES)
        build_pp_menu.FN_AYUDA.clear()
        build_pp_menu.FN_AYUDA.update(dict.fromkeys(fn_pp, AYUDA_PP))
        build_pp_menu.SD_USERLAND = False
        if not film:                                                   # G105: solo PP (menú, Fn y el selector en la rueda, valor 9)
            build_pp_menu.EXTRA_TREES[:] = []
            build_pp_menu.RUEDA[:] = [fn_pp[0]]
            return kw
        for a in (*aj, todas):
            M.SETTINGS[a.id] = M.S(a.id, a.label, 0, tuple((t, i) for i, (t, _) in enumerate(a.opciones)), "g97", backup=a.backup)
        M.PIDS[:] = range(M.PIDS[0], M.PIDS[0] + len(M.SETTINGS))
        build_pp_menu.EXTRA_TREES[:] = [("folder", FU.CARPETA, M.paginar([a.id for a in aj]))]
        build_pp_menu.FN_TREES[:] = [todas.id, *fn_pp]
        build_pp_menu.RUEDA[:] = [todas.id, fn_pp[0]]                  # el selector de perfil
        return kw
    M.SETTINGS.clear()
    for a in (*aj, todas):
        M.SETTINGS[a.id] = M.S(a.id, a.label, 0, tuple((t, i) for i, (t, _) in enumerate(a.opciones)), "g97", backup=a.backup)
    M.TREE = ("folder", FU.CARPETA, M.paginar([a.id for a in aj]))
    M.PIDS[:] = range(M.PIDS[0], M.PIDS[0] + len(aj) + 1)
    build_pp_menu.EXTRA_TREES[:] = []
    build_pp_menu.RUEDA[:] = [todas.id]          # G101: «Film» también en la rueda de control (al girarla, la franja horizontal de los 39)
    build_pp_menu.FN_TREES[:] = [todas.id]       # G100: «Film» con Off + los 38 en el menú Fn (franja horizontal) y en las listas de las 12 ranuras
    build_pp_menu.SD_USERLAND = False
    return {}


def build_files(work: Path, looks: Path, pp: bool = False, maximo: int = 99, funciones=None) -> Path:
    """`funciones` (G105) ⊆ FUNCIONES sobre la base Silent; None = el CFW Film (POR_DEFECTO, más «pp» si `pp`)."""
    funciones = frozenset(funciones if funciones is not None else POR_DEFECTO | ({"pp"} if pp else set()))
    assert funciones <= FUNCIONES | BISECCION, funciones - FUNCIONES - BISECCION
    pp, film = "pp" in funciones, bool(UI_FILM & funciones)
    orig = C.DEV_A / C.USR
    silent = work / "silent"
    build_silent_menu_test.main(C.DEV_A, C.DEV_B, silent, pid_silent=C.PID_SILENT)
    stage = work / "stage"
    for rel in ("lib/libObj.so", "lib/CautionConfig.so", "lib/viewUnified2.so", "lib/viewUnified4.so", "lib/viewUnified7.so"):
        (stage / C.USR / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(orig / rel, stage / C.USR / rel)
    (stage / C.USR / "share/app").mkdir(parents=True, exist_ok=True)
    for f in (orig / "share/app").glob("string_*.uxc"):
        shutil.copy(f, stage / C.USR / "share/app" / f.name)
    shutil.copy(silent / "lib/CautionConfig.so", stage / C.USR / "lib/CautionConfig.so")
    for f in (silent / "share/app").glob("*.uxc"):
        shutil.copy(f, stage / C.USR / "share/app" / f.name)
    pp_dir = work / "pp"
    if pp or film:
        kw = menu_film(pp, maximo, film)
        build_pp_menu.main(stage, C.DEV_B, pp_dir, entradas_previas=[C.SILENT_DELTA], silent=True, **kw)
    else:
        menu_silent(stage, pp_dir)
    lib_obj = patch_libobj_ppeco.patch(C.eco((pp_dir / "lib/libObj.so").read_bytes())) if pp else C.eco((orig / "lib/libObj.so").read_bytes())
    pp = pp_dir
    files = work / "files"
    parcheados = sorted(json.loads((pp / "MANIFEST.json").read_text())["parcheados"]) + ["lib/libObj.so"]
    for rel in parcheados:
        (files / rel).parent.mkdir(parents=True, exist_ok=True)
        if rel != "lib/libObj.so":
            shutil.copy(pp / rel, files / rel)
    (files / "lib/libObj.so").write_bytes(lib_obj)
    if film:
        (files / "lib/viewUnified2.so").write_bytes(FU.patch_vu2((files / "lib/viewUnified2.so").read_bytes(), FU.compila(looks)))
    if "exfine" in funciones:
        cau = files / "lib/CautionConfig.so"
        cau.write_bytes(quality_exfine_patch.patch(cau.read_bytes()))   # G39/G103: «Extra fine» en Calidad (menú y Fn usan la misma clase)
        (files / "lib/libmprctrl.so").write_bytes(exfine_size_patch.patch((orig / "lib/libmprctrl.so").read_bytes()))   # G106: tamaños EXFINE a 0 en la A6000
        parcheados.append("lib/libmprctrl.so")
    if UI_ISO & funciones:
        vu4 = files / "lib/viewUnified4.so"
        if not vu4.exists():
            shutil.copy(orig / "lib/viewUnified4.so", vu4)
            parcheados.append("lib/viewUnified4.so")
        # G104 §8.5–8.7: pantalla ISO hasta 409600 (filas de vu4, WrapperIso de vu2, códigos 0x4b…0x50 en libObj, textos e iconos de la A7S)
        textos, iconos, recursos = iso_ui_recursos.aplicar(files, orig)
        parcheados += recursos
        vu4.write_bytes(iso_ui_patch.patch_filas(vu4.read_bytes(), textos, iconos, iso_ui_patch.N_CFW))
        vu2 = files / "lib/viewUnified2.so"
        vu2.write_bytes(iso_ui_patch.patch_vu2(vu2.read_bytes(), iso_ui_patch.N_CFW))
        (files / "lib/libObj.so").write_bytes(iso_libobj_patch.patch((files / "lib/libObj.so").read_bytes()))
    man = {"idiomas": json.loads((pp / "MANIFEST.json").read_text())["idiomas"], "nuevos": {}, "originales": {}, "parcheados": {}, "md5": {}}
    for rel in sorted(set(parcheados)):
        o, n = (orig / rel).read_bytes(), (files / rel).read_bytes()
        man["originales"][rel], man["parcheados"][rel] = C.sha(o), C.sha(n)
        man["md5"][rel] = {"original": C.md5(o), "parcheado": C.md5(n)}
    (files / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))
    (files / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in man["parcheados"].items()))
    return files


def main(out: Path, version: str, looks: Path = LOOKS, pp: bool = False, maximo: int = 99, funciones=None) -> dict:
    funciones = frozenset(funciones if funciones is not None else POR_DEFECTO | ({"pp"} if pp else set()))
    out.mkdir(parents=True, exist_ok=True)
    files = build_files(out, looks, pp, maximo, funciones)
    nf15 = out / f"nflasha15-{version.replace('.', '')}.bin"
    rep15 = build_nflasha15.main(C.DEV_A / "nflasha15", files, nf15)
    base = out / "base-film.tar"
    rep_base = build_base_pp.main(C.BASE_TAR, base, bionz=bionz_de(funciones))
    res = build_package_nflasha15.main(nf15, out / f"pkg-{version}", base, version, darwin_v3=True, sin_wbi=True)
    (out / "build-nflasha15.json").write_text(json.dumps(rep15, indent=1))
    (out / "build-base.json").write_text(json.dumps(rep_base, indent=1))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("salida", type=Path)
    ap.add_argument("--version", default="3.87")
    ap.add_argument("--looks", type=Path, default=LOOKS)
    ap.add_argument("--pp", action="store_true", help="G102: con Picture Profile (menú, Fn, rueda, libObj y núcleo)")
    ap.add_argument("--max-opciones", type=int, default=M.OPCIONES_POR_LISTA, help="opciones por fila del menú PP antes de partirla (G106: 7, tope de la lista en la cámara; 99 = filas enteras de G102, solo para el arnés)")
    ap.add_argument("--funciones", help="G105: lista separada por comas de " + ",".join(sorted(FUNCIONES | BISECCION)) + " sobre la base Silent ('' = solo Silent); sin ella, el CFW Film")
    a = ap.parse_args()
    fun = None if a.funciones is None else {x for x in a.funciones.split(",") if x}
    print(json.dumps(main(a.salida, a.version, a.looks, a.pp, a.max_opciones, fun), indent=1))
