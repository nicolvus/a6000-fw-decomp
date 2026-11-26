# FILM-PB-1 · Los logs como trazador de la reproducción (27-11-2026)

Estado: **mecanismo de log localizado y ruta instrumentada sin depurador**. La reproducción imprime
**cuatro líneas de texto**; tres son incondicionales y separan los tres productores del `0x1A`.
Cámara no accesible: todo estático (bytes + desensamblado local con Capstone).

VA = **VA del ELF** (libmpr/libObj 3.21, base 0). En libmpr, REA = ELF + 0x10000: el manejador
`0x437BC0` es `FUN_00447BC0` en REA. **Corrección al informe del 26-11**: `FUN_00722938` y
`FUN_007211B0` eran VA de REA; en el ELF son `0x712938` (emisor de log) y `0x7111B0` (traductor de
errores, que **no** imprime). Los tres breakpoints (`0x437C0A`/`0x437C3C`/`0x437CFC`) sí son VA del
ELF y coinciden instrucción a instrucción.

## 1. Mecanismo

La ruta usa **dos** emisores distintos:

| | Emisor | VA | Destino |
|---|---|---|---|
| **E1** | ostream propio de libmpr: `0x712938(stream,str,flush)` y `0x712960(stream,str,code)` → `operator<<` `0x68323C` + flush `0x683118` | `0x712938`, `0x712960` | **`putchar` + `fflush(stdout)`**: sink `0x683E04`, GOT `stdout` en `0x683E18`; bucle de caracteres `0x683E1C`. Es el **stdout del proceso MPR** (`im.elf`). Sin fichero, sin anillo propio y **sin nivel**: si la rama se ejecuta, la línea sale |
| **E2** | consola de monitor `MprIfMcmd` (grupo `"MPR"`, `0x90232A`, registrado en `0x72832E`; ayuda `"Media Player Recorder Monitor Command"` `0x928120`) | tabla de subcomandos `0x928E00` (39 entradas) | anillo de salida del monitor (`MprIfMcmd::m_msg`), que vuelca `/usr/bin/mpr_monio.elf` |

- El "stream" que usa el manejador es un objeto en **`[FeaCore+8]`** (`0x437C00`, `0x437D12`); su
  byte `+8` es un *enable*. Un conmutador global en `.bss` **`0xA52630`** elige entre `putchar`
  (stdout) y el dispositivo interno `0x683D74`. Valor por defecto: `0`. **NO_VERIFICADO** quién lo
  pone a 1 (dos setters en `0x6830xx`, sin símbolo).
- **Nivel configurable (E2)**: `MprIfMcmd::DebugApiTraceMode` `0x729928` escribe el byte
  `MprIfMcmd::mb_isApiTraceEnable` (**VA `0xAD49A0`**) con `on`(`0x7E4304`)/`off`(`0x839089`) y
  responde `" API trace mode is "` (`0x929637`). Uso documentado en la propia biblioteca:
  `" ex) mpr debug ApiTrace [on/off]\r\n"` (`0x929684`). Subcomandos hermanos: `TimeTrace`,
  `BBTrace`, `FileIfTrace` (`0x928EF0`/`0x928EFC`/`0x928F08`).
- **Nivel configurable (libObj, E3)**: `testmode_debugPrint` `0x7F0CB8` = `(nivel, subsistema, fmt, …)`
  → mensaje OSAL (`osal_valloc_msg_wait`/`osal_snd_sync_msg`, cola `0x008F0139`; cabecera
  `{op=1, subsys=0x83, +4, nivel@+0x10, texto≤0x81}`). Compuerta global en `.bss` `0x8EEEB6`,
  conmutada por `testmode_changeDebugPrint` `0x7F0CA8`: con 0 sólo pasan `nivel==1` y `-1`.
  `0x83` = subsistema APPSYSTEM (`bin/appdbglv.sh`; 131=0x83, el `< 83:: …>` del log real se imprime en hex).
- **Nivel de texto de la cámara (E4)**: `bin/appdbglv.sh` → `ulogio.elf filter on <subsys> <cat> <nivel>`
  (131 APPSYSTEM, 135 model, 136 view, 137 wgt; `clear|error|warning|debug|info|off`).
- libmpr **no** importa `testmode_debugPrint` ni ninguna función `osal_*send*` (lista de importados
  revisada entera): por eso E1 no puede acabar en la cola OSAL de E3.

## 2. Cadenas de la ruta, en orden (VA ELF, libmpr)

| # | VA cadena | Cadena exacta | Emitida en | Condición |
|---:|---|---|---|---|
| 1 | `0x85E95B` | `" API CALL PlayMovie()"` + `0x85DF8A` `" + regionId : "` + valor | `0x44EEC8` (FeaIf::PlayMovie) | sólo si `mb_isApiTraceEnable` (`0xAD49A0`) ≠ 0 |
| — | — | *(sin texto)*: `MprIfLog::AsyncApiDone(0x4000001D, 9)` | `0x44EF16` | la cola de FeaCore rechaza la orden → devuelve 9 |
| 2 | `0x85A51C` | `" Pb Disable!! ref) dsm get"` | `0x437C06` | **guarda A** `0x447A1E` devuelve 0 (capacidades/«dsm») → `status=0x1a` en `0x437C0A` |
| 3 | `0x85A7D8` | `" Detect UnSupported Content "` | `0x437C38` | **guarda B** `0x447F26` devuelve 0 (contenido no soportado) → `status=0x1a` en `0x437C3C` |
| 4 | `0x85A7F5` | `" ResumeInfo is updated "` | `0x437C6A` | igual que 3 **y** `ctrl[0x24] != 0` (tras `0x447EE2`) |
| 5 | `0x85E965` | `"PlayMovie()"` + `0x920D04` `", ErrorCode = "` + `status` | `0x437D1A` (`0x712960`) | **toda finalización fallida**: se llega a `0x437D0E` con `0x0a`, con `0x1a` de A/B o con el código de `0x7111B0`. El éxito retorna en `0x437D2C` **sin** esta línea |
| 6 | `0x806CF5`, `0x806D07`, `0x806D19`, `0x806D2D`, `0x806D3F`, `0x806D51`, `0x806D68`, `0x806D88`, … | volcado de parámetros de `PbStart` (`"    - category  ["`, `"    - groupId   ["`, `"  - pResumeInfo [0x"`, `"  - playSpeed   ["`, `"  - regionId    ["`, `"  - bContinuousFlag  ["`, …) | `0x307F92` y siguientes (`0x2FB510`/`0x2FB59C`/`0x2FB628`) | **compilado en off**: enable en `.bss` `0xA4B4C9`, inicializado a 0 en `0x2FAF5C` y **sin ningún otro escritor** (barrido de literales) |
| 7 | `0x85D4FB` | `" GetPlayMovieStatus Err!"` | pools `0x446BC0`/`0x4470DC` | consulta de estado de reproducción; **NO_VERIFICADO** si está en este camino |
| 8 | `0x85AAB7` | `" SetUpPlayerInstance ..."` (+`0x85AAD0` `" + SetUp mode     :"`, `0x85AAE4` `" + bIsFinalizeMode:"`) | pool `0x4393D8` (zona FeaCore movie) | **NO_VERIFICADO** función y compuerta exactas |

En el manejador hay **exactamente** cuatro llamadas de log (`0x712938`×3 en `0x437C06/38/6A`, `0x712960`×1 en
`0x437D1A`); el despachador `0x429C38` no imprime nada para `0x4000001D`.

## 3. Leerlo sin depurador

El texto de la cámara vive en un **búfer de RAM en `0x83400000`** (1,2 MiB = 19×64 KiB, anillo que
sobrevive a reinicios), volcado ya una vez con `dd` sobre `/dev/mem` y conservado en
`analysis/camera-dumps/mem-20261020-log/` (251 957 B de texto; formato
`\x1b[31m[%05d.%06d] <%x:: %x> texto`). **Ese fichero NO sirve como evidencia de esta ruta**: no
contiene ninguna de las cadenas de §2 (`grep` = 0 en las cuatro), porque la captura es de menú, sin
intento de reproducción. Sirve para probar el camino de lectura y el formato.
`ulogio.elf`, `mpr_viewLog.elf`, `mpr_monio.elf` y `ujlog.elf` abren **`/dev/mem`** y hacen `mmap`;
`ulogio.elf` además lee **`/proc/klog`** y `/proc/snsc_boot_time`.

Comandos exactos (en cuanto haya cámara; `skip=33600` = `0x83400000/0x10000`):

```sh
# 0) DECISIVO y barato: ¿dónde apunta el fd 1 del proceso MPR?
ls -l /proc/$(pidof im.elf | cut -d' ' -f1)/fd/1            # esperado: /dev/console | /dev/kmsg | pipe
# 1) marcar el final del búfer antes de reproducir
dd if=/dev/mem bs=65536 skip=33600 count=19 2>/dev/null | strings -n 6 | tail -2
# 2) reproducir el clip (MAH04198) en la cámara
# 3) volcar y filtrar
dd if=/dev/mem bs=65536 skip=33600 count=19 2>/dev/null | strings -n 6 \
  | grep -aE 'Pb Disable!! ref\) dsm get|Detect UnSupported Content|ResumeInfo is updated|PlayMovie\(\), ErrorCode|API CALL PlayMovie'
# 3-bis) alternativa corta, sólo el arranque actual
cat /proc/klog | strings | grep -aE 'Pb Disable|UnSupported Content|PlayMovie\(\)'
```

Trazador opcional (añade la línea 1 y el `regionId`): consola del monitor de MPR y dentro
`MPR debug ApiTrace on` (responde `API trace mode is ON`); volcado con `/usr/bin/mpr_monio.elf`
(anillo de 1024 entradas, `"### monio start ###"`, comandos `dump`/`slow`/`fast`/`quit`/`exit`).
Para el log de texto de libObj: `/usr/bin/ulogio.elf filter on 131 1 debug` (o `bin/appdbglv.sh`).

## 4. Regla de decisión (los tres productores de `0x1A`)

La línea 5 imprime el código **ya traducido**, así que vale `0x1a` en los tres casos y **no discrimina**.
Discrimina la combinación:

| Observado en el volcado | Productor |
|---|---|
| `Pb Disable!! ref) dsm get` + `PlayMovie(), ErrorCode = 0x1a` (sin línea 3 ni 4) | **1 — guarda A** (`0x447A1E`, capacidades/«dsm») ⇒ favorece **H1 arranque en frío/WBI** |
| `Detect UnSupported Content` (+ `ResumeInfo is updated` si `ctrl[0x24]`) + `PlayMovie(), ErrorCode = 0x1a` | **2 — guarda B** (`0x447F26`, contenido) ⇒ favorece **H2 catálogo/BD** |
| **sólo** `PlayMovie(), ErrorCode = 0x1a`, ninguna guarda | **3 — motor** `PbStart` (`0x307F54`) traducido por `0x7111B0` |
| con ApiTrace: además `API CALL PlayMovie()` + `regionId : N` | confirma llegada a `FeaIf::PlayMovie` y da el `regionId` (útil para EntryId↔MAH04198) |

## 5. Límites

- **NO_VERIFICADO** que el fd 1 de `im.elf` sea el búfer de `0x83400000`: no hay script de arranque en
  la imagen (`bootin.elf` lanza `im.elf <letra> &` con `system()`, así que **hereda** el fd 1); el paso
  0 lo resuelve en un comando. Si el fd 1 fuese `/dev/null` o un pipe sin lector, E1 sólo se lee
  con E2/monio.
- **NO_VERIFICADO** el valor de `0xA52630` en ejecución (putchar vs dispositivo interno) y el formato del volcado `0x7168E4` tras la línea 1.
- Las líneas 1–5 son código de fábrica: el CFW auditado no toca `libmpr.so` (auditoría del 27-11).

Evidencia: [evidence/film-pb-1-sub-20261127](evidence/film-pb-1-sub-20261127/) (`logs-handler-llamadas.txt`, `logs-strings-ruta.txt`, `logs-comandos-monitor.txt`, `logs-testmode-libobj.txt`).
