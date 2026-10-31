# E26-R30 — Cierre de Fase A (residuo ARM7), acotación de Fase B (0x32) y avance de Fase C (frontera Done)

Fecha: 30-10-2026. Continúa [E26-RECOVERY](e26-recovery.md) Fases A/B/C y [R5](e26-r5-loader3-servicio.md),
[R16](e26-r16-ldec-hardware-audit.md), [R17](e26-r17-arm7-ldec-segment-analysis.md),
[R27](e26-r27-arm7-isr-geometria.md). **Solo análisis estático offline**: sin encendido, sin
conexión, sin escritura a la cámara. Se reutilizó el respaldo privado existente
`analysis/camera-dumps/nand-20261020/dev_nflasha1.bin` (ya capturado el 20-10-2026, no una
nueva extracción de la cámara) para releer su CRAMFS; no se tocó `camera-dumps` ni
`exp2-session-log.jsonl`.

## 1. Fase A — CERRADA (auditoría de contradicciones, sin trabajo nuevo de ARM7)

El bloque "Fase A parcial" de [PENDIENTES](../PENDIENTES.md) y la Fase A de
`e26-recovery.md` (29-10-2026) quedaron **desactualizados por R16/R17/R27** (30-10-2026,
misma jornada, posteriores): esos informes ya trazaron exhaustivamente qué hace el ARM7
con el residuo de 256 B. Resultado ya establecido (no se repite el análisis):

- El campo `trabajo+0xc` (origen del residuo `offset & 0x1ff`) se **escribe una vez** en el
  registro LDEC `+0xc` y **no lo lee ninguna instrucción** del ARM7 en la ruta op 0 (R17 §4-6,
  prueba `test_op0_never_reads_job_plus8`).
- Las 17 operaciones restantes del despachador comparten la misma base SRAM de trabajo que
  op 0, pero ninguna llama al LDEC (`0xf2903000`); solo 3 funciones del ARM7 tocan ese
  periférico (R17 §1.2) y los comandos NAND concretos de esas 17 operaciones no se
  clasificaron (R27 §3, límite declarado).
- **Decisión C** (R17 §14): semántica parcialmente reconstruida. Qué hace el **silicio** del
  LDEC con esos primeros 256 B es indecidible desde software sin acceso físico al chip.

No hay nada más que trazar en software sobre el "residuo leído por ARM7": el límite actual
es de hardware, no de cobertura de análisis. Pendientes `E26-R5-L3`/`E26-R7-D-TPZL-ARM7`
deben leerse ya con este cierre, no como abiertos.

## 2. Fase B — acotada: no describe un evento observado en este incidente

Se releyó el respaldo real de la cámara para confirmar que los binarios/scripts citados en
Fase B siguen siendo los mismos (no una suposición):

```
usr/lib/libsenupdater.so  sha256 3683de6c998876e67c6e16b5137d65dd7c8fd6ba207ade4726bb950d2d1e2e1d
usr/bin/mf                sha256 85590243764cbb5de11ae576c7c7a5b96e20da787c2c860b3532148321799aeb
usr/bin/us_error.sh       (script; llama blink_error $1 y sale 0)
usr/bin/common.src        (define blink_error: uc_portctl.elf -b $1 -n 0)
```

(extracción: FAT12 → `mcopy`/`mdir` sobre `dev_nflasha1.bin`; CRAMFS → `fakeroot fsck.cramfs
--extract` porque el filesystem contiene nodos de dispositivo que `fsck.cramfs` sin privilegios
no puede crear). Los tres hashes coinciden exactamente con los citados en `e26-recovery.md`
Fase B: es el mismo respaldo, no una reconstrucción.

**Límite que ya estaba pero no se había dicho con esta claridad:** el usuario informa que el
actualizador llegó a mostrar **100 % y Done**. La cadena de propagación de un byte de error
(`ApiException(0x3000c,…)` → FIFO2 → `mf` → `us_error.sh`/`blink_error`) solo se activa si
`system()` devuelve un estado de salida distinto de cero **durante la actualización**; un
Done gráfico implica que esa cadena no se disparó (o si se disparó, no llegó a bloquear la
finalización — ver §3). Por tanto, la investigación del byte 0x32 sigue siendo una
exploración de la arquitectura de reporte de errores del actualizador, **no una traza de un
evento documentado de este incidente**. Se mantiene como "NO hay evidencia de que el byte
0x32 del FIFO se haya observado físicamente" (cita literal ya presente en Fase B); R30 no
añade esa evidencia porque no existe en los archivos disponibles.

## 3. Fase C — avance real: `UpdaterBody::Execute` decompilado con símbolos completos

El respaldo contiene `libupdaterbody.so` con símbolos de depuración (no solo direcciones):
esto permite completar lo que R3/R5 dejaron con direcciones sueltas. **BINARIO, Ghidra 12.1.4,
mismo archivo que Fase B** (`sha256 8d1dc242…`, idéntico en `firmware/extracted/fw321/...` y en
el respaldo real de la cámara — confirma que la copia de archivo usada en todo E26 es la que
estaba en la cámara).

`Updater::UpdaterBody::Execute` (`0x1f4c8`), pseudocódigo íntegro con nombres de clase:

1. **Desempaquetado por archivo (bucle principal):** por cada `PackedFileHeader` del paquete,
   `BodyInformation::GetCurrentKeyTag()` selecciona el `KeyTag` según el índice del archivo
   empaquetado y llama a su método virtual `+0xc` (verificación/escritura del archivo). Si ese
   método devuelve 0 (fallo) y no se llegó al fin de flujo (`Parse` código 3), `Execute`
   **lanza `ApiException(0x30002)` de inmediato** — no hay ruta hacia "Done" con un archivo
   empaquetado corrupto. Esto incluye previsiblemente la escritura de `part_image`
   (`nflasha3`) y de `darwin_core`, que viajan como archivos empaquetados del mismo flujo.
2. **Frontera de hilos y Done:** al agotarse el flujo (`Parse` = 3), `Execute` llama
   `XmlConfigHandler::Join()` (espera los plugins con `thread="yes"`: `ca`, `darwin`, `prfile`),
   comprueba `StopFlag` y luego `XmlConfigHandler::HasError()`.
   - **Si `HasError()==0`:** llama `BuildInPlugin::EndUpdate()`, aplica una excepción
     específica para la cadena `"J1"` (variante de modelo/región, no analizada aquí),
     actualiza `Backup.bin`/`Backup.bak` bajo condiciones, y **solo entonces** llama
     `FlagFirmwareInformationHandler::CompleteUpdate()` (que en R3 ya se había mostrado que
     limpia `mode1/2/3/5/6` y crea `CompleteFlagFile`). Retorna 1.
   - **Si `HasError()!=0`:** `Execute` retorna 0 **sin excepción y sin `CompleteUpdate()`**:
     no limpia las banderas de modo ni corrige el backup. (Qué hace el llamador del host con un
     retorno 0 frente a Done no se trazó aquí — pendiente nuevo, ver §5.)
3. **`XmlConfigHandler::HasError()`** (`0x2370c`) no es un cálculo local: delega a un objeto
   agregador en `this+0x14` vía su vtable `+0x14` (lanza `ApiException(0x3001a)` si ese
   puntero es nulo). **`ThreadPlugin::HasError()`** (`0x23c42`) es más simple: devuelve un
   campo booleano ya fijado en `this+0x48`, puesto por el propio hilo del plugin al terminar.
   Esto confirma la arquitectura de dos vías de error ya intuida en Fase B: fallos síncronos
   (un archivo empaquetado, un `BuildInPlugin` no threaded) lanzan excepción inmediata;
   fallos de plugins con hilo (`darwin`, `ca`, `prfile`) solo fijan una bandera que se
   consulta recién en el `Join`/`HasError` de cierre.
4. **Verificación post-escritura de `part_image` (hallazgo nuevo, no documentado antes):**
   `config.xml` asocia `part_image_sum/part_image.sum` únicamente con
   `us_crc32sum.sh param="part_image image"` (sin script de "firmup" propio — a diferencia de
   `front_sum`/`darwin_sum`/`loader_sum`, que sí tienen un escritor dedicado). Leído completo,
   `us_crc32sum.sh` en modo `image` fija `TARGET_DIR=/` y ejecuta `uc_crc32sum.elf -s -c
   $SUM_FILE` **desde la raíz del sistema de archivos real**, no desde el directoro de
   extracción (`$EXTRACT_ROOT`) que usan los demás modos. Es decir: si `part_image.sum` lista
   rutas de dispositivo (p. ej. `/dev/nflasha3`), este paso relee la partición ya escrita y
   compara su CRC32 contra el valor de referencia del paquete, con error LED `0x81`
   (`getledval.elf`) si no coincide. **Límite:** `part_image.sum` se genera dentro del
   paquete FDAT en tiempo de empaquetado y no está presente de forma estática en
   `updater.img`; no se pudo confirmar aquí que sus entradas sean rutas de dispositivo y no
   copias en `$EXTRACT_ROOT` — **INFERENCIA, no demostrado**, pendiente nuevo (§5).

### Lectura para la recuperación

Si la inferencia del punto 4 es correcta, el hecho de que el usuario viera **Done** implica
que, en el momento de la actualización, el contenido escrito en `nflasha3` coincidía con el
CRC32 de referencia del paquete 3.25 — es decir, la escritura NAND en sí no se corrompió de
forma detectable por esa vía. Esto **no descarta** la anomalía TPZL (residuo 256 B / un
segmento de 64 KiB en los bloques 0/48/57), porque esa comprobación es un CRC32 de bytes, no
una simulación del LDEC/ARM7 en tiempo de arranque: una imagen "bien escrita y bien
empaquetada" según el actualizador puede seguir siendo una imagen que el **hardware** LDEC no
descomprime igual que el formato de 16×4 KiB universal de Sony. Esto es consistente con, y no
sustituye, la Decisión C ya cerrada en R16/R17: la causa más probable sigue estando en la
frontera hardware de Loader3/ARM7 en tiempo de arranque, no en la escritura del actualizador.

## 4. Verificación de continuidad

Hashes de `libupdaterbody.so`, `libsenupdater.so`, `mf`, `us_error.sh`, `common.src`
re-extraídos en esta sesión coinciden exactamente con los citados en `e26-recovery.md`
Fase B (§4 de este informe). No se alteró ningún archivo de `analysis/camera-dumps/`.

## 5. Pendientes nuevos

- **E26-R30-SUMCONTENT** (NO DEMOSTRADO): confirmar si `part_image.sum`/`darwin.sum` dentro
  del FDAT 3.21/3.25 listan rutas de dispositivo (`/dev/nflasha3`) o copias en
  `$EXTRACT_ROOT`; sin esto, el hallazgo del §3.4 es una inferencia del script, no una
  verificación post-escritura demostrada. Fuente: descomprimir el FDAT 3.21/3.25 ya
  disponible localmente (`analysis/e25-27/artifacts/package-3.25/firmware_packed.fdat`) y
  listar el contenido de esos `.sum` sin instalar ni ejecutar nada.
- **E26-R30-HOSTRET0** (NO DEMOSTRADO): qué hace el adaptador/host del PC cuando
  `UpdaterBody::Execute` retorna 0 (HasError sin excepción) frente a cuando retorna 1 (Done):
  ¿muestra error, cuelga, o podría mostrar Done igual? Sin esto no se puede descartar que un
  fallo de hilo silencioso (p. ej. en `darwin`) coexista con una UI que no lo refleja.
- Cierran con este informe (reclasificar en PENDIENTES): `E26-R5-L3` (parte ARM7),
  `E26-R7-D-TPZL-ARM7`.

## 6. Pruebas y validación

Sin herramienta nueva de software del repo (solo lectura/decompilación); no se añadió
código, por lo que no aplica suite de tests nueva. `ruff`/`mypy`: sin cambios en `scripts/`.
Reindexado pendiente vía `knowledge-maintenance` tras este commit.
