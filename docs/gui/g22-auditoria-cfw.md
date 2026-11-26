# G22 — Auditoría de CFW instalables: estática + arranque en el arnés

**Estado (26-11-2026): IMPLEMENTADO Y PROBADO con un CFW REAL construido aquí y con el `.dat` oficial de
Sony 3.21.** Los `.dat` de CFW del proyecto no están en este clon, así que el CFW auditado se construyó
desde el firmware de Sony **sin cámara y sin instalar nada** (`/usr` con un byte distinto, versión 3.40,
WBI invalidado): `reports/evidence/g22-audit-cfw-20261126/` guarda su JSON, su Markdown, las capturas y la
receta. El CLI es `scripts/gui/harness/audita_cfw.py`; las pruebas están en `tests/test_gui_audita_cfw.py`.
Se lanza también **desde el configurador** (`lanzador.py`, pestaña Firmware: botones, tabla de
comprobaciones, informe enlazado e historial) — ver §8.

Sustituye al auditor específico `scripts/gui/audit_package_nflasha15.py` (atado al CFW Silent y a la base
3.38) por una auditoría general de cualquier CFW instalable de la A6000: `.dat`, directorio de paquete con
`nflasha15` o `nflasha15.bin` suelto. Sigue siendo **solo lectura**: no escribe firmware, NVRAM ni MMIO,
no flashea y no toca la cámara.

Desde esta entrega la etapa 1 comprueba además el **acoplamiento WBI**: un paquete que cambia `/usr` y
conserva la instantánea `nflasha5` de Sony se rechaza (o se marca con su motivo) en vez de pasar por bueno
(§2, etapa 1, y §7.4).

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
  LDEC (`tpzl.hardware_violations`), **bloque 0 idéntico al de Sony 3.21** (R55) y mismo número de bloques;
- **acoplamiento WBI ↔ `nflasha15`** (`contenedor.wbi_acoplamiento`, NUEVO en esta entrega). El arranque
  normal no carga Linux de `nflasha3`: reanuda la instantánea `WBI1` de `nflasha5`, que lleva dentro el TOC
  TPZL del `nflasha15` de Sony, el superbloque del ext2 y parte de su caché de páginas (G11 §11). Reglas:
  sin `dev/nflasha5` en el paquete → OK (arranque en frío, G11 §12); `nflasha15` idéntico al de Sony → OK;
  `/usr` cambiado con el TOC movido y el WBI de Sony byte a byte → **FALLO** (es el fallo de arranque
  medido 6/6 en cámara) con el motivo y la orden que lo arregla; `/usr` cambiado con el TOC intacto → OK con
  **AVISO** `INFERENCIA` (la instantánea reanudada conserva los procesos y la caché de Sony: el cambio puede
  no tener efecto); WBI presente pero distinto del de Sony y TOC movido → `NO_VERIFICADO` (descomprimir el
  WBI no es viable aquí), nunca OK. El WBI de Sony se busca en
  `firmware/extracted/fw321/…/dev/nflasha5` o en `AUDITA_SONY_NFLASHA5`.

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
| **CFW real 3.40, `--completo --sin-arranque`** | **53 s** | contenedor 170 MB + diff del `/usr` real (2 377 ficheros) + estructura; 38 ok, 0 fallos |
| **CFW real 3.40, `--completo --arranque`** | **316 s** | incluye 3 min de sesión de QEMU, la espera de hueco (otros agentes ocupaban QEMU) y la captura de la base Sony (cacheada) |
| construcción del CFW (offline): `build_nflasha15` + `build_package` | 1 min 40 s + 1 min 30 s | descomprimir 155 MB de ext2, `debugfs`, `e2fsck`, recomprimir 4 bloques y cifrar el `.dat` |

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
- **WBI (`nflasha5`) más allá de la comparación estática**: se compara el miembro con el de Sony 3.21 y el
  TOC del `nflasha15` con el de Sony; **no** se descomprime el WBI (ni el de Sony ni uno regenerado) para
  leer el TOC que lleva dentro, no se ejecuta Loader3 (así que la elección `BootMode 11` frente al arranque
  en frío no se observa) y el arnés no usa `nflasha5` para arrancar: un paquete aceptado aquí puede seguir
  fallando en cámara por esta ruta.
- **Seguridad/legalidad**: no valida que un CFW sea seguro, solo su coherencia con el firmware de Sony y
  el arranque emulado.

## 6. Pruebas

```sh
/home/nicolas/a6000-arnes/.venv/bin/python -m pytest tests/test_gui_audita_cfw.py -q
/home/nicolas/a6000-arnes/.venv/bin/python -m pytest tests/test_gui_harness.py -k "pkg_usr or shimenv" -q
```

Medido en esta entrega: **13 passed, 1 skipped** (el marcador de arranque real) en 0,9 s. Las siete pruebas
nuevas cubren el acoplamiento WBI sin QEMU, llamando a `analiza_wbi` con imágenes TPZL falsas: sin
`nflasha5` → OK; `nflasha5` de Sony con el `nflasha15` de Sony → OK; **TOC movido + WBI de Sony → FALLO**
(puerta 1) con el motivo y `--sin-wbi` en el detalle; TOC intacto con el `/usr` cambiado → OK con AVISO;
WBI regenerado con el TOC movido → `NO_VERIFICADO`/`PARCIAL`; miembro sin magia WBI → FALLO; sin
`nflasha5` de Sony → `NO_VERIFICADO`. El resto (detección/rechazo, fichero de Sony quitado → FALLO, parche
no declarado → AVISO, informe JSON/Markdown, lote y orquestación de la etapa 4 con una sesión simulada) no
usa QEMU. El marcador de arranque se omite salvo que existan los artefactos y se pida:

```sh
AUDITA_CFW_ARRANQUE=1 … -m pytest tests/test_gui_audita_cfw.py::test_arranque_real_del_arnes -q
```

Variables de entorno: `AUDITA_SONY_NFLASHA15` y `AUDITA_SONY_NFLASHA5` (bases Sony), `AUDITA_BK_TBL`
(volcado de ids), `AUDITA_WORKERS` (procesos de descompresión TPZL), `AUDITA_ESPERA`,
`AUDITA_REINTENTOS`, `AUDITA_BASE_RECAPTURA=1` (rehacer la base de Sony), `AUDITA_CONSERVA_PERFIL=1` (no
borrar el perfil de la auditoría).

## 7. Resultado en este equipo (26-11-2026)

### 7.1 Primera tanda: no había ningún CFW en disco

- **CFW auditables encontrados: ninguno.** No hay ningún `.dat` de CFW en el equipo (los paquetes están en
  `.gitignore`); `analysis/gui/g22/pkg*` y `pkgdat` no existen, y tampoco
  `analysis/e25-27/artifacts-338/firmware.integrated.tar` en este clon. Por eso aquí no se afirmaba que
  ningún CFW funcionara; §7.2 construye uno y lo audita.
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
- **Lanzada desde el configurador** (misma sesión, §8): el `.dat` oficial 3.21 auditado con «Auditar el
  .dat» dos veces → `POST /api/auditar` **202**, `GET /api/auditar/estado` **código 0** y **veredicto OK**
  con **33 comprobaciones, 0 ✗, 0 ? y 0 avisos** en **48,8 s** y **45,5 s**; el segundo `POST` mientras
  corría dio **409**, una ruta inexistente **400**, `GET /api/auditar/informe?f=…` sirvió el JSON
  (`application/json`) y el Markdown (`text/markdown`) del propio trabajo, y `..%2F..%2F..%2Fetc%2Fpasswd` →
  **400**. Informes en
  `analysis/gui/g22/harness/audit-ui/20261126-012200-FirmwareData_ILCE6000V321-dat/` y
  `…/20261126-012422-FirmwareData_ILCE6000V321-dat/` (ignorados por git). El historial listó las dos
  auditorías nuevas (OK, 3.21) y los cuatro `analysis/gui/g22/audit-3.7{6,7,8,9}.json` antiguos con `—` de
  veredicto y la fecha del fichero.

### 7.2 El CFW real: construido offline y auditado (esta entrega)

**Artefacto auditado** (fuera del repo, no se versiona):
`/home/nicolas/cfwbuild/out-sinwbi/package-3.40/firmware_packed.dat`,
**sha256 `04f6c18b0b4b782f819aebfc6be9821a5ff911fedce3b25b7a9400bf95e6cdf9`**, 170 528 920 B, versión 3.40,
modelo A6000 y updater oficial 3.21. Construido en este equipo **sin cámara y sin instalar nada**
(`CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA`).

Receta (scripts y huellas en `reports/evidence/g22-audit-cfw-20261126/construccion/`):

1. base `firmware/extracted/fw321/firmware.tar` (Sony 3.21, 105 miembros): `artifacts-338` no existe en
   este clon;
2. `/usr`: `share/app/string_english.uxc`, id `0xE001` «Extra fine» → «Extra Fine» (misma longitud: el
   fichero sigue en 219 996 B y cambia **1 byte**, el offset 11 950);
3. `scripts/gui/build_nflasha15.py` → `nflasha15` 84 042 977 → **84 043 264 B**, 4 bloques de 64 KiB
   recompuestos, CRC-32 `d5da505c`, bloque 0 byte a byte como el de Sony (R55);
4. `scripts/gui/build_package_nflasha15.py --base-tar … --version 3.40 --sin-wbi` → `.dat` + `.fdat` +
   `part_image.sum` con la línea nueva y **sin** `dev/nflasha5` (WBI invalidado, G11 §11);
5. declaración `declara.json`: `parcheados` con el sha256 resultante y `recursos` con la etiqueta nueva.

Coste de construcción: 1 min 40 s (`build_nflasha15`) + 1 min 30 s (`build_package`) por paquete.
Reproducibilidad: construir con **`LC_ALL=C`**; `build_nflasha15.py` reconoce el resumen de `e2fsck` por
textos en inglés (`FSCK_ONLY_COUNTS`) y con el locale en español la aserción falla aunque el sistema de
ficheros esté bien. Ese script no se ha tocado (no es de esta fila).

**Resultado** (`--completo --arranque --declara …`, **316 s**; JSON y Markdown adjuntos en
`reports/evidence/g22-audit-cfw-20261126/cfw-real-3.40/`): **VEREDICTO OK, 47 ok, 0 fallos, 2 no
verificados** (código 0).

| Etapa | Comprobaciones | Resultado |
|---|---|---|
| 1 contenedor | 30 | todas OK; `contenedor.wbi_acoplamiento` = «el paquete no incluye `dev/nflasha5`: … arranca en frío» |
| 2 `/usr` | 4 | 1 cambiado (`share/app/string_english.uxc`, declarado), 0 añadidos, 0 quitados |
| 3 estructura | 6 | ELF, parches declarados, 25 tablas de cadenas y la etiqueta declarada OK; 196 `.uxc` de otro formato y la NVRAM quedan NO_VERIFICADO |
| 4 arranque | 9 | **arranca**: primera pantalla a los 124,1 s, MENÚ abre, 3 PNG, sin `IMEXIT`, comparación con Sony 0,0 (§7.3) |

Los dos `NO_VERIFICADO` son `estructura.uxc_formato` (196 `.uxc` que no son tablas de cadenas) y
`estructura.nvram` (el CFW no declara ids de Backup/NVRAM), no el arranque. Sin arranque
(`--completo --sin-arranque`) tarda 53 s y da 39 ok más el `arranque.no_arrancado` no verificado.

### 7.3 Arranque del CFW real en el arnés (etapa 4)

`--completo --arranque --perfil-dir cfwreal --puerto 8641` (perfil y puerto propios; el auditor esperó hueco
hasta que bajaron de 2 `qemu-system-arm`, y el 3.40 arrancó en frío porque no lleva WBI):

- `arranque.primera_pantalla` ✓ a los **124,1 s**, `arranque.pantalla_no_negra` ✓, `arranque.capturas` ✓ (3 PNG),
  `arranque.menu_abre` ✓, `arranque.qemu_vivo` ✓, `arranque.im_elf` ✓ (**0 `IMEXIT`** en la consola del
  invitado), `contenedor.wbi_acoplamiento` ✓ («sin `dev/nflasha5`: arranca en frío»);
- capturas en `analysis/gui/g22/audit-04f6c18b/` y copiadas a
  `reports/evidence/g22-audit-cfw-20261126/cfw-real-3.40/`: `cfw-1-primera.png`, `cfw-2-menu.png` (el MENÚ de
  la cámara en 640×480, 67 KB) y `cfw-3-disparo.png`;
- comparación con el Sony de serie capturado igual (`analysis/gui/g22/harness/audit-base-sony/`):
  `fraccion_distinta 0.0` y **87 845** píxeles con contenido en los dos. Los PNG son **byte a byte iguales** a
  los de Sony (mismos sha256): el cambio auditado es una cadena de `string_english.uxc` que no se pinta en
  esas tres pantallas, así que la etapa 4 demuestra que el paquete **arranca**, no que el cambio se vea;
- al terminar hizo `POST /salir`, esperó el cierre y **no queda ningún QEMU del perfil `cfwreal`**; el perfil
  se conserva (`--perfil-dir` explícito) con su `consola.log`, copiado al informe.

Esto es emulación (kernel ajeno + shim): **no sustituye a la cámara** y no prueba Loader3/WBI/Darwin (§5).

### 7.4 Puertas G22-CFW-ARRANQUE: el auditor ya distingue los tres casos

Se construyeron tres `.dat` con el mismo `/usr` de partida y solo cambia lo que se indica. Antes de esta
entrega el auditor daba **el mismo veredicto (AVISO, 34 ok, 0 fallos) a los dos primeros**: no distinguía
un paquete abortable de uno correcto (línea base preservada en
`reports/evidence/g22-audit-cfw-20261126/antes-sin-comprobacion/`).

| `.dat` | Configuración | sha256 | Veredicto |
|---|---|---|---|
| 3.40 | `/usr` cambiado + **WBI invalidado** (sin `dev/nflasha5`) | `04f6c18b…` | **OK** (47 ok, 0 fallos; arranca en el arnés, §7.3) |
| 3.39 | mismo `/usr` cambiado + **WBI de Sony**, TOC del `nflasha15` intacto | `833619df…` | **AVISO** con ⚠ `INFERENCIA`: «la instantánea reanudada conserva los procesos y la caché del `/usr` de Sony → el cambio puede no tener efecto» |
| 3.41 | `/usr` recompuesto distinto (tabla vietnamita refluida) + **WBI de Sony**, TOC movido (973 entradas, primera 1400) | `c19eafb2…` | **FALLO** (código 1): «TOC movido … la cámara reanudaría la instantánea con el TOC y la caché del `/usr` de Sony (6/6 fallos de arranque medidos, G11 §11) → quitar `0700_part_image/dev/nflasha5` … (`--sin-wbi`)» |

**Puerta «rechazar»**: el 3.41 sale ✗ con el motivo y la orden que lo arregla; el 3.39 sale ⚠ con motivo
(cambio que probablemente no surtiría efecto) y el resto de sus comprobaciones siguen OK.
**Puerta «aceptar»**: el 3.40, construido con el mismo camino que un CFW instalable (contenedor oficial,
sumas, `/usr` declarado, bloque 0 de Sony), no pierde ninguna comprobación por el WBI y sus únicos
`NO_VERIFICADO` son los de siempre (`.uxc` no soportados y NVRAM no declarada).
**Límite de la comprobación**: solo se compara con el WBI de Sony 3.21; un WBI *regenerado* deja el TOC
interno sin verificar (`NO_VERIFICADO`, nunca OK) y el arnés no ejecuta Loader3.

## 8. Desde el configurador (`lanzador.py`, pestaña Firmware)

El configurador **no reimplementa la auditoría**: lanza `audita_cfw.py` como subproceso con las mismas
banderas y enlaza los informes que ese proceso escribe. Así un CFW se puede auditar sin terminal, pero el
veredicto sigue siendo el del CLI (una sola fuente de verdad).

### Botones y banderas

| Botón de la página | Órdenes que se ejecutan |
|---|---|
| «Auditar el .dat» | `audita_cfw.py RUTA --rapido --sin-arranque --salida <carpeta del trabajo>` |
| «Auditar el .dat» + «incluir estructura» | `… --completo --sin-arranque --salida …` |
| «Auditar con arranque» | `… --completo --arranque --salida …` (pide confirmación: ≈3 min y hueco de QEMU) |

Por defecto `--rapido --sin-arranque`: solo contenedor y `/USR` (≈46–49 s con el `.dat` de 200 MB). El
arranque real es **opt-in** y la página avisa antes de lanzarlo de que tarda ≈3 min, de que el auditor solo
arranca con menos de 2 `qemu-system-arm` en el sistema (espera hasta 15 min) y de que no sustituye a la
cámara. Un solo trabajo a la vez.

### API (servidor propio del configurador, `127.0.0.1:<puerto>`)

- `GET /api/auditar/estado` → `{corriendo, ruta, codigo, salida, informe, inicio, fin}` (más `tipo`,
  `completo`, `arranque`, `destino`, `comando`, `qemu`). `salida` es stdout+stderr del auditor tal cual;
  `informe` es el JSON del trabajo reducido a `{veredicto, version, sha256, fecha, coste_s, checks[],
  usr{}, f, markdown_f, json, markdown, arranque}` y `null` si aún no hay informe.
- `POST /api/auditar {"ruta", "arranque", "completo"}` → **202** con el estado del trabajo recién lanzado
  (y `avisos`), **400** si la ruta no es auditable (con el motivo), **409** si ya hay una auditoría en
  marcha. La ruta relativa se resuelve contra `analysis/gui/g22/harness` (así vale lo que guarda
  `importa_dat`); la absoluta, tal cual. Se valida que exista y sea `.dat`, directorio de paquete,
  `nflasha15`/`nflasha15.bin` u overlay `cam/usr` — lo decide `audita_cfw.detecta_tipo`, no una copia de la regla.
- `GET /api/auditar/informe?f=…` → el informe (`.json` o `.md`) servido con su `Content-Type`. `f` es
  relativo a `analysis/gui/g22` (o absoluto) y **solo** se sirven ficheros de la carpeta del trabajo
  (`harness/audit-ui/<fecha>-<artefacto>/`) o `audit-*.json` de la raíz de G22: `config.json`, `nota.txt`,
  `../../etc/passwd` y cualquier ruta fuera de esas carpetas dan **400**.
- `GET /api/auditar/historial` → `{auditorias: [{f, fecha, fecha_fuente, veredicto, version, sha256, ruta,
  coste_s, markdown, error}], vacio, raiz, carpetas}`. Lista `analysis/gui/g22/audit-*.json` (lo que deja
  el CLI) **y** cada `harness/audit-ui/*/audit-*.json` (lo que lanza la página). `fecha_fuente` = `informe`
  o `fichero` (los informes del auditor anterior a esta herramienta no traen fecha ni veredicto: se listan
  con la fecha del fichero y `—` de veredicto, sin inventarlo); un JSON ilegible sale con `error` y no
  rompe la lista. Si no hay ninguna, `vacio: true` y la página lo dice.

### Panel de resultado

Veredicto con color (`OK`/`AVISO`/`PARCIAL`/`FALLO`), tabla de comprobaciones (`id`, ✓/✗/?, aviso y
detalle con la evidencia en el `title`), enlaces al JSON y al Markdown del propio trabajo, y la consola en
un `<pre>` con scroll. Estado en vivo cada 2 s (`setInterval`), que se para al terminar. El pie del panel
recuerda **por qué un ✗ es del CFW y no de la cámara** (emulación con kernel ajeno y shim, LDEC real,
Darwin, flasheo, NVRAM no declarada, hardware y layouts `.uxc` fuera: §5).

### Importar y auditar sin volver a subir nada

«Importar .dat» por **ruta** guarda esa ruta en `emu.importado.ruta_dat`, y «Usar el importado» la pone en
el campo de auditoría: no se sube ni se copia nada otra vez. Si el `.dat` llegó **desde el navegador**, el
fichero del anfitrión no queda en disco y solo existe el overlay **parcial** de `pkgdat/` (solo lo distinto
de Sony); auditarlo como `/usr` completo marcaría todo Sony como «quitado» → **FALLO falso**, así que el
servidor lo **rechaza** con ese motivo y la página pide la ruta del `.dat` original (que sigue en el disco
del usuario). Con `audit-cfw.json` (o `MANIFEST.json`) en el paquete, el overlay parcial sí se acepta: la
declaración es la que convierte los ausentes en `NO_VERIFICADO` en vez de FALLO.

### Dónde quedan los informes

Cada trabajo usa su propia carpeta `analysis/gui/g22/harness/audit-ui/<AAAAMMDD-HHMMSS>-<artefacto>/`
(ignorada por git) y ahí van el JSON `audit-<AAAAMMDD>-<sha8>.json`, el resumen `<sha8>.md`, las capturas
del arranque si se pidió y los temporales. El auditor **escribe en el informe sus propias rutas** `json` y
`markdown` (cambio de esta entrega, antes quedaban vacías en el fichero), así que la página enlaza
exactamente lo que escribió el proceso: no hay una segunda copia de la regla de nombres.

### Cómo se audita un CFW real (el de §7.2 se auditó así)

```sh
# 1) configuración del arnés levantada (una vez; escucha en 127.0.0.1:8799)
/home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/lanzador.py --puerto 8799

# 2a) desde la página: pestaña Firmware → «Artefacto» = /ruta/al/cfw.dat → «Auditar el .dat»
#     (para un CFW: marcar «incluir estructura»; el arranque, solo con hueco de QEMU)

# 2b) o por HTTP, igual que hace la página
curl -X POST http://127.0.0.1:8799/api/auditar -H 'Content-Type: application/json' \
     -d '{"ruta":"/ruta/al/cfw.dat","completo":true,"arranque":false}'
curl http://127.0.0.1:8799/api/auditar/estado          # sondeo cada 2 s; codigo!=null al terminar
curl http://127.0.0.1:8799/api/auditar/historial       # veredicto y fecha de cada auditoría
```

Medido con el CFW real de §7.2: `--completo --sin-arranque` en 53 s; `--arranque` añade la etapa 4 (≈3 min
de sesión más la espera de hueco: con otros agentes manteniendo 2 `qemu-system-arm` durante 15 min el
resultado es `PARCIAL` con `arranque.no_arrancado` NO VERIFICADO, nunca un OK falso). La página no pasa
`--declara`, así que sin declaración junto al `.dat` los cambios salen como AVISO.

### Límites de esta integración

- La consola del auditor **aparece de golpe al terminar**: `imprime_consola` se ejecuta después de las
  cuatro etapas (el subproceso va con `-u`, pero no hay salida de progreso). El estado en vivo es el del
  trabajo (`corriendo`, `inicio`, `fin`), no el de cada etapa.
- El configurador no pasa `--declara`, `--usr-sony`, `--perfil-dir`, `--puerto` ni `--teclas`: usa los
  valores por defecto del CLI (base Sony 3.21 y perfil propio `audit-<sha8>`), y `AUDITA_SONY_NFLASHA15` si
  está en el entorno del servidor. Para esos ajustes, CLI.
- Sigue valiendo todo lo de §5: un OK de la página es tan limitado como un OK del CLI.
- Los informes de la página **no se versionan** (caen en `harness/`, ignorado). Para adjuntarlos a un
  informe del repo, cópialos o lanza el CLI con su `--salida` por defecto.
- La página se validó por su API (peticiones reales, más abajo) y su JavaScript con `node --check`, pero
  **no se abrió en un navegador** en esta sesión: el pintado de la tabla y del `<pre>` no está verificado
  visualmente.

### Pruebas de esta parte

`tests/test_gui_lanzador.py` cubre la API con servidores reales en hilos y sin QEMU: 400 con ruta
inexistente / fichero cualquiera / directorio sin paquete / overlay parcial, 409 con un trabajo en curso,
`/api/auditar/estado` antes de nada, un `.dat` sintético de 72 B auditado **con el subproceso real**
(código 1, JSON de FALLO y enlaces servibles), un paquete con `nflasha15` y comando falso (stdout+stderr,
código 0, informe OK), `?f=` que no permite salir de las carpetas y el historial vacío / con informes
(incluido uno ilegible). Medido en esta entrega: `23 passed, 1 skipped` (el marcador de arranque real).

## PARA PENDIENTES.md

| ID | Estado | Descripción | Origen |
|---|---|---|---|
| G22-AUDIT-CFW | PARCIAL (26-11-2026, esta entrega) | Auditar un CFW instalable real desde el arnés. **Hecho**: CFW 3.40 construido offline (`/usr` con 1 byte distinto, WBI invalidado, sha256 `04f6c18b…`) auditado con `--completo --arranque` → **OK (47 ok, 0 fallos, 2 NO_VERIFICADO)**, arranca en el arnés (primera pantalla 124 s, MENÚ abre, 3 PNG, sin IMEXIT) y comparado con Sony (0,0); JSON, Markdown, capturas, consola y receta en `reports/evidence/g22-audit-cfw-20261126/`. Etapa 1 gana la comprobación `contenedor.wbi_acoplamiento` (§2) y 7 pruebas nuevas (13 passed, 1 skipped). **Queda**: auditar los `.dat` de CFW históricos (3.79 y siguientes, que no están en este clon) con su declaración de parches/recursos/NVRAM completa para bajar los AVISOS, y decidir si el arnés debe montar el WBI real (`nflasha5`) para probar el camino de Loader3. Cierre: todos los CFW instalables del proyecto con su JSON adjunto y veredicto razonado. | G22 (26-11-2026) |
| G22-CFW-ARRANQUE | PARCIAL (26-11-2026, esta entrega) | **Por qué un CFW no arranca en la cámara y sí en el arnés**: el arranque normal reanuda el WBI de `nflasha5` con el TOC y las cachés del `/usr` de Sony (ver [G11](g11-auditoria-307-nflasha15.md) §11). **Hecho**: el auditor ya lo distingue con `contenedor.wbi_acoplamiento` — `/usr` recompuesto (TOC movido, 973 entradas distintas) + WBI de Sony → **FALLO** con el motivo y la orden `--sin-wbi`; mismo `/usr` con el TOC intacto → AVISO `INFERENCIA` (el cambio puede no surtir efecto); paquete sin `nflasha5` → OK, y ese es el que arranca en QEMU. Antes de esta entrega los dos paquetes daban el mismo AVISO (§7.4). **Queda**: el arnés no ejecuta Loader3 ni lee `nflasha5`, así que la elección de BootMode en cámara sigue sin probarse. Cierre: paquete `--sin-wbi` instalado y arrancando en cámara, con el WBI regenerado o descartado explícitamente. | G22 (26-11-2026) |
| G22-AUDIT-CFW-UI | PARCIAL (26-11-2026, implementado) | Auditoría de CFW desde el configurador: `GET /api/auditar/estado`, `POST /api/auditar` (202/400/409, un trabajo a la vez), `GET /api/auditar/informe?f=` (solo dentro de las carpetas del trabajo) y `GET /api/auditar/historial`; pestaña Firmware con los botones «Auditar el .dat» / «Auditar con arranque», tabla de comprobaciones ✓/✗/?, enlaces al JSON/Markdown, consola en `<pre>`, sondeo cada 2 s y aviso de que el fallo es del CFW y no de la cámara (§8). Probado con el `.dat` oficial 3.21 (OK, 33 comprobaciones, 45,5 s y 48,8 s) y con `tests/test_gui_lanzador.py` (23 passed, 1 skipped). **Queda**: lanzarlo desde la página con el CFW real de §7.2 (el CLI de esta entrega ya lo audita). | G22 (26-11-2026) |

## Fuzz del contenedor (27-11-2026): un CFW dañado se identifica, no revienta

El requisito del usuario es que **cualquier** error de un CFW se vea en el arnés y no en la cámara. Se ha
probado con el 3.40 real (`out-sinwbi/package-3.40/firmware_packed.dat`, 170 528 920 B) estropeado de tres
maneras, con `audita_cfw.py --rapido --sin-arranque`:

| Variante | Qué se le hizo | Resultado del auditor |
|---|---|---|
| `truncado.dat` | cortado a la mitad | **FALLO** (17 ok, 5 fallos) con informe JSON+Markdown |
| `cabecera-mala.dat` | primeros 32 B a `0xff` | **ERROR** claro: «no es un .dat de Sony, ni un nflasha15 TPZL, ni un directorio de paquete» (código 2) |
| `byte-medio.dat` | un byte del cuerpo invertido | **FALLO** (31 ok, 3 fallos) con informe |

Ninguna de las tres lanza una excepción ni devuelve un OK falso. Evidencia:
`reports/evidence/g22-audit-fuzz-20261127/` (informes y la salida del caso de cabecera).
Los tres casos quedan como test sin QEMU en `tests/test_gui_audita_cfw.py`.

Límite: los CFW históricos (3.79 y siguientes) **no están en este clon**, así que la auditoría de esos
paquetes sigue pendiente de tener los `.dat` (fila G22-AUDIT-CFW).
