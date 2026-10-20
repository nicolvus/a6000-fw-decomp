# Puente Camera → Effect → Recorder — verificación directa del investigador principal (sesión 15)

Alcance: análisis estático de `libObj.so` fw 3.21, hecho personalmente (no delegado), en paralelo a la Rama A (Claude Sonnet 5, subagente) y la Rama B (Codex GPT-5.6 Terra). Direcciones ELF (Ghidra VA = ELF + 0x10000). Herramienta: `llvm-objdump -d --triple=thumbv7-linux-gnueabi` directo sobre el binario (Ghidra headless falló al decompilar estas direcciones — ver nota al final).

## 1. Constructor real de ObjCamera (NUEVO, VERIFICADO)

`ObjCamera_Create` (símbolo exportado, ELF `0x959bdc`, 44 B) es un wrapper: `operator new(0x20c)` + llamada al constructor real en **ELF `0x98c380`**. Este construye la base `MWF::ObjActiveBase` con id interno `9` (`movs r1,#0x9` antes de `blx _ZN3MWF13ObjActiveBaseC2EiPKcjii@plt`, ELF `0x98c394`) — **este `9` es un identificador de otra tabla (categoría/tipo de la clase base `ObjActiveBase`), NO el `ObjId` de la tabla del TopologyManager**; no debe confundirse con el objeto 9 de dicha tabla (confirmado abajo que allí Camera es el objeto 8). El mismo patrón en `ObjStillRecorder` (ELF `0x9178f0`) usa `movs r1,#0x8` para su propio `ObjActiveBase`, es decir, dos espacios de numeración distintos y ya documentados como no equivalentes (sesión 14).

Tras la base, el constructor de ObjCamera llama a cuatro subfunciones (`0x987788`, `0x987d6c`, `0x987dc6`, `0x9880a4`); la tercera incluye el bloque de construcción de pines.

## 2. Firma de pines de ObjCamera — VERIFICADO (antes INFERENCIA fuerte)

Función interna ELF `0x987dc6` (desensamblado directo, no decompilado): nueve llamadas a `MWF::ObjPin::ObjPin(DefObjPin::PinType pin1, int pin2, DefObjPin::PinDir pin3, EventSender* pin4)` (PLT ELF `0xdcb90`). Orden real de argumentos en el ABI thumb: r1=PinType, r2=número de pin, r3=PinDir, pila=EventSender.

| Dirección de la llamada | PinType | Nº | PinDir | Campo `this+` |
|---|---|---|---|---|
| `0x987de0` | 0 (YC) | 0 | 1 (salida) | `0x58` |
| `0x987dfa` | 0 (YC) | 1 | 1 (salida) | `0x5c` |
| `0x987e14` | 0 (YC) | 2 | 1 (salida) | `0x60` |
| `0x987e2e` | 0 (YC) | 3 | 1 (salida) | `0x64` |
| `0x987e48` | 9 (STILL_DATA) | 0 | 1 (salida) | `0x68` |
| `0x987e62` | 4 (SOUND) | 0 | 1 (salida) | `0x6c` |
| `0x987e7c` | 0xb (CAMERA_STATUS) | 0 | 1 (salida) | `0x70` |
| `0x987e96` | 0 (YC) | 4 | 1 (salida) | `0x74` |
| `0x987eb0` | 0 (YC) | 5 | 1 (salida) | `0x78` |

**Resultado clave: las nueve llamadas tienen `PinDir = 1` (salida). ObjCamera no construye ningún pin de entrada.** Coincide exactamente con la firma inferida en sesión 14 para el objeto 8 de la tabla del TopologyManager ("única fuente de STILL_DATA y CAMERA_STATUS; 6 salidas YC"). **Esto eleva esa identidad de INFERENCIA fuerte a VERIFICADO: objeto 8 = ObjCamera.**

Consecuencia directa: ObjCamera no puede recibir `YcPinReqDeliver` ni ningún mensaje de pin de entrada — es un productor puro. Cualquier ruta "Camera → EncodeStill" tiene que pasar forzosamente por un objeto intermedio con pin de entrada (Effect), nunca por una conexión directa Camera↔Recorder.

## 3. Filas de topología 0x0A, 0x07 y 0x2A — StsId confirmado

Lectura directa de `analysis/topology-table-libobj.json`:

| Fila | pin_type | sts_id | src_obj → dst_obj | dirección/no |
|---|---|---|---|---|
| `0x0a` | 0 (YC) | **0** | 8 (Camera) → 9 (Effect) | Camera out#0 (dir1) → Effect in#0 (dir0) |
| `0x07` | 0 (YC) | **0** | 9 (Effect) → 5 (Renderer) | Effect out#0 (dir1) → Renderer in#0 (dir0) |
| `0x2a` | 0 (YC) | **6** | 9 (Effect) → 11 (StillRecorder) | Effect out#1 (dir1) → Recorder in#0 (dir0) |

VERIFICADO con los datos ya extraídos por `dump_topology_table.py`. Dato nuevo: `0x0a` y `0x07` comparten `sts_id=0`; `0x2a` tiene `sts_id=6`, distinto. Fuente de ese campo en el código del TopologyManager: `TM::createLifeCycles` (ELF `0x4185c0`, Ghidra `0x4295c0`) lee `StsId` de cada fila (`+4`) y lo pasa como quinto argumento al constructor de `TopologyLifeCycle` (`0x42b6c0`), que lo almacena en un objeto auxiliar interno (`0x4518d4`) — en el código revisado no se usa para bloquear ni excluir otras filas; es un dato que se propaga para el visor de estado (`StsViewer`), no un cerrojo de exclusión mutua. **INFERENCIA:** nada en `TM::createLifeCycles` impide que las tres filas estén activas a la vez; la exclusión, si existe, tendría que imponerla el propio ObjEffect (sus modos internos) al decidir si reenvía el YC entrante hacia ambas salidas o solo una.

## 3bis. Todas las filas que tocan a Effect(9) — patrón de agrupación por StsId (VERIFICADO, nuevo)

Volqué todas las filas de la tabla con `src_obj==9` o `dst_obj==9` (21 filas). Confirma que Effect tiene exactamente 6 entradas YC (in#0..in#5) y 5 salidas YC (out#0..out#4), como ya se afirmaba en sesión 14 (ahora contrastado con el volcado completo, no solo una fila).

Patrón por `sts_id`:
- `sts_id=0`: conexiones "principales" de un solo pin — Camera(8) out0→Effect in0 (`0x0a`), Effect out0→Renderer in0 (`0x07`), Player(12) out0→Effect in0 (`0x4`), Scalar(30) out0→Effect in0 (`0x85`), Effect out1→Scalar in0 (`0x86`), objeto 31→Effect in0 (`0x36`), objeto 53→Effect in0 (`0xaf`), objeto 62→Effect in0 (`0xd1`), Effect out0→objeto 0 (`0x43`).
- `sts_id=2`: **grupo de feeds auxiliares de Camera** — Camera out1→Effect in1 (`0xb`), Camera out3→Effect in3 (`0x94`), Camera out5→Effect in5 (`0xce`), objeto 53 out3→Effect in1 (`0xcc`), Effect out3→MovieRec in0 (`0x96`), Effect out4→MovieRec in1 (`0xcf`). Seis filas comparten el mismo `sts_id`, consistente con que `StsId` agrupa topologías que un modelo activa/desactiva **como conjunto** (p. ej. todas las salidas secundarias de Camera hacia Effect/MovieRecorder).
- `sts_id=6`: **solo la fila `0x2a`** (Effect out1→Recorder in0). Ninguna otra fila comparte ese StsId. Es decir, `0x2a` es un grupo de un solo elemento, independiente de los grupos 0 y 2 que usa Live View.
- `sts_id=8`: solo `0x9f` (objeto 46→Effect in0).

**INFERENCIA reforzada:** si `StsId` sirve para agrupar activación/desactivación conjunta (consistente con el uso que le da `TM::createLifeCycles`, §3), entonces activar `0x2a` (grupo StsId 6) es, a nivel de agrupación, independiente de los grupos StsId 0 y 2 que sostienen Live View. Esto no demuestra que Effect internamente reenvíe el mismo frame a ambas salidas (sigue dependiendo de `EffectInternalMode`), pero sí refuerza que el TopologyManager no tiene, en su propio diseño de agrupación, un motivo para impedir que `0x2a` se añada mientras Live View sigue activo.

## 3ter. Camera y Player comparten el mismo pin de entrada de Effect (VERIFICADO, nuevo)

Fila `0x4`: Player(12) out#0 → Effect **in#0** (mismo pin que Camera en `0x0a`). Es decir, Camera y Player **no pueden alimentar el pin de entrada 0 de Effect a la vez**: un pin de destino solo admite una conexión (un mensaje `ObjIf::ConnectPin` por pin; conectar un segundo origen al mismo `(obj,dir,no)` requeriría desconectar el primero). Esto explica por qué los modelos de reproducción usan la lista `{0xa1,0x7,0x5,0x6}` (Player→Effect→Renderer→Display) y `ModelBootEE` usa `{0xa,0x7}` (Camera→Effect→Renderer): son alternativas mutuamente excluyentes sobre el mismo pin de entrada, nunca ambas activas.

Esto **no afecta** a la topología `0x2a`: `0x2a` conecta la **salida** #1 de Effect (no la entrada 0) con el Recorder. Conectar o desconectar `0x2a` no compite por el mismo pin que `0x0a`/`0x4`. Confirma, con un argumento adicional al de StsId (§3bis), que no hay un conflicto de pines entre tener Camera alimentando Effect (Live View) y tener el Recorder colgado de la salida 1 de Effect (PbCap) al mismo tiempo — la única pregunta abierta (asignada a la Rama A) es si el **modo interno** de Effect reenvía el contenido de in#0 hacia out#1 cuando el origen es Camera y no Player.

## 4. Consecuencia para el puente Camera → Effect → Recorder

- Camera solo empuja (6 salidas YC, nunca recibe). El único punto de entrada de un frame de Camera al sistema de edición/captura es el pin **Effect in#0** (topología `0x0a`).
- Effect tiene **un único pin de entrada YC** (in#0) pero **dos salidas YC independientes** (out#0 a Renderer, out#1 al Recorder vía `0x2a`). Si ambas topologías (`0x0a`+`0x07` para Live View, `0x2a` para el grabador) se crean a la vez, el TopologyManager no lo impide (§3); que Effect internamente copie/reenvíe el mismo frame de in#0 a ambas salidas depende de `EffectInternalMode` (bloqueo ya identificado en sesión 14, asignado a la Rama A en esta sesión).
- `ModelBootEE` (Live View) solo crea `{0x0a, 0x07}` (sesión 14); ningún modelo de disparo localizado crea `0x2a`. Esto sigue siendo el bloqueo real: aunque la topología lo permitiría en teoría, no hay evidencia de que algún modelo de Sony active `0x2a` durante EE.
- Aun si `0x2a` se activara durante EE, la Rama B (Codex) confirma que el PlayData que llega al Recorder en PbCap **no es el frame original**: Effect reserva un par DMM nuevo (`0x50b3f`+`0xe0b00`, tamaños reales ahora verificados: `0x3fc000` B y `0x800` B) y lo rellena por SDF antes de publicarlo. No hay mecanismo verificado por el que Effect reenvíe el frame EE *tal cual* sin ese paso de conversión.

## 5. Clasificación

| Afirmación | Estado |
|---|---|
| Objeto 8 de la tabla = ObjCamera | **VERIFICADO** (antes INFERENCIA fuerte) — constructor real ELF `0x987dc6`, nueve pines, todos de salida, firma idéntica a la fila de la tabla |
| ObjCamera no tiene ningún pin de entrada | VERIFICADO |
| Filas `0x0a`/`0x07` comparten StsId=0; `0x2a` tiene StsId=6 | VERIFICADO (dato de tabla) |
| StsId no bloquea la coexistencia de topologías en `TM::createLifeCycles` | INFERENCIA (por lectura del código; no se encontró comprobación de exclusión) |
| Camera→Effect→(Renderer y Recorder) simultáneos son posibles a nivel de TopologyManager | INFERENCIA — depende de si ObjEffect los permite (pendiente de la Rama A) |
| Ningún modelo de disparo conocido activa `0x2a` durante EE | NO VERIFICADO descartado solo parcialmente (sesión 14: búsqueda no exhaustiva) |

## Nota metodológica

Ghidra headless (`scripts/libobj_dec.sh`) falló en decompilar `0x98c380`/`0x959bdc` directamente (salida corta e incoherente, posible desalineación de función en el proyecto sin análisis completo —se usó `-noanalysis`—). Todo lo anterior se obtuvo con `llvm-objdump` crudo, leyendo literales de registro a mano; es una vía más lenta pero fiable cuando el decompilador falla.

## NO VERIFICADO / pendiente

- Qué hacen las cuatro subfunciones de `0x98c380` después de construir pines (p. ej. `bl 0xa281dc` al final de `0x987dc6`, aparenta construir otro objeto de 0x54 B en `this+0xa0`: no identificado).
- Si existe una topología distinta (no `0x2a`) que un modelo de disparo real cree para alimentar al Recorder desde Camera/Effect durante EE.
- El contenido exacto de `EffectInternalMode` y qué modo permite el reenvío simultáneo a ambas salidas — depende del resultado de la Rama A.
