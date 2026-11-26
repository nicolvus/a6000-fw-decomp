# G22 — Auditoría de CFW instalables: estática + arranque en el arnés

**Estado (26-11-2026): IMPLEMENTADO Y PROBADO con el `.dat` oficial de Sony 3.21 y con paquetes
sintéticos sobre el `/usr` real.** No había ningún `.dat` de CFW en este equipo, así que **ningún CFW
instalable se ha auditado todavía** (ver §7). El CLI es `scripts/gui/harness/audita_cfw.py`; las pruebas
están en `tests/test_gui_audita_cfw.py`.

Sustituye al auditor específico `scripts/gui/audit_package_nflasha15.py` (atado al CFW Silent y a la base
3.38) por una auditoría general de cualquier CFW instalable de la A6000: `.dat`, directorio de paquete con
`nflasha15` o `nflasha15.bin` suelto. Sigue siendo **solo lectura**: no escribe firmware, NVRAM ni MMIO,
no flashea y no toca la cámara.

## 1. Uso

```sh
# .dat de un CFW (etapas 1–4; el arranque se activa solo si están los artefactos del arnés)
/home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/audita_cfw.py ruta/al/cfw.dat

# solo estática (contenedor + /usr + estructura), sin QEMU
… audita_cfw.py cfw.dat --sin-arranque
… audita_cfw.py cfw.dat --rapido          # solo contenedor y /USR

# paquete ya extraído (directorio con nflasha15/nflasha15.bin)
… audita_cfw.py analysis/gui/g22/pkg-379w --completo --sin-arranque

# nflasha15.bin suelto y una base Sony distinta de la 3.21
… audita_cfw.py nflasha15-379.bin --usr-sony /ruta/al/usr/sony

# lote: todos los .dat/paquetes de un directorio (índice JSON + tabla Markdown)
… audita_cfw.py /ruta/a/paquetes --lote --sin-arranque
```

Opciones: `--completo|--rapido`, `--arranque|--sin-arranque`, `--salida DIR`, `--perfil-dir X`,
`--puerto N` (8630–8645), `--json`, `--teclas menu,intro,derecha`, `--declara FICHERO.json`,
`--usr-sony DIR`, `--espera S` (tope de la primera pantalla, 300 s por defecto).

Salidas por defecto:

- JSON: `analysis/gui/g22/audit-<AAAAMMDD>-<sha8>.json` con
  `{ruta, sha256, version, checks[], veredicto, fecha, coste_s}` (más `usr`, `estructura`, `arranque`);
- Markdown: `docs/gui/auditorias/<sha8>.md` con la tabla de comprobaciones, el diff de `/usr` y los límites;
- capturas y overlay del arranque: `analysis/gui/g22/audit-<sha8>/` (o `--salida`).

Códigos de salida: `0` sin fallo demostrable (OK/AVISO/PARCIAL), `1` si falla una comprobación de las
etapas 1–3 o el arranque, `2` si no se puede auditar (claves de `fwtool`, base Sony o artefactos del arnés
ausentes, ruta desconocida): **nunca un OK falso**.

Cada comprobación lleva `id`, `ok` (`true`/`false`/`null`), `detalle` y `evidencia`
(`VERIFICADO`, `INFERENCIA`, `NO_VERIFICADO`). `ok=null` significa que no se puede demostrar; nunca se
presenta como OK. El veredicto global es `FALLO` si algo falla, `AVISO` si solo hay avisos, `PARCIAL` si
falta algo material (p. ej. el arranque no se probó) y `OK` en el resto.

## 2. Qué cubre cada etapa

### Etapa 1 — Contenedor `.dat`

Reutiliza `scripts/e25_06/audit_packages.py` y `references/fwtool` (claves AES) para leer el contenedor
sin instalar nada:

- cabecera DAT de Sony, orden de chunks `DATV/PROV/UDID/FDAT/DEND`, `DEND` sin cola y su CRC-32;
- `DATV`/`PROV` (isLens=0), FDAT múltiplo de 1024;
- descifrado FDAT (AES-ECB doble, 512 B iniciales con una capa), suma de 16 bits de cada bloque, bandera
  de último bloque, longitudes y relleno 0xFF; comparación con el `.fdat` hermano si existe;
- cabecera FDAT (magia `UDTRFIRM`, formato 0100, CRC), versión BCD, **modelo 0x41030035**, región 0,
  fuera de la familia de accesorios, modo `U`/LUW `N`, tabla de sistemas de ficheros;
- `updater` oficial: sha256 del `updater.img` frente al de Sony 3.21 (`build.UPDATER_SHA256`); si no se
  puede cargar el constructor queda `NO_VERIFICADO`, no OK;
- tar del firmware: miembros, todas las líneas `0,…` de los `.sum`, presencia de `dev/nflasha15`;
- `nflasha15` TPZL: número de bloques y tamaño, cabe en la partición de 100 MiB, violaciones de la ruta
  LDEC (`tpzl.hardware_violations`), **bloque 0 idéntico al de Sony 3.21** (R55) y mismo número de bloques.

### Etapa 2 — `/usr` frente al Sony de la misma versión

Extrae el `nflasha15` del CFW con el mismo camino que el arnés (`TPZL → ext2 → debugfs rdump`, sin root) y
lo compara con el `/usr` de Sony 3.21 extraído igual (o con `--usr-sony DIR`). Lista, con sha256:

- **añadidos** (no están en Sony): se marcan declarados si figuran en `nuevos`/`parcheados`;
- **cambiados** (mismo nombre, otro contenido): declarados si su sha256 coincide con `parcheados` o si hay
  una tabla de offsets en `parches`;
- **quitados**: **FALLO** si no están justificados en `quitados`. Los cambios y añadidos no declarados son
  **AVISO**, no fallo.

La comparación es fichero a fichero por contenido; los enlaces simbólicos no se comparan (el extractor no
los conserva). Un directorio con `cam/usr` se trata como el `/usr` **completo** del CFW; si es la salida
parcial de `pkg_usr.py`, hay que declarar `"overlay_parcial": true` para que los ausentes queden
`NO_VERIFICADO` en vez de FALLO.

### Etapa 3 — Estructura y coherencia

a) **ELF** de cada fichero añadido/cambiado: magia, ELF32 little-endian, máquina ARM (40), EABI v5,
   segmentos y secciones dentro del fichero, `PT_LOAD`, `DT_STRTAB`/`DT_SONAME` dentro de rango y
   `DT_NEEDED` no vacío. Cada `DT_NEEDED` debe resolverse contra los nombres del `/usr` del invitado
   (CFW + Sony) y de `/lib` de la raíz de la cámara. Un `DT_NEEDED` que ya era irresoluble en la versión
   de Sony del mismo fichero se marca como preexistente (AVISO), no como fallo del CFW.

b) **Parches binarios**: se comparan los bytes del fichero del CFW con los del Sony y cada offset distinto
   debe caer en un cambio declarado (`parcheados` con el sha256 del resultado o `parches` con offsets y
   rangos). Un byte cambiado sin declarar es **AVISO/posible error**; un rango declarado que se sale del
   fichero es **FALLO**.

c) **Recursos y cadenas**: los `.uxc` con cabecera `uxc\x07` se validan contra su índice (ranuras dentro
   del fichero) y, si son tablas de cadenas (`string_*`, registro `0x1e04`), se parsean con
   `scripts/gui/uxc_strings.py`: ids en `0xE000–0xFFFE` y etiquetas declaradas presentes. Los demás `.uxc`
   (layouts, guías, imágenes) usan otro formato y quedan `NO_VERIFICADO`; `uxc_imagenes.py` no se usa
   todavía. Si el CFW declara `recursos`/`etiquetas`, el fichero debe existir y contener la etiqueta.

d) **Backup/NVRAM**: si el CFW declara `nvram.escrituras`, cada id se comprueba contra los ids del volcado
   (`analysis/gui/g22/harness/overlay/cam/usr/share/bk.tbl`, generado del volcado total de 2026-11-05):
   presente en el volcado es VERIFICADO; dentro de `[mín, máx]` pero no presente es INFERENCIA; fuera es
   **FALLO**. Sin declaración, es `NO_VERIFICADO`: el arnés no puede adivinar qué ids escribe un parche.

### Etapa 4 — Arranque en frío en el arnés

Con el `/usr` del CFW como overlay (`--pkg`), perfil propio (`--perfil-dir`, por defecto `audit-<sha8>`) y
puerto propio (8630–8645; espera si ya hay 2 `qemu-system-arm` en el sistema, hasta 15 min):

- arranque en frío y espera a la primera pantalla con tope (300 s; `--espera`/`AUDITA_ESPERA`);
- **fallo** si QEMU muere, si `im.elf` sale (`IMEXIT` en `live/<perfil>/consola.log`), si hay 0 fotogramas
  al vencer o si la pantalla es negra;
- guarda `cfw-1-primera.png`, `cfw-2-menu.png` (tras pulsar MENU) y `cfw-3-disparo.png` (tras cerrar el
  menú), más `cfw-4-teclas.png` si se pasa `--teclas`;
- captura la base de Sony de serie con las mismas teclas y perfil propio, la cachea en
  `analysis/gui/g22/harness/audit-base-sony/` y compara el menú (píxeles con contenido y fracción
  distinta). Un menú vacío o negro frente al de serie es **FALLO**; una diferencia grande de píxeles es
  AVISO (un CFW puede añadir entradas legítimamente). La comparación es INFERENCIA: emulación no es cámara;
- al acabar hace `POST /salir`, espera el cierre y termina cualquier QEMU de **su** perfil. Los
  reintentos del arnés (`LIVE_REINTENTOS`, 2 por defecto vía `AUDITA_REINTENTOS`) quedan registrados como
  AVISO si hicieron falta (SEGV intermitente conocido de `im.elf`);
- el perfil es nuevo en cada auditoría (se borra antes de arrancar para forzar el frío y al terminar),
  salvo que se pase `--perfil-dir` o `AUDITA_CONSERVA_PERFIL=1`; la consola del invitado se copia a
  `cfw-consola.log` en la salida antes de borrar el perfil.

### Etapa 5 — Informe

JSON + Markdown + consola, con el veredicto, el diff de `/usr` y las capturas. El modo `--lote` recorre un
directorio, audita cada CFW y genera `audit-lote-<fecha>.json` y `docs/gui/auditorias/lote-<fecha>.md`
(o ambos en `--salida`) con una fila por CFW y su veredicto.

## 3. Declaración del CFW (opcional pero recomendable)

`--declara FICHERO.json`, o `audit-cfw.json`/`MANIFEST.json` junto al paquete, o `<ruta>.audit.json` junto
al `.dat`/`.bin`. Formato:

```json
{
  "version": "3.79",
  "nuevos": {"lib/libNueva.so": "0755"},
  "parcheados": {"lib/libObj.so": "<sha256 del fichero resultante>"},
  "quitados": ["share/app/string_arabic.uxc"],
  "parches": {"lib/libObj.so": ["0x1a2b-0x1a30", 0x2000, [0x3000, 8]]},
  "recursos": [{"fichero": "share/app/string_english.uxc", "etiqueta": "Silent Shooting"}],
  "nvram": {"escrituras": ["0xFA0028", 4133]},
  "overlay_parcial": false
}
```

Sin declaración, el CFW se audita igual, pero cada cambio/añadido no declarado es AVISO y los ids de
NVRAM quedan NO_VERIFICADOS. `MANIFEST.json` del constructor (`parcheados`, `nuevos`, `originales`) se
acepta tal cual.

## 4. Coste medido

| Caso | Tiempo | Nota |
|---|---|---|
| `.dat` oficial 3.21, `--rapido` | 48 s | descifrar 200 MB (≈ 8 s) + extraer CFW y Sony (≈ 2 × 10 s) + sumas |
| CFW sintético sobre el `/usr` real, `--completo --sin-arranque` | ≈ 2,8 s | `/usr` ya extraído; diff de `libObj.so` (17 MB) incluido |
| arranque en frío del Sony de serie (medido 26-11-2026) | 145 s de sesión; primera pantalla ≈ 2 min | 3 PNG de 640×480, MENÚ abre, sin IMEXIT; el perfil guarda estado para la siguiente (≈ 7 s) |
| auditoría completa con la base Sony cacheada (paquete sintético idéntico a Sony) | 209 s | incluye la espera de hueco de QEMU; 9 comprobaciones de arranque OK y comparación de menú 0,0 |
| primera captura de la base Sony | 120–145 s | queda cacheada en `analysis/gui/g22/harness/audit-base-sony/` |

## 5. Qué **no** puede cubrir el arnés (sigue siendo riesgo de cámara)

- **Loader2/Loader3 y la ruta hardware del LDEC**: el arnés descomprime TPZL en software; las reglas del
  LDEC se comprueban estáticamente (`tpzl.hardware_violations`), pero no se ejecuta el cargador real.
- **Darwin** (`darwin_core.bin`), `nflasha3`, el updater y el instalador: no se ejecutan; solo se comprueba
  que el contenedor y sus sumas sean coherentes. Un fallo de Darwin o del flasheo no se detecta aquí.
- **NVRAM/Backup**: solo se comprueban ids *declarados* contra el volcado; no se demuestra la semántica de
  la escritura, el tamaño, el orden ni el momento. Sin declaración queda NO_VERIFICADO.
- **Tabla de recursos de NVRAM y arranque del kernel de Sony**: el arnés usa un kernel Debian y un shim;
  diferencias de temporización, prioridades RT, módulos `.ko` o servicios de kernel no aparecen.
- **Hardware**: sensor, obturador, AF, lentes, GPU DMP, LDEC, Wi-Fi, USB, tarjeta SD física; la imagen del
  sensor es sintética y ningún ajuste de imagen se procesa.
- **Recursos que no son tablas de cadenas**: `uxc_imagenes.py` no se usa; layouts, guías y `.uxc`
  comprimidos quedan NO_VERIFICADO. Un CFW que añada una entrada de menú en un layout no se valida.
- **Modos/permisos/UID/GID del ext2**: la comparación es por contenido; `pkg_usr`/overlay no reproducen
  todos los atributos. Un fichero instalado sin bit de ejecución podría no detectarse hasta el arranque.
- **Borrados**: el overlay del arnés no puede quitar ficheros de Sony; si el CFW los quita, QEMU los
  conserva (se marca `arranque.quitados` NO_VERIFICADO).
- **Modelo/región distintos de la A6000** y bases Sony distintas de la 3.21 sin `--usr-sony`: se rechazan
  o quedan sin base; no se generaliza a otras cámaras.
- **Seguridad/legalidad**: no valida que un CFW sea seguro, solo su coherencia con el firmware de Sony y
  el arranque emulado.

## 6. Pruebas

```sh
/home/nicolas/a6000-arnes/.venv/bin/python -m pytest tests/test_gui_audita_cfw.py -q
/home/nicolas/a6000-arnes/.venv/bin/python -m pytest tests/test_gui_harness.py -k "pkg_usr or shimenv" -q
```

Las seis primeras pruebas no usan QEMU (detección/rechazo, fichero de Sony quitado → FALLO, parche no
declarado → AVISO, informe JSON/Markdown, lote y orquestación de la etapa 4 con una sesión simulada). El
marcador de arranque se omite salvo que existan los artefactos y se pida:

```sh
AUDITA_CFW_ARRANQUE=1 … -m pytest tests/test_gui_audita_cfw.py::test_arranque_real_del_arnes -q
```

Variables de entorno: `AUDITA_SONY_NFLASHA15` (base Sony), `AUDITA_BK_TBL` (volcado de ids),
`AUDITA_WORKERS` (procesos de descompresión TPZL), `AUDITA_ESPERA`, `AUDITA_REINTENTOS`,
`AUDITA_BASE_RECAPTURA=1` (rehacer la base de Sony), `AUDITA_CONSERVA_PERFIL=1` (no borrar el perfil de la
auditoría).

## 7. Resultado en este equipo (26-11-2026)

- **CFW auditables encontrados: ninguno.** No hay ningún `.dat` de CFW en el equipo (los paquetes están en
  `.gitignore`); `analysis/gui/g22/pkg*` y `pkgdat` no existen. Por eso no se ha podido auditar ningún CFW
  instalable real y **no se afirma que ninguno funcione**.
- **Sí se auditó el `.dat` oficial de Sony 3.21** (`FirmwareData_ILCE6000V321.dat`, sha256 `29aef21a…`):
  etapas 1 y 2 completas, 33 comprobaciones OK, sin fallos ni avisos. Sirve de autocomprobación del
  contenedor, no de CFW.
- **Se rechaza** el `.dat` de la A6300 2.01 (`FirmwareData_ILCE6300.dat`): modelo `0x61030034` y versión
  2.01 → **FALLO** (2 fallos, sin comparar su `/usr` con el de la A6000); cualquier fichero que no sea
  `.dat`/`nflasha15`/paquete sale con error claro (código 2).
- **Paquete sintético sobre el `/usr` real**: se modificó `libObj.so` (un byte), una tabla
  `string_english.uxc` (etiqueta nueva) y se quitó un fichero de Sony; con declaración completa las etapas
  1–3 dan OK, sin declaración el quitado da FALLO y los cambios AVISO. Los 25 `string_*.uxc` reales se
  validan; 195 `.uxc` de otros formatos quedan NO_VERIFICADO.
- **Arranque real: SÍ, con el Sony de serie y con la etapa 4 completa sobre un paquete sintético idéntico
  a Sony.** El Sony de serie arrancó por el mismo camino (`live.py`, perfil y puerto propios): primera
  pantalla en ≈ 2 min, 3 PNG de 640×480, MENÚ abre (87.845 píxeles con contenido), sin IMEXIT, y QEMU
  cerrado al acabar (sesión de 145 s). Después, la auditoría completa de un paquete sintético idéntico a
  Sony reutilizó la base cacheada: 9 comprobaciones de arranque OK, comparación de menú con diferencia 0,0
  y veredicto OK en 209 s (incluida la espera de hueco: otros agentes mantenían 2–3 QEMU y el auditor solo
  arranca con menos de 2). **No es un CFW**: sirve para probar la etapa 4 de punta a punta.
- El marcador `test_arranque_real_del_arnes` sigue disponible (`AUDITA_CFW_ARRANQUE=1`); no se ejecutó en
  pytest para no dejar QEMU colgados en la suite, pero el mismo código se ejecutó a mano con el Sony real.

## PARA PENDIENTES.md

| ID | Estado | Descripción | Origen |
|---|---|---|---|
| G22-AUDIT-CFW | ABIERTO | Auditar los `.dat` de CFW reales (3.79 y siguientes) con `scripts/gui/harness/audita_cfw.py --completo` y adjuntar su JSON/Markdown; completar la declaración de parches/recursos/NVRAM de cada build para bajar los AVISOS, y ejecutar el arranque en frío con hueco de QEMU. Cierre: al menos un CFW real con veredicto OK/AVISO justificado y capturas comparadas con Sony. | G22 (26-11-2026) |
