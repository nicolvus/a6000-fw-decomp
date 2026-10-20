# Hilo Claude A — sesión 18: Connect(), vtables LifeCycle y filas dinámicas del selector LIRO

Clasificación: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.
**No se afirma en ningún punto que SilentShutter funcione.** No se conectó ni flasheó la cámara; todo el trabajo fue desensamblado estático de archivos ya extraídos del firmware 3.21 (`firmware/extracted/fw321/...`) y de `av-cam.bin` vía Ghidra headless `-noanalysis -readOnly`. No se editó `CONTEXT.md` ni ningún binario original. No se delegó en subagentes (prohibido por la tarea); todo el análisis de este documento lo ejecuté yo directamente con `Bash`/`llvm-objdump`/`scripts/ghidra_dec.sh`.

Modelo/esfuerzo realmente usado: **Sonnet 5** (`claude-sonnet-5`), confirmado por el system reminder del entorno — coincide con lo solicitado ("sonnet"). No tengo forma de leer desde dentro de la conversación el valor numérico de "esfuerzo" con el que me configuró el orquestador en este hilo concreto (no es un dato expuesto al modelo); no hay discrepancia que pueda declarar más allá de esto, y no until ahora until usé subagentes ni herramientas de delegación, tal como exige la tarea.

---

## 1. Caller real de `MWF::ObjPin::Connect` — avance parcial del blocker (INFERENCIA fuerte + límite de la técnica, NO VERIFICADO el sitio exacto)

**Método**: `llvm-objdump -T/-R/-d --triple=thumbv7-none-eabi` directo sobre los `.so` extraídos de `firmware/extracted/fw321/.../lib/`, sin pasar por Ghidra (que sesión 17 ya reportó incompleto en modo `-noanalysis` para este tipo de xref).

**VERIFICADO**: `MWF::ObjPin::Connect(MWF::ObjPin*, MWF::ObjStatusViewer*)` es el símbolo dinámico `_ZN3MWF6ObjPin7ConnectEPS0_PNS_15ObjStatusViewerE`, exportado por `libMWF.so` en `0x29588` (tamaño `0x150`). Es un símbolo **global exportado**, no interno — por eso cualquier `.so` del sistema puede importarlo vía PLT/GOT.

**VERIFICADO**: busqué qué bibliotecas de todo `lib/` (157 `.so`) importan este símbolo (`R_ARM_JUMP_SLOT`). Lo importan exactamente estas 5, y **ninguna otra**:

| Biblioteca | GOT slot | PLT stub |
|---|---|---|
| `libBizFw.so` | `0x57eb4` | `0x29244` |
| `libBizFw2.so` | `0x43ee4` | `0x20588` |
| `libInfraCacheMgr.so` | `0x2df1c` | `0xca40` |
| `libInfraScalarMpr.so` | `0x3d528` | `0x1540c` |
| `libmprctrl.so` | `0x3be2c` | `0xef3c` |

**Dato nuevo clave, no reportado en sesión 17**: `libObj.so` **no** está en esta lista para esta firma concreta — `libObj.so` solo importa la variante *wrapper* `AVBIZ::UNIVERSE::UObjPin::Connect(MWF::ObjPin*, MWF::ObjStatusViewer*, bool)` (GOT `0x102d420`) y `ConnectPinWrapper::Connect(MWF::ObjPin*, MWF::ObjStatusViewer*)` (GOT `0x102d780`), ambas junto a la importación directa de `MWF::ObjPin::Connect` en `0x102dfc4`. Esto **reduce el espacio de búsqueda** del blocker de sesión 17 ("¿quién llama a Connect desde un LifeCycle construido por `TM::createLifeCycles`?") de "todo el stack" a estas 5 bibliotecas concretas — es un avance metodológico real, no solo una repetición de lo ya sabido.

**NO VERIFICADO (límite honesto de la herramienta)**: busqué, en el `.text` completo de las 5 bibliotecas y de `libObj.so`, toda instrucción `bl`/`blx` apuntando literalmente a estos stubs PLT por nombre de símbolo (`grep` sobre `llvm-objdump -d`), y **no encontré ningún `bl` directo** en ninguna de las 6 bibliotecas. Tampoco encontré relocaciones `R_ARM_ABS32` (puntero estático a función, típico de una vtabla o tabla de callbacks) que referencien estos símbolos en ninguna de las 5 importadoras (sí existe una `R_ARM_ABS32` para el wrapper `UObjPin::Connect` en `libBizFw2.so`, offset `0x43728` — un dato de tabla/vtabla, pero para el wrapper, no para `MWF::ObjPin::Connect` directo).

Conclusión honesta: la llamada real a `Connect` casi seguro se produce por **llamada indirecta vía registro** (`blx r3` tras cargar la dirección GOT-relativa con aritmética PIC — `ldr r3,[base,#offset_pequeño]`), un patrón que **`objdump`/`grep` no puede resolver estáticamente** porque el operando no es un literal de dirección completo sino un offset relativo a un registro base cargado en otro punto de la función. Resolver esto requiere análisis de flujo de datos (que Ghidra con análisis completo sí hace, pero el proyecto usa `-noanalysis` deliberadamente). **El blocker de sesión 17 no se cierra**, pero se reduce de forma verificable a 5 bibliotecas concretas en las que seguir buscando con herramientas de flujo de datos.

## 2. Comparación de vptrs: patrón LIRO (`DAT_44020894`) vs. `LifeCycle` real de `libObj.so` (VERIFICADO — son clases/jerarquías distintas)

Pregunta original: ¿el inicializador LIRO de `0x437ebed8` (vptr=`DAT_44020894`) usa el mismo vptr/patrón que el `LifeCycle` de `libObj.so`? **Respuesta: no, son mecanismos distintos, verificado por lectura directa de bytes.**

### 2.1 `DAT_44020894` en LIRO (`av-cam.bin`, verificado leyendo el archivo crudo con offset `vaddr - 0x43541000`)

```
DAT_44020894 (0x44020894) -> 0x43afb3bb   (puntero Thumb, bit0=1)
```

Decompilé la función en `0x43afb3ba` (`scripts/ghidra_dec.sh`):

```c
void candidate_43afb3ba(int param_1, undefined4 param_2) {
    (**(code **)(param_1 + 8))(param_2);
    return;
}
```

Es un **trampolín único y compartido**: no es un array de punteros a función (vtabla real), es una única función que reenvía la llamada al puntero guardado en el propio offset `+8` del objeto (el "payload/descriptor" que cada fila trae de su slot GOT). Es el idioma C clásico de "objeto con un solo campo de función", no C++ polimórfico.

### 2.2 `LifeCycle` real en `libObj.so` (VERIFICADO por desensamblado directo del constructor)

Localicé el constructor real en `libObj.so` en `0x41b6c0`, invocado desde la función que empieza en `0x4195c0` (exactamente la dirección ELF de `TM::createLifeCycles` citada en sesión 17 y en `CONTEXT.md` línea 899) tras un `blx _Znwj@plt` (`operator new(unsigned int)`, asignación real en heap de 0x14 bytes — no una fila estática).

```
41b6d4: ldr r3, [pc, #0x4c]   @ literal pool -> 0x41b724
41b6da: str r3, [r4]         ; vptr = 0xcc6698
```

Leí el literal (`0xcc6698`) directamente del archivo (`.text` de este `.so` tiene `vaddr == file offset`, verificado con `readelf -S`). `0xcc6698` cae dentro de `.rodata` (`0xbc9598`–`0xd91fb2`), **no** en `.data.rel.ro` ni en BSS. Volqué las primeras 4 palabras:

```
vtable[0] = 0x41b605  -> complete-object destructor (libera subobjetos, no `delete` de sí mismo)
vtable[1] = 0x41b649  -> deleting destructor (llama a [0] y luego operator delete)
vtable[2] = 0x41b65d  -> método virtual real: toma un Event*, llama Event::getId(), testmode_debugPrint, setBlogData
vtable[3] = 0x00000000  -> terminador / fin de la tabla (solo 3 slots)
```

Esto **es** una vtabla C++ real estilo Itanium ABI (dtor completo + dtor "deleting" + 1 método virtual), con 3 entradas — consistente con una clase polimórfica pequeña pero genuina, con RTTI.

**Decompilé `vtable[2]` (0x41b65c)**: es un manejador de eventos/logging (recibe un `Event*`, obtiene su Id, hace `testmode_debugPrint` y `setBlogData`) — **no llama a `Connect`**. Cierra, para esta clase concreta, la hipótesis de que `Connect` se invoca desde su único método virtual no-destructor.

### Veredicto Q2/Q7

**DESCARTADO** que el patrón `0x437ebed8`/`DAT_44020894` de LIRO y el `LifeCycle` de `libObj.so` compartan vptr o mecanismo: uno es un trampolín C manual de un solo slot operando sobre filas estáticas de una tabla, el otro es una clase C++ polimórfica real con vtabla Itanium de 3 slots operando sobre objetos de heap. Son **jerarquías de ciclo de vida independientes, sin puente verificado entre ambas** en lo que pude inspeccionar — responde también, con evidencia concreta en vez de solo hipótesis, a la pregunta 7: no encontré ningún puente directo (ni llamada cruzada, ni vptr compartido, ni dato común) entre el patrón LIRO y la arquitectura E/`LifeCycle` de `libObj.so`. Esto es **INFERENCIA fuerte, no prueba de ausencia total** — solo examiné esta vtabla concreta y el inicializador de `0x437ebed8`; no descarté que otras clases LifeCycle de `libObj.so` (hay más de una fila, ver sesión 17: 211 filas de topología) usen vptrs distintos de los 0x14-byte.

## 3. Filas dinámicamente seleccionables del selector de captura LIRO: `0xa0`, `0xc8`, `0xdc`, `0x104`

Pendiente de sesión 18 anterior (`s18-main-init-437ebed8.md`, sección 6). Decompilé las 4 con `scripts/ghidra_dec.sh` sobre el proyecto compartido `silent-liro` (solo lectura).

| Offset fila | Función real | Resultado |
|---|---|---|
| `0xa0` | `0x43b1be37` | **NO VERIFICADO** — Ghidra en modo `-noanalysis` lanza `ContextChangeException: Context register change conflicts with one or more instructions` al intentar fijar el modo Thumb en esta dirección, tanto en invocación normal como forzada (`!0x...`). Esto indica que la dirección cae dentro de una región ya desensamblada en otro modo/alineación por una pasada anterior del proyecto compartido (probablemente solapa el final de la función vecina `0x43b1be01`, fila `0x8c`). No forcé un re-análisis destructivo del proyecto compartido (usado por otros hilos en paralelo) para no arriesgar su estado — decisión deliberada, documentada aquí como limitación, no como hallazgo. |
| `0xc8` | `0x43b1bf04` | **INFERENCIA fuerte**: decompilada íntegra. Switch de 7 casos (`0`–`6`) sobre el resultado de `FUN_43afdf16()`. Caso 0: lógica de reintento/cancelación de petición de captura (strings `Capture_Req_Retry`, `Capture_Cancel`, `Panorama_DEBUG_CAPTURE_START`). Caso 5: inicialización RAW (`RawDevInit_WAIT_IMG_PARAM`, `Stage_Raw.cpp`). Default: rama final que escribe bytes en offsets `+0x23..+0x27` tras `FUN_43ae9226(..., 0x9400, ...)` — igual que la fila `0xb4` ya conocida (metadatos tipo EXIF/lente). **Sin ninguna marca de modo Silent/EFCS.** |
| `0xdc` | `0x43b1bf66` | **INFERENCIA fuerte**: prácticamente **idéntica byte a byte en estructura** a la fila `0xc8` (mismo switch de 7 casos, mismas cadenas, mismo patrón final `0x9400`/offsets EXIF). Difiere solo en variantes menores de generación de código (uso de registros, truncamiento de constantes). **Sin marca Silent/EFCS.** |
| `0x104` | `0x43b1c034` | **INFERENCIA fuerte**: mismo patrón que `0xc8`/`0xdc` en el caso 0 (confirmado por lectura de los primeros ~120 líneas del pseudocódigo: mismas cadenas `Capture_Req_Retry`, `Capture_Cancel`, misma lógica). No decompilé el cuerpo completo de los casos 2–6 por límite de tiempo de esta tanda — **NO VERIFICADO si difiere en el resto**, aunque el patrón de cabecera es indistinguible de las otras dos. |

**Conclusión Q4**: las 3 filas que sí pude decompilar completas (`0xc8`, `0xdc`, y la cabecera de `0x104`) son variantes casi idénticas de **un mismo manejador genérico de etapas de captura** (reintento, cancelación, inicialización RAW, metadatos EXIF al final) — consistente con ser modos de captura normales (quizá burst/panorama/variantes), **no** con un modo electrónico/Silent diferenciado. Ninguna de las filas examinadas (`0xb4` de sesión 18 anterior, `0xc8`, `0xdc`, `0x104` de este hilo) contiene cadena, constante o rama que mencione Silent/EFCS/electronic shutter. La fila `0xa0` permanece sin verificar por la limitación de herramienta descrita arriba.

## 4. Relación de las ~9 tablas de `0x437ebed8` con `ObjCamera`/`ObjEffect`/ciclo de vida de pines (NO VERIFICADO — no completado)

No alcancé a decompilar y clasificar sistemáticamente las ~9 tablas base que itera `0x437ebed8` dentro del tiempo de esta tanda; solo profundicé en la tabla del selector de captura (ya conocida de sesión 17) y en el trampolín común `DAT_44020894`. **No verifiqué** si alguna de las otras ~8 tablas (`DAT_44022970`, `DAT_4402559c`, `DAT_44020100`, `DAT_4401f96c`, `DAT_44022c18`, y las no listadas por brevedad en el documento previo) contiene callbacks relacionados con `ObjCamera`/`ObjEffect`/`ObjStillRecorder`. Esto queda como blocker abierto explícito para continuación, no como hallazgo negativo.

## 5. Fuentes Sony del kernel: ¿algo de IPC/sincronización relevante? (VERIFICADO — nada relevante encontrado, declarado explícitamente)

Grep dirigido sobre `arch/arm/mach-cxd90014` (108 archivos) y `arch/arm/mach-cxd4132` (75 archivos) en `analysis/session18/main/sony-oss-extracted/linux/` buscando `mailbox|ipc|rpmsg|shared.?memory.*queue|message.?queue`: solo coincidencias superficiales por nombre de archivo (`cmpr.c` = compresión de memoria RAM genérica del kernel, no IPC entre subsistemas de cámara; `qemu.c`, `clock.c`, `pcie_setup.c` = soporte de plataforma estándar). **No hay nada relacionado con el IPC propietario entre LIRO/`libObj.so`/`libMWF.so`** — como se esperaba, esa capa es propietaria y vive en espacio de usuario (los `.so` de `firmware/extracted/fw321/.../lib/`), no en este paquete GPL de plataforma base. Declarado explícitamente: **esta fuente no aporta nada al blocker de IPC**, no es una laguna de búsqueda sino una ausencia real confirmada por la naturaleza del paquete (BSP genérico CXD90014/CXD4132, sin drivers de cámara).

## 6. `DAT_44020894` como clase (VERIFICADO — no es una vtabla, no hay "clase" que inspeccionar)

Resuelto en la sección 2.1: `DAT_44020894` no apunta a una vtabla ni a una clase C++ con RTTI — es directamente la dirección de una única función trampolín (`param_1+8` dispatch). No hay más "métodos" que inspeccionar porque no hay array de punteros, solo ese único puntero de función compartido por las ~9 tablas que inicializa `0x437ebed8`.

## 7. Puente entre arquitectura E y patrón LIRO (ver sección 2, veredicto)

Respondido en la sección 2: **DESCARTADO** un puente directo verificable con la evidencia disponible en esta tanda; **NO VERIFICADO** de forma exhaustiva (solo se examinó una vtabla LifeCycle de las potencialmente múltiples en `libObj.so`).

## 8. Licencias de los paquetes OSS tocados (VERIFICADO)

- **Linux kernel 3.0.27 (Sony, `mach-cxd90014`/`mach-cxd4132`)**: `COPYING` en la raíz del tarball extraído confirma **GNU GPL v2**, con la nota estándar de que no cubre programas de usuario que usan el kernel vía syscalls normales. Sin excepciones ni cláusulas adicionales de Sony detectadas en el `COPYING` mismo.
- **iproute2**, **iptables**: `COPYING` presente en ambos — **GPL v2** (verificado por presencia de archivo, no releí el texto completo línea por línea).
- **wpa_supplicant**: `COPYING` presente — licencia propia tipo BSD (wpa_supplicant usa dual BSD/GPLv2 según versión; no verifiqué cuál de las dos variantes aplica en este `COPYING` concreto, **NO VERIFICADO** el detalle exacto).
- **libpng**: `LICENSE` + `MODULE_LICENSE_BSD_LIKE` en la raíz del tarball (sin extraer, solo listado con `tar -tzf`) — licencia libpng, permisiva estilo BSD. **No extraído ni leído el texto**, solo confirmada la presencia del archivo por nombre.
- **webkit**: **NO VERIFICADO** — el tarball (27 MB) no estaba extraído y no lo extraje en esta tanda por límite de tiempo; no encontré `LICENSE`/`COPYING` en el listado de nivel superior con `tar -tzf`, lo cual no implica ausencia (WebKit upstream usa públicamente una mezcla de BSD y LGPL 2/2.1 por archivo, pero no confirmé esto contra el tarball concreto de Sony).

**Restricción relevante para este proyecto**: ninguna de estas licencias GPL/BSD impone restricciones sobre el análisis estático de ingeniería inversa que este proyecto ya realiza (no se distribuye código derivado, no se modifica y redistribuye el kernel). El riesgo legal real de este proyecto sigue siendo el de la parte **propietaria** (`libObj.so`, `libMWF.so`, LIRO), no estos paquetes GPL/BSD de plataforma base.

## 9. Qué no pude verificar por falta de tiempo/herramientas (honesto)

- El sitio exacto (instrucción concreta) que llama a `MWF::ObjPin::Connect` dentro de las 5 bibliotecas identificadas en la sección 1 — reducido el espacio de búsqueda, pero no resuelto el blocker.
- El contenido completo de la fila `0xa0` (`0x43b1be37`) del selector — bloqueado por conflicto de contexto en Ghidra `-noanalysis`, no forzado para no arriesgar el proyecto compartido.
- El cuerpo completo (casos 2–6) de la fila `0x104` (`0x43b1c034`).
- Clasificación de las ~8 tablas restantes que inicializa `0x437ebed8` (solo se examinó la del selector de captura).
- Si `libObj.so` tiene más de una clase "LifeCycle" con vptrs distintos — solo se inspeccionó la instancia construida desde la función en `0x4195c0`.
- Texto exacto de las licencias de iproute2/iptables/wpa_supplicant (confirmada presencia de archivo, no releído el contenido íntegro) y licencia real de webkit.tar.gz (no extraído).

## 10. Riesgo/limitación que el usuario debe conocer

Todo lo anterior es análisis estático de direcciones y bytes; **ninguna fila, vtabla o trampolín examinado contiene evidencia de un modo de disparo electrónico por S2** — al contrario, cada pieza nueva examinada en esta tanda (filas dinámicas del selector, vtabla real de `LifeCycle`) refuerza el patrón ya visto en sesiones anteriores: son manejadores de captura mecánica convencional (retry, cancelación, RAW init, metadatos EXIF) sin marca Silent. La reducción del blocker de `Connect()` a 5 bibliotecas concretas es un avance de alcance, no una prueba de que esas bibliotecas efectivamente activen algo relevante para S2 — podrían ser rutas completamente ajenas (conexión de pines de otros subsistemas, no relacionados con el obturador). No se debe interpretar ningún hallazgo de este documento como evidencia a favor de que `SilentShutter` o cualquier mecanismo equivalente funcione en este hardware.
