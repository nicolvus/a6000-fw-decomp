"""G22-E/T4b — foto y clip desde la ventana y desde las teclas de la cámara, y galería de la SD (sin QEMU)."""
from __future__ import annotations

import io
import json
import shutil
import sys
import time
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
sys.path.insert(0, str(HARNESS))

import captura as C
import emu_config as E
import sd_emu as S
import sensor_web as W


class H:
    """Manejador HTTP mínimo de `live.py`: `responde` no hace falta, los puntos escriben con send_response/wfile."""

    def __init__(self, headers: dict | None = None) -> None:
        self.codigo: int | None = None
        self.cabeceras: list[tuple[str, str]] = []
        self.wfile = io.BytesIO()
        self.headers = headers or {}

    def send_response(self, codigo: int) -> None:
        self.codigo = codigo

    def send_header(self, k: str, v: str) -> None:
        self.cabeceras.append((k, v))

    def end_headers(self) -> None:
        pass

    def send_error(self, codigo: int) -> None:
        self.codigo = codigo

    def json(self) -> dict:
        return json.loads(self.wfile.getvalue())


def jpg(color: tuple[int, int, int] = (180, 30, 30), lado: int = 64) -> bytes:
    b = io.BytesIO()
    Image.new("RGB", (lado, lado), color).save(b, "JPEG", quality=90)
    return b.getvalue()


def _cfg(tmp_path: Path, **extra) -> Path:
    """config.json de prueba con SD y fuente de sensor propias de la prueba."""
    cfg = {"sd": {"carpeta": str(tmp_path / "sd"), "tamano_gb": 4},
           "sensor": {"fuente": "imagen", "ruta": str(tmp_path / "fuente.png")}, **extra}
    (tmp_path / "fuente.png").write_bytes(jpg((10, 120, 200), 96))
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    return p


def _cap(cfg: Path, perfil: Path) -> C.Captura:
    return C.Captura(perfil, lambda: E.carga_config(cfg))


def test_foto_nombra_exif_y_registro(tmp_path: Path) -> None:
    cfg, perfil = _cfg(tmp_path), tmp_path / "live/sony"
    cap = _cap(cfg, perfil)
    r1 = cap.foto(jpg())
    r2 = cap.foto(jpg((0, 0, 0)))
    assert r1["ruta"] == "DCIM/100MSDCF/DSC00001.JPG" and r2["ruta"] == "DCIM/100MSDCF/DSC00002.JPG"
    ex = Image.open(tmp_path / "sd" / r1["ruta"]).getexif()
    assert ex[0x010F] == "SONY" and ex[0x0110] == "ILCE-6000"
    lineas = (perfil / "capturas.jsonl").read_text().splitlines()
    assert [json.loads(x)["ruta"] for x in lineas] == ["DSC00001.JPG", "DSC00002.JPG"]
    assert cap.estado()["ultimo"]["tipo"] == "foto"


def test_foto_rechaza_lo_que_no_es_jpeg(tmp_path: Path) -> None:
    cap = _cap(_cfg(tmp_path), tmp_path / "live")
    assert "error" in cap.foto(b"no soy un jpeg")


def test_tecla_disparador_usa_la_fuente_de_sensor(tmp_path: Path) -> None:
    """La tecla del disparador (sin navegador) saca un fotograma de la fuente configurada y lo deja en la SD."""
    cfg, perfil = _cfg(tmp_path), tmp_path / "live"
    cap = _cap(cfg, perfil)
    cap.tecla("disparador", 1)
    for _ in range(100):
        if (tmp_path / "sd/DCIM/100MSDCF").is_dir() and any((tmp_path / "sd/DCIM/100MSDCF").iterdir()):
            break
        time.sleep(0.1)
    f = next((tmp_path / "sd/DCIM/100MSDCF").iterdir())
    assert f.name == "DSC00001.JPG" and f.stat().st_size > 500
    cap.tecla("disparador", 0)  # la suelta no dispara otra foto
    assert len(list((tmp_path / "sd/DCIM/100MSDCF").iterdir())) == 1


def test_clip_desde_imagen(tmp_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        pytest.skip("sin ffmpeg")
    cap = _cap(_cfg(tmp_path), tmp_path / "live")
    assert cap.video_inicia()["grabando"] is True
    assert cap.estado()["grabando"] is True
    time.sleep(1.5)
    r = cap.video_para()
    assert r["ruta"] == "PRIVATE/M4ROOT/CLIP/C0001.MP4", r
    f = tmp_path / "sd" / r["ruta"]
    assert f.read_bytes()[4:8] == b"ftyp"
    assert "XAVC S" in r["nota"]
    assert cap.video_para()["error"]  # ya no hay grabación en curso


def test_clip_sin_fuente_avisa(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, sensor={"fuente": "imagen", "ruta": str(tmp_path / "no-existe.png")})
    assert "error" in _cap(cfg, tmp_path / "live").video_inicia()


def test_sd_lista_ruta_segura_borra_y_formatea(tmp_path: Path) -> None:
    cap = _cap(_cfg(tmp_path), tmp_path / "live")
    cap.foto(jpg())
    assert [d["ruta"] for d in S.lista(tmp_path / "sd")] == ["DCIM/100MSDCF/DSC00001.JPG"]
    with pytest.raises(ValueError):
        S.ruta_segura(tmp_path / "sd", "../../etc/passwd")
    S.borra(tmp_path / "sd", "DCIM/100MSDCF/DSC00001.JPG")
    assert S.lista(tmp_path / "sd") == []
    S.escribe_atomico(tmp_path / "sd/DCIM/100MSDCF/DSC00007.JPG", jpg())
    assert S.formatea(tmp_path / "sd") == 1
    assert (tmp_path / "sd/DCIM/100MSDCF").is_dir() and S.lista(tmp_path / "sd") == []


def test_importa_nombra_como_la_camara(tmp_path: Path) -> None:
    d = S.importa(tmp_path / "sd", "vacaciones.jpg", jpg())
    assert d.name == "DSC00001.JPG" and Image.open(d).getexif()[0x0110] == "ILCE-6000"
    clip = S.importa(tmp_path / "sd", "clip.mp4", b"\x00\x00\x00\x18ftypmp42")
    assert clip == tmp_path / "sd/PRIVATE/M4ROOT/CLIP/C0001.MP4"  # un vídeo entra como clip de la cámara, no con su nombre


def test_http_sd_galeria_importar_y_formatear(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    W.registra_captura(_cap(cfg, tmp_path / "live"))
    try:
        h = H()
        assert W.maneja(h, "POST", "/sd/foto", jpg(), str(cfg))
        assert h.codigo == 200 and h.json()["ruta"].endswith("DSC00001.JPG")

        h = H()
        assert W.maneja(h, "GET", "/sd/lista", b"", str(cfg))
        items = h.json()["items"]
        assert len(items) == 1 and items[0]["media"] is True

        h = H()
        assert W.maneja(h, "GET", "/sd/fichero?r=DCIM/100MSDCF/DSC00001.JPG", b"", str(cfg))
        assert h.codigo == 200 and h.wfile.getvalue()[:2] == b"\xff\xd8"

        h = H({"X-Nombre": "otra.jpg"})
        assert W.maneja(h, "POST", "/sd/importa", jpg((1, 2, 3)), str(cfg))
        assert h.json()["ruta"] == "DCIM/100MSDCF/DSC00002.JPG"

        h = H()
        assert W.maneja(h, "POST", "/sd/borrar", json.dumps({"r": "DCIM/100MSDCF/DSC00001.JPG"}).encode(), str(cfg))
        assert h.json() == {"ok": True}

        h = H()
        assert W.maneja(h, "POST", "/sd/formatea", b"", str(cfg))
        assert h.json()["borrados"] == 1

        h = H()
        assert W.maneja(h, "GET", "/sd/fichero?r=../../x", b"", str(cfg))
        assert h.codigo == 400  # ruta fuera de la SD: ValueError -> 400
    finally:
        W.registra_captura(None)


def test_http_foto_invalida_es_400_y_ajena_no_se_atiende(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    W.registra_captura(_cap(cfg, tmp_path / "live"))
    try:
        h = H()
        assert W.maneja(h, "POST", "/sd/foto", b"basura", str(cfg))
        assert h.codigo == 400 and "error" in h.json()
        assert W.maneja(H(), "GET", "/otra/cosa", b"", str(cfg)) is False
    finally:
        W.registra_captura(None)


def test_http_captura_video_desde_el_servidor(tmp_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        pytest.skip("sin ffmpeg")
    cfg = _cfg(tmp_path)
    cap = _cap(cfg, tmp_path / "live")
    W.registra_captura(cap)
    try:
        h = H()
        assert W.maneja(h, "POST", "/captura/video/inicia", b"", str(cfg))
        assert h.json()["grabando"] is True
        time.sleep(1.2)
        h = H()
        assert W.maneja(h, "GET", "/captura/estado", b"", str(cfg))
        assert h.json()["grabando"] is True
        h = H()
        assert W.maneja(h, "POST", "/captura/video/para", b"", str(cfg))
        assert h.json()["ruta"] == "PRIVATE/M4ROOT/CLIP/C0001.MP4", h.json()
    finally:
        W.registra_captura(None)


def test_formatear_no_vacia_una_carpeta_cualquiera(tmp_path: Path) -> None:
    """QA F01: «Formatear» solo toca el árbol de la cámara; una carpeta de trabajo se rechaza."""
    curro = tmp_path / "trabajo"
    (curro / "src").mkdir(parents=True)
    (curro / "src/main.c").write_text("int main(){}")
    with pytest.raises(ValueError, match="no parece una tarjeta SD"):
        S.formatea(curro)
    assert (curro / "src/main.c").is_file()  # nada borrado
    sd = tmp_path / "sd"
    S.escribe_atomico(sd / "DCIM/100MSDCF/DSC00001.JPG", jpg())
    (sd / "apuntes.txt").write_text("del anfitrión")
    assert S.formatea(sd) == 1
    assert not (sd / "DCIM/100MSDCF/DSC00001.JPG").exists() and (sd / "apuntes.txt").is_file()


def test_importar_concurrente_no_pisa_y_respeta_la_cuota(tmp_path: Path) -> None:
    """QA F07/F08: dos subidas a la vez sacan números distintos y la cuota se mide con el tamaño final."""
    import threading
    sd = tmp_path / "sd"
    rutas: list[Path] = []
    hilos = [threading.Thread(target=lambda c=c: rutas.append(S.importa(sd, "f.jpg", jpg(c)))) for c in ((1, 2, 3), (9, 8, 7), (4, 5, 6))]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    assert sorted(p.name for p in rutas) == ["DSC00001.JPG", "DSC00002.JPG", "DSC00003.JPG"]
    with pytest.raises(ValueError, match="llena"):
        S.importa(sd, "grande.jpg", jpg(lado=512), cuota=S.usado(sd) + 10)


def test_escribir_no_sigue_un_enlace_fuera_de_la_sd(tmp_path: Path) -> None:
    """QA F09: un enlace en la SD no puede sacar la escritura fuera de la carpeta."""
    sd = tmp_path / "sd"
    fuera = tmp_path / "fuera.txt"
    fuera.write_text("intacto")
    (sd / "DCIM/100MSDCF").mkdir(parents=True)
    (sd / "DCIM/100MSDCF/DSC00001.JPG").symlink_to(fuera)
    S.escribe_atomico(sd / "DCIM/100MSDCF/DSC00001.JPG", jpg())
    assert fuera.read_text() == "intacto"
    assert (sd / "DCIM/100MSDCF/DSC00001.JPG").is_file() and not (sd / "DCIM/100MSDCF/DSC00001.JPG").is_symlink()


def test_importar_sin_cuota_da_507(tmp_path: Path) -> None:
    """QA F07: si el tamaño final no cabe, la subida se rechaza con 507 (no se escribe nada)."""
    cfg = _cfg(tmp_path, sd={"carpeta": str(tmp_path / "sd"), "tamano_gb": 1e-6})
    W.registra_captura(_cap(cfg, tmp_path / "live"))
    try:
        h = H({"X-Nombre": "grande.jpg"})
        assert W.maneja(h, "POST", "/sd/importa", jpg(lado=512), str(cfg))
        assert h.codigo == 507 and "llena" in h.json()["error"]
        assert S.lista(tmp_path / "sd") == []
    finally:
        W.registra_captura(None)
