#!/usr/bin/env python3
"""Auditoría independiente del .dat con `nflasha15` reconstruida (menú Silent, G09 §8). Solo lee; sale con 1 si algo falla.

Parte del `.dat` final: descifrado con el auditor E25-06 (no fwtool), comparación miembro a miembro con el CFW base 3.38,
todas las sumas del tar, disposición TPZL frente a Sony, bloque 0 intacto (R55), decodificador independiente (`fwtool.lz77`)
en los bloques recompuestos, ext2 montado en solo lectura comparado fichero a fichero con el de Sony, y parche Darwin v3 opcional.
Uso: audit_package_nflasha15.py DAT PAQUETE_SILENT [--base-dat DAT_3.38] [--darwin-v3]  → JSON a stdout
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/fwtool"))
from e25_06 import audit_packages as A
from e25_27 import build, sums, tarball, tpzl
from fwtool import lz77

sys.path.insert(0, str(ROOT / "scripts/gui"))
import build_nflasha15

N15 = "0700_part_image/dev/nflasha15"
STOCK15 = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15"
BASE_DAT = ROOT / "analysis/e25-27/artifacts-338/package-3.38/firmware_packed.dat"
LIMIT = 104_857_600
SUDO = os.environ.get("SUDO_PASS", "") + "\n"  # montar el ext2 en solo lectura necesita root


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def open_dat(path: Path, keys):
    dat = path.read_bytes()
    info = A.parse_dat(dat)
    fdat = path.with_suffix(".fdat").read_bytes()
    dec = A.decrypt_fdat(dat, info["fdat_offset"], info["fdat_size"], keys, compare=fdat)
    hdr = A.parse_fdat_header(fdat[: A.FDAT_HDR])
    tar = fdat[hdr["firmware_offset"]:hdr["firmware_offset"] + hdr["firmware_size"]]
    upd = next(fs for fs in hdr["filesystems"] if fs["mode"] == "U")
    checks = {
        "dend_ok": info["dend_stored"] == info["dend_computed"],
        "descifrado_igual_a_fdat": dec.first_mismatch_vs_fdat is None,
        "bloques_cifrado_sin_error": not (dec.bad_sum or dec.bad_flag or dec.bad_len),
        "crc_cabecera_ok": hdr["checksum_stored"] == hdr["checksum_computed"],
        "modelo_region": (hdr["model"], hdr["region"]) == (build.MODEL, build.REGION),
        "updater_oficial_3_21": sha(fdat[upd["offset"]:upd["offset"] + upd["size"]]) == build.UPDATER_SHA256,
    }
    return hdr["version"], checks, {e.name: e.data for e in tarball.parse(tar)[0]}


def all_sums_ok(members: dict) -> dict:
    bad, n = [], 0
    for name, data in members.items():
        if not name.endswith(".sum"):
            continue
        for line in data.decode("ascii").splitlines():
            f = line.split(",")
            if len(f) < 11 or f[0] != "0":
                continue
            target = next((m for m in members if m.endswith("/" + f[10])), None)
            if target is None:
                continue
            n += 1
            if not sums.verify(data.decode("ascii"), f[10], members[target]):
                bad.append(f[10])
    return {"lineas_verificadas": n, "fallidas": bad}


def layout(img: tpzl.TpzlImage, raw: bytes) -> dict:
    ends = [o + s for o, s in img.entries]
    return {"bloques": len(img.entries), "no_alineados_512": sum(o & 0x1FF != 0 for o, _ in img.entries),
            "contiguos": all(ends[i] == img.entries[i + 1][0] for i in range(len(ends) - 1)),
            "max_sectores": max(-(-s // 512) for _, s in img.entries), "violaciones_ldec": len(tpzl.hardware_violations(img)),
            "tamano": len(raw)}


def fw_decode(img: tpzl.TpzlImage, i: int) -> bytes:
    b, out = io.BytesIO(img.block(i)), b""
    while len(out) < img.block_size:
        out += lz77.inflateLz77(b)
    return out


def mounted_diff(ext_new: bytes, ext_old: bytes) -> list[str]:
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "a.img").write_bytes(ext_old)
        (t / "b.img").write_bytes(ext_new)
        (t / "a").mkdir()
        (t / "b").mkdir()
        try:
            for x in "ab":
                subprocess.run(["sudo", "-S", "mount", "-o", "loop,ro", str(t / f"{x}.img"), str(t / x)], input=SUDO, text=True,
                               capture_output=True, check=True)
            out = subprocess.run(["diff", "-rq", "--no-dereference", str(t / "a"), str(t / "b")],
                                 capture_output=True, text=True, check=False).stdout
        finally:
            for x in "ab":
                subprocess.run(["sudo", "-S", "umount", str(t / x)], input=SUDO, text=True, capture_output=True, check=False)
    def rel(ln: str) -> str:
        if " differ" in ln:
            return ln.split(f"{t}/b/")[1].split(" differ")[0]
        if ln.startswith(f"Only in {t}/b/"):  # fichero nuevo (G18): «Only in …/b/bin: x» → bin/x
            d, name = ln[len(f"Only in {t}/b/"):].split(": ", 1)
            return f"{d}/{name}"
        return ln
    return sorted(rel(ln) for ln in out.splitlines())


def run(dat: Path, pkg: Path, base_dat: Path, darwin_v3: bool, sin_wbi: bool = False) -> dict:
    keys = A.load_keys()
    ver, cont, new = open_dat(dat, keys)
    bver, _, base = open_dat(base_dat, keys)
    man = json.loads((pkg / "MANIFEST.json").read_text())
    expected = {N15, build.PART_SUM} | ({build.DARWIN_CORE, build.DARWIN_SUM} if darwin_v3 else set())
    changed = sorted(n for n in new if new[n] != base.get(n))
    removed = sorted(set(base) - set(new))
    stock_raw = STOCK15.read_bytes()
    p_new, p_old = tpzl.TpzlImage.parse(new[N15]), tpzl.TpzlImage.parse(stock_raw)
    lay_new, lay_old = layout(p_new, new[N15]), layout(p_old, stock_raw)
    same = [i for i in range(len(p_old.entries)) if p_new.block(i)[:len(p_old.block(i))] == p_old.block(i)]
    recomp = sorted(set(range(len(p_old.entries))) - set(same))
    indep_bad = [i for i in recomp if fw_decode(p_new, i) != tpzl.decode_block(p_new.block(i), 65536)]
    ext_new, ext_old = p_new.decompressed(), p_old.decompressed()
    files = mounted_diff(ext_new, ext_old)
    new_files = man.get("nuevos", {})  # G18: ficheros que Sony no tiene (contenido = el del paquete, root:root, modo del MANIFEST)
    want = sorted([r for r, h in man["parcheados"].items() if h != man["originales"].get(r)] + list(new_files))  # control 3.48: reescritos con los bytes de Sony
    files_ok = files == want
    with tempfile.NamedTemporaryFile(suffix=".img") as f:
        f.write(ext_new)
        f.flush()
        fsck = subprocess.run(["e2fsck", "-fn", f.name], capture_output=True, text=True, check=False)
    fsck_lines = [ln for ln in fsck.stdout.splitlines() if "wrong" in ln or "error" in ln.lower()]
    hashes_ok, attrs_bad = True, []
    with tempfile.TemporaryDirectory() as t:
        img, old = Path(t) / "n.img", Path(t) / "o.img"
        img.write_bytes(ext_new)
        old.write_bytes(ext_old)
        for rel, h in man["parcheados"].items():
            subprocess.run(["debugfs", "-R", f"dump /{rel} {t}/f", str(img)], capture_output=True, check=True)
            hashes_ok &= sha((Path(t) / "f").read_bytes()) == h
            got, want_attrs = (build_nflasha15.stat_fields(x, "/" + rel) for x in (img, old))
            if any(got[k] != want_attrs[k] for k in ("mode", "uid", "gid")):  # 3.39–3.42 quedaron en 0644 (G11 §3)
                attrs_bad.append(rel)
        for rel, mode in new_files.items():
            subprocess.run(["debugfs", "-R", f"dump /{rel} {t}/f", str(img)], capture_output=True, check=True)
            hashes_ok &= (Path(t) / "f").read_bytes() == (pkg / rel).read_bytes()
            got = build_nflasha15.stat_fields(img, "/" + rel)
            if (got["mode"] & 0o7777, got["uid"], got["gid"]) != (int(mode, 8), 0, 0):
                attrs_bad.append(rel)
    darwin = {}
    if darwin_v3:
        core, _ = build.efcs_tabla_diff(base[build.DARWIN_CORE])
        darwin = {"darwin_v3_presente": new[build.DARWIN_CORE] == core,
                  "darwin_solo_rango_r82": all(build.PD.BASE + i in build.efcs_tabla_allowed_addresses()
                                               for i, (a, b) in enumerate(zip(base[build.DARWIN_CORE], new[build.DARWIN_CORE])) if a != b)}
    checks = {
        **{f"contenedor.{k}": v for k, v in cont.items()},
        "contenedor.version_mayor_que_base": tuple(map(int, ver.split("."))) > tuple(map(int, bver.split("."))),
        "tar.solo_cambian_los_miembros_previstos": set(changed) == expected,
        "tar.solo_se_quitan_los_previstos": removed == (["0700_part_image/dev/nflasha5"] if sin_wbi else []),
        **({"tar.sum_sin_linea_nflasha5": b",dev/nflasha5," not in new[build.PART_SUM]} if sin_wbi else {}),
        "tar.todas_las_sumas_verifican": not all_sums_ok(new)["fallidas"],
        "nflasha15.cabe_en_la_particion": lay_new["tamano"] <= LIMIT,
        "nflasha15.sin_violaciones_ldec": lay_new["violaciones_ldec"] == 0,
        "nflasha15.alineado_512": lay_new["no_alineados_512"] == 0,
        "nflasha15.contiguo": lay_new["contiguos"],
        "nflasha15.mismo_numero_de_bloques": lay_new["bloques"] == lay_old["bloques"],
        "nflasha15.max_sectores_no_mayor_que_sony": lay_new["max_sectores"] <= lay_old["max_sectores"],
        "nflasha15.bloque_0_identico_a_sony_(R55)": 0 not in recomp,
        "nflasha15.decodificador_independiente_coincide": not indep_bad,
        "ext2.solo_cambian_los_ficheros_del_paquete": files_ok,
        "ext2.hashes_de_los_ficheros_parcheados": hashes_ok,
        "ext2.modo_uid_gid_como_sony": not attrs_bad,
        "ext2.fsck_solo_contadores_de_libres": all("count wrong" in ln or "still has errors" in ln for ln in fsck_lines),
        **darwin,
    }
    return {"dat_sha256": sha(dat.read_bytes()), "version": ver, "base_version": bver, "todo_ok": all(checks.values()),
            "comprobaciones": checks, "tar_cambios_vs_base": changed, "tar_quitados_vs_base": removed, "bloques_recompuestos": len(recomp),
            "disposicion": {"nuevo": lay_new, "sony": lay_old}, "ficheros_distintos_ext2": files, "atributos_distintos": attrs_bad, "fsck": fsck_lines,
            "sumas": all_sums_ok(new)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dat", type=Path)
    ap.add_argument("paquete", type=Path)
    ap.add_argument("--base-dat", type=Path, default=BASE_DAT)
    ap.add_argument("--darwin-v3", action="store_true")
    ap.add_argument("--sin-wbi", action="store_true")
    a = ap.parse_args()
    r = run(a.dat, a.paquete, a.base_dat, a.darwin_v3, a.sin_wbi)
    print(json.dumps(r, indent=1))
    sys.exit(0 if r["todo_ok"] else 1)
