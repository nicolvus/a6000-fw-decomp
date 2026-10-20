# Darwin: fases, notificaciones y escrituras de control

Continuación del 16-10-2026. Análisis estático; ninguna ejecución sobre cámara.
Direcciones **ROM**, base `0x4200`; offset de archivo = dirección − `0x4200`.
Complementa [las entradas verificadas](darwin-shutter-entrypoints.md) y
[el transporte CAIF](silent-caif-transport.md).

## Fuentes y comprobación independiente

| Firmware | Archivo relativo a `firmware/extracted/` | SHA-256 |
|---|---|---|
| A6000 3.21 | `fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin` | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` |
| A6300 2.01 | `a6300-fw201/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin` | `6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac` |

**VERIFICADO:** `src/darwin.py` exige uno de estos hashes, valida la instrucción
TBB y recupera las cuatro entradas directamente del original. No modifica
firmware ni proyectos. Reproducción desde la raíz del proyecto:

```sh
python3 -m src.darwin firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin
python3 -m src.darwin firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin
```

Exports en `analysis/ghidra/`: `a6000-darwin-phase-table-verified.json` y
`a6300-darwin-phase-table-verified.json`. Incluyen bytes, destinos y ocurrencias
de punteros de callbacks. Contraste LLVM conservado en
`darwin-phase-caif-independent-disassembly.txt`. Las supuestas instrucciones
que LLVM imprime dentro de los cuatro bytes de tabla son **datos**.

## Cuatro destinos recuperados

**VERIFICADO:** TBB usa `PC = dirección de instrucción + 4`, sin el redondeo
a palabra de las cargas literales. Destino = PC + 2 × byte sin signo.

| Elemento | A6000 | A6300 |
|---|---|---|
| Consumidor | `0x2089c` | `0x23e16` |
| TBB / tabla | `0x208e0` / `0x208e4` | `0x23e58` / `0x23e5c` |
| Bytes de tabla | `44 02 23 49` | `4c 02 23 51` |
| Estado 0 | `0x2096c` | `0x23ef4` |
| Estado 1 | `0x208e8` | `0x23e60` |
| Estado 2 | `0x2092a` | `0x23ea2` |
| Estado 3 | `0x20976` | `0x23efe` |
| Objeto S | `0x200036d8` | `0x200034e4` |
| Configuración C | `0x20000300` | `0x20000300` |
| Rearme de seguimiento | `0x21014` | `0x24d1a` |
| Desactivación de seguimiento | `0x20fde` | `0x24ce4` |

El byte de fase es `S+0x153`. Para cualquier fase >=4 se toma directamente
la misma salida que para 0. No se recupera una rama de error exclusiva para
un índice fuera de rango.

Antes del salto se calcula `m = min(diferencia_unsigned/5, 0xffff)`.
Con selector de variante `0x20cee` / `0x2486e` igual a cero, diferencia =
lector `S+0x180` − contador `0x93e6` / `0x9032`; en la otra variante,
diferencia = `S+0x15c` − lector `S+0x180`. Los lectores son `0x20f8e` /
`0x24c94`. **NO VERIFICADO:** unidad física del contador. La saturación
`0xffff` no equivale por sí sola a un timeout.

| Fase al entrar | Escritura común | Paso siguiente |
|---|---|---|
| 0 o >=4 | No guarda medición ni rearma ADC | Retener la etapa del planificador |
| 1 | `u16(S+0x156)=m` | Rearmar con `(0, u16(C+0x34), buffer, 1)`; fase=2 |
| 2 | `u16(S+0x158)=m` | Rearmar con `(1, u16(C+0x36), buffer, 1)`; fase=3 |
| 3 | `u16(S+0x15a)=m` | Desactivar seguimiento; fase=4 |

Buffer de rearme: A6000 `0x20003834`, A6300 `0x20003640`.
En cada fase 1/2/3 se puede añadir un indicador a `u16(S+0x154)` si
ambos predicados `0x20cee` y `0x21096`, o `0x2486e` y `0x24d9c`,
son no nulos. Máscaras A6000 `2/4/8`; A6300 `0x10/0x20/0x40`.
El predicado A6300 `0x24d9c` salta a `0x1d3e6`, que comprueba si
`u32(0x20002abc+4)==0`. No es una lectura del ajuste Silent.

El monitor de sondeo es independiente: A6000 `0x2065c`, A6300 `0x23752`.
Solo cuando su selector de variante es cero, compara ADC8 con `C+0x36`
en fases 1/3 (estrictamente mayor), y con `C+0x34` en fase 2
(estrictamente menor), y añade las mismas máscaras. **VERIFICADO:** este
monitor no cambia `S+0x153`; las transiciones anteriores ocurren en el TBB.

## Retención del planificador y notificación de fase

**CORRECCIÓN / VERIFICADO:** la salida común salta a `0x1e4c2` / `0x20dae`
y hace `u16(argumento+0x10) |= 0x80`. No llamarlo ACK, final de movimiento
ni captura completada. En A6300, `0x20b20` comprueba precisamente ese bit:
si está activo **no incrementa el índice de la secuencia**. El bit `0x40`
es el que solicita otra iteración inmediata del despachador. Esto corrige
la interpretación provisional de «finalización del callback»; los exports
anteriores se conservan sin reemplazar sus bytes ni su pseudocódigo.

**VERIFICADO:** `0x20c2a` busca el ID actual en registros `{ID, callback}`
de ocho bytes, pasa al callback un bloque local de 20 bytes inicialmente
cero y entrega ese bloque a `0x20b20`. El descriptor `0x2f8e8` usa la tabla
`0x2fa28`, con `0x23e17` (Thumb) para IDs `3/5/7`. Su descriptor hermano
`0x2f8cc` usa `0x2f958`: el ID 3 apunta al inicializador `0x23af5`.
Ambos comparten los punteros de índice/ID `0x20003628/0x20003629` y
la referencia de secuencia `0x20003624`. No confundir estos IDs externos
con las fases internas `S+0x153`.

Ruta estática de notificación A6300:

```text
0x1d3a8: [0x20002abc+4] = 1
  si 0x2486e()!=0
    → 0x22e3e(1)
    → 0x24666(1)
    → descriptor = [literal ROM 0x246f4] - 0x38 + 1*0x1c
                  = 0x2f904 - 0x38 + 0x1c = 0x2f8e8
    → 0x20c2a(descriptor)
    → callback 0x23e16 si el ID actual es 3, 5 o 7
```

**NO VERIFICADO:** qué entrada de interrupción o registro de callback invoca
`0x1d3a8`. No se ha reconstruido toda la cadena desde la señal eléctrica.
La asociación al subsistema ADC se apoya en el estado compartido y sus
consumidores, no en una supuesta correspondencia con CAIF.

A6000 tiene pares equivalentes en ROM `0x29e00` y `0x29e70`, referidos por
descriptores `0x29d90` y `0x29dac`. El inicializador `0x20735` corresponde
al ID 2, y `0x2089d` a IDs `2/4/6` en la segunda tabla. La conexión del
evento externo equivalente A6000 todavía requiere seguimiento dirigido.

## Iniciar, inhibir y escribir control

**VERIFICADO:** A6300 `0x1b988` permite determinadas operaciones si
`(u32(S+0x170)&1)==0` y `0x1788c(0x10)!=0`. Este segundo predicado
comprueba que `u16(S+0x444)&0x10` esté limpio. Hay, por tanto, dos
condiciones diferentes; ninguna ha sido ligada al byte Silent de CAIF.

El escritor `0x1b318` limpia **todo** `S+0x170`, tras inicializar dos módulos.
Lo llama `0xce40`, desde `0x1d1b4`, a su vez llamado por `On main` en
`0x7c74`. El escritor `0x1b906` añade el bit 0, limpia secuencias y ajusta
salidas; lo llama `0xce7c` desde `0xd48a`.
**INFERENCIA:** corresponde a una inhibición de ciclo general/inicialización
y retirada del subsistema. **NO VERIFICADO:** exclusividad de ese ciclo,
significado preciso de `0xd48a` y relación con Silent.

`0x1b366` y `0x1b506` comprueban esa puerta antes de llamar a `0x231f2`.
Esta última llama a `0x24792`, selecciona una secuencia mediante `0x20a3c`,
escribe `S+0x152=3` y despacha por `0x24666`. Esto separa el inicio de
operación del seguimiento de posición.

**VERIFICADO:** A6000 `0x51c0` y A6300 `0x5248` escriben una palabra en
`0x42668000 + argumento0` con el valor del segundo argumento.
Literales ROM `0x55a0` / `0x5648`. No son solo funciones que leen posición.

| Ruta de control | A6000 | A6300 |
|---|---|---|
| Escribir `0x42668234=0` | `0x20cb2`, tipos 1/2 | `0x24792`, tipos 1/2, si argumento habilita |
| Escribir `0x42668234=1` | `0x20c90`, tipos 1/2 | `0x24808`, tipos 1/2, si argumento habilita |
| Limpiar `0x42668238` | `0x20cd4`, tipo !=0 | `0x248be`, tipo !=0 y argumento habilita |
| Variante tipo 4 | No aceptada por selector | `0x24792`: `0x4266811c=0`, `0x42668234=1`; `0x24808` limpia ambos |

**NO VERIFICADO:** si cada dirección corresponde a un pin, señal lógica,
alimentación, bobina o temporizador. No se asignan nombres de cortina a las
salidas. Tampoco se identifica tipo 4 como Silent. La A6300 añade una ruta
de adquisición con tres valores `S+0x19c/+0x1a0/+0x1a4` para tipo 4;
eso es una diferencia de controlador, no prueba de captura electrónica.

## Finalización, errores y frontera siguiente

**VERIFICADO:** la fase 4 termina esta secuencia de seguimiento; el consumidor
deja de guardar mediciones. `0x23c82` consulta esa fase en una rama del cierre:
para fase distinta de 4 llama a desactivación y registra
`0x1781c(6,1,0x20,fase)`. Para fase 4 añade las máscaras `0x10/0x20/0x40`.
Hay otras condiciones y una ruta tipo 4; no generalizar esta prueba a toda
captura ni confundir los indicadores sintetizados con tres lecturas físicas.

**NO VERIFICADO:** timeout exacto que lleva al cierre, final del movimiento
de una cortina concreta y sincronización con la integración/lectura del sensor.

Próximos puntos precisos:

1. Enlazar `0x1d3a8` con la instalación/entrada real de su notificación;
   seguir el equivalente A6000 desde el callback `0x2089c`.
2. Seguir productores de `S+0x444` y resolver el contexto de `0xd48a`.
3. Identificar el banco `0x42668000` y las señales `+0x11c/+0x234/+0x238`
   usando controladores o documentación física; evitar atribuirlas por nombre.
4. Seguir el receptor de la cola CAIF `0x740017` y su canal configurado.
   El enlace con Darwin continúa **NO VERIFICADO**.

Evidencia Ghidra adicional en `analysis/ghidra/`:
`a6300-darwin-shutter-inhibit-writers.json`, `a6300-darwin-capture-shutter-gate.json`,
`a6300-darwin-phase-dispatch.json`, `a6300-darwin-phase-tables-lifecycle.json`,
`a6300-darwin-phase-engine.json`, `a6300-darwin-phase-events.json`,
`a6300-darwin-adc-phase-event.json`, `a6300-darwin-phase-event-dispatch-exact.json`
y `a6000-darwin-control-register-writes.json`.
Algunas consultas interiores resuelven a funciones contenedoras por colas
compartidas; usar las ventanas LLVM para el tramo local. `0x20dae` sigue
fusionado con `0x1afce` en Ghidra: su bloque local fue contrastado con LLVM,
sin eliminar otras funciones ni forzar límites nuevos.

**ACEPTO:** tablas, transiciones locales, retención, ruta de notificación
condicional y escrituras de control demostradas por instrucciones originales.
**RECHAZO:** usar estos resultados como prueba de una foto sin cortinillas,
de un receptor Darwin CAIF o de imposibilidad física del IMX210.
**VEREDICTO: CAMBIOS**. Falta conectar señal, protocolo y lectura fotográfica.

## Validación de esta entrega

- TDD del extractor: prueba inicial fallida por módulo aún inexistente;
  implementación posterior, seis casos nuevos correctos. Incluyen PC Thumb
  sin redondear, imagen alterada, truncamiento y destinos fuera de ROM.
- Suite completa: **32 pruebas correctas** (`python3 -m unittest discover -s tests`).
- Ruff y Mypy: sin avisos, usando los ejecutables del entorno solicitado
  `/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/`.
- SHA-256 de ambas ROM y LIRO A6300 comprobados; vistas ELF Darwin con
  `.text` idéntica al original y dirección virtual `0x4200`.
- Ocho logs de consultas A6300 revisados: sin errores/excepciones; los casos
  `no_recorded_function` y colas compartidas se conservan como limitaciones.
- Enlaces locales de documentos afectados comprobados. Sin instalaciones
  ni acciones sobre cámara. Sin commit: este directorio no es un repositorio Git.
