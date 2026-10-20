# A7S 3.20 Silent Shooting: reconstrucción estática y comparación con A6000 3.21 (19-10-2026)

Investigación coordinada: Agente A Claude (Opus 5.5, `work/claude/`) y Agente B Codex (`gpt-5.6-terra`, esfuerzo
`medium`, verificado en el registro de sesión Codex; `work/codex/`). Solo estático: sin cámara, sin ejecución, sin flasheo.
Binarios: A7S `av-cam.bin` `b857d338…103e`, A6000 `av-cam.bin` `b60c845c…6bb9` (base `0x43541000` en ambos),
A6000 `dfe.bin` `fc4e314d…9fcd`. Auto-comprobación: `python3 -I work/claude/tests/test_a7s_silent_facts.py` (11 hechos).

## 1. Arquitectura implicada

- Sensor: **IMX235** en A7S, IMX210 en A6000; mismo DFE **CXD90027GF**, 12 pares sub-LVDS, 54 MHz (manuales Level 3,
  [comparación](../references/a7s-vs-a6000-service-manuals.md)). **REFUTADO** «A7S = IMX157». **DESCARTADO** como sustentado «432 Mb/s» (no figura).
- A7S 3.20 **no incluye `dfe.bin`** (búsqueda por patrón de vectores en todo el árbol: VERIFICADO); `av-cam.bin` A7S contiene host DFE
  (`DFECore`, `DFE_INT`, `GCS2RxLink`, `MPHYRx4ch`, `SubLVDS`) y `C_ImagerCtrl_IMX235`. Dónde reside el código DFE A7S: NO VERIFICADO.
- Toda la lógica Silent localizada vive en LIRO (`av-cam.bin`, ARM dentro del kernel) y en userland (`libObj.so`, UI).

## 2. Traza Silent (detalle: [work/claude/a7s_silent_execution_trace.md](../../work/claude/a7s_silent_execution_trace.md))

UI `CustomSilentShutter` → `libObj` comando `0x40e3` (INFERENCIA en A7S) → receptor `0x437a9cb0` (estado `+0x250`) →
conversor `0x4379ec04` (`{0,2}`) → captura `+0x78c` (tipo 2 ⇒ `+0x748=1`) →
**(a)** selector `0x43826d58`: tipo 2 ⇒ drive_mode `0x4e/0x4f` en `captura+0x4d0` → IMX235 SetMode `0x436f3b44` → columnas 12/13
de la matriz `0x43fee598` (**45/69 campos distintos** de la foto normal `0x0b`) ·
**(b)** banco `0x43862e24` (`banco+0x404 = captura+0x78c`) → política `0x438649bc`: tipo 2 ⇒ **clase de obturación 0** →
(INFERENCIA) SetExposure IMX235 `0x436f4168` ShutMode 0. Transferencia/guardado de imagen: NO VERIFICADO.

## 3. DFE y sensor

- IMX235 SetMode acepta 34 modos (`0x43fee370`) incluidos `4e 4f 50 51`; IMX210 solo 13, sin ellos (SetMode devuelve error 2). VERIFICADO.
- SetExposure: IMX235 ShutMode 0/1/3/4, **2 no soportado**  (S52: la escritura `|=8` en `0x44021ff2` ocurre en todos los modos 0/1/3/4, no solo en 0 — [s52](s52-imx210-electronic-exposure.md)) (VERIFICADO: entrada `tbb` 2 = rama de error). IMX210: 0..4.
  Patrones de bits por clase distintos entre sensores ([tabla](../../work/claude/a7s_shutter_modes_comparison.md)). Significado eléctrico: NO VERIFICADO.
- Direcciones de registro (u16 en ptr-2) y transporte serie al sensor: NO VERIFICADO. DFE A6000: código ARM arrancable,
  83 procedimientos (REA); dispatcher/mailbox sin semántica (Codex, [crosscheck](../../work/codex/crosscheck.md)).

## 4. Comparación A7S / A6000

| Eslabón | A7S | A6000 |
|---|---|---|
| UI Silent | presente | sin `ACT_SilentShutter`/`CustomSilentShutter` |
| `0x40e3` → estado | `+0x250` | `+0x238` (presente, sin consumidor de captura conocido) |
| Conversor tipo 0/2 | `0x4379ec04` | no localizado |
| Selector drive_mode | rama Silent `0x4e/0x4f` | `0x437f7f98`: mismo código **sin** rama |
| Política de clase | rama `tipo==2 ⇒ 0` | `0x43842158`: **sin** rama |
| Modos del sensor | `0x4e/0x4f` con columnas propias | inexistentes |

Discrepancias A/B resueltas por bytes: «ShutMode 2 no soportado en IMX235» (Codex: NO VERIFICADO) → VERIFICADO; fila `0x40e3`
(estructura `{ID, handler|1, 0}` VERIFICADA en ambos; uso por el despachador INFERENCIA). Codex atribuyó a `0x43826dc0` la llamada al
conversor: **incorrecto** (llama al selector; los llamadores del conversor son `0x437b65a0` y `0x43813d90`, REA).

## Hipótesis

| H | Veredicto | A favor | En contra / pendiente |
|---|---|---|---|
| H1 código Silent oculto en A6000 | **Mayormente refutada** | Persisten el comando `0x40e3` y su receptor (`+0x238`) | Faltan conversor, rama de selector, rama de política y modos IMX210 |
| H2 BIONZ carece pero el DFE conserva | NO VERIFICADO | Mismo CXD90027GF | No se trazó ningún comando DFE por drive_mode; A7S sin `dfe.bin` comparable |
| H3 IMX210 admite fin electrónico completo | NO VERIFICADO | IMX210 tiene ShutMode 0 y lectura completa 6000×4000 (~66,8 ms/cuadro, [doc](imx210-video-readout.md)) | Sin datasheet; bits de ShutMode 0 distintos del IMX235 |
| H4 depende de rasgos del IMX235 | **Apoyada parcialmente** | Silent A7S usa modos de sensor dedicados (45/69 campos) | No prueba que el IMX210 no pueda; puede ser solo tabla |
| H5 el DFE requiere comandos por sensor | NO VERIFICADO | Tablas de registros por sensor distintas (en LIRO) | Nada a nivel DFE |
| H6 el límite es coordinación, no sub-LVDS | INFERENCIA débil | Mismo DFE y 12 pares; A6000 ya lee 24 MP electrónicamente en vídeo/LV | Tiempo de barrido 24 MP (~67 ms) vs 12 MP no medido en A7S |
| H7 vídeo/LV A6000 contienen parte de la lógica | INFERENCIA | Modos de lectura electrónica existentes; ShutMode 0 implementado | Sin columna de modo foto-silenciosa equivalente |

## 5. Viabilidad

La A7S implementa Silent con **dos** cambios coordinados (modo de sensor dedicado + clase de obturación 0) y UI. En la A6000
faltan los dos en LIRO y el IMX210 no tiene tabla para `0x4e/0x4f`. Activar «código existente» no es posible: no existe.
Un port requeriría (i) elegir un modo IMX210 válido de lectura completa (`0x0b`/`0x2f`), (ii) forzar clase 0 en la política,
(iii) demostrar que con clase 0 el secuenciador no acciona la cortina, y (iv) que ShutMode 0 del IMX210 inicia/termina la integración
electrónicamente. (iii) y (iv) no están demostrados. **La decisión S51 (no parchear) se mantiene**; esta reconstrucción concreta el
objetivo, no lo habilita.

## 6. Experimentos siguientes (estáticos primero)

1. A7S: consumidores de `captura+0x748` y de la clase 0 en el secuenciador de cortinas (¿se omite el driver mecánico?). Alto valor, sin riesgo.
2. A7S: copia clase → `param+9` (equivalente A6000 `0x4383fd6c`; firma no encontrada aún) para cerrar la INFERENCIA del paso (b).
3. A6000: qué hace el secuenciador con clase 0 (override `+0x36/+0x37`, [S50](s50-parallel-conclusions.md)).
4. A7S `libObj.so`: desensamblar el emisor `0x40e3` (subir INFERENCIA a VERIFICADO).
5. Con datasheet IMX235/IMX210 o traza pasiva autorizada del bus serie del sensor: semántica de ShutMode y de las columnas 12/13.
