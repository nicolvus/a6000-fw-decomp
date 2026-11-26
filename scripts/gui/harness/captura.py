"""Foto y clip del arnés (G22-E/T4b): la misma vía para el botón de la ventana y para las teclas de la cámara.

- La foto del botón llega del lienzo del navegador (ISP emulado aplicado: es lo que se ve). La de la tecla del
  disparador se genera desde la fuente de sensor configurada (imagen, o un fotograma del vídeo).
- El clip lo graba ffmpeg en el anfitrión desde esa misma fuente (imagen en bucle, vídeo en bucle, /dev/videoN).
  NO es XAVC S: MP4 H.264 con la resolución de la fuente, sin audio, sin XML ni base de datos de la cámara; se dice
  en `nota` y en la galería.

Ambas acaban en la carpeta de la SD de `sd_emu` con la numeración de la cámara (`DSCnnnnn.JPG`, `Cnnnn.MP4`) y quedan
apuntadas en `live/<perfil>/capturas.jsonl`. El firmware del invitado no interviene: su ruta de captura depende de
BIONZ (av-cam + ISP de hardware) y sigue sin producir imagen (pendiente G22-E/T4b en docs/PENDIENTES.md).
"""
from __future__ import annotations

import json
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path

import sd_emu as S

MAX_CLIP_S = 1200  # tope de seguridad del clip (20 min); la A6000 corta a 29:59 en FAT32
NOTA_CLIP = "MP4 H.264 de la fuente del sensor; NO es XAVC S (sin audio, sin XML ni base de datos de la cámara)"


class Captura:
    """Estado de captura de una VM. `cfg` devuelve la configuración del configurador (sensor, sd)."""

    def __init__(self, dir_perfil: Path, cfg: Callable[[], dict]) -> None:
        self.dir = Path(dir_perfil)
        self._cfg = cfg
        self.cerrojo = threading.Lock()
        self.ultimo: dict = {}
        self.aviso = ""
        self._proc: subprocess.Popen | None = None
        self._tmp: Path | None = None
        self._t0 = 0.0

    # ---------------------------------------------------------------- estado
    @property
    def grabando(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def estado(self) -> dict:
        return {"grabando": self.grabando, "segundos": round(time.time() - self._t0) if self.grabando else 0,
                "ultimo": self.ultimo, "aviso": self.aviso}

    def _apunta(self, tipo: str, ruta: Path, origen: str, nota: str = "") -> None:
        d = {"t": time.time(), "tipo": tipo, "ruta": ruta.name, "origen": origen, "bytes": ruta.stat().st_size, "nota": nota}
        self.ultimo = d
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            with (self.dir / "capturas.jsonl").open("a") as f:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        except OSError:
            pass  # sin registro se pierde la traza, no la foto

    def configura(self) -> dict:
        try:
            return self._cfg()
        except (OSError, ValueError):
            return {"sensor": {"fuente": "imagen", "ruta": ""}, "sd": {"tamano_gb": 4, "carpeta": ""}}

    # ---------------------------------------------------------------- foto
    def foto(self, jpeg: bytes, origen: str = "boton") -> dict:
        """Guarda un JPEG ya revelado en la SD con la numeración de la cámara. Devuelve {ruta, bytes} o {error}."""
        cfg = self.configura()
        raiz, gb = S.raiz_sd(cfg["sd"]["carpeta"]), cfg["sd"]["tamano_gb"]
        try:
            jpg = S.jpeg_con_exif(jpeg)
        except (OSError, ValueError) as e:
            return {"error": f"no es un JPEG válido: {e}"}
        with self.cerrojo:
            if not S.cabe(raiz, gb, len(jpg)):
                return {"error": "SD llena (cuota superada)"}
            n, num = S.siguiente_foto(raiz)
            d = S.ruta_foto(raiz, n, num)
            S.escribe_atomico(d, jpg)
            self._apunta("foto", d, origen)
        return {"ruta": d.relative_to(raiz).as_posix(), "bytes": len(jpg), "nombre": d.name}

    def foto_de_fuente(self, origen: str = "tecla") -> dict:
        """Foto a partir de la fuente de sensor configurada (la tecla del disparador, sin navegador abierto)."""
        jpeg, err = self._fotograma()
        if err:
            return {"error": err}
        return self.foto(jpeg, origen)

    def _fotograma(self) -> tuple[bytes, str]:
        """Un fotograma JPEG de la fuente configurada: imagen tal cual, vídeo/cámara con ffmpeg."""
        cfg = self.configura()
        sen = cfg.get("sensor", {})
        ruta = Path(sen.get("ruta", "")).expanduser()
        fuente = sen.get("fuente", "imagen")
        if fuente == "imagen":
            if not ruta.is_file():
                return b"", "la fuente de sensor es una imagen y no hay ruta válida en el configurador"
            import io

            from PIL import Image
            img = Image.open(ruta).convert("RGB")
            out = io.BytesIO()
            img.save(out, "JPEG", quality=92)
            return out.getvalue(), ""
        ff = shutil.which("ffmpeg")
        if not ff:
            return b"", "falta ffmpeg para sacar un fotograma del vídeo"
        if fuente == "webcam":
            args = ["-f", "v4l2", "-i", str(ruta or "/dev/video0")]
        else:
            if not ruta.is_file():
                return b"", "la fuente de sensor es un vídeo y no hay ruta válida en el configurador"
            args = ["-i", str(ruta)]
        r = subprocess.run([ff, "-v", "error", "-nostdin", *args, "-frames:v", "1", "-f", "image2", "-vcodec", "mjpeg", "pipe:1"],
                           check=False, capture_output=True, timeout=120)
        return (r.stdout, "") if r.returncode == 0 and r.stdout else (b"", "ffmpeg no dio fotograma de la fuente")

    # ---------------------------------------------------------------- vídeo
    def video_inicia(self) -> dict:
        """Empieza a grabar en el anfitrión. Devuelve {grabando} o {error}."""
        if self.grabando:
            return {"grabando": True, "segundos": round(time.time() - self._t0)}
        ff = shutil.which("ffmpeg")
        if not ff:
            return {"error": "falta ffmpeg para grabar vídeo"}
        cfg = self.configura()
        sen = cfg.get("sensor", {})
        ruta = Path(sen.get("ruta", "")).expanduser()
        fuente = sen.get("fuente", "imagen")
        if fuente == "webcam":
            entrada = ["-f", "v4l2", "-i", str(ruta or "/dev/video0")]
        elif ruta.is_file():
            entrada = (["-loop", "1", "-framerate", "30", "-i", str(ruta)] if fuente == "imagen"
                       else ["-stream_loop", "-1", "-i", str(ruta)])
        else:
            return {"error": "elige en el configurador la imagen, el vídeo o la cámara web que graba el clip"}
        self._tmp = Path(tempfile.mkdtemp(prefix="a6000-clip-")) / "clip.mp4"
        self._proc = subprocess.Popen([ff, "-v", "error", "-nostdin", *entrada, "-an", "-c:v", "libx264", "-preset", "veryfast",
                                       "-crf", "20", "-pix_fmt", "yuv420p", "-t", str(MAX_CLIP_S), "-movflags", "+faststart", str(self._tmp)],
                                      stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._t0 = time.time()
        self.aviso = ""
        return {"grabando": True, "segundos": 0}

    def video_para(self) -> dict:
        """Cierra el clip en curso (SIGINT a ffmpeg) y lo deja en la SD con su nombre."""
        with self.cerrojo:
            p, tmp, segs = self._proc, self._tmp, round(time.time() - self._t0)
            self._proc, self._tmp = None, None
            if not p or not tmp:
                return {"error": "no hay grabación en curso"}
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
                try:
                    p.wait(30)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(10)
            if not tmp.is_file() or not tmp.stat().st_size:
                shutil.rmtree(tmp.parent, ignore_errors=True)
                return {"error": "el clip quedó vacío (ffmpeg no escribió nada)"}
            cfg = self.configura()
            raiz, gb = S.raiz_sd(cfg["sd"]["carpeta"]), cfg["sd"]["tamano_gb"]
            if not S.cabe(raiz, gb, tmp.stat().st_size):
                shutil.rmtree(tmp.parent, ignore_errors=True)
                return {"error": "SD llena (cuota superada)"}
            n = S.siguiente_clip(raiz)
            d = S.ruta_clip(raiz, n)
            S.escribe_atomico(d, tmp.read_bytes())
            shutil.rmtree(tmp.parent, ignore_errors=True)
            self._apunta("clip", d, "tecla", NOTA_CLIP)
        return {"ruta": d.relative_to(raiz).as_posix(), "bytes": d.stat().st_size, "segundos": segs, "nota": NOTA_CLIP}

    # ---------------------------------------------------------------- teclas
    def tecla(self, nombre: str, v: int) -> None:
        """Reacciona a las teclas de la cámara como ella: disparador = foto, MOVIE = empieza/para el clip. No bloquea."""
        if nombre == "disparador" and v:
            threading.Thread(target=self._foto_tecla, daemon=True).start()
        elif nombre == "movie" and v:
            threading.Thread(target=self._video_tecla, daemon=True).start()

    def _foto_tecla(self) -> None:
        r = self.foto_de_fuente("tecla")
        self.aviso = "" if "ruta" in r else r.get("error", "")

    def _video_tecla(self) -> None:
        r = self.video_para() if self.grabando else self.video_inicia()
        self.aviso = "" if ("grabando" in r or "ruta" in r) else r.get("error", "")
