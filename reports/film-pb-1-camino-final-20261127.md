# FILM-PB-1 — Camino final: qué queda entre el error y el arreglo

Fecha: 27-11-2026. Nueve investigaciones en paralelo (subagentes) sobre el estado del
26-11. Este documento sustituye al plan de cuatro experimentos de la
[auditoría del CFW](film-pb-1-auditoria-cfw-20261127.md) §4: ahora hay dos productores
reales, un índice de tarjeta localizado y un kit de medida probado en seco.

Cámara sigue **no accesible** (sin ping a `192.168.1.30`, sin USB, sin `adb`).

## 1. Lo que cambia respecto al estado del 26-11

| Antes | Ahora | Fuente |
|---|---|---|
| Tres productores de `0x1A` | **Dos guardas reales** (A: capacidades/`dsm`, B: contenido soportado) y dos `bl` al traductor `0x7111B0` | [motor](film-pb-1-sub-motor-20261127.md) |
| `FUN_007211B0` en REA `0x7211B0` | Es **ELF `0x7111B0`** (REA `0x7211B0`); traductor puro; solo 6 de 65 536 entradas dan `0x1A` | [motor](film-pb-1-sub-motor-20261127.md), [kit](film-pb-1-sub-kit-captura-20261127.md) |
| `PbStart` (`0x307F54`) produce `0x1A` | `PbStart` **devuelve 0 siempre** según el motor: la rama `0x437CFC` sería muerta. El `bl` vivo es `0x437C7E`, tras `0x447DA8`, hacia `vtable+0xB4` = `AviMMgr::MovieReadStart` | ídem (falsable con el kit) |
| `m_durationOfContent` en modelo+`0x108` | Bloque `PbTimeInfo` en modelo+**`0x534`**: duración `0x5AC/0x5B0/0x5B4`, posición `0x594/0x598/0x59C`, cuadros `0x5CC`. Lo de `0x90…0x108` era `PbStatus` | [catálogo](film-pb-1-sub-catalogo-20261127.md) |
| El `0:02` podía venir del catálogo | El catálogo queda **descartado** (`GetMovieContentProperty` solo lo usa el volcado `0x7258F8`; `libObj` no importa `GetContentDuration`). Hipótesis viva: es `m_pbTimeInContent`, el **punto de reanudación** (`Get/SetContentResumePoint` `0x8CAE60`/`0x8CB4B2`) | ídem |
| La DB de películas, sin localizar | Índice persistente en la **raíz del volumen**: `AVF_INFO\AVIN0001.INP` (primario), `.BNP` (respaldo), `.INT`, `PRV00001.BIN`; `PRIVATE\M4ROOT\MEDIAPRO.XML` es la BD XAVC, no la de MP4 | [tarjeta](film-pb-1-sub-tarjeta-20261127.md) |
| El MP4 podía no ser conforme | **Es conforme**: `MSNV` minor `0x015A0070`, `uuid PROF/USMT/MTDT`, `moov` al final, anamórfico 1440×1080 (`SQZ_HD`), `avcC` Main/L4.0, AAC `esds` coherente. Reempaquetar lo empeoraría | [clip](film-pb-1-sub-clip-20261127.md) |
| H1 (arranque en frío) viva | **Pierde fuerza**: el WBI sí lleva el kernel y el TOC de `nflasha15`, pero **no** `av-cam` (`0x83541000`) ni `idt_cam`; el manejador `0x437BC0` no consulta el modo de arranque | [wbi](film-pb-1-sub-wbi-20261127.md) |
| Logs como alternativa informal | 4 líneas, incondicionales, a **stdout de `im.elf`** (búfer `0x83400000`); regla de decisión por línea | [logs](film-pb-1-sub-logs-20261127.md) |
| Sin forma de medir | `scripts/camera_filmpb1_trace.py` (934 líneas, `--dry-run`/`--verify` → EXIT 3 sin cámara, `--autotest` OK) | [kit](film-pb-1-sub-kit-captura-20261127.md) |
| Restauración por decidir | DAT oficial 3.21 **verificado** (con `nflasha5`); el build 4.04 solo difiere en `nflasha5`: es control, no arreglo | [restauración](film-pb-1-sub-restauracion-20261127.md) |

## 2. Estado real del diagnóstico

El error no lo produce código parcheado (auditoría del 27-11) y el fichero es conforme.
Quedan exactamente **tres** explicaciones, y cada una tiene su medida:

| # | Explicación | Cómo se confirma | Coste |
|---|---|---|---|
| **H-A** | La guarda de capacidades falla: `GetPlayMovieStatus` (`0x60945C`) / `dsm` no da reproducción | línea «Pb Disable!! ref) dsm get» en el log, o golpe en `0x437C0A` | log o breakpoint |
| **H-B** | La guarda de contenido falla: `isSupportContent` (`0x61A8F0`) → `vtable+0x58` sobre el objeto de medios devuelve «no soportado» | línea «Detect UnSupported Content» o golpe en `0x437C3C` | ídem |
| **H-C** | El motor falla: `AviMMgr::MovieReadStart` (`0x608698`) o el paso asíncrono devuelven error interno traducido a `0x1A` | línea «PlayMovie(), ErrorCode = 0x1a» sin las otras dos | ídem |

Y una incógnita que explica el `0:02` sin ser la causa: el **punto de reanudación**
guardado (`m_pbTimeInContent`), que valdría 2 s para ese clip.

## 3. Plan, en orden, con lo que desbloquea cada paso

| # | Acción | Quién | Desbloquea |
|---|---|---|---|
| **P0** | Sacar la tarjeta SD y copiarla al PC (basta con `reports/` fuera): leer `AVF_INFO/AVIN0001.INP`, `.BNP`, `PRIVATE/M4ROOT/MEDIAPRO.XML` y `STATUS.BIN` | usuario | **Sin cámara**: dice si el índice guarda 2 s (H-B) y si el punto de reanudación está corrupto |
| **P1** | En la cámara: menú → «Recuperar BD imág.» y reproducir. Si sigue: renombrar `AVF_INFO` y reproducir (la cámara reconstruye) | usuario | Cierra o descarta H-B sin flashear |
| **P2** | `python3 scripts/camera_filmpb1_trace.py` con la cámara encendida y telnet | yo | Dice si el `0x1A` lo pone A, B o el motor; a partir de ahí, reparación o parche de una guarda |
| **P3** | Solo si H-A: restaurar el 3.21 oficial (DAT verificado) para separar CFW de cámara | yo, con autorización | Descarta el CFW como causa |

P0 y P1 son del usuario y no requieren flashear nada. P2 es la medida que cierra el
diagnóstico. P3 es el último recurso y ya no parece probable, porque el manejador no
consulta el modo de arranque y el WBI no cubre `av-cam`.

## 4. Material entregado en esta tanda

- Nueve informes `reports/film-pb-1-sub-*.md` (wbi, catálogo, kit, restauración, motor,
  tarjeta, logs, clip, arnés) y sus evidencias en `reports/evidence/film-pb-1-sub-*/`.
- `scripts/camera_filmpb1_trace.py`: kit de traza con verificación de mapas y hashes,
  `--dry-run`, `--verify`, `--simular` y `--autotest`, ya probado en seco.
- `reports/evidence/film-pb-1-sub-arnes-20261127/mpr_pb.py`: ejecuta en Unicorn el
  manejador real de libmpr y reproduce las tres salidas (`0x437C0A`, `0x437C3C`,
  `0x437CFC`) con 8 pruebas verdes. Sirve para ensayar sin cámara.

## 5. Límites

- Nada de esto se ha medido en la cámara: la cámara no responde y no se ha flasheado.
- La clase que implementa `vtable+0x58` no está identificada (108 tablas candidatas).
- El escritor real de `m_durationOfContent` (`0x5AC`) no se ha encontrado: solo una
  copia de bloque puede escribirlo.
- La discrepancia `PbStart` «siempre 0» (motor) frente al punto C2 del kit no se
  resuelve en estático: el kit la falsa en la primera reproducción.
