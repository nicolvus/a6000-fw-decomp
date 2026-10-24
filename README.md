# Sony A6000 Firmware Reverse Engineering

## Auditoría vigente (23-10-2026)

[Revisión de la validación S605–S627](docs/capture/S605-S627_tabla_hallazgos.md): las 263 pruebas originales ocultaban siete direcciones gemelas erróneas, 13 textos truncados y cinco longitudes adicionales incorrectas. Corregidos JSON, informes y verificadores; 94 trazas y siete gemelas comprobadas con bytes exactos. El logger dual de S607/S611 está verificado estáticamente para seis/cinco trazas; las otras 21 fichas, equivalencias y ausencia funcional del obturador siguen NO_VERIFICADO. Ampliación S605–S627: diez marcadores `level`/`sub_prefix` verificados; S625 corregido a prefijo `[CAM_UTIL_SENS]: ` (17 B). Quedan **67 de 69** afirmaciones de logger dual/equivalencias sin verificar. [Auditoría](docs/capture/S605-S627_tabla_hallazgos.md).

[Resultados, correcciones y límites](docs/auditoria-2026-10-23.md): errores de destinos BL, encodings S384, 94 direcciones de trazas y 21 longitudes corregidos; triaje automático reabierto. Censo documental sincronizado (133/372); 21 pruebas físicas propuestas. [Contrato RecordStill/RecordImage](docs/capture/recordstill-contract-audit-2026-10-23.md): corregida la etiqueta de `0x90b248`, recuperadas las parejas A6000/A7S y el consumidor `StateMgr::CallFunc` de 25 punteros Thumb; activación real y equivalencia de ejecución pendientes. Los demás logger dual siguen pendientes.

Proyecto de ingeniería inversa del firmware **Sony A6000 (fw 3.21)**, con foco en la línea de captura y el obturador electrónico.

> Restricciones activas: sin ejecutar firmware en cámara, sin flasheo y sin pruebas físicas no autorizadas.

## Estado rápido

- **Resumen operativo:** [`knowledge/CURRENT.md`](knowledge/CURRENT.md)
- **Estado de investigación y reglas:** [`docs/STATE.md`](docs/STATE.md)
- **Historial de fases:** [`knowledge/PROGRESS.md`](knowledge/PROGRESS.md)
- **Agentes autónomos y triaje S400:** [`docs/agentes-opencode.md`](docs/agentes-opencode.md), [`revisión manual y evidencia S400`](analysis/s400_open_questions_triage/README.md) (471 filas históricas; 47 relaciones vigentes pendientes; 37 decisiones anteriores revisadas)
- **Catálogo de hitos técnicos:** [`docs/capture/linea-general-re.md`](docs/capture/linea-general-re.md)

## Avance total

- **Censo documental de etiquetas:** **35.75%** (**133/372**) cubiertas — **94** con hito propio y **39** como subetiqueta; **226 pendientes y 13 fragmentos descartados como módulos**. La [auditoría S178](docs/capture/s178-census.md) acepta cuatro candidatas sin cerrar su decodificación y mantiene 222 NO_VERIFICADO. Descartar no aumenta cobertura.
- **Cobertura de la ruta del obturador:** [matriz de descompilación y límites REA/Unicorn](docs/capture/s51-static-coverage-and-tool-limits.md). Persisten enlaces y cuerpos sin reconstruir; se posponen todas las pruebas físicas hasta completar la ingeniería inversa necesaria.
- **Módulos “contenido nuevo” (S130):** **100%** (**17/17**) cerrados.
- **Obturador completamente electrónico:** [S51](docs/capture/s51-decision.md) mantiene la decisión de no parchear; [P1–P8](docs/capture/physical-test-plan.md) y [P13–P21](docs/capture/physical-test-plan-2.md) siguen sin ejecutarse.

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)

![progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/progress.svg)

<sub>GitHub no permite incrustar páginas en el README: los badges se leen de Pages y se actualizan con cada despliegue; el tablero completo (cuadrados, familias, prioridades) está en la [página de progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/).</sub>

Fuente de métricas: [`analysis/s178_census/census.md`](analysis/s178_census/census.md).

### Visualización en GitHub Pages

- Tablero de avance en cuadrados (módulos, sesiones y pruebas físicas, estilo [AnyPS5](https://boykopovar.github.io/AnyPS5/progress.html)): <https://nicolvus.github.io/a6000-fw-decomp/progress/>
- Índice de sesiones y verificador Sx: <https://nicolvus.github.io/a6000-fw-decomp/> (generado desde los informes versionados).

El flujo [Pages](.github/workflows/pages.yml) publica solo `site/`; el generador
`scripts/build_pages_status.py` actualiza el índice y genera `docs/progress/index.html` y los badges `site/badge-*.json` y `progress.svg` (solo en Pages).

## Agente A — sensor y driver (S200–S204)

Completado: comparación de registros y tiempos de lectura/exposición IMX235 (A7S fw3.20) vs IMX210 (A6000 fw3.21), una tabla por subsistema (`docs/capture/s201-imx210-imx235-registers.md`, `s202-imx210-imx235-timing.md`, `s204-clasificacion-final.md`). La A7S implementa el obturador silencioso por **drive mode** (`tipo==2` → modos `0x4e`/`0x4f`, selector `0x43826d58`) y su tabla de timings, no por `CheckSet*` de LiroSeq (0/0 en ambos) ni por mensaje `…ForLiro` (rechazado en ambos). La A6000 no tiene modos de lectura silenciosa equivalentes. **S51 sin cambios (A=NO, B=NO, C=NO).**

## Agente B — imager: estado, drive modes y gates (S300–S399)

S300 cierra el barrido único de xrefs al objeto de estado del IMX210 (`0x43f72d02`, slot GOT `0x4401f990`): 67 sitios clasificados (56 lectura, 6 escritura, 3 spill, 1 propagación, 1 dato), **cero escritores de los gates `+3`/`+6`** (8 lectores de cada uno en el dumper `FUN_43858338`) y únicos stores a `+0x00`/`+0x02`. Corrige el sesgo +0x58 de la rev.1. [`docs/capture/s300-state-xref-sweep.md`](docs/capture/s300-state-xref-sweep.md).

S301 repite el barrido en la **A7S fw3.20** (estado `0x43f7bce6`, slot GOT `0x440251e4`): 79 sitios (65 lectura, 8 escritura, 4 spill, 1 propagación, 1 dato). Gates `+3`/`+6` **idénticos** a la A6000 (mismo dumper, 8+8 lecturas, cero escritores) → no son el mecanismo silent. La A7S añade escrituras en `+0xde` y `+0xe6/+0xe8/+0xea` y 11 campos de lectura que la A6000 no usa. [`docs/capture/s301-a7s-state-xref-sweep.md`](docs/capture/s301-a7s-state-xref-sweep.md).

S302 compara drive mode y exposición campo a campo: la función de comprobación de parámetros desplaza **todos** sus offsets (contexto +8, `VdNum` +0xc, `svr_num` +0x10) y el bloque copiado pasa de 4 a 3 palabras; la A7S añade una indirección modo→columna (34 códigos en `0x43fee370`, mapa `0x43c9c5b5`) sobre una matriz de 69 filas × 16 B (A6000: 59). Los modos Silent `0x4e/0x4f` comparten columna de registro con `0x4c/0x4d` (contradicción a re-verificar con S204). [`docs/capture/s302-drive-modes.md`](docs/capture/s302-drive-modes.md).

S303 resuelve el árbol de referencias de la tabla `0x43ff3200`: **148** entradas (la rev.1 contaba 60), terminador `0x43ff3450`, estado en el índice 18; único literal de la base en el slot GOT `0x4401f080`. El dumper de gates tiene **2** callers directos (`0x43859868`/`0x43859892`, ambos en `FUN_43859710`), que a su vez recibe 10 llamadas de 7 funciones; `FUN_43859944` acumula 35. Corrige el sesgo +0x58 de S303rev1/S304. REA confirma 1/5 funciones y **no ve** el slot `0x4401f080` (undecodable); por bytes su usuario está en `0x4378bb6c`. [`docs/capture/s303-ref-tree-43ff3200.md`](docs/capture/s303-ref-tree-43ff3200.md).

S307 localiza el origen de las escrituras exclusivas de la A7S: `+0xde` (`0x4386521a`) y `+0xe6/+0xe8/+0xea` (`0x438643a6/b2/bc`) viven en funciones cuya firma de store de 24 B **no existe en la A6000** (0 coincidencias); dos escritores de `+0x02` también son A7S-only. `FUN_438645bc` (tiempos: lee `+0xae`×1000) tiene un único caller directo (`0x43861be4`) y ningún puntero. [`docs/capture/s307-a7s-only-writers.md`](docs/capture/s307-a7s-only-writers.md).

S308 cierra el flujo: el código de modo del selector (`0x4e/0x4f`) se guarda en `[sp+0x2c]` y se pasa a `0x43ad9704` (thunk de llamada virtual, S310), **no** al bloque de tiempos; éste (`0x438645bc`, entrada corregida) tiene un único caller `0x43861be4` y ningún puntero en tablas. El enlace silent→tiempos queda **NO_VERIFICADO**. [`docs/capture/s308-silent-flow.md`](docs/capture/s308-silent-flow.md).

S309 comprueba la presencia de la cadena silent/config en la A6000: las **siete** funciones (selector, caller, constructor de mensaje, bloque de tiempos y sus dos escritores) tienen **0 coincidencias** de sus primeros 24 B. La diferencia no es un valor distinto en el mismo código: es **código ausente**. [`docs/capture/s309-chain-presence.md`](docs/capture/s309-chain-presence.md).

S310 corrige el mecanismo del paso anterior: `0x43ad9704` es un **thunk de llamada virtual** (`obj->vtable[slot]`), no un constructor de mensajes; la familia contigua usa slots `0x64/0x94/0x58/0x74/0x40/0x18`. El consumidor del modo queda en una llamada virtual no resuelta → **NO_VERIFICADO**. [`docs/capture/s310-vtable-thunk.md`](docs/capture/s310-vtable-thunk.md).

S311 cierra la comparación simétrica: de los cuatro escritores de `+0x00`/`+0x02` de la A6000, **dos no están en la A7S** y dos son helpers compartidos. Cada firmware trae su propio código de configuración; el de la A7S añade el selector y el bloque de tiempos. [`docs/capture/s311-a6000-config.md`](docs/capture/s311-a6000-config.md).

S312 cierra el círculo del cluster A7S `+0xae`/`+0xde..+0xea`: sus **seis** funciones consumidoras también tienen **0 coincidencias** en la A6000. Con S300–S311, el cuadro queda: gates idénticos sin escritor, matriz de registros con indirección en la A7S, selector `tipo` y subsistema de tiempos exclusivos de la A7S. [`docs/capture/s312-cluster-consumers.md`](docs/capture/s312-cluster-consumers.md).

S313 consolida el carril B (S300–S312): gates `+3/+6` idénticos y sin escritor, matriz de registros con indireccion solo en la A7S, y un subsistema de selector/tiempos (`0x43826d58`, `0x438645bc`) exclusivo de la A7S; documenta lo abierto (objeto/vtable del slot `0x64`, tabla `0x43fee3f8`, semántica física). [`docs/capture/s313-synthesis-carril-b.md`](docs/capture/s313-synthesis-carril-b.md).

S314 corrige la premisa del slot `0x64`: en `0x43549084` se carga `r1` (`[ctx+8]+0x21c`), el thunk del slot `0x64` es `0x43ad96f8` y `0x43ad9704` va a `0x43ad9ada` (`vtable+0x24`). La tabla `0x43fee3f8` es un array de **95** registros de 6 B (no 19), terminador `0x43fee574`; la A6000 no tiene el par `+0x21c/+0x220`. [`docs/capture/s314-selector-object.md`](docs/capture/s314-selector-object.md).

S315 localiza el consumidor `0x436f44c4(obj,modo,lista)`: aplica tres listas NULL-terminated — L95 (95 registros, modo 2), L5 (5, modo 0) y L1 (1, modo 2) — resueltas por getter/GOT (`0x436f4588`→`0x4402c940`, `0x44025ec0`, `0x440292b0`). L5 no es subconjunto de L95 y el consumidor es exclusivo A7S. [`docs/capture/s315-register-lists.md`](docs/capture/s315-register-lists.md).

S316 identifica la clase dueña de las listas: constructor `0x436f27b4`, vtable `0x43fce050` (45 entradas, metadata `0x43fce048`), métodos de listas en `+0x38`/`+0x44` y wrapper `0x43ad9840` en `+0x04`; exclusiva A7S. [`docs/capture/s316-class-vtable.md`](docs/capture/s316-class-vtable.md).

S317: `obj+0x2b4` indexa tres tablas paralelas de stride `0x1c` (T1 `0x43bbeb70`, T2 `0x43bbf2ec`, T3 `0x43bbef34`; campos `+0x14`/`+0x18`), con 34 filas entre T3 y T2; bases confirmadas por REA/Ghidra y entrada exclusiva A7S. [`docs/capture/s317-mode-tables.md`](docs/capture/s317-mode-tables.md).

S318 identifica el constructor paramétrico `0x436f3fc0(obj,idx)` (misma vtable), la tabla `0x43bbe1cc` y el mapeo `1→0x10`/`2→0x40` de `0x43ad9162`; único llamador con `idx=0` y rango válido NO_VERIFICADO. REA confirma el pseudo-código y el segundo usuario del slot GOT `0x4402ac80`. [`docs/capture/s318-ctor-mode.md`](docs/capture/s318-ctor-mode.md).

S319 cierra la frontera estática del `ctx 0x43ea70a0`: 40 sitios, ninguno escribe `[ctx]`/`[ctx+8]`, y 0 literales absolutos en `av-cam` y en `kmod/*`/`lib/*`; veredicto NO_VERIFICADO con candidatos `0x437c7b0c`/`0x437ca5c8`. [`docs/capture/s319-ctx-boundary.md`](docs/capture/s319-ctx-boundary.md).

S320 demuestra que los dos aplicadores de listas usan la misma trama y el mismo formateador: el modo 2 solo añade un reintento tras `0x43ad92e6` si `r0==2`. El modo elige la lista, no la codificación. [`docs/capture/s320-frame-retry.md`](docs/capture/s320-frame-retry.md).

S321 corrige la supuesta tabla de 68 filas: `0x43fee5ac` es la fila 1 de una matriz A7S de 69 filas desde `0x43fee598`; `0x436f3928` selecciona un byte por el mapa de modos y lo escribe en cada registro. Los códigos `0x4e`/`0x4f` comparten columna con otros modos, sin semántica física demostrada. [`docs/capture/s321-matrix-rows.md`](docs/capture/s321-matrix-rows.md).

S322 decodifica `0x43ad9666`: cada registro A7S produce `81|03|device|address8|data8`; 12 escenarios previos confirman 1200/1200 tramas y una trama por registro. El modo 2 conserva la codificación y solo añade el reintento de S320. [`docs/capture/s322-frame-format.md`](docs/capture/s322-frame-format.md).

S324 audita la contradicción «34 columnas» (S202/S204) vs «15 columnas» (S302/S321): `0x43fee370` es un **`u32[34]`** (136 B, termina en L95) y el «29/30» de S204 son **posiciones** en ese array (`0x4c..0x4f` en 27..30), no columnas de la matriz de 16 B. La matriz no tiene ningún par de columnas que difiera en un solo registro (mínimo 2), así que la afirmación «1 registro (`0x000c`/`0x000a`)» no es reproducible con ella; la tabla de 34 columnas queda **NO_VERIFICADA**. Se cierra el setter de modo/sub (slot 8 de la vtable): A7S `0x436f3b44` admite `1..0x51` y guarda `sub` en `+0x2b0`; A6000 `0x436d6b50` corta en **`0x47`** → **rechaza `0x4e`/`0x4f`**, y guarda `sub` en `+0x266`. S51 sin cambios. [`docs/capture/s324-columns-audit.md`](docs/capture/s324-columns-audit.md).

S325 **corrige** la lectura del mapa de columnas: `0x43c9c5b5` es `posición→columna` de **34** entradas (no `modo→columna` de 82), porque el accesor recibe el **índice** que devuelve la búsqueda lineal `0x43ada284` sobre el `u32[34]` de `0x43fee370`. Así, `0x4e` → columna **12** y `0x4f` → **13**, mientras `0x4c`/`0x4d` → **5**: la matriz **sí distingue** el modo silent (14 y 11 registros distintos). Deja sin efecto el «columna 1 / no distingue» de S302/S321. S51 sin cambios. [`docs/capture/s325-position-map.md`](docs/capture/s325-position-map.md).

S326 localiza la tabla de «34» de S202/S204: es **T2** (`0x43bbf2ec`, 34 **filas** de `0x1c`, una por modo) y no una tabla de 34 columnas. `0x4c`/`0x4d` llevan `+0x14 = 0x3ff`; `0x4e` lo baja a 0 (1 campo de diferencia) y `0x4f` además sube `+0x18` de 2 a 3. Igualdades exactas: `0x4e ≡ 0x51`, `0x4f ≡ 0x50`, `0x4c ≡ 0x4d`. Los valores no son una firma silent: `0x3ff` agrupa `{0x13,0x1f,0x4c,0x4d}` y `3` agrupa `{0x0b,0x35,0x4f,0x50}`. S51 sin cambios. [`docs/capture/s326-t2-fingerprint.md`](docs/capture/s326-t2-fingerprint.md).

S327 localiza el escritor de `obj+0x2b4` (índice de fila de T1/T2/T3): solo hay dos, y el único no nulo es el **constructor paramétrico** `0x436f3fc0(obj,idx)`, que guarda su argumento (`r6 = r1`); el único llamador estático pasa **idx = 0**. En la instancia visible se lee la **fila 0**, así que la correspondencia fila↔modo de S326 queda **sin soporte** y las filas 29/30 de T2 no son alcanzables por esa vía. S51 sin cambios. [`docs/capture/s327-row-index-writer.md`](docs/capture/s327-row-index-writer.md).

S328 cierra la segunda matriz de la puerta `sub`: el slot `0x44026088` (A7S) / `0x44026694` (A6000) apunta a una tabla **a cero** (`0x43e8de00` / `0x43e80160`), su offset solo lo usa el propio bucle del accesor y no hay ningún store estático; como la primera palabra es el terminador, **el segundo bucle no ejecuta**. Solo un productor en runtime (otro módulo/DMA) la activaría → NO_VERIFICADO. S51 sin cambios. [`docs/capture/s328-second-matrix.md`](docs/capture/s328-second-matrix.md).

S329 cierra la pregunta de la «tabla de tiempos por modo» del A7S: **no existe**. Las estructuras por modo son la lista `u32[34]`, el mapa posición→columna, la matriz de 69 filas (valores de registro) y tres tablas T de `34 × 0x1c` cuyas filas son **(índice a una tabla de 2 descriptores, máscara de 12 bits)** — el único consumidor `0x436f618c` lee solo `+0x14` y `+0x18` y deja 22 B por fila sin leer. De paso **corrige las bases de S317/S326**: T2 está en `0x43bbf2e8` y T3 en `0x43bbef30` (4 B por debajo), con lo que el índice encaja en las 2 filas del descriptor y `T3→T2 = 34 × 0x1c`; las igualdades `0x4e≡0x51`/`0x4f≡0x50` de S326 desaparecen. En la matriz de 69 filas, `0x4e`/`0x4f` difieren de `0x4c`/`0x4d` en **14 y 11** registros (`0x4c≡0x4d`), las 16 columnas son vectores únicos y ningún registro tiene un valor exclusivo de silent. El barrido de las dos regiones de tablas no encuentra ningún array de 34/69 tiempos referenciado. S51 sin cambios. [`docs/capture/s329-mode-timing-tables.md`](docs/capture/s329-mode-timing-tables.md).

S330 comprueba que el constructor `0x436f3fc0(obj, idx)` tiene **una sola** invocación estática (`0x436f2a8a`, con `movs r1,#0`), que no aparece como literal ni en la vtable, y que vive en una **factoría singleton** que publica el objeto en `0x440245cc`. Resultado: `obj+0x2b4 = 0` siempre, así que T1/T2/T3 solo aportan la **fila 0** (modo `0x0b`) y las diferencias por modo de S326 no se aplican por esa vía. S51 sin cambios. [`docs/capture/s330-ctor-instances.md`](docs/capture/s330-ctor-instances.md).

S331 corrige la firma del consumidor `0x436f618c`: la fila de T1/T2/T3 la elige la **posición del modo** (índice de la búsqueda lineal `0x43ada284`), no `obj+0x2b4`, que es un **flag de log** comparado con `#1` antes de reutilizar `r2` como stride. Con esto la correspondencia fila↔modo queda **verificada**, S327 y S330 quedan refutados en su lectura del campo, y la huella silent vuelve a existir en **T2**: `0x4c`/`0x4d` llevan máscara `0x3ff` y `0x4e`/`0x4f` máscara 0 (T1 y T3 idénticas). [`docs/capture/s331-consumer-signature.md`](docs/capture/s331-consumer-signature.md).

S332 mide el mismo mecanismo en la A6000: el setter `0x436d6b50` busca el modo en una lista de **13** códigos, guarda la posición en `obj+0x17c`, aplica la matriz por el slot 40 y llama a `0x436d8e6c(obj+0x18, posición, flag)`, que con stride `0x1c` lee `+0x14`/`+0x18` y rellena **dos** bloques (`obj+0x14`, `obj+0xa1`). Los descriptores están en `0x43c949a7` (3 filas: identidad, la misma permutación del A7S y `1,1,1,1,0,…`). Diferencias medidas: 13 vs 34 modos, 2 vs 3 tablas, descriptores usados `{0}` vs `{0,1}`, máscaras `{0xf00,0xfff}` sin ningún cero vs 30 máscaras cero en el A7S. [`docs/capture/s332-a6000-tables.md`](docs/capture/s332-a6000-tables.md).

S333 contrasta el vocabulario de modos: 12 de los 13 códigos de la A6000 existen en el A7S, `0x2f` es exclusivo de la A6000 y 22 códigos del A7S (incluidos `0x4c`–`0x51`) no están en la A6000. La matriz de 59 filas × 13 columnas de la A6000 produce solo **7** vectores de registro distintos (alias `{0x05,0x07,0x10,0x18,0x19,0x1a}` y `{0x0b,0x2f}`), frente a **15** del A7S (34 modos, 12 grupos de alias); los silent no tienen configuración de registro exclusiva — su distinción está en la máscara de T2. [`docs/capture/s333-mode-vocabulary.md`](docs/capture/s333-mode-vocabulary.md).

S334 sigue el dataflow de los 12 pares que deja `0x436f618c`: **no son valores**, son `(flag, índice de bit)` y se colapsan en una **máscara de 16 bits** (`0x43ada370` → `obj+0x68`; `0x43ada402` → `obj+0xf8`). El `w0` de T1/T2 es un **código de operación** (T1 ∈ {0,1}, T2 ∈ {2,3}) que consume `0x436f5eac`; la máscara se aplica con `0x436f822c` leyendo, complementando, xorando y escribiendo (`op` 0/1). La capa de acceso `0x436f82xx` queda sin resolver. [`docs/capture/s334-pair-dataflow.md`](docs/capture/s334-pair-dataflow.md).

S335 resuelve la capa de acceso de S334: las nueve funciones `0x436f82xx` son **accesores directos de MMIO** (`0xf292b000/4/8` y `0xfc02a00c`, campo de 12 bits + bit 12), no escrituras P2S. La cadena queda `modo → matriz/T → pares (flag,bit) → máscara u16 → MMIO`. La A6000 tiene la misma capa en `0x436dbdf8..0x436dbe8c` con los mismos literales y el mismo número de sitios, lo que confirma que la diferencia A7S/A6000 está en los datos, no en el acceso. [`docs/capture/s335-mmio-layer.md`](docs/capture/s335-mmio-layer.md).

S336 corrige el alcance de «solo se leen `+0x14` y `+0x18`»: las cuatro tablas tienen **13 referencias en 7 funciones** y **cinco** de ellas leen campos de la fila. `0x436f5f7c` copia 20 B de la fila, parchea `+5`/`+7` si `[estado+0x18]&1` y los pasa a `0x43ada310`; `0x436f6240` usa los bytes `+4/+5/+6` como selectores de dos tablas de punteros; `0x436f605c` suma `0x43ada4d8(w0 T1)+0x43ada4d8(w0 T2)`. El significado de `w0` y de `+4/+5/+6` queda NO_VERIFICADO. [`docs/capture/s336-table-consumers.md`](docs/capture/s336-table-consumers.md).

S337 cierra el último candidato del barrido de S329: `0x43fef404` **no** es un `u16[69]` de tiempos sino una tabla de **69 entradas `{u16 código, u16 0x000d}`** (códigos `0x01`..`0x64`), precedida de 169 palabras `0x43f9c622` y **sin ninguna referencia literal** en el blob. El «array de 69» era una ventana que cruzaba dos estructuras. [`docs/capture/s337-fef404-table.md`](docs/capture/s337-fef404-table.md).

S338 identifica el bloque de destino de las máscaras: `0xfc02a00c` es el cuarto DWORD de **`0xfc02a000`**, bloque DFE (literal del bloque en ambos modelos, getter `base+8` en `0x436f2014`/`0x436d2c9c`, y `_DAT_fc02a008 |= 8` en el `DFE_INIT_Start` del mapa Ghidra del repo) y receptor **CISIF** (mismo par de tablas y mismo colapso de 12 pares que S56-B). La cadena completa queda `modo → matriz/T → pares → máscara → registro DFE/CISIF`, sin tocar la RAM P2S (`0xfc088300`). `0xf292b000` sigue sin identificar. [`docs/capture/s338-block-identity.md`](docs/capture/s338-block-identity.md).

S339 acota `0xf292b000..8`: solo hay **6 literales** del bloque en el A7S y **todos** están en los accesores `0x436f8290..0x436f82d0`; la interfaz es de 3 registros con campos de 12 bits y controles `0x1000`/`0x10000`, idéntica en la A6000. Está en la ventana `0xf292x000` (vecinos documentados: GPIO `0xf2910000`, DSP de lente `0xf292d000`) pero **no aparece en la documentación**: identidad NO_VERIFICADA. [`docs/capture/s339-block-f292b.md`](docs/capture/s339-block-f292b.md).

S340 identifica `w0`: `0x43ada4d8` es un *tail-call* a `0x436f74c0`, un conmutador `tbb` de **6 casos** que lee un registro MMIO distinto por caso (`0xf3122300/2200/3300/3200`, `0xfc0a3100/4100`; offset `+0x30` en cuatro y `+0x24` en dos). `0x436f605c` suma la lectura seleccionada por `w0` de T1 y de T2. Por modo, T1 usa canales 0/1 y T2 2/3 (solo `0x50`/`0x51` cambian a 1/3). Qué mide cada canal queda NO_VERIFICADO. [`docs/capture/s340-w0-selector.md`](docs/capture/s340-w0-selector.md).

S341 consolida el carril B (S314–S340) en una síntesis con 27 cifras comprobadas por script: cadena `modo → matriz 69/59 filas → T1/T2/T3 (selector + descriptor + máscara) → pares (flag,bit) → máscara u16 → MMIO DFE/CISIF`, lista de correcciones (mapa posición→columna, bases T2/T3 4 B más bajas, `obj+0x2b4` = flag, pares = índices de bit, destino MMIO, `w0` = selector de canal) y 5 preguntas abiertas con el experimento que las cerraría. [`docs/capture/s341-synthesis-b2.md`](docs/capture/s341-synthesis-b2.md).

S342 reabre `0x43fef404` con el sesgo correcto: S337 solo descartó **literales absolutos**, pero el firmware direcciona tablas con `ldr rX,[pc,#imm]` + `add rX,pc`. Barriendo esas bases aparecen **dos consumidores** (`0x437056f8`/`0x437056fc` y `0x43705754`/`0x43705756`, base `0x43fef404`) que iteran **69** veces y emparejan cada `{u16 id, u16 0x000d}` con un array de 69 punteros a `.bss` (`0x43fef520`, slot GOT `0x44028c78`); los llamadores están en el init de **`Camera::Lens::ODL`**. La tabla tiene **69** entradas en A7S/A6300 y **47** en A6000 (ids `0x4f..0x64` ausentes; subconjunto estricto) y el bucle siempre vale el número de entradas. Sigue **sin** ser una tabla de tiempos y no se indexa por modo: S329 se mantiene. [`docs/capture/s342-fef404-consumers.md`](docs/capture/s342-fef404-consumers.md).

S343 sigue el único camino de datos de las filas T que quedaba abierto: `0x436f5f7c` copia 20 B de la fila, `0x43ada310` les añade los 12 pares y forma un bloque de **44 B**, y `0x43ada480` lo reparte a **5 manejadores** usando `[obj+4]` como **id de canal (0..5)**. El descompresor `0x436f6710` convierte los bytes impares de la fila en nibbles y `0x436f7480` escribe 1 bit por canal; ambos trabajan sobre los **mismos seis bloques MMIO** que lee `w0` (`0xf3122300/2200/3300/3200`, `0xfc0a3100/4100`), con **178** escritores de campo en A7S (177 en A6000: solo falta `0xfc0a3100+0xc` bit 24). La ruta no toca el DFE (`0xfc02a00c`) ni la P2S: es independiente de la ruta de máscaras. [`docs/capture/s343-row-copy-chain.md`](docs/capture/s343-row-copy-chain.md).

S344 decodifica las dos tablas de 3 entradas que `0x436f6240` usa con los bytes `+4/+5/+6` de la fila T1: `0x43bbeb64 = [0,1,4]` (termina en la base de T1) y `0x43bbef28 = [6,5,4]` (empieza al terminar T1). La selección es `row[5]==0 → B[row[6]]` y `row[5]==1 → A[row[4]]`, con el envoltorio `0x436f6278` limitando el índice a `0x21`. Con las filas reales, **32 de los 34 modos A7S dan 1** y solo `0x37`/`0x38` dan 4; los 13 modos A6000 dan 1. Ni el cuerpo ni el envoltorio tienen llamador estático (0 `bl`, 0 literales) → el significado del valor queda NO_VERIFICADO. [`docs/capture/s344-selector-tables.md`](docs/capture/s344-selector-tables.md).

S345 mide la alcanzabilidad de la escritura de máscara: en el A7S el tramo `0x436f4476..0x436f449c` llama en línea recta a `0x436f618c`, `0x436f61f8` (op 0) y `0x436f60ac` (op 1), y en la A6000 el tramo `0x436d8f46..0x436d8f6e` aplica las mismas dos operaciones (`0x43ad94d8`, `b.w 0x43ad9512`) también sin ramas condicionales. No existe un camino de máscara exclusivo de los modos silent: la diferencia A7S/A6000 está en los datos (pares y máscaras), no en la alcanzabilidad. [`docs/capture/s345-mask-reachability.md`](docs/capture/s345-mask-reachability.md).

S346 cierra el origen del array `.bss` `0x43e906f4` que recorre el consumidor B de S342: su dirección aparece **una sola vez** (slot GOT `0x44026240`) y el slot se referencia desde **dos** sitios, ambos de S342, que pasan el array a *thunks* con vtable `+0x2c8`/`+0x2cc`. No hay escritor estático (0 literales fuera del slot, 0 bases PIC); el array lo rellena el servicio de runtime. La A6000 repite el patrón (`0x44020730` → `0x43e8197c`). [`docs/capture/s346-array-producer.md`](docs/capture/s346-array-producer.md).

S347 responde a S342: el segundo campo `0x000d` de la tabla no es un dato por id — vale **13 en las 138 entradas** de los tres modelos y es la **capacidad del bloque de datos** del ODL. El mismo `0x0d` se pasa al inicializador del camino de carga (una sola pareja `0221 0d22` por modelo) y al allocador de la tabla completa, mientras la **cabecera** del mensaje se dimensiona aparte con `0x18` (24 B); el id viaja en el `u16 +0x12` de un prólogo de 20 B **idéntico en los tres modelos**. Los ids de la A6000 son **exactamente** la lista A7S filtrada por `id ≤ 0x4e` con el mismo orden (faltan `0x4f..0x64`); la A6300 es idéntica a la A7S. `LensAberrationData.bin` existe y es **byte a byte idéntico** en los tres firmware (161766 B), no contiene la tabla ni la lista → la lista es código. Corrige el homónimo: en la A6000 `0xd` también es el id de módulo del logger. [`docs/capture/s347-odl-field.md`](docs/capture/s347-odl-field.md).

S348 identifica el callback que el consumidor A del ODL entrega por cada id: **no es un manejador de datos, es un adaptador de `memcpy`**. El puntero (Thumb) apunta a un *shim* de 12 B idéntico en los tres modelos (`push; mov r4,r1; mov r0,r3; mov r1,r2; mov r2,r4; pop; b.w`) con semántica `memcpy(dst=arg4, src=arg3, len=arg2)`, que salta por un veneer `bx pc` a una implementación **ARM** de `memcpy` (huella `e92d4001/e2522004/ba000020/e210c003`: A7S `0x439b3918`, A6000 `0x439c5320`, A6300 `0x43a60384`). Cada shim tiene **un solo usuario**: el bucle de la tabla (A7S `0x43705702`, A6000 `0x436eb2e2`, A6300 `0x43734bee`). Como el único tamaño por entrada es el `13` de la mitad alta de la palabra de especificación, el servicio copia **13 B** hacia el buffer del consumidor: INFERENCIA ALTA, porque la llamada vive en la interfaz importada. [`docs/capture/s348-odl-callback.md`](docs/capture/s348-odl-callback.md).

S380: `libObj.so` A6000 fw3.21 tiene 26 secciones, 1387 imports FUNC y 1771 exports FUNC. PLT corregido: 2420 cuerpos ARM + 391 veneers Thumb; relocaciones GOT separadas de entradas PLT. [Informe](docs/capture/s380-libobj-a6000-map.md).

S381: despacho corregido mediante resolución PLT → GOT. Hay 83/53 candidatos BL/BLX a los registradores de callback síncrono/asíncrono; recuperar el registro de `0x40193` sigue pendiente. [Informe](docs/capture/s381-libobj-a6000-dispatch.md).

S382: dos sitios BL confirmados hacia `RecordStill::Execute`: `0x90de2e` y `0x91634e`. Los supuestos llamadores `0x7484dc` y `0x755af8` eran artefactos de recalcular un destino absoluto. Límites de función y despacho indirecto NO_VERIFICADO. [Informe](docs/capture/s382-recordstill-callers.md).

S383 mensajes `…ForLiro` y SilentShutter en `libObj.so` A6000: los 5 nombres del obturador (`SetSilentShutterModeForLiro`, `SetShutDriveForLiro`, `SetFrontEShutterModeForLiro`, `SetIrisDriveForLiro`, `SetDriveModeForLiro`) están **rechazados** (NON SUPPORTED). `SetShutterTypeForLiro` **no está** en A6000 (solo A6300). Sin efecto en S51. [`docs/capture/s383-forliro-silentlibobj.md`](docs/capture/s383-forliro-silentlibobj.md).

S384 corregido: **9 literales `.text` A6000 con LDR**, transporte de 16 B hasta `osal_snd_msg` y receptor LIRO `0x4381d16c` verificados. `0x4379e93c` instala su puntero en descriptor `0x43ea048c` (campo+0x14=`0x46`). El bucle `0x4356082c`, alcanzable desde una entrada de cabecera LIRO, consume los 372 inicializadores e incluye `0x4379e93c`. `0x4379e8f4 → 0x43b2a162 → 0x43560bb0` consume el descriptor. Pendientes: efecto del servicio indirecto, callback OSAL Linux y enlace Linux↔LIRO. [Informe y evidencia](docs/capture/queue-40193-flow-2026-10-23.md).

S385: métricas ELF A6000/A7S comparadas; `RecordStill::Execute` en A7S NO_VERIFICADO, con referencias a cadenas recuperadas para continuar. No se demuestra ausencia de función ni del ID `0x40193`. [Informe](docs/capture/s385-libobj-a6000-vs-a7s-diff.md).

## Agente C — ruta de control: configuración → LIRO → imager (S401+)

S401 compara la ruta `SilentShutter` A7S fw3.20 vs A6000 fw3.21: el handler LIRO `0x40e3` está **ausente** en la tabla de 220 comandos de la A7S y presente en la A6000 (`0x438032d5`); `…ForLiro` está rechazado (0 soportados) en ambos. [`docs/capture/s401-a7s-silent-control-path.md`](docs/capture/s401-a7s-silent-control-path.md).

S402 mapea cada diferencia a las pruebas físicas P1–P8 (P5, analizador lógico del bus CAIF/Darwin, es la crítica para el bit `no_silent` `0x20` solo visto en la A7S) y propone pruebas nuevas; solo redactado, nada ejecutado. [`docs/capture/s402-physical-test-mapping.md`](docs/capture/s402-physical-test-mapping.md).

## Agente D — módulos de línea general (S500+)

S500 cerrado: módulo `[VDF]` (visor/display) — 243 cadenas en A6000 vs 162 en A7S/A6300; 81 exclusivas de la A6000 concentran la ruta QFHD/4K, el índice EO y el paralaje EVF. 78 funciones contenedoras y 298 xrefs. Informe `docs/capture/s500-vdf.md`, tests `tests/test_s500_vdf.py` (5 verdes). S501 cerrado: módulo `[STK]` (saliencia/tracking) — 76 cadenas en A6000/A7S, 0 en A6300; idéntico A6000/A7S. Código Thumb no sembrado: 143 xrefs sin función resuelta. Informe `docs/capture/s501-stk.md`, tests `tests/test_s501_stk.py` (5 verdes). S502 cerrado: módulo `[EIS]` (estabilización) — 4 cadenas `[CAMERA_IS][EIS]` exclusivas de A6000; 3 funciones. Informe `docs/capture/s502-eis.md`, tests `tests/test_s502_eis.py` (5 verdes). S503 cerrado: módulo `[ZPD]` (zero point detection/AF) — 55 cadenas en A6000 vs 10 A7S/48 A6300; RTTI `Camera::ZPD` completo; 9 funciones. Informe `docs/capture/s503-zpd.md`, tests `tests/test_s503_zpd.py` (5 verdes). S504 cerrado: módulo `[STABILIZER]` (estabilización) — 3 cadenas exclusivas de A6000; 1 función. Informe `docs/capture/s504-stabilizer.md`, tests `tests/test_s504_stabilizer.py` (5 verdes). S505 cerrado: módulo `[VEF]` (efectos/mapas del visor) — 149 cadenas; 59 funciones. Informe `docs/capture/s505-vef.md`, tests `tests/test_s505_vef.py` (5 verdes). S506 cerrado: módulo `[TD]` (codec transcode/decode) — 73 cadenas; 12 funciones. Informe `docs/capture/s506-td.md`, tests `tests/test_s506_td.py` (5 verdes). S507 cerrado: módulo `[VIDENCSTAT]` (estado codificador vídeo) — 70 cadenas; 32 funciones. Informe `docs/capture/s507-videncstat.md`, tests `tests/test_s507_videncstat.py` (5 verdes). S508 cerrado: módulo `[GOLFSHOT]` (detección swing golf) — 63 cadenas REA; 9 funciones. Informe `docs/capture/s508-golfshot.md`, tests `tests/test_s508_golfshot.py` (5 verdes). S509 cerrado: módulo `[WSX]` (BSFS) — 59 cadenas; 28 funciones. Informe `docs/capture/s509-wsx.md`, tests `tests/test_s509_wsx.py` (5 verdes). S510 cerrado: subetiqueta `[RE]` (remote engine) — 54 cadenas; 6 funciones. Informe `docs/capture/s510-re.md`, tests `tests/test_s510_re.py` (5 verdes). S511 cerrado: subetiqueta `[INT_ERROR]` (errores internos SDF) — 53 cadenas; 275 funciones. Informe `docs/capture/s511-int-error.md`, tests `tests/test_s511_int_error.py` (5 verdes). S512 cerrado: módulo `[ENCOUCSTAT]` (estado codificador couc) — 49 cadenas; 29 funciones. Informe `docs/capture/s512-encoucstat.md`, tests `tests/test_s512_encoucstat.py` (5 verdes). S513 cerrado: módulo `[CONFIG]` (volcado config) — 47 cadenas; 1 función. Informe `docs/capture/s513-config.md`, tests `tests/test_s513_config.py` (5 verdes). S514 cerrado: subetiqueta `[BT]` (background tracking) — 44 cadenas; 5 funciones. Informe `docs/capture/s514-bt.md`, tests `tests/test_s514_bt.py` (5 verdes). S515 cerrado: subetiqueta `[AUDPINEDTR]` (emisor de dataflow, audio) — 34 cadenas en A6000/A7S, 79 en A6300; xrefs pendientes. Informe `docs/capture/s515-audpinedtr.md`. Cola regenerada S516+.

## Agente E — módulos exclusivos A6000 (S600+)

**S600** decodifica `[CAM_FUNC_MGR]` (43 trazas, **exclusivo A6000 fw3.21**): gestor de funciones de cámara — cambio de `CapMode` (0x19/0x17/0x1c/0x03), cola de peticiones Snd/Rsv vía **LRB (Link Bridge)** 12 tipos de mensaje, sincronismo HS/VD, predicados AF/AE. 36 cadenas únicas, 14 funciones emisoras (0x43787bc8–0x43809d9a). Ausente en A7S fw3.20 y A6300 fw2.01 (verificado por `strings -a`). Sin efecto directo en S51 (no menciona shutter/silent/electronic). [`docs/capture/s600-cam-func-mgr.md`](docs/capture/s600-cam-func-mgr.md), test `tests/test_s600_cam_func_mgr.py`.

**S601** decodifica `[CAM_SCALAR]` (34 trazas, **exclusivo A6000 fw3.21**): procesado escalar de imagen — pipeline HAPI, `req_sequence_create_stream`, `req_filter_develop`, YC/sdsYC, DMM handles (YCC_FULL/RAW_FULL), NR Level, parámetros ExposureCount/RecordCount/CapMode. 34 cadenas únicas, funciones en 0x4380a710–0x4380c6fa (código Thumb no decompilado por Ghidra ARM). Ausente en A7S fw3.20 y A6300 fw2.01. Sin efecto directo en S51. [`docs/capture/s601-cam-scalar.md`](docs/capture/s601-cam-scalar.md), test `tests/test_s601_cam_scalar.py`.

**S602** decodifica `[REMOTE]` (bajo `[ACCY]`, 32 trazas, **exclusivo A6000 fw3.21**): control remoto de accesorio vía UART — protocolo header `0x25 0x37 0x36` (`%76`), state byte, terminator `0*`. Comandos: NotifyUartCommand, SendCmd, TallyControlCmd (Tally Light), CallForTransaction, AccyCmdClr. Eventos: NotifyAttached/Detached, NotifyUartResponse, Timeout. Estado: GF/SS/Freeze/Photo/Zoom/Tally. 30 cadenas únicas `[ACCY][...][REMOTE]`, funciones en 0x43566xxx (OSAL logger). Ausente en A7S fw3.20 y A6300 fw2.01. Sin efecto directo en S51. [`docs/capture/s602-remote.md`](docs/capture/s602-remote.md), test `tests/test_s602_remote.py`.

**S603** decodifica `[CAMERA_DSP_APL]` (18 trazas, **exclusivo A6000 fw3.21**): driver APL del DSP — MemOpen, DMA (Tar/MEOut/MBLOut/Out/ParamBuffer), eSRAM/DDR alloc/free, sapl_mov_stop TIMEOUT (200 retries), IIB stop timeout. Memoria: TARGET, MEPRIVATE, MARBLEOUT, ESRAM, DDR Base/TAR, 4K2K CORE1. HME, MARBLE, FMT, LGR, IIB. Función principal FUN_436be5ac (13 entry points, ~600 líneas). 18 cadenas únicas, funciones en 0x436bd830–0x436bf7c6. Ausente en A7S fw3.20 y A6300 fw2.01. Sin efecto directo en S51. [`docs/capture/s603-camera-dsp-apl.md`](docs/capture/s603-camera-dsp-apl.md), test `tests/test_s603_camera_dsp_apl.py`.

**S604** decodifica `[LENS_YC]` (22 trazas) y `[IMAGING_RAW]` (18 trazas), **exclusivos A6000 fw3.21**:
- `[LENS_YC]`: lente aberración, Open/Close/LoadLensAberrationData/FreeLensAberrationData/AllocLensAberrationData, AsyncSend/Recieve, structs base (msg_code, option, prg_num, timeout, err_code) y prg (prg_id, usr_unq_id, offset, unit_type).
- `[IMAGING_RAW]`: RawMemMgr (DisableSetMode_Unlock, GetMem, isMemEmpty, FreeRemainingMem, FreeAll, ReserveAll), MemPool (Wait Alloc, AllocArea MemQue/ImgPrm, DMM), MemQue (Req id, FrontQue, Remaining Queue, SetMemoryPool, Add Que Front/Full).
- VERIFICADO: 0 en A7S fw3.20, 0 en A6300 fw2.01. Sin efecto directo en S51. [`docs/capture/s604-lens-yc-imaging-raw.md`](docs/capture/s604-lens-yc-imaging-raw.md), test `tests/test_s604_lens_yc_imaging_raw.py`.

**S605–S617** (misma plantilla, todos exclusivos A6000 fw3.21 y sin efecto en S51; nº de trazas entre paréntesis): `[JPEG]` (17), `[NSX_VOT]` (7), `[CAM_CMD]` (6), `[MOUNT_INFO]` (6), `[CAMERA_IS][DIST]` (5), `[ACCY][INFO][HOUSING]` (5), `[IMAGING_RSRC]` (5), `[CAMERA_IS][MOUNT]` (5), `[MOUNT_WARNING]` (5), `[ZPD]` (5), `[CAMERA_IS][EIS]` (4), `[LENS_PDR]` (4), `[CAMERA_DEVICE][DET_DIR]` (3). Informes `docs/capture/s605-*.md` … `s617-*.md`.

**S618–S627** (mismas condiciones): `[DET_DIR]` (3, idéntico a `[CAMERA_DEVICE]`), `[SENSER]` (3), `[STABILIZER]` (3), `[AVOUT]` (2), `[AVR]` (2), `[JIRO]` (2), `[UTILITY]` (2), `[ADR]` (1), `[CAMERA_DETECT_FC]` (1), `[EO_SW]` (1). Informes `docs/capture/s618-*.md` … `s627-*.md`. Siguiente: S628 `[FILE_NUM]`.

## Objetivo técnico vigente

Responder con evidencia estática si la A6000 puede soportar captura totalmente electrónica a resolución completa, separando siempre:

- **HECHO verificado**
- **INFERENCIA**
- **NO VERIFICADO**

## Estructura mínima del repo

- `docs/capture/`: informes por hito (Sxx)
- `analysis/`: scripts y evidencia reproducible
- `knowledge/`: estado operativo y continuidad
- `projects/electronic-shutter/`: subproyecto del obturador electrónico

## Nota histórica

La versión extensa anterior del README se conserva en:
[`docs/history/README-historial-2026-10-21.md`](docs/history/README-historial-2026-10-21.md)
