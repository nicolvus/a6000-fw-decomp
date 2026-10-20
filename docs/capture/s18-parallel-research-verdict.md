# Veredicto integrado — sesión 18 (investigación paralela: 4 Claude + 4 Codex + principal)

Clasificación obligatoria: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO. **No se afirma en ningún punto que SilentShutter funcione.**

## 1. Configuración real verificada

| Agente | Rol | Modelo pedido | Modelo real | Esfuerzo pedido | Esfuerzo real | Incidente |
|---|---|---|---|---|---|---|
| Principal | S2/RelMgr + inicializador LIRO + inventario Sony OSS | — | Sonnet 5 | — | — | Conflicto de recursos con Ghidra compartido (resuelto pasando a `llvm-objdump`) |
| Claude A | LifeCycle/MWF | sonnet | **Sonnet 5 confirmado** | medium | **no verificable desde dentro del propio agente** (limitación de visibilidad declarada, no discrepancia) | ninguno |
| Claude B | CameraSequence/Android | sonnet | **Sonnet 5 confirmado** | medium | **bajo (confirmado, igual que sesión 17)** | Intentó autocorregir con `set_session_effort`; la herramienta lo bloqueó — declarado, no oculto |
| Claude C | RelMgr/CaptureStart | sonnet | **Sonnet 5 confirmado** | medium | **medium confirmado** | Excepción de Ghidra por dirección Thumb impar — resuelta y documentada |
| Claude D | Topologías dinámicas | sonnet | **Sonnet 5 confirmado** | medium | **medium confirmado** | ninguno |
| Codex E | YC de ObjCamera | gpt-5.6-terra/medium | GPT-5 (Codex), flags de lanzamiento correctos | medium | **no expuesto por el runtime al propio agente** (misma limitación que Claude A) | ninguno |
| Codex F | SDF/transformación YC | gpt-5.6-terra/medium | GPT-5 (Codex) | medium | no expuesto | ninguno |
| Codex G | FEA/DMM + cruce Sony OSS | gpt-5.6-terra/medium | GPT-5 (Codex) | medium | no expuesto | ninguno |
| Codex H | MPR/DCF | gpt-5.6-terra/medium | GPT-5 (Codex) | medium | no expuesto | ninguno |

**Límite de verificación de esfuerzo numérico declarado honestamente**: 6 de los 8 agentes no pudieron confirmar desde dentro de su propia ejecución el nivel de esfuerzo numérico real (no es un dato expuesto al modelo en su contexto). Los comandos de lanzamiento (`Agent` tool con `effort: "medium"` para Claude A-D; flags `-c model_reasoning_effort="medium"` explícitos para Codex E-H) especificaron correctamente "medium" en los 8 casos — no hay evidencia de que se haya usado un nivel distinto salvo en **Claude B, que repitió el mismo patrón de sesión 17** (esfuerzo bajo autoinformado, sin que el agente pueda explicar por qué el orquestador lo configuró así).

**Límite de recursos respetado**: exactamente 4 Claude + 4 Codex, ningún agente lanzó subagentes propios (confirmado explícitamente por los 8). Un conflicto real de recursos (Ghidra `-noanalysis` compartido, `ContextChangeException`) ocurrió entre el hilo principal, Claude A y Claude C al decompilar simultáneamente direcciones cercanas de la misma tabla — resuelto en los tres casos pasando a `llvm-objdump` puro o restando 1 al puntero Thumb impar, sin dañar el proyecto compartido.

## 2. Verificación cruzada de hallazgos críticos (principal, independiente)

| Hallazgo | Agente origen | Verificación independiente del principal | Resultado |
|---|---|---|---|
| `GOT[0x44020894] = 0x43afb3bb` (trampolín único de LIRO, no vtabla C++) | Claude A | Lectura cruda de `av-cam.bin` en el offset `0x44020894 - 0x43541000` | **CONFIRMADO** |
| `sdc.c`/`sdc-zqcal*.c` de `mach-cxd4132` son calibración de **LPDDR**, no controlador SD | Codex G/H | Lectura directa de `regs-dmc.h`: registros `SDC_COMMAND1/2` documentados explícitamente "for LPDDR1"/"for LPDDR2" | **CONFIRMADO** — corrige mi propia hipótesis inicial del inventario |
| Las 4 filas dinámicas (`0xa0,0xc8,0xdc,0x104`) son variantes casi idénticas de la fila `0xb4`, sin marca Silent | Claude A + Claude C (independientes entre sí) | Ambos hilos llegaron, por métodos ligeramente distintos (Ghidra vs. diff textual completo), a la misma conclusión sin coordinarse directamente — convergencia cruzada entre dos agentes | **CONFIRMADO por duplicado** |
| Tabla de topología `.rodata 0xcc4210`, filas `0x2a`/`0xb4` con valores `[0,6,9,1,1,0xb,0,0]`/`[0,6,0x35,1,2,0xb,0,0]` | Claude D | Coincide exactamente con lo ya registrado en `CONTEXT.md` (verificación de reproducibilidad, no de novedad) | **CONFIRMADO (reproducible por segundo método)** |
| No existe `dmm.ko` ni interfaz DMM Sony literal en el kernel OSS | Codex G | Coincide con la búsqueda independiente que ya hizo el principal en `drivers/{mmc,mtd,video,media}` (sesión 18, fase de inventario) — Codex G amplió a todo el árbol y confirmó la ausencia total | **CONFIRMADO, ampliado** |

**Sin contradicciones técnicas** entre los 8 hilos y el principal. Un solo caso de **corrección cruzada real** (sdc.c), documentado arriba y ya corregido en `sony-oss-inventory.md`/`.json`.

## 3. Hallazgos nuevos consolidados por rama

### Principal
- Base de carga LIRO confirmada: `0x43541000` (corrige un desliz de transcripción del resumen de sesión 17, no un error del proyecto).
- Inicializador maestro `0x437EBED8`: resuelve la tabla del selector de captura (antes creída BSS irrecuperable) vía punteros GOT estáticos — cierra metodológicamente ese blocker. Técnica reutilizada por Claude A/C/D.
- Las 15 filas de esa tabla son trampolines de 4 bytes hacia implementaciones reales (`~0x43b1c2xx`–`0x43b1c3xx`).
- Único hallazgo "Silent" en LIRO es de sincronización de **audio**, no del obturador — DESCARTADO como pista.

### Claude A
- Reduce el blocker de `Connect()` (sesión 15-17) a 5 bibliotecas candidatas concretas (`libBizFw.so`, `libBizFw2.so`, `libInfraCacheMgr.so`, `libInfraScalarMpr.so`, `libmprctrl.so`) — `libObj.so` queda descartado como importador directo.
- Confirma con evidencia dura (vtabla real de 3 slots, Itanium ABI) que `LifeCycle` de `libObj.so` y el trampolín de LIRO son mecanismos de clase completamente distintos.
- Decompiló 3 de las 4 filas dinámicas restantes: variantes de un manejador genérico de captura (retry/cancel/RAW/EXIF), sin marca Silent.

### Claude B
- **Corrige sesión 17**: el puente `CameraSequence→ScalarDaemon` usa una librería propia `libsdcom.so` ("SDCom"), no Binder. Binder solo aparece en el tramo convencional (`libcameraex_client.so→libbinder.so`).
- Reafirma con firmeza: cero conexión entre S2 y `CameraSequence` en cualquier código real revisado.
- Veredicto de arquitectura **sin cambios: A > E > P ≈ E2**.

### Claude C
- Localiza `0x43807f4c` como el llamador real de `0x43807d80` (dispatcher denso de dominio local `0x100..0x207`).
- El puente entre ese dominio y el dominio `0x3011/0x3013/0x3015`/cola `0x40193` **sigue sin probarse** — blocker de sesión 17 reducido en alcance, no cerrado.
- Confirma (vía diff textual completo) que las 4 filas dinámicas son semánticamente idénticas a la `0xb4`.
- Kernel Sony: solo GPIO genérico sin `request_irq` — sin evidencia de IRQ de teclado específico.

### Claude D
- Confirma por método independiente (objdump crudo, no Ghidra) el hallazgo de sesión 17: ningún llamador común entre `createLifeCycles` y `Connect`.
- Aclara que la técnica "inicializador GOT→BSS" de LIRO **no tiene equivalente** en `libObj.so`: la tabla de topología ya es `.rodata` estática; el problema real (ObjId 53→clase) es de *registro dinámico* en runtime, no de inicialización estática.
- Re-deriva byte a byte, por segundo método, las filas `0x2a`/`0xb4` de la tabla de topología — coinciden con `CONTEXT.md`.

### Codex E
- Confirma superficie propietaria real de memoria YC en `libObj.so`: `AvbbcPhycMem`, DMM (`DmmCh::*`, `DmmAccessPLA::*`), metadatos `C_DataflowInfra_StdData_YC`.
- El kernel OSS no contiene nada de esto — es contexto de plataforma DMA genérica, sin enlace estático a `ObjCamera`/YC.

### Codex F
- Reconstruye con mayor precisión el contrato YC/SDS: raster `0x50b3f` + SDS `0xe0b00` (bloque de control de `0x800` B, no píxeles), vía `YcSdsAcsr`.
- El acelerador CMPR del kernel (`mach-cxd90014/cmpr.c`) es LZPART genérico — DESCARTADO como evidencia del formato YC/JPEG real.

### Codex G
- Confirma que `ashmem` es el único mecanismo de memoria compartida presente en este kernel 3.0.27 (ION/DMA-BUF no existen en esta versión) — DESCARTADO cualquier DMM/`dmm.ko` Sony literal.
- Hallazgo sin explicación (**NO VERIFICADO, declarado explícitamente, no forzado**): dispositivos UDIF `ldec` y `mia` con IRQ/canal DMAC registrados en `mach-cxd4132/udif/platform.c`, sin controlador fuente ni semántica documentada en el OSS — podrían o no relacionarse con imagen; no hay evidencia para afirmarlo.

### Codex H
- **Corrige la hipótesis inicial del inventario** (ver §2): `sdc.c` es LPDDR, no SD.
- Confirma FAT/VFAT real y habilitado en los defconfigs Android CXD90014, con `fsync`/`fdatasync` disponibles en el VFS.
- `libmpr.so` tiene cadenas DCF/DCIM reales (`RegisterDCFContent`, `GetDCFContentAttribute`, patrón `DSC0%04ld.JPG`) pero la secuencia semántica completa de escritura/catálogo sigue sin reconstruirse por desensamblado — la lógica DCF es propietaria de MPR, no del kernel GPL.

## 4. Qué aportaron realmente los archivos oficiales de Sony al proyecto SilentShutter

**Confirmaciones de plataforma (no de la pieza propietaria)**:
- Kernel real Linux 3.0.27 con SoCs propios Sony (`mach-cxd90014`, `mach-cxd4132`), arrancando Android (defconfigs `cxd90014_android_*`).
- Mecanismo de memoria compartida real: `ashmem` (ION/DMA-BUF no existen en esta versión de kernel).
- Sistema de archivos real para el medio extraíble: FAT/VFAT, con `fsync`/`fdatasync` disponibles.
- Integración de caché PL310 específica de plataforma CXD4132.

**Hallazgos nuevos que SÍ cambiaron una conclusión previa**: ninguno sobre el mecanismo de disparo S2 o sobre el obturador; **uno sobre infraestructura** (corrección de que `sdc.c` es LPDDR, no SD — un detalle de inventario propio, no de sesión 17).

**Información genérica sin aplicación directa**: la inmensa mayoría del árbol (DMA ARM genérico, coherencia de caché genérica, VFS, `completion`/`kref` genéricos) — útil como contexto de analogía conceptual, nunca como prueba de comportamiento propietario.

**Componentes no publicados (confirmado por ausencia, no por omisión de búsqueda)**: DMM, FEA, MPR, RelMgr, CaptureManager, ObjCamera/ObjEffect/ObjStillRecorder, CameraSequence/CameraEx/ScalarDaemon/SDCom, y cualquier driver de sensor/ISP/JPEG reconocible — **nada de la pieza propietaria de cámara está en este código GPL/BSD**, confirmado de forma independiente por 3 ramas distintas (principal, Codex G, Codex H) sin contradicción entre ellas.

**Veredicto de la pregunta obligatoria**: los archivos Sony OSS **no aportaron evidencia sobre FEA, DMM ni el pipeline fotográfico** — se declara explícitamente, tal como exigía el encargo, y la investigación continúa por las rutas de desensamblado ya identificadas (bloqueo de `Connect()`, dominio `0x3011`/`0x40193`, filas restantes de la tabla LIRO).

## 5. Criterios de éxito (continuación de sesión 17)

1. **¿Camera→Effect→Recorder alcanzable?** Sin cambios: el bloqueo de control sigue debilitado (sin arbitraje activo), sin nuevo bloqueo ni nueva vía encontrada.
2. **¿YC de Camera convertible a EncodeStill?** Más caracterizado (contrato raster+SDS, superficie DMM/AvbbcPhycMem confirmada), pero el formato real y el enlace PlayData↔ObjCamera siguen **NO VERIFICADOS**.
3. **¿CameraSequence ofrece ruta más corta?** Sin cambios de fondo; corregido el mecanismo de enlace (SDCom, no Binder), pero S2 sigue sin ninguna conexión.
4. **¿Cuándo es seguro liberar el buffer / cómo concluye la escritura?** Sin avance: ningún liberador DMM real localizado; cadena DCF completa sigue sin reconstrucción por código fuente (propietaria de MPR).

## 6. Veredicto final de arquitecturas

**A > E > P ≈ E2 — sin cambios respecto a sesión 17.** Ningún hallazgo de sesión 18 (ocho ramas + principal + fuentes oficiales Sony) debilita ni fortalece sustancialmente este orden. Los avances son de **caracterización** (más detalle sobre mecanismos internos, dos blockers reducidos en alcance) y de **corrección** (SDCom≠Binder, sdc.c≠SD), no de **viabilidad**.

## 7. Próximo bloqueo concreto para la siguiente sesión

1. Cerrar el bloqueo de `Connect()` dentro de las 5 bibliotecas identificadas por Claude A, usando análisis de flujo de datos (no solo desensamblado crudo).
2. Probar o refutar el puente entre el dominio `0x100..0x207` (Claude C) y el dominio `0x3011/0x40193` — es ahora el blocker más concreto y mejor delimitado de toda la investigación.
3. Decompilar las 10 filas restantes de la tabla de 15 de LIRO (offsets no dinámicamente seleccionados).
4. Identificar la clase real de ObjId 53 (fila `0xb4` de `libObj.so`) por el mecanismo de auto-registro, no por tabla de constructores (que no existe para este caso).

No se afirma que SilentShutter funcione.
