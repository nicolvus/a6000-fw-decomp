# FILM-PB-1 — traspaso de investigación de reproducción

Fecha: 25-11-2026. Estado: **causa raíz ABIERTA**. El usuario pide que continúe otro agente.
Repositorio: `/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter`.

## 1. Qué está demostrado y qué no

La cámara graba vídeos que se pueden leer en PC, pero al pulsar el botón central para reproducir muestra «No se puede visualizar.» durante unos segundos. La sesión consiguió enlazar físicamente el mensaje con una finalización fallida de `PlayMovie`, no con una reserva DMM concreta:

```text
MprIf::EnterMoviePb → retorno inmediato 0
MprIf::PlayMovie    → retorno inmediato 0
    procesamiento asíncrono
ObjPlayerCore.cpp::PlayMovieCmp, línea 2530
    resultado MPR::ER_FAILED = 0x1A
    conversor ObjPlayer → DefObjPlayer::ER_FAILED = 7
    modelo @M0E9 / ModelScrollSinglePb
    manejador de error → bloqueo de reproducción
    ViewMoviePb, acción 0x0F
    setCautionTrigger(0x135, true)
    recurso 0x0204E4A6 → «No se puede visualizar.»
```

**Los eslabones se observaron en varias reproducciones, no en una única traza completa.** El usuario identificó el archivo exacto al final; no se capturó aún la relación EntryId de MPR → nombre de archivo.

No está demostrado que `0x1A` sea un timeout, falta de RAM, error de demux o error del decoder. Es un error genérico. Los retornos iniciales cero aceptan una solicitud asíncrona: **no prueban que el fichero se haya abierto o decodificado bien**.

Los ceros de las primeras trazas de AVC tampoco demuestran ausencia de ejecución: hubo instrumentación defectuosa, cobertura inicial de un solo núcleo y capturas sin un control completo. La ausencia de tipos AVC en la configuración integrada DMM no prueba ausencia en el mapa externo. Conservar las correcciones de [G111 §14.5](../docs/gui/g111-film-receta-gui-iconos.md#145-mapa-externo-recuperado-y-selector-de-tipo-avc).

## 2. Archivo exacto que aporta el usuario

- Ruta: `/home/nicolas/Documents/a6000/MAH04198.MP4` (**fuera del repositorio; no añadido a Git**).
- Tamaño: **14 545 696 bytes**.
- SHA-256: `148c204cdea843ebafee0ffc9123b1614a493c083a931e5e499489ce27b7dba6`.
- Pantalla comunicada por el usuario: **`1-1-2014`, `11/87`, `30p`, `1080`, `MP4`, `0:02`**.
- `ffprobe`: duración del contenedor y vídeo **9,509500 s**, **285 fotogramas**, H.264 Main, nivel 4.0, `avc1`, 1440×1080, `yuv420p`, **30000/1001 fps**.
- Audio: AAC LC, 48 kHz, 2 canales, duración **9,493333 s**, 445 tramas.
- `ffmpeg -v error -i ... -map 0:v:0 -f null -`: salida 0 y registro vacío, decodificación completa del vídeo sin errores.

Evidencia: [ffprobe del archivo aportado](evidence/film-pb-1-20261125/provided-04198-ffprobe.json), [registro de decodificación](evidence/film-pb-1-20261125/provided-04198-decode.txt).

**Discrepancia abierta:** la cámara indica `0:02`, pero el archivo dura 9,5095 s. No asumir todavía que el contador es la duración total: podría ser posición de reproducción, estado conservado, otro dato de catálogo o un cálculo incorrecto. Identificar la propiedad que alimenta ese texto antes de atribuirlo a corrupción del índice o a una tasa de cuadros equivocada.

### Tarjeta leída en esta sesión

Acceso mediante `/android/mnt/sdcard` en Telnet y `/mnt/sdcard` en ADB. `PRIVATE/M4ROOT/CLIP` y `PRIVATE/AVCHD/BDMV/STREAM` estaban vacíos. Se encontraron siete MP4 en `MP_ROOT`:

| Archivo | Carpeta | Duración real |
|---|---|---:|
| MAH04114.MP4 | 100ANV01 | 72,5725 s |
| MAH04115.MP4 | 100ANV01 | 34,5345 s |
| MAH04165.MP4 | 100ANV01 | 24,5245 s |
| MAH04167.MP4 | 100ANV01 | 31,5315 s |
| MAH04191.MP4 | 103ANV01 | 52,5525 s |
| **MAH04198.MP4** | **103ANV01** | **9,5095 s** |
| MAH04199.MP4 | 103ANV01 | 5,005 s |

Todos declaraban H.264 1440×1080 a 30000/1001 y AAC. Se leyeron solamente sus cabeceras finales `moov`, salvo MAH04199, descargado completo por ADB como candidato inicial. **MAH04199 no es el archivo confirmado por el usuario**. Las cabeceras de MAH04198 leídas de la tarjeta coinciden en duración y número de cuadros con el archivo aportado; no se hizo un hash completo del archivo de la tarjeta.

[Resumen de metadatos](evidence/film-pb-1-20261125/clip-metadata-summary.json). La extracción binaria por `adb shell` requirió revertir CRLF del PTY; se comprobó byte a byte el procedimiento contra MAH04199 descargado por el servicio `sync` de ADB.

## 3. Evidencia física válida y traducción de errores

### A. Mensaje exacto de interfaz

En `string_spanish.uxc`, ID `0xE4A6` = «No se puede visualizar.». En `CautionRsrcConfig.so`:

- ELF VA `0x4338` contiene `0x0204E4A6`.
- Descriptor de trigger 8 de `m_rsrcTriggerTbl_5WAY_M_R`, base ELF `0x172F8`, apunta a ese recurso.
- La tabla `m_caution2RsrcIdTbl_5WAY_M_R`, base ELF `0x4AE4`, entradas de 12 bytes, asigna el descriptor 8 únicamente al caution `0x135`.
- `viewUnified3.so`, ELF `0x44658`, carga `r1=0x135`; `0x44662` llama a `ViewBase::setCautionTrigger` con `true`.

REA y los bytes/instrucciones se contrastaron. REA importa estos ELF con desplazamiento adicional de `0x10000`; distinguir sus direcciones de las ELF originales y de las de ejecución.

El selector de acciones de `ViewMoviePb` (ELF `0x46A70`) lleva la acción `0x0F` a ese emisor. En estados 2/3/5, evento 3, se selecciona esa acción cuando la condición 1 es verdadera. La condición (`0x443F8`, también incorporada por Ghidra al dispatcher `0x45B5C`) consulta:

- modelo `@M0E9`, información `0xD10`, parámetro `0x11FFFE4A`: compara con **−4 o −2**;
- información `0xD20`, parámetro `0x11FFFE49`: indicador booleano;
- la condición es verdadera si cualquiera de esas pruebas indica bloqueo.

La asociación `@M0E9` → `modelScrollSinglePb.so` / `ModelScrollSinglePbToInstance` está en el registro de fábricas de `libObj.so` (la implementación está integrada allí; no se encontró una biblioteca independiente con ese nombre).

### B. Error del modelo

[model-correct-live.txt](evidence/film-pb-1-20261125/model-correct-live.txt) captura `r1=7` al entrar en ELF `libObj+0x42D5DC`, con objeto `0x1DB54168`, y después el emisor de caution. El manejador lleva el código 7 a la rama que escribe 1 en el campo `objeto+0x5D4` (ELF `0x42D73E/0x42D740`). **Ese puntero es histórico y efímero; localizarlo de nuevo.**

[code7-origin-live.txt](evidence/film-pb-1-20261125/code7-origin-live.txt) registra el callback ELF `0x42F7EC` con argumentos `r1=1, r2=7, r3=1` y **`lr_usr=0x05EE30BD`**, correspondiente al llamador ELF `0x4310BC`. Ese llamador obtiene el entero de una respuesta ObjPlayer y lo pasa al callback. El helper ELF `0x41C964` verifica categoría, message ID y tipo de parámetro; no sintetiza un error 7 por falta de parámetro.

El código 7 es **`DefObjPlayer::ER_FAILED`**, no el error específico del decoder. El conversor ELF `0x8CCDE0` recorre 97 entradas de 16 bytes en ELF `0xFD9248`. Entre muchas otras conversiones, **`MPR::ER_FAILED (0x1A)` → `DefObjPlayer::ER_FAILED (7)`**. [Tabla extraída](evidence/film-pb-1-20261125/mpr-error-map.json).

### C. Punto de fallo asíncrono ya identificado

[raw-mpr-live.txt](evidence/film-pb-1-20261125/raw-mpr-live.txt) registra:

1. ELF `libObj+0x8CC958`: retorno de `MprIf::EnterMoviePb`, `r0=0`.
2. ELF `libObj+0x8C9BAE`: retorno de `MprIf::PlayMovie`, `r0=0`.
3. Conversor ELF `libObj+0x8CCDE0`: `r0=0x26`, **`r1=0x1A`**, `lr_usr=0x0639B5B5`.
4. El llamador ELF `0x8E95B0` está en **`ObjPlayerCore.cpp::PlayMovieCmp`, línea `0x9E2` = 2530**. Lee el resultado de la estructura de finalización (`ldr r1,[r6]` en `0x8E957E`) y llama al conversor cuando no es cero.

El nombre `PlayMovieCmp` se contrastó con la cadena ELF `0xDD5FBE`; el intento de leer 96 bytes desde su dirección de ejecución cruzó una página no mapeada y OpenOCD devolvió data abort de lectura de depuración. Se reanudó y la limpieza terminó; **no reinterpretar ese error del lector como un crash de la cámara**.

Esto cierra la propagación hasta el mensaje visible, **pero no identifica al productor interno del `0x1A` en MPR**.

## 4. Sesión y mapa de memoria — históricos, revalidar

Última red usada: cámara `192.168.1.30`, host `192.168.1.6`. Telnet puerto 23, ADB TCP 5555. Hubo varios reinicios: **no reutilizar los mapas sin volver a leer `/proc/PID/maps`**. En la última sesión `im.elf` era PID 144. La versión instalada exacta no se volvió a acreditar; 4.01/4.02 pertenecen al contexto previo del incidente.

| Biblioteca | Base de ejecución observada | MD5 leído en cámara |
|---|---|---|
| libObj.so | `0x05AB2000` | `406ffd33e185e2543ac61e5e275b8f8b` |
| viewUnified3.so | `0x0F35C000` | `4ed7d3b5aff44565ffddfd02e4d9c474` |
| libmpr.so | `0x06B95000` | no se midió hash completo |
| CautionRsrcConfig.so | `0x0CF8C000` | `12a8d7f77ba0546b2ecdfbc3718d9480` |

El `libObj.so` instalado **no tiene el mismo hash completo que el original local**. Antes de armar los puntos relevantes se verificaron por `/proc/144/mem` hashes de 16 bytes de cada dirección contra el original. `viewUnified3` y `CautionRsrcConfig` sí coincidieron con los MD5 de sus originales locales.

Calcular siempre en código `base + ELF_offset`, y comprobar que se verifica **la misma dirección que se arma**. Hubo errores manuales de suma: ver §6.

| Punto | Desplazamiento ELF | Dirección de ejecución observada |
|---|---:|---:|
| Condición: valor de estado | viewUnified3 `0x44434` | `0x0F3A0434` |
| Condición: booleano | viewUnified3 `0x44474` | `0x0F3A0474` |
| Emisor de caution | viewUnified3 `0x44658` | `0x0F3A0658` |
| Callback del modelo | libObj `0x42F7EC` | `0x05EE17EC` |
| Manejador del código 7 | libObj `0x42D5DC` | `0x05EDF5DC` |
| Conversor MPR → ObjPlayer | libObj `0x8CCDE0` | `0x0637EDE0` |
| Retorno EnterMoviePb | libObj `0x8CC958` | `0x0637E958` |
| Retorno PlayMovie | libObj `0x8C9BAE` | `0x0637BBAE` |
| Callback genérico FeaIf | libmpr `0x4502E8` | `0x06FE52E8` |

SWD: CMSIS-DAP, 250 kHz al final; AP1 para depuración, bases de cuatro Cortex-A5 `0x80110000`, `0x80112000`, `0x80114000`, `0x80116000`. Cada núcleo ofrece **3 breakpoints y 2 watchpoints**. AP0 permite leer RAM física sin detener la CPU; para el mapeo lineal Linux/av-cam usado aquí, PA = VA + `0x40000000`.

`0x40049E9C` no era un cuelgue: bytes comprobados en RAM `DSB; WFI; MOV PC,LR` corresponden a reposo de Linux. Se leyeron muestras de PC por AP1 en `debug_base+0x84` sin halt; hubo actividad de av-cam en los cuatro núcleos.

## 5. Método útil para continuar

- La captura con breakpoints **de un solo uso** funcionó y es la base más fiable disponible. Los guiones se conservan como `.cfg.txt`, evidencia histórica, **no un protocolo listo para ejecutar tras un reinicio**.
- `chip.cpu poll` **no existe**. Usar `TARGET arp_poll`; consultar `TARGET curstate`.
- `get_reg` devuelve un diccionario. Para la pila y el retorno de una parada en modo usuario fue necesario **`TARGET get_reg -force {sp_usr lr_usr}`**: los alias `sp`/`lr` devolvían cero.
- `mdw` imprime; para recoger datos en Tcl usar `read_memory`. Comprobar errores, límites de página y longitud real de la estructura.
- Retirar breakpoints/watchpoints con el núcleo detenido; comprobar después la reanudación. No ocultar errores de `resume` ni anunciar READY sin sondear todos los núcleos.
- `wait_halt 100` agota normalmente su espera mientras la CPU corre. Sus mensajes repetidos de timeout **no son por sí solos pérdida del enlace**. Hubo otros errores DSCR reales en capturas iniciales.
- REA importa estos ELF con una base adicional de `0x10000`. Los scripts `scripts/gui/elf_scan.py` trabajan con VA del ELF original. La importación completa de libObj por REA agotó tiempos de espera; se contrastaron las partes decisivas con bytes, símbolos, relocalizaciones y desensamblado del original. No dar por existente una sesión REA `libobj.sock` solo porque el archivo del socket permanece: hubo `ConnectionRefused`.
- En esta sesión funcionó ADB mediante `.venv/bin/python` y `adb_shell.adb_device.AdbDeviceTcp`. `pull` acepta `transport_timeout_s` y `read_timeout_s`, no `timeout_s`. El servicio `sync` sirvió para lectura binaria sin transformar.
- `adb shell` puede pasar por un PTY que convierte LF en CRLF. No tratar su salida binaria como íntegra sin control. `camera_telnet.run` es textual y tampoco sirve para volcar binarios.

## 6. Pruebas descartadas y efectos de instrumentación

1. Primeras trazas solo en core 0: cero hits sin cobertura suficiente. Un intento quiso armar 4 breakpoints, pero el hardware solo permite 3. Las pruebas posteriores cubrieron los cuatro núcleos y los controles Thumb sí pararon en cada uno.
2. Configuración v2: usaba `chip.cpu poll`, comando inválido. Los guiones originales ocultaban errores de reanudación y no comprobaban instrucciones antes de armar.
3. **Direcciones nativas erróneas:** `model-error-live`, `model-error2-live` armaban `0x05EDA5DC` y `0x05EDFD3E`, pero las sumas correctas eran `0x05EDF5DC` y `0x05EE1D3E`. Los registros y el puntero deducidos de aquellos puntos **no pertenecen al manejador buscado**.
4. **Watchpoint inválido:** `flag-writer-live` vigiló `0x2415E144`, derivado de la prueba anterior. No sirve para afirmar nada sobre el escritor real del bloqueo.
5. **Capturas genéricas de MPR inválidas:** `mpr-callback-live` y `mpr-callback2-live` registraron 24 paradas repetidas del evento `0x40000084`, dato `0`, con la misma pila y argumentos. No capturaron `0x1A`. El primer guion rearmaba sin avanzar. En el segundo, `step` entraba a IRQ y el retorno volvía al mismo breakpoint antes de ejecutar la primera instrucción. Esto perturbó el tiempo de ejecución; **descartar ambos intentos para inferir la causa del error**.
6. El control ARM en reposo con retirar → step → rearmar funcionó, pero **no valida ese procedimiento en Thumb con IRQ habilitada**. Se investigó `cortex_a maskisr on`: el código de OpenOCD enmascara interrupciones solo durante el paso y las restaura al acabar. **No quedó probado en la cámara:** el control Thumb elegido no se alcanzó dentro del plazo. No volver a afirmar que el paso Thumb está validado ni reutilizar `mpr-callback2.cfg.txt` tal cual.
7. Al principio se ejecutó un monitor muy frecuente Telnet/ADB. Aparecieron `Cannot allocate ASID` y dejaron de responder comandos mientras la cámara seguía viva. El kernel Sony limita a 255 ASID en esa configuración; la instrumentación creó procesos y es un factor de confusión. No atribuir ese incidente a Play. Tras reiniciar se abandonó el sondeo continuo de shells.
8. Se observaron numerosos `sh` de sesiones Telnet aún vivos. `camera_telnet.run` cierra el socket sin enviar `exit`; la causa exacta de la persistencia no quedó auditada. En adelante cerrar explícitamente sesiones propias, reutilizar conexiones y no matar procesos ajenos por patrones amplios.

Las pruebas no escribieron parches en RAM, NAND, firmware o NVRAM. Sí usaron halt/resume, registros de depuración y un paso de CPU; **no fueron observación completamente pasiva**. Hubo copias de lectura hacia el host. No se alteró el vídeo de la tarjeta.

## 7. Estado al entregar y siguiente tarea concreta

- No queda ningún OpenOCD ni traza física activa; las últimas limpiezas registraron los cuatro núcleos `RUNNING` y `shutdown`.
- El servidor FTP local de la prueba de transferencia fallida se cerró. El lector Telnet binario fallido se terminó. La descarga correcta se hizo por ADB, cerrando el cliente.
- No se instaló firmware, no se reparó ni reseteó el catálogo y no se cambió la configuración de captura.
- No se hace otro Play dentro de este traspaso.

**Siguiente tarea, en orden:**

1. Leer este informe, el archivo MAH04198 aportado y [G111 §14.5](../docs/gui/g111-film-receta-gui-iconos.md#145-mapa-externo-recuperado-y-selector-de-tipo-avc). Confirmar el SHA-256 del vídeo.
2. Seguir estáticamente **el productor de la finalización fallida de `PlayMovie` dentro de libmpr**, no volver a empezar en la advertencia de la GUI. Los API originales relevantes son `MprIf::PlayMovie` ELF `0x7229E0`, `FeaIf::PlayMovie` `0x44EE9C` y `FeaIf::MprIfCallbackPoint` `0x4502E8`. Este último es demasiado genérico para dejar un breakpoint persistente sin un paso validado.
3. Identificar el evento concreto de finalización de PlayMovie y el lugar interno donde se construye el `0x1A`. El callback genérico observado con resultado cero tenía evento `0x40000084`, LR de ejecución `0x06FBE18F` (ELF `0x42918E`); **su identidad funcional exacta no quedó demostrada**. No confundirlo con el error buscado.
4. Para otra prueba física, revalidar cámara, IP, PID, mapas y bytes. Preferir puntos de un solo uso **en ramas específicas de error**, o solucionar y comprobar primero el avance Thumb sin IRQ antes de usar un callback frecuente. El resultado esperado es una causa anterior a `0x1A`: nombre de fichero, error del lector/demux, estado de sesión, retorno DMM o del hardware, con su valor real.
5. Resolver por separado qué representa `0:02` en el layout MoviePb y qué propiedad lo alimenta. Compararlo con mvhd/mdhd, número de cuadros y EntryId → ruta de **MAH04198**. La discordancia temporal es un hallazgo real; **su conexión causal con la reproducción no está cerrada**.
6. Solo si se identifica una reserva fallida, volver a reglas/extents DMM. No reabrir como hecho la hipótesis del mapa externo sin los cinco tipos AVC: el mapa histórico los contiene. Mantener pendiente FILM-PB-1 hasta demostrar la causa o una reproducción controlada que la descarte.

## 8. Evidencias y reproducibilidad

Carpeta persistente: [reports/evidence/film-pb-1-20261125](evidence/film-pb-1-20261125/). [SHA256SUMS.json](evidence/film-pb-1-20261125/SHA256SUMS.json) contiene hashes de los artefactos archivados. Los `.cfg.txt` son copias históricas para auditoría; los de callback reiterado son explícitamente inválidos.

El resto de la sesión permanece en `/tmp/a6000-playback-live/` mientras no se limpie `/tmp`: consultas REA, configuraciones, logs de red y scripts auxiliares. El vídeo aportado y otros binarios grandes **no** forman parte de esta carpeta versionada de evidencias.
