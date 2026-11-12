# Emulador de la UI de la A6000: uso (G22-E / T3)

## Acceso directo
`/home/nicolas/Desktop/A6000-Emulador.desktop` ejecuta `scripts/gui/harness/a6000-emu.sh`: arranca el lanzador (si no corre ya) y abre el configurador en el navegador por defecto (`http://127.0.0.1:8700/`). Si el lanzador ya corre, solo abre el navegador. Registro: `~/.cache/a6000-emu/lanzador.log`. Variable `A6000_EMU_PUERTO` para cambiar el puerto. El `.desktop` es ejecutable; `gio set … metadata::trusted` no está soportado en este sistema de ficheros.

## Configurador (`lanzador.py`)
Guarda `~/.config/a6000-emu/config.json` (fuera del repo; `--config` lo cambia). Secciones:
- **Firmware/perfil**: Sony 3.21 de serie, overlay CFW existente (`pkg*` y los importados) o `.dat` importado. Cada perfil tiene su estado en `analysis/gui/g22/harness/live/<perfil>/` (primer arranque en frío ≈ 2,5 min; después se restaura en segundos).
- **Importar `.dat`** (fichero o ruta): valida contenedor, CRC y claves, comprueba que la cabecera FDAT sea de la A6000 (modelo `0x41030035`), saca `nflasha15` del tar y `pkg_usr.py` deja solo los ficheros distintos del `/usr` de Sony en `harness/pkgdat/dat-<versión>-<hash>/`. No instala nada. Errores claros: otro modelo, no es un `.dat`, CRC/bloque dañado, sin `nflasha15`, `nflasha15` idéntico al de Sony (no hay nada que superponer: usar «Sony de serie»).
- **Mapa de teclas**: tabla botón → teclas (`KeyboardEvent.code`), con captura pulsando; varias teclas por botón, una tecla en un solo botón. Los botones son las claves de `TECLAS` de `live.py` (códigos de cámara medidos en §5.18z′); para añadir uno basta ampliar ese diccionario. La ventana en vivo lee el mapa de `/config` en cada carga (recargar la ventana tras cambiarlo).
- **Sensor, SD (4 GB), red**: se guardan en el config y figuran como «próximamente»: ningún proceso los aplica todavía (T4/T5).
- **Iniciar** lanza `live.py` (puerto 8600; `--puerto-vm`) con el overlay elegido y salta a su ventana; en la ventana, «⚙ Configurador» guarda el estado, cierra la VM y vuelve. «Cerrar emulador» detiene VM y lanzador. Solo se toca el proceso lanzado por el propio lanzador.

## Opciones de `live.py` añadidas
`--perfil-dir NOMBRE` (directorio de perfil propio, útil para pruebas en paralelo), `--config` (mapa de teclas), `--lanzador URL` (enlace de vuelta).

## Verificación (12-11-2026)
Tests `tests/test_gui_harness.py` (`emu_config`); importación real de `analysis/gui/g22/pkg-3.63/package-3.63/firmware_packed.dat` → 31 ficheros, ≈ 6 s; el `.dat` de A6300 y un fichero cualquiera se rechazan; los `.dat` 3.22/3.37 del repo llevan el `nflasha15` de Sony y se detectan como idénticos. E2E con Chromium (puerto 8701/8601, perfil `t3`): configurador → Iniciar → `/tecla` con el mapa nuevo (KeyP → disparador, Espacio ya no) → Configurador (estado guardado) → reinicio restaurado. Capturas en `analysis/gui/g22/harness/t3/` (ignorado por git).

## Límites
Sin servidor de ficheros ni imagen del sensor persistentes (T4); solo escritorio con navegador; el overlay se compara con el `/usr` de `harness/stage` (hay que haber ejecutado `setup.sh`). Fn, reproducción, rueda y dial no tienen código verificado aún y no figuran.
