"""G70: tasa máxima de lectura por modo del IMX210 (A6000 3.21) a partir de HMAX/VMAX de av-cam (solo lectura de bytes).
HMAX = a (ciclos/línea), VMAX = b (líneas/cuadro), reloj 54,054 MHz (ver imx210-video-readout.md). margen = líneas no activas mínimas supuestas.
Uso: python3 -I scripts/imx210_fps_limits.py"""
import importlib.util
import pathlib

CLK, MARGIN = 54.054e6, 12  # shortcut: margen de 12 líneas sin datasheet; sustituir si se mide el VMAX mínimo real
_s = importlib.util.spec_from_file_location("t", pathlib.Path(__file__).parent / "imx210_param_tables.py")
_t = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_t)  # type: ignore[union-attr]


def table() -> list[dict]:
    out = []
    for m in _t.per_mode(_t._read()):
        cols, lin = m["row72_camcore"][7], m["row72_camcore"][15]
        (h60, v60, _), (_, v50, _) = m["ab12_variant0"], m["ab12_variant1"]
        out.append({"mode": m["mode"], "cols": cols, "lines": lin, "hmax": h60, "vmax60": v60, "vmax50": v50,
                    "t_line_us": h60 / CLK * 1e6, "fps60": CLK / (h60 * v60), "fps_max": CLK / (h60 * (lin + MARGIN)),
                    "mpx_s": cols * lin * CLK / (h60 * v60) / 1e6})
    return out


if __name__ == "__main__":
    for r in table():
        print(f"0x{r['mode']:02x} {r['cols']}x{r['lines']} HMAX={r['hmax']} VMAX={r['vmax60']}/{r['vmax50']} "
              f"t_lin={r['t_line_us']:.2f}us fps={r['fps60']:.2f} max={r['fps_max']:.0f} {r['mpx_s']:.0f}Mpx/s")
