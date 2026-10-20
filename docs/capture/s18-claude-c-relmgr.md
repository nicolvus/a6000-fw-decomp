# Sesión 18 — hilo Claude C (RelMgr / consumidor 0x40193 / filas dinámicas / kernel)

Clasificación obligatoria en cada hallazgo: **VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO**.
No se afirma en ningún punto que SilentShutter funcione. Análisis puramente estático sobre `av-cam.bin` (LIRO,
base de carga `0x43541000`) vía `scripts/ghidra_dec.sh` (Ghidra headless `-noanalysis -readOnly`) y
`llvm-objdump -d --triple=thumbv7-none-eabi analysis/av-cam-analysis-view.elf` para desensamblado crudo.
No se tocó la cámara física, no se instaló nada, no se modificó `av-cam.bin` ni `CONTEXT.md`. Trabajo
realizado enteramente en el hilo principal, sin delegar en subagentes.

Modelo/esfuerzo real: **Claude Sonnet 5, esfuerzo "medium"** (pedido por el usuario), ejecutado en una sesión
en segundo plano (background job) de Claude Code.

## Nota metodológica previa: corrección de direcciones de tabla (bit Thumb)

Las 4 direcciones "candidatas dinámicas" heredadas del resumen de sesión 17/18 (`0x43b1be37`, `0x43b1bf05`,
`0x43b1bf67`, `0x43b1c035`) son **punteros Thumb con el bit 0 puesto a 1** (convención ARM estándar para
indicar modo Thumb en un puntero a función almacenado en tabla). Al pasarle `0x43b1be37` literal al
decompilador, Ghidra lanzó `ContextChangeException: Context register change conflicts with one or more
instructions` porque esa dirección cae **a mitad de la instrucción anterior**, no en un inicio de función
real. Verificado por desensamblado crudo: la instrucción `push {r4,lr}` real empieza en `0x43b1be36` (par),
no en `0x43b1be37` (impar). Las otras tres (`...bf05`, `...bf67`, `...c035`) decompilaron "bien" con la
dirección impar porque Ghidra, sin bloqueo previo de contexto en esa región, las reinterpretó solo; sus
entradas reales confirmadas por el propio JSON de salida son `0x43b1bf04`, `0x43b1bf66`, `0x43b1c034`
(pares). **VERIFICADO.** Para cualquier trabajo futuro sobre esta tabla de 20 bytes: restar 1 a los
punteros GOT antes de pedirle a Ghidra que decompile en esa dirección exacta.

## 1. Las 4 filas dinámicas (0xa0, 0xc8, 0xdc, 0x104) — comparación con la fila 0xb4

Decompiladas con `scripts/ghidra_dec.sh` (una invocación por dirección, usando las direcciones pares
corregidas):

| Fila | Dirección real (par) | Estado Ghidra |
|---|---|---|
| 0xa0 | `0x43b1be36` | decompiled |
| 0xc8 | `0x43b1bf04` | decompiled |
| 0xdc | `0x43b1bf66` | decompiled |
| 0x104 | `0x43b1c034` | decompiled |

**VERIFICADO** (por diff textual de los 4 pseudocódigos completos, no solo el primer bloque): los cuerpos de
las 4 funciones son **semánticamente idénticos byte a byte en su lógica de control**, difiriendo
únicamente en: (a) nombres de variable asignados arbitrariamente por el decompilador (`sVar10` vs `sVar8`
vs `uVar10`, etc. — artefacto de Ghidra, no del binario), y (b) en las 2 últimas (`0xdc`, `0x104`) el
compilador generó una variante de 64 bits para el valor de retorno de `FUN_43afdf16()` (`undefined8` con
`uStack_14 = (uint)(uVar>>0x20)`) mientras las dos primeras (`0xa0`, `0xc8`) tratan ese retorno como 32 bits
puros. Esta es la única diferencia estructural real detectada, y es un detalle de ABI/firma, no de
contenido ni de rama de ejecución.

Las 4 funciones:
- Llaman a `FUN_43afdf16()` al entrar y despachan por `switch` sobre su resultado (0..6, vía tabla `tbb
  [pc,r0]` en el desensamblado crudo — confirma el "árbol de 4 niveles" y las "8 filas candidatas" ya
  descritos en sesión 17, visto ahora desde el lado de la fila, no del selector).
- En el `case 0` operan sobre los **mismos campos de struct** que usa el selector `0x437eabfc` y que ya
  usaba la fila `0xb4`: `+0x1d8`, `+0x1e0`, `+0x4b70`, `+0x4b95`, `+0x4c`, `+0x54a5`, `+0x548c`/`+0x5488`,
  `+0x750`/`+0x754`, `+0x4ad8`/`+0x4d8` (acceso indirecto vía puntero en `+0x4ad8`), y referencian las
  mismas cadenas literales: `"Capture_Req_Retry: exp_id=%d fa=..."`, `"Warning: CA_CaptureReq RETRY
  count..."`, `"Capture_Cancel <%x>"`, `"[Panorama] DEBUG CAPTURE_START"`.
- **Ninguna de las 4 contiene ninguna marca, campo o cadena de modo electrónico/EFCS/Silent.** No hay
  referencias a `Silent`, `EFCS`, `Electronic`, `shutter curtain`, ni a ningún campo distinto de los que ya
  usa la ruta mecánica estándar (fila `0xb4`, documentada en sesión 18 previa como "sin marca Silent").

**Conclusión (VERIFICADO con la salvedad de ABI arriba indicada):** ninguna de las 4 filas dinámicamente
seleccionables difiere cualitativamente de la fila `0xb4`. Las 5 filas conocidas (`0xa0`, `0xb4`, `0xc8`,
`0xdc`, `0x104`) son variantes casi idénticas del mismo manejador de captura mecánico estándar con
reintentos/cancelación, sin bifurcación visible a una ruta puramente electrónica. **Esto no descarta** que
alguna de las 10 filas restantes de la tabla de 15 (no seleccionables por el cálculo `iVar7*0x14` conocido,
pero presentes en la tabla) tenga contenido distinto — **NO VERIFICADO** para esas 10, quedan fuera del
alcance de esta tanda.

## 2. Caza del consumidor de la cola 0x40193 / mensaje 0x3011 — avance parcial, blocker persiste

**Hallazgo nuevo (VERIFICADO por desensamblado crudo):** la función que realmente contiene los 4 primeros
de los 7 sitios `bl 0x43809ed8` (los de `0x43807e74`..`0x43807f2a`, dentro del "manejador de
transición de estado de tecla" ya identificado como `0x43807d80`) termina en `0x43807f2a`
(`pop {r4,pc}` / `movs r0,#5`). **Inmediatamente después**, en `0x43807f4c`, empieza una **función nueva y
distinta** con un prólogo inusual (`push.w {r0,r1,r2,r3,r4,r5,r6,r7,r8,lr}` — guarda los 4 registros de
argumento además de 5 registros adicionales, patrón típico de un *handler* llamado indirectamente que debe
preservar todo su contexto de entrada).

Decompilada (`scripts/ghidra_dec.sh 0x43807f4c`): es un **dispatcher denso** sobre
`iVar4 = *param_2` (el primer campo de la estructura de mensaje recibida en `param_2`), con ramas para
valores literales `0x100, 0x101, 0x102, 0x103, 0x206`, etc. (dominio `0x100..0x207`). La rama
`iVar4 == 0x100` llama exactamente a `0x43807d80` (sin argumentos explícitos adicionales en el pseudocódigo,
heredando `param_1`/registro); la rama `0x101` llama a `0x43809e98` (la función que en sesión 17 ya
aparecía junto a `0x43809ed8` en el mismo rango). **Esto demuestra que `0x43807f4c` es el llamador directo
real de `0x43807d80`** — un dato nuevo que cierra el "¿quién llama a 0x43807d80?" planteado en la tarea.

**Blocker que persiste (NO VERIFICADO):** `0x43807f4c` despacha por el dominio de IDs **`0x100..0x207`**, que
es **distinto** del dominio `0x3011/0x3013/0x3015` de los mensajes `ObjMsg` manejados por `RelMgr` y la cola
`0x40193`. No se encontró, en esta pasada, ninguna referencia textual ni de constante a `0x3011`, `0x3013`,
`0x3015` ni `0x40193` dentro de `0x43807f4c` ni de `0x43807d80`. Búsqueda exhaustiva por `llvm-objdump`
de llamadas directas (`bl`) hacia `0x43807f4c`: **ninguna encontrada** en todo el binario — es decir,
`0x43807f4c` se invoca exclusivamente de forma indirecta (puntero de función / tabla de vtable / callback
registrado), consistente con ser el *handler* de un objeto tipo `LifeCycle`/dispatcher de mensajes locales,
pero **sin que se haya podido demostrar, por desensamblado crudo, el puente entre el dominio `0x3011..`
(ObjMsg/cola `0x40193`) y el dominio `0x100..0x207` que consume `0x43807f4c`**.

**Conclusión honesta:** el "receptor real" del mensaje `ObjMsg` tipo 2 id `0x3011` (y de los `0x3013`/`0x3015`
producidos vía `LAB_43b01ec4`) **sigue sin identificarse por desensamblado crudo** en esta tanda. Lo que se
identificó es un nivel distinto y más cercano al hardware/tecla (`0x43807f4c` → `0x43807d80`/`0x43809e98`,
dominio `0x100..0x207`), que podría ser upstream o downstream del dominio `0x3011`, pero la relación entre
ambos dominios **no está probada** — queda como **HIPÓTESIS abierta**, igual que en el cierre de sesión 17.

## 3. Primitivas del kernel Sony (cxd90014 / cxd4132) — ¿mecanismo real de S2?

Inspeccionado el árbol extraído en `analysis/session18/claude-c/` (kernel Linux 3.0.27, `arch/arm/mach-
cxd90014/` y `arch/arm/mach-cxd4132/`).

**VERIFICADO:** no existe en ninguno de los dos árboles mach-* ningún archivo, símbolo o cadena relacionado
con teclas de cámara, `RelMgr`, `CaptureManager`, `ObjMsg`, `av_cam` o similar — búsqueda
`grep -rli "av_cam|avcam|relmgr|capturemgr|objmsg"` sobre el árbol completo del kernel extraído: **0
resultados**. Los únicos archivos relevantes a GPIO son genéricos de plataforma:
`arch/arm/mach-cxd4132/gpio.c` (driver de `/dev/gpio` sobre el framework propio de Sony `udif` —
*registro de dispositivo de caracteres genérico*, sin ninguna lógica específica de teclado o disparador).

**DESCARTADO** (para esta tanda): que el kernel OSS disponible contenga una primitiva de interrupción GPIO
específica para teclas físicas de la cámara. Lo que sí hay es infraestructura **genérica** de SoC (GPIO,
reloj, IRQ del controlador PL310/GIC, `udif` como capa de abstracción de drivers Sony) que **podría**, en
teoría, ser usada por un driver de teclado no incluido en este volcado OSS (probablemente propietario y
ausente de los tarballs disponibles) — pero esto es **HIPÓTESIS**, no verificado.

## 4. ¿Hay un manejador de interrupción GPIO/teclado reconocible que mapee a S2?

**NO VERIFICADO — honestamente, no.** Inspección de `arch/arm/mach-cxd4132/gpio.c`: el único uso de "irq" en
todo el archivo es `udif_spin_lock_irqsave`/`udif_spin_unlock_irqrestore` (bloqueo de spinlock con
guardado de flags de interrupción para proteger acceso concurrente a registros GPIO), **no** hay ninguna
llamada `request_irq`, `udif_request_irq`, ni registro de ISR en este archivo. No se encontró en los árboles
`mach-cxd90014`/`mach-cxd4132` ningún manejador de interrupción de teclado reconocible. La explicación más
probable (**HIPÓTESIS**, no verificable con el material disponible) es que el escaneo de teclas S1/S2 ocurra
por *polling* desde userspace (LIRO) sobre un registro GPIO leído vía el driver genérico, o que el driver de
teclado real sea un módulo propietario no incluido en `linux-kernel.tar.gz`. **Se declara explícitamente: no
se puede probar ninguna de las dos alternativas con el material estático disponible.**

## 5–14. Estado consolidado de la cadena S2 → captura → selección → adquisición

Resumen de qué partes están VERIFICADAS tras los hallazgos de esta tanda vs. las que siguen sin consumidor
confirmado:

| Eslabón | Estado | Evidencia |
|---|---|---|
| `RelMgr` (0x4379d838) envía ObjMsg tipo 2 id 0x3011 → cola 0x40193 | VERIFICADO (sesión 17, no reconfirmado esta tanda) | heredado |
| Construcción del callback `CaptureStart` (GOT 0x44021ed0→0x437df641) hacia `FUN_439018b0` | VERIFICADO (sesión 17) | heredado |
| 7 sitios reales `bl 0x43809ed8` en dos funciones (`0x43807d80`, `0x438089d4`) | VERIFICADO (re-confirmado esta tanda por `llvm-objdump`, exactamente 7 coincidencias) | esta tanda |
| `0x43807d80` termina en `0x43807f2a`; función **distinta** `0x43807f4c` empieza justo después | VERIFICADO (nuevo) | esta tanda |
| `0x43807f4c` es dispatcher de dominio local `0x100..0x207`, llama a `0x43807d80` en case `0x100` | VERIFICADO (nuevo) | esta tanda |
| `0x43807f4c` se invoca solo indirectamente (0 `bl` directos en todo el binario) | VERIFICADO (nuevo) | esta tanda |
| Relación entre dominio `0x100..0x207` y dominio `0x3011/0x3013/0x3015`/cola `0x40193` | **NO VERIFICADO** — HIPÓTESIS abierta | esta tanda |
| Receptor real de cola `0x40193` / mensajes `0x3011`,`0x3013`,`0x3015` | **NO VERIFICADO**, blocker persiste | esta tanda |
| `0x438089d4` descartado como consumidor de `0x40193` | DESCARTADO (sesión 17, no reconfirmado) | heredado |
| Inicializador `0x437ebed8` puebla la tabla del selector `0x437eabfc` vía GOT resuelto estáticamente | VERIFICADO (sesión 18 previa) | heredado |
| Offsets dinámicamente seleccionables reales: `0xa0,0xc8,0xdc,0x104` (no los de memoria citados antes) | VERIFICADO (sesión 18 previa) | heredado |
| Direcciones reales de esas 4 filas (corrigiendo bit Thumb): `0x43b1be36,0x43b1bf04,0x43b1bf66,0x43b1c034` | VERIFICADO (nuevo, esta tanda) | esta tanda |
| Las 4 filas dinámicas son semánticamente idénticas entre sí y a la fila `0xb4`, sin marca Silent/EFCS | VERIFICADO (nuevo, esta tanda) | esta tanda |
| Primitivas de kernel Sony (cxd90014/cxd4132) específicas de tecla física S2 | NO VERIFICADO / DESCARTADO parcial — solo hay GPIO genérico, sin IRQ de teclado | esta tanda |
| Existencia de una ruta electrónica (EFCS puro, sin cortina mecánica) activable solo cambiando un campo del struct de petición, en cualquiera de las 5 filas conocidas (`0xa0,0xb4,0xc8,0xdc,0x104`) | **HIPÓTESIS puramente especulativa, NO VERIFICADA, análisis estático únicamente**: las 5 filas comparten exactamente los mismos campos de control (`+0x1d8`,`+0x1e0`,`+0x4b70`,`+0x4b95`,`+0x54a5`,`+0x750`/`+0x754`) sin ninguna bandera visible que distinga "mecánico" de "electrónico"; **no hay ninguna evidencia de que modificar cualquiera de esos campos produjera una captura puramente electrónica** — la ausencia de una bifurcación visible es tan compatible con "no existe tal ruta en estas 5 filas" como con "la bifurcación vive en una de las 10 filas restantes de la tabla de 15, aún no decompiladas". **Nunca se afirma que SilentShutter funcione; esto es análisis puramente teórico, jamás una propuesta de implementación real.** |

### Qué queda abierto explícitamente para la próxima tanda

1. Decompilar las 10 filas restantes de la tabla de 15 (offsets `0x0,0x14,0x28,0x3c,0x50,0x64,0x78,0x8c,
   0xf0,0x118`) — recordando restar 1 a los punteros GOT antes de pasarlos a Ghidra (ver nota metodológica).
2. Buscar quién llama a `0x43807f4c` de forma indirecta (tabla de vtable / registro de callback) para
   intentar cerrar el puente entre dominio `0x100..0x207` y dominio `0x3011..`.
3. Revisar si el kernel propietario ausente de `linux-kernel.tar.gz` (módulos no incluidos en el tarball
   genérico) podría contener el driver de teclado real — esto requeriría material adicional no disponible
   actualmente en el proyecto; no se descargó nada nuevo, conforme a las reglas.

## Incidentes de esta tanda

- Un intento de decompilación falló con `ContextChangeException` por pasar una dirección Thumb impar
  (`0x43b1be37`) que cae a mitad de instrucción; resuelto restando 1 (`0x43b1be36`). Documentado en la
  sección metodológica arriba para que no se repita en tandas futuras.
- No se tocó `CONTEXT.md`. No se instaló software. No se conectó ni flasheó ninguna cámara física. No se
  delegó ningún trabajo a otro agente — todo el análisis de esta tanda se ejecutó en el hilo principal.
