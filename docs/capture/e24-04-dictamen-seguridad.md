# E24-04 — Dictamen de seguridad y recuperabilidad ante un nuevo flasheo persistente de Darwin (27-10-2026)

Sesión 100 % offline: no se conectó ni reinició la cámara, no se emitió ningún comando USB, no se escribió firmware, NAND, NVRAM ni RAM, y no se preparó ningún FDAT. Evidencia leída íntegra: [E24-01](e24-01-arranque-recuperacion.md), [E24-02](e24-02-protocolo-actualizacion-darwin.md), [E24-03](e24-03-auditoria-recuperacion-usb.md), [custom-fw-recovery-and-install](custom-fw-recovery-and-install.md), [darwin-via-actualizacion](darwin-via-actualizacion-2026-10-26.md), [registro-pruebas-camara](registro-pruebas-camara.md) (T001–T039), [PENDIENTES](../PENDIENTES.md) y `AGENTS.md`. Las 26 pruebas E24-01..03 se re-ejecutaron hoy y pasan; la única comprobación nueva sobre binarios está en §7.

Candidato que motiva el dictamen: un FDAT 3.24 que anule el rearme (E23: primitivas `0x1fe50/0x1fe86/0x1feb6` y comprobaciones de leva), con recuperación 3.25. **No existe aún** (ni parche ni FDAT).

## 1. Resumen ejecutivo

**Veredicto: NO hay evidencia técnica suficiente para autorizar un nuevo flasheo persistente de Darwin.** Es un límite de evidencia, no una imposibilidad demostrada.

1. **Lo que está probado** es estrecho: con Darwin sano (energía, `InitCom`, `Upd` y arranque propio intactos) la cámara acepta un FDAT con `darwin_core` distinto y lo arranca (T024, 3.21→3.22, un parche de 7 bytes en la compuerta de bobinas). Y el FDAT de recuperación 3.23 es íntegro, trae el core original y se reconstruye bit a bit.
2. **Lo que no está probado** es lo que decide el riesgo: ninguna recuperación de un Darwin defectuoso, ninguna instalación 3.22→3.23, ninguna vía independiente de la aplicación Darwin. De las diez familias de fallo analizadas, **solo la A (mecánica rota con Darwin vivo) tiene una ruta de software plausible; ninguna tiene ruta demostrada**, y en D, E, F, G y H la ruta de software no existe o depende de código del arranque que nunca se ha visto.
3. **La aceptación del riesgo por el usuario no cambia el estado técnico** de ninguna condición. M14 sigue en FAIL aunque el usuario acepte.
4. **Un respaldo no resuelve el riesgo.** El respaldo de NVRAM (único restaurado en hardware) y el FDAT 3.23 existen, pero ambos se instalan por el actualizador, que depende de Darwin (E24-01). Una NAND volcada no se puede escribir de vuelta por software.
5. **Las alternativas menos persistentes no son seguras por defecto.** Una modificación persistente de LIRO/`nflasha3/5/7` usa el mismo actualizador y, si deja sin arrancar el sistema principal, también cierra la entrada por software (F6 de E24-03). Lo que sí tiene recuperación demostrada es lo **volátil** en RAM del BIONZ (T029, T037: apagado completo, con una vez batería fuera).
6. **La ingeniería inversa estática puede y debe continuar**; el hueco que más pesa es que la lista «no tocar» de M6 no está cerrada (E24-02b abierto, §3 D).

Riesgo si se flashea igualmente, tal como está la evidencia: la peor consecuencia (Darwin vivo pero sin entrar a `Upd`, o sin `DD_ON*`) no tiene salida por software y solo la tendría por el puerto de descarga del MCU (`CN4906`, no montado), que exige abrir la cámara, algo que el usuario descartó (F4/F5). No se estima una probabilidad: no hay base para ello.

## 2. Matriz M1–M14 auditada

Estados: PASS / FAIL / NO DEMOSTRADO. Clase: **I** = integridad de archivos y aceptación formal; **R** = recuperación real (que la cámara pueda volver a un estado bueno). «Offline» = comprobable sin cámara.

| # | Condición | Estado hoy | Evidencia | Consecuencia si no se cumple | Obligatoriedad / clase | Offline | Acciones para resolverla |
|---|---|---|---|---|---|---|---|
| M1 | Recuperación estrictamente mayor que el FDAT de prueba y la instalada; nunca 9.99 | **FAIL** frente al candidato 3.24 (3.23 < 3.24); PASS frente a lo instalado (3.23 > 3.22) | Guard medido con 3.21: acepta solo mayores (3.20/3.21 `Invalid version`, 3.22/9.99 aceptadas); [custom-fw](custom-fw-recovery-and-install.md) | El FDAT de recuperación es rechazado por el actualizador y deja de ser recuperación (J) | Obligatoria · I (aceptación formal) | Sí | Reempaquetar la recuperación como ≥3.25 con `fwtool pack` antes de cualquier prueba. La versión se guarda en BCD (3.23 → menor `0x23`): cada prueba consume un número; tope 3.99 (INFERENCIA del formato). 9.99 cierra la vía |
| M2 | Guard medido con la versión instalada | **NO DEMOSTRADO** | Regla medida solo con 3.21; para 3.22 es inferencia | Rechazo del 3.23 el día que se necesite, sin otra alternativa | Obligatoria · I | **No** (exige conectar). Parcial: leer la comparación de versión en `libupdaterufp.so` | `fdat_guard_probe.py` (solo chequeo) con permiso para conectar; o confirmar la comparación por desensamblado |
| M3 | FDAT de recuperación íntegro y reproducible | **PASS** | `test_e24_03_recovery.py` (8/8 hoy): reconstrucción byte a byte, hashes, CRC | Paquete inservible | Obligatoria · I | Sí | Ninguna. Límite: el mismo `fwtool` empaqueta y verifica |
| M4 | Core de recuperación = original y `darwin.sum` coincide | **PASS** | `darwin_core.bin` `5f2be06d…`, CRC `9ff7148c`; `darwin.sum` coincide | Restaurar un core que no es el original | Obligatoria · I | Sí | Ninguna |
| M5 | FDAT de prueba difiere del oficial solo en lo previsto | **NO DEMOSTRADO** (no hay candidato) | Existe el patrón (`test_type0_fdat_differs_only_in_darwin`) | Cambios involuntarios en `nflasha3/5/7` o en el empaquetado | Obligatoria · I | Sí, con candidato | Diff por miembros del tar y por bytes del core |
| M6 | El parche no toca la zona crítica de recuperación (`0x45c8/0x43fc`, `0x4638`, `0x51c0`, tabla `0x28c6c` y manejadores, `0xece4`, `0x4bca`, `0x8da8`, `0x45bc`, `0xa500/0xa524`, `0xa1dc`) | **NO DEMOSTRADO**, y **la lista está incompleta**: el camino estado 4 → `Upd` no se ha trazado (E24-02b), así que no se sabe qué *más* debe funcionar | E24-02 §2 y §9 | Un parche «fuera de la lista» puede cortar de todos modos la entrada a `Upd` (escenario D) | Obligatoria · R | Sí | Cerrar E24-02b (cola `0x452c`, tabla `0x25b50`, mensaje de `0xed12`) y calcular la clausura de código alcanzable desde el arranque, `InitCom` y `Upd`; solo entonces el diff por bytes tiene sentido |
| M7 | El parche conserva `VERM.mm` | **PASS** para el tipo 0; por candidato en otros | `VER0.78` en `0x2193c` | `ud_darwin_firmup` devuelve «not found/invalid»: no hay reescritura | Obligatoria · I | Sí | Comprobar en cada candidato |
| M8 | El paquete sigue sin `darwin_boo.bin` | **PASS** | Los tres paquetes conocidos no lo traen; sin él el core se reescribe siempre (F8) | Un boo no previsto o la omisión del core si coinciden versiones | Obligatoria · I | Sí | Ninguna |
| M9 | NVRAM íntegra y reciente, con firmware conocido | **FAIL** | Existe la referencia de 3.21 y la previa a T024 (3.21). No hay ninguna de 3.22; las pruebas posteriores a T024 solo escribieron RAM | Restaurar sobre 3.22 una NVRAM de 3.21 no está probado (F12); sin copia no hay vuelta de ajustes | Obligatoria por el protocolo del proyecto · R solo para NVRAM (no restaura Darwin ni firmware) | **No** | `senser_backup_dump.py` + `sha256sum -c` con la cámara conectada |
| M10 | Estado de la cámara re-verificado (modelo, versión, batería) | **NO DEMOSTRADO** | «3.22» es un supuesto (T024) | Cualquier decisión sobre versión parte de un dato no medido | Obligatoria · I | **No** | `pmca info` |
| M11 | Batería > 50 %, cable directo, PC sin suspensión | **NO DEMOSTRADO** | Procedimental; el actualizador rechaza con «battery NG» | Rechazo o interrupción en la ventana de escritura (F10) | Obligatoria · I/R | No | Operador |
| M12 | Copia externa de NVRAM, NAND, FDAT y `firmware/` | **FAIL** | R1 abierto: todo en un disco, fuera de git | Un fallo del disco elimina el FDAT 3.23, la NVRAM y las entradas para reconstruirlo | Obligatoria como condición de que «exista» la recuperación (el FDAT de recuperación solo vive en local) · R | No (decisión del usuario) | Copia en otro disco |
| M13 | Autorización expresa del usuario para ese flasheo | **NO DEMOSTRADO** | Procedimental | Incumple la regla del proyecto | Obligatoria · procedimental | No aplica | Chat, al final, no antes |
| M14 | Aceptación del riesgo residual (C y D = NO) | **FAIL** como condición técnica | C y D siguen en NO (§5) | — | Informativa/procedimental. **No sustituye** ninguna comprobación | No | Solo se transforma en PASS si C y D pasan a SÍ con evidencia (no por aceptación) |

**Integridad frente a recuperación real.** M3, M4, M5, M7, M8 y la parte formal de M1/M2 (I) prueban que *el paquete está bien hecho y que el actualizador podría aceptarlo*. Solo M6, M9 (NVRAM), M11 y M12 tocan la recuperación real, y ninguna demuestra que un Darwin roto se repare. **No hay en M1–M14 ninguna condición que exija una vía de recuperación independiente de la aplicación Darwin**: M14 la sustituía por aceptación. Se añaden tres condiciones que faltan:

| # | Condición añadida | Estado | Por qué falta |
|---|---|---|---|
| M15 | Recuperación demostrada de un Darwin defectuoso (o vía independiente demostrada) | **FAIL / NO DEMOSTRADO** | Es lo que M14 daba por supuesto. No verificable offline: exige binario del arranque o el puerto de descarga |
| M16 | Modo de la actualización: orden y atomicidad de la escritura de `nflasha3/5/7/15/16` y de Darwin | **NO DEMOSTRADO** | Un FDAT que solo cambia Darwin reescribe igualmente 212 MB de particiones principales (idénticas), con `us_darwin_firm.sh` en un hilo aparte (`thread="yes"`); qué ocurre si Darwin falla («NG», LED `0x63`) con las particiones ya escritas es NO_VERIFICADO (F7). La ventana de exposición a una interrupción es mayor que la estrictamente necesaria |
| M17 | Criterio de aceptación posterior a la instalación (arranque en frío, apagado/encendido completo con el core nuevo, `pmca info`) antes de declarar bueno el estado | **NO DEMOSTRADO** | T024 lo hizo de facto; no consta como requisito. Un core que arranca una vez pero falla tras un apagado completo (Darwin siempre alimentado) pasaría inadvertido |

## 3. Escenarios de fallo

«Demostrada» significa que la ruta se ejercitó en esta cámara. Componentes requeridos: **Dw** = arranque y `darwin_core` en energía (`DD_ON*`), **IC** = `InitCom` y comunicación SIO, **Up** = salto a `Upd` y arranque de Darwin que reprograma, **SP** = sistema principal (`nflasha3/5/7/15`) con `usb_extcmd`/`upm.ko`/pmca, **UP1** = `nflasha1` con `nflasha2` sin `uincomp`, **FD** = FDAT 3.23 aceptado por el guard.

| | Escenario | Qué debe seguir funcionando para recuperar | Ruta por software | Demostrada | Lo que se sabe y lo que no |
|---|---|---|---|---|---|
| A | Motor bloqueado, Darwin funcional | Dw, IC, Up, SP, UP1, FD | **Sí, plausible**: pmca → actualizador → `ud_darwin_firmup` con el core original | **No** (solo 3.21→3.22 con mecanismo sano) | El actualizador no usa el mecanismo (E24-02 §5). Dudas: si el rearme bloqueado impide arrancar el SP o priva a la tarea COM de CPU (NO_VERIFICADO); y **reinstalar el core no libera un atasco físico**: restaura el software, no el hardware |
| B | Darwin devuelve error de posición (categoría 6, `0x16558`) | Igual que A, más que el sistema principal no se detenga en pantalla de error y mantenga `usb_extcmd` | Depende de qué haga el BIONZ con ese error | **No** | NO_VERIFICADO (E23: «qué hace la cámara principal con el error 6»). Si lo trata como fallo fatal, pmca no puede entrar (F6) y no hay otra entrada por software |
| C | Máquina de rearme en espera indefinida | Igual que A; que COM (`0xece4`) siga atendiendo aunque otra tarea esté esperando | Probable si COM y el SP viven; no si el BIONZ espera la notificación de fin de rearme en el arranque | **No** | La notificación de fin de rearme y quién arranca la máquina exterior (`0x29d0c`) no se han localizado. Si el bloqueo provoca el «virtual watchdog» de tarea, pasa a F. Un cuelgue de RAM del BIONZ sí se ha recuperado con apagado completo (T029, T037), pero eso es RAM, no Darwin |
| D | Darwin responde por SIO pero no permite entrar a `Upd` | Up (estado 4 → `Upd` → salto a 0x0 con buzón 4) | **No**: `ud_darwin_firmup` espera el estado 5 y falla («NG», LED `0x63`); 0x14/0x15 los atiende el arranque, que solo se alcanza vía `Upd` | **No** | **El caso más peligroso**: la cámara parece viva y es irrecuperable por software. Es exactamente lo que provoca un parche mal situado en `InitCom`, `0x45bc`, `0x8da8` o la tabla de estados. Como el camino 4→`Upd` es INFERENCIA, la zona «a no tocar» podría ser más ancha de lo que M6 enumera |
| E | Darwin deja de comunicarse con BIONZ | IC | **No** | **No** | `ud_darwin_init` se ignora y está acotado, pero `ud_darwin_firmup` necesita el enlace. La lectura de batería de la entrada de pmca (`battery NG`) probablemente viene de Darwin (INFERENCIA) y bloquearía incluso entrar. Sin enlace, el único medio de escribir Darwin es de hardware |
| F | Reinicios constantes por watchdog | Que Darwin se mantenga estable el tiempo suficiente para encender el BIONZ y llegar al actualizador | **No** | **No** | El reinicio de Darwin deja `DD_ON1/2/3=0` (E24-01): **cada reinicio quita la alimentación al BIONZ**, así que un bucle más corto que el arranque del BIONZ impide el actualizador. Nuevo (§7): el watchdog se rearma con un byte de configuración `+0x40..+0x43` (recarga = valor × `0x1869f`; 0 lo desarma) en seis sitios (cinco cargan el byte justo antes de la llamada) y se alimenta en dos. El valor real de esos bytes y el reloj del contador no se conocen |
| G | Darwin no consigue activar `DD_ON1/2/3` | Dw | **No** | **No** | Sin núcleo ni LPDDR2 no corre el BootROM ni el actualizador (esquema pág. 9, tabla `0x28c6c`). Solo SWD/serie del MCU, hardware |
| H | `darwin_core.bin` incompleto tras una actualización interrumpida | Que el arranque (`0x0–0x41ff`) detecte la imagen incompleta, no alimente el sistema por fallo y vuelva a admitir una descarga | **No**; el arranque no es visible | **No** | No se sabe si valida la imagen (CRC/firma), si se queda en modo descarga ni qué hace con `DD_ON*`. T024 solo indica que acepta un core con CRC-32 recalculado. La ventana de riesgo incluye además `nflasha3/5/7` (M16) |
| I | BIONZ arranca pero no entra al modo actualizador | SP con `usb_extcmd`/`up.sh user`; Loader2/3 y las banderas `/setting/updater/mode*`; UP1 | Solo la entrada de pmca | **Sí en 3.21→3.22** | Loader2/3 no están volcados (quién lee las banderas es INFERENCIA). Un SP dañado cierra la entrada (F6). No hay otro disparador conocido |
| J | Versión instalada ≥ la del FDAT de recuperación | FD (reempaquetado a ≥ instalada+1) | Sí, **en el host**: `fwtool pack` reproduce el FDAT con otra versión | Reempaquetado demostrado (byte a byte); aceptación en cámara **no** | Exige conservar `firmware/extracted/fw321` (R1). Limitación de BCD (tope 3.99). 9.99 cierra la vía. La regla para 3.22 es inferencia (M2) |

Regla común: **todo lo que pasa por `ud_darwin_firmup` presupone Dw + IC + Up**. No se asume que el arranque de Darwin pueda programar un core defectuoso: sin su binario es una pregunta abierta, no una premisa.

## 4. Límites del FDAT 3.23 (tres afirmaciones distintas)

| Afirmación | Estado | Base |
|---|---|---|
| **1. Paquete correctamente construido** | **SÍ** | Cabecera `UDTRFIRM`, CRC-32, suma de 16 bits por bloque, cifrado `CXD90014`, modelo `0x41030035`, región 0, versión 3.23; tar interno = oficial; `updater.img` = oficial; `darwin_core.bin` = `5f2be06d…`; `darwin.sum` coincide; sin `darwin_boo.bin`; reconstrucción byte a byte (re-ejecutado hoy: 8/8) |
| **2. Actualizador capaz de aceptarlo** | **Probable, no demostrado** | Misma tubería y estructura que el 3.22 aceptado en T024 y mismos modelo/región; **pero**: guard no medido con 3.22 (M2), el actualizador solo se ejercitó en el sentido 3.21→3.22, la verificación del paquete la hace el mismo `fwtool` que lo creó, y quedan rechazos posibles: versión (F1), batería (F5), `uincomp` (F9) |
| **3. Procedimiento de recuperación demostrado ante un fallo** | **NO** | Ningún fallo de Darwin ni del firmware principal se ha recuperado nunca; solo una restauración de NVRAM y recuperaciones de RAM por apagado |

Dependencias, en orden: `InitCom` (estado 4) → `Upd` (salto al arranque) → arranque (sin binario) → `ud_darwin_firmup` (destino 2, sin boo: reescritura incondicional). La reescritura del core es robusta frente a versiones (F8), pero **no frente a un arranque que no la acepte**. El FDAT 3.23 restaura el *software* de Darwin, nunca el arranque `0x0–0x41ff`, que ningún paquete conocido contiene. Condiciones en que la cámara no lo aceptaría o no lo completaría: F1 (versión), F5 (batería/temperatura), F6 (sin entrada al actualizador), F7 (estado 4 sin respuesta), F9 (`uincomp`), F10 (interrupción).

## 5. Alternativas menos persistentes

| | 1. Parche persistente de Darwin | 2. Modificación persistente de BIONZ/LIRO (`nflasha3/5/7`) | 3. Configuración volátil de Darwin por una ruta existente | 4. Comandos `InitCom 0x12/0x13/0x16` |
|---|---|---|---|---|
| **Riesgo de perder el arranque** | Alto en el caso del peor fallo (D, G, H): irrecuperable por software; bajo solo para parches aislados de la compuerta (precedente T024, 7 bytes) | **Alto y simétrico**: un SP que no arranca cierra la entrada por software (F6) aunque Darwin e `nflasha1` estén intactos. LIRO/`av-cam` viven en `nflasha3` junto con el resto del arranque | Bajo: no se escribe flash; el core no tiene código de programación de flash (verificado), así que no puede persistir | Bajo en persistencia (mismo argumento); riesgo de colgar o reiniciar Darwin si se pisa estado/pila (`0x16` acepta direcciones `0x20000000–0x20004000`) |
| **Riesgo de bloquear capturas** | Alto para «sin rearme»: sin leva, el core llegaría a `0x1fa3a` (error 6); notificación de fin de rearme no localizada | Alto: toda la captura pasa por el SP; T029/T030/T038 muestran que forzar el modo de sensor cuelga la captura | Medio: el tipo ya es tipo 0 en 3.22; la compuerta del rearme (`0x1fe66`, nibble alto) es otro dato; **corrección E24-05:** con `0x1fe66`=0 los arrancadores de la máquina exterior eligen la lista `[0,7,8,9,10]` y no alcanzan el motor (E23 lo daba por no desactivado; ver [E24-05](e24-05-upd-y-rearme.md) §1) | Medio-alto si el consumidor no es el supuesto |
| **Reversibilidad** | Solo por el mismo actualizador y solo si Dw+IC+Up viven (no demostrada la inversa) | Idem (mismo actualizador) | **Alta**: reinicio de Darwin. Ojo: Darwin está siempre alimentado, así que apagar la cámara puede no reiniciar su SRAM; seguro con la batería fuera (precedente de BIONZ en T037, no de Darwin) | Idem |
| **Dependencias del mecanismo físico** | Total (motor, levas, bobinas) | Parcial: puede evitar pedir la secuencia, pero el rearme interno y el control de posición de Darwin siguen existiendo | Total | Total |
| **Limitaciones de recuperación** | C y D = NO; irrecuperable por software en D, E, F, G, H | Idem: el actualizador es el mismo | La mejor: sin flasheo | La mejor, pero sin demostrar |
| **Ingeniería inversa que falta** | E24-02b (clausura de `Upd`), notificación de fin de rearme, quién arranca la máquina exterior, comportamiento del arranque | Quién pide la secuencia al rearme en Darwin (mensaje BIONZ→Darwin que dispara `0x20120/0x20134`), el contrato Silent y la semántica del sensor (D5) | Origen y relectura del byte de tipo (`0x20000050+ch`, `0x1b080`) y si se relee en cada disparo | Contrato de 0x12/0x13/0x16, emisor BIONZ (`adjstctl`/`libsencore`, E24-02d), efecto real sobre el rearme |

**No se declara segura ninguna opción.** «No toca `darwin_core`» no la hace segura (2). Y lo volátil (3, 4) es seguro respecto del arranque, no respecto de que *sirva*: la evidencia actual dice que forzar el tipo no desactiva el rearme, que es lo que falta.

Referencia ya ejercida: los parches en RAM del BIONZ (T020, T026–T039) son reversibles con apagado completo, con dos incidentes (T029 y T037, este último con batería fuera). Es la única clase de modificación con recuperación demostrada en esta cámara.

## 6. Respuestas

| | Pregunta | Respuesta | Tipo de límite |
|---|---|---|---|
| **A** | ¿Está demostrado que un Darwin defectuoso puede recuperarse por software? | **NO** | Límite de evidencia. Hay evidencia en contra para D–H (E24-01/02), no una imposibilidad demostrada. Solo A tiene una ruta plausible |
| **B** | ¿El FDAT 3.23 es íntegro y reproducible? | **SÍ** | Probado y re-ejecutado hoy (8/8). No equivale a «instalable» ni a «recuperación demostrada» (§4) |
| **C** | ¿Existe una vía de recuperación independiente de la aplicación Darwin demostrada en la A6000? | **NO** | Límite de evidencia. Existe en el esquema un puerto de descarga del MCU (`MD0_DWN`, `XDWN_RESET`, UART, SWD en `CN4906` sin montar), nunca usado; exige abrir la cámara (descartado por el usuario) y la protección de flash es desconocida |
| **D** | ¿Hay evidencia suficiente para autorizar técnicamente un nuevo flasheo persistente de Darwin? | **NO** | Límite de evidencia, con bloqueantes concretos (§8). No es una prohibición: la decisión final sigue siendo del usuario, pero con C y D = NO no puede presentarse como técnicamente respaldada |
| **E** | ¿Puede continuar la ingeniería inversa estática del motor y su máquina de estados? | **SÍ** | Es trabajo offline sin riesgo; hay tareas abiertas concretas (§9) |
| **F** | ¿Conviene priorizar la investigación de una ruta alternativa desde BIONZ/LIRO o RAM? | **SÍ, solo la parte volátil (RAM)** | La razón es de recuperación: la clase RAM es la única con vuelta atrás demostrada. Una modificación **persistente** de LIRO no es más segura (F6) y no debe priorizarse por eso |

## 7. Comprobación nueva (única de la sesión)

`tests/test_e24_04_watchdog.py` (2 pruebas, <1 s; se omite sin `darwin_core.bin` oficial; requiere `capstone`) verifica sobre los bytes:

- `0xa4c4` es la rutina que arma el watchdog hardware (`0x40011000`, clave `0x1acce551`): con argumento 0 lo desarma (`cbnz`), y si no escribe como recarga `arg × 0x1869f` (`muls` en `0xa4d0`, `str` en `0xa4d8`).
- Seis llamadores arman el watchdog: cinco pasan un byte de configuración `+0x40`…`+0x43` (`0x73d4`, `0x7956`, `0x804e`, `0x823c`, `0x8460`; el sexto, `0x1bfae`, lo carga antes de un `pop.w`) y la alimentación (`0xa524`) se llama solo desde `0x79a6` y `0x8a3e`.

Consecuencia (INFERENCIA, sin el valor de los bytes ni el reloj del contador): el tiempo del watchdog depende de una configuración por estado (reposo, sueño) y puede ser 0, de modo que el periodo no puede afirmarse; corrige E24-02 §9 «frecuencia del watchdog» a *parametrizado, valor desconocido*. No se añadieron más pruebas: el resto del dictamen es síntesis de lo ya verificado en E24-01..03 y sus 26 pruebas.

## 8. Bloqueantes para un flasheo

| # | Bloqueante | Naturaleza | Quién lo resuelve |
|---|---|---|---|
| X1 | C y D = NO: ninguna recuperación de Darwin defectuoso ni vía independiente (M15) | Límite de evidencia | Binario del arranque `0x0–0x41ff` (SWD/serie, no autorizado) o prueba de recuperación; no resoluble offline |
| X2 | M1: la recuperación 3.23 es rechazable ante un FDAT 3.24 | Resoluble | Reempaquetar ≥3.25 (offline) antes de cualquier prueba |
| X3 | M6/E24-02b: la clausura de código «imprescindible para `Upd`» no está cerrada | Resoluble offline | Estático, §9 |
| X4 | M2, M9, M10, M11: guard con 3.22, NVRAM de 3.22, estado y batería | Exigen conectar | Usuario autoriza conectar (sin flashear) |
| X5 | M12/R1: sin copia externa | Decisión del usuario | Copia en otro disco |
| X6 | M16: se reescriben también las particiones principales; orden y fallo parcial no verificados (F7) | Resoluble offline en parte | Estático de `libupdaterbody.so` y `config.xml` |
| X7 | M13: autorización expresa para ese caso | Procedimental | Usuario, al final |
| X8 | Utilidad: «sin rearme» no está diseñado. **Corrección E24-05:** `0x1fe66`→0 *sí* selecciona la lista `[0,7,8,9,10]` sin motor (salvo el freno de la operación 5); queda sin medir qué espera BIONZ al fin del rearme | Parcialmente resuelto offline | Ver [E24-05](e24-05-upd-y-rearme.md): arranque (mensaje BIONZ de la secuencia de captura) y lectura de fin por BIONZ siguen abiertos |

## 9. Próxima tarea recomendada (no iniciada)

> **Cerrado en E24-05 (27-10-2026):** la cadena `InitCom` → `Upd` → `0x45bc` está trazada (X3 cerrado en lo estático; M6 se refina, no se declara PASS) y la máquina exterior se arranca por tres funciones cuya lista de estados depende de `0x1fe66`. Ni X1 ni la recuperación cambian.

**Un único trabajo estático:** trazar en `darwin_core.bin` **(a)** el camino real del estado 4 de `InitCom` a la entrada `Upd` (cola `0x452c/0x4530`, tabla `0x25b50`, mensaje publicado en `0xed12`) para fijar la clausura de código imprescindible para la recuperación (cierra X3, M6, escenario D) y **(b)** con el mismo grafo, **qué mensaje o evento arranca la máquina exterior `0x29d0c` por `0x20120/0x20134`** (X8). Si (b) depende de un mensaje que el BIONZ envía, existiría una vía de **RAM** para evitar el rearme (alternativa 2/3) sin flashear; si es interno de Darwin, queda confirmado que solo un parche persistente lo evita y entonces se vuelve a este dictamen con la clausura calculada. En paralelo, y sin tocar Darwin, X2 y la elección de la copia externa (X5) son baratas.

## Límites

Todo lo dicho del arranque de Darwin, de Loader2/3 y de lo que haga el actualizador ante un fallo de Darwin es deducido de lo que los llama y de lo que los usa; ninguno de esos binarios está disponible. La versión instalada y la regla del guard con 3.22 no se re-verificaron. «Ruta plausible» no es «ruta demostrada». No se cuantifica probabilidad de fallo.

## Addendum 28-10-2026 — E25-25 (carga del BIONZ, no cambia el dictamen)

E25-25 verificó, con el `liro.ko` ya documentado en S49, que `tsk_entry` lee
`av-cam.bin` completo (`filp_open`/`vfs_read`), comprueba `LIRO`/versión 4 y hace
`memcpy(hdr[0x14]+0x24, tabla_API, 0x344)`; el stub ARM de `0x0` se ejecuta desde el
mismo buffer. Eso sostiene que una cueva en el área reservada de la cabecera
(`0x4354141c–0x435418d8`) se carga y comparte permisos con el texto, pero **no**
demuestra que el cargador acepte la imagen ni que ignore esos campos.

No hay checksum ni firma dentro de la imagen: la única integridad conocida es el CRC-32
del paquete (`us_crc32sum.sh`, E24-03), recalculable offline. **El dictamen no cambia:**
un Darwin defectuoso sigue sin recuperación demostrada; no se autoriza un flasheo
persistente. La reubicación de cuevas elimina un riesgo de corrupción de datos, no el
riesgo de arranque. Detalle: [E25-25](e25-25-validacion-carga-caves.md).
