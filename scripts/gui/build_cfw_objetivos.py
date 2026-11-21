#!/usr/bin/env python3
"""CFW «objetivos» (3.82+): el CFW 3.81 (tres estados, Picture Profile completo, S-Log3/B&W/Hi-Light) MÁS todas las funciones objetivo de wiki/16 con parche hecho
(`build_overlay_objetivos`: carpeta «CFW» de 13 ajustes, Extra Fine, ISO 51200/MAX, HD120, XAVC S sin tarjeta, Intervalo, DR Prioridad, Zebra Nivel, S&Q, Flicker Scan,
Bulb Timer, Color Chrome, LUT, contador Live ND). Sin lógica propia: encadena `build_cfw_completo` y los parches sueltos. NO instala nada.
Fuera: Focus Bracket (gancho sin localizar; su ajuste de menú se deja), HLG, Keystone.
Uso: build_cfw_objetivos.py SALIDA [--version 3.82]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in ("scripts/gui", "scripts", "scripts/g55", "scripts/g61", "scripts/g63", "scripts/g65", "scripts/g68", "scripts/g69", "scripts/g76", "scripts/g84", "scripts/lut", "references/pmca"):
    sys.path.insert(0, str(ROOT / d))
import build_base_pp
import build_cfw_completo as C
import build_nflasha15
import build_overlay_objetivos as O
import build_package_nflasha15
import build_pp_menu
import bulb_timer_patch
import cfw_ajustes
import jpeg_hook_patch
import pp_menu_spec as M

_configurar = build_pp_menu.configurar


def _cuevas_fuera_del_bloque_0() -> None:
    """Bulb Timer y el contador Live ND tienen su cueva en el hueco de la cabecera de av-cam (`0x43541600/700`), dentro del bloque TPZL 0 de `nflasha3`: R55 mostró
    que un bloque 0 distinto del de Sony cuelga la lectura de `dnflasha3`. Se reubican en el hueco G18 verificado (g72: `0x43fb7ec0…0x43fb8ee0`, cero fichero/vivo, sin referencias)."""
    bulb_timer_patch.CAVE, bulb_timer_patch.CAVE_END = 0x43FB7F00, 0x43FB7F80
    jpeg_hook_patch.CAVE, jpeg_hook_patch.CAVE_END = 0x43FB7F80, 0x43FB7FC0
    jpeg_hook_patch.COUNTER = jpeg_hook_patch.CAVE_END


def bionz_objetivos(tri: bytes) -> bytes:
    """BIONZ del CFW de objetivos a partir del 3.38 + tres estados (lo usa también la auditoría)."""
    _cuevas_fuera_del_bloque_0()
    return O.encadena(build_base_pp.bionz_cfw(tri, silent_r5=False), O.AVCAM)


def _configurar_con_cfw(*a, **k):
    """Tras configurar el menú PP, añade los 13 ajustes CFW como segunda carpeta (pids a continuación de los de PP)."""
    r = _configurar(*a, **k)
    ids = []
    for aj in cfw_ajustes.AJUSTES:
        M.SETTINGS[aj.id] = M.S(aj.id, aj.label, 0, tuple((t, i) for i, (t, _) in enumerate(aj.opciones)), "g56", backup=aj.backup)
        ids.append(aj.id)
    M.PIDS[:] = range(M.PIDS[0], M.PIDS[0] + len(M.SETTINGS))
    build_pp_menu.EXTRA_TREES[:] = [("folder", cfw_ajustes.CARPETA, M.paginar(ids))]
    build_pp_menu.FN_TREES[:] = ["lut"]       # G86/G86-B: «LUT» también en el menú Fn (hijo 39 de la raíz Fn, listas de las 12 ranuras, tabla de valores)
    return r


def aplicar_objetivos(files: Path) -> None:
    """Parches de /usr de las funciones objetivo sobre los ficheros del 3.81 (CautionConfig y libObj), manifiesto actualizado."""
    man = json.loads((files / "MANIFEST.json").read_text())
    for rel, parches in (("lib/CautionConfig.so", O.CAUTION), ("lib/libObj.so", O.LIBOBJ)):
        antes = (files / rel).read_bytes()
        despues = O.encadena(antes, parches)
        (files / rel).write_bytes(despues)
        o = (C.DEV_A / C.USR / rel).read_bytes()
        man["parcheados"][rel], man["md5"][rel] = C.sha(despues), {"original": C.md5(o), "parcheado": C.md5(despues)}
    (files / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))
    (files / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in man["parcheados"].items()))


def main(out: Path, version: str) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    _cuevas_fuera_del_bloque_0()
    build_pp_menu.configurar = _configurar_con_cfw
    files = C.build_files(out)
    aplicar_objetivos(files)
    nf15 = out / f"nflasha15-{version.replace('.', '')}.bin"
    rep15 = build_nflasha15.main(C.DEV_A / "nflasha15", files, nf15)
    base = out / "base-pp.tar"
    build_base_pp.main(C.BASE_TAR, base, silent_r5=False, post=lambda av: O.encadena(av, O.AVCAM))   # misma composición que bionz_objetivos
    res = build_package_nflasha15.main(nf15, out / f"pkg-{version}", base, version, darwin_v3=True, sin_wbi=True)
    (out / "build-nflasha15.json").write_text(json.dumps(rep15, indent=1))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("salida", type=Path)
    ap.add_argument("--version", default="3.82")
    a = ap.parse_args()
    print(json.dumps(main(a.salida, a.version), indent=1))
