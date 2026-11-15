# G53 — Multiple Exposure: ¿se puede reutilizar el motor de fusión nativo? (parcial, estático)

Fecha 15-11-2026. Solo estático sobre `av-cam.bin` 3.21 (Capstone + cadenas) y `libObj.so`; sin cámara, sin parche, sin CFW, sin sesión REA (consultas por bytes).

## 1. Qué es el «motor» (hipótesis de partida corregida)
- `HME_BaseTar/Ref_Addr` (`0x7ab1c6`/`0x7ab23c` en g49) pertenecen al módulo `[APL]` = **ApolloSA** ([s119](../../analysis/s119_apl/apl.md)). Sus entradas son imagen objetivo, imagen de referencia, `Work`, `Vec` y `Result`; la salida es la «Output Ref Img» y vectores. **Es estimación de movimiento (HME), no un mezclador**: no hay en `InputPrm` ni en las cadenas campo/enum de operación (suma, máximo, mínimo, peso).
- Consumidores verificados: panorámica (`ExecutePanoramaTC1ST`, llamada `0x437f1324`) y la etapa de captura `Stage_Apollo` (`0x438bddf0` → `bl 0x438730b0` en `0x438bdeac`, error `ApolloNrBase err:0x%x`). `Stage_Apollo` solo corre con `ctx+0x534c ∈ {2,4}` y exige el contexto `ctx+0x4ad0` (≠0); despacha por modo (`0x43b1bb4c`, `0x438be020`, `0x437f06c0`, `0x437ed568`).
- La mezcla ponderada de MFNR no está en ese HW: los parámetros del filtro de las tomas combinadas aparecen en `MARBLE STL_APOLLO` (`ccnr.cc_bl14/48_*`, `marble_y.yy_emodu_*`; mismas formas que STL_CAP/STL_KKNR/STL_PANORAMA), es decir, **coeficientes de reducción de ruido**, no una operación seleccionable.
- En `libObj.so` solo hay los ParamID `PARAMID_MULTI_FRAME_NR`, `…_NR_LEVEL`, `PARAMID_MULTI_NR_PROGRESS_POS/MAX` y `pvt_subActionObjectMultiNrProcEvt` (g41): nivel y progreso, sin operación.
- No hay cadena `Twilight`/`HandHeld`/`AntiMotion` en `av-cam.bin`; el HHT/AMB de la A6000 es la misma ruta Apollo/MFNR con otro `PARAMID`, no un motor distinto.

## 2. Respuestas a (a), (b), (c)
| | Resultado |
|---|---|
| (a) operaciones | **No encontradas** (ni promedio/suma/máx/mín como parámetro). La fusión es NR ponderada con vectores de movimiento; no se ve un selector de operación. NO VERIFICADO el interior de `sa_func_*` (firmware del SA, no en `av-cam`). |
| (b) desactivar alineación | **No hay parámetro**: la HME produce `Vec`/`Result` y la fusión los consume. Poner el vector a 0 exigiría parchear el contenido de `Vec_Addr` o saltarse `0x438730b0`, no un bit de configuración. NO VERIFICADO sin ejecución. |
| (c) nº de tomas / ráfaga | NO VERIFICADO. Solo hay contadores de progreso (`MULTI_NR_PROGRESS_MAX`); el modelo es una ráfaga única por S2 (`CapMgr ExpCnt`). Nada indica búfer conservado entre pulsaciones. |
- Referencia Sony (app «Multiple Exposure»): no hay copia en el repo (`firmware/`, `analysis/`); no se pudo mirar qué servicio llama. Además, por regla, no cuenta como solución.

## 3. Diseño integrado (lo que sí es concreto)
- **Menú**: entrada nueva sin sustituir, por `scripts/gui/add_menu_entry.py` + `menu_tables.py` (patrón g39, páginas `PAGES`); validada en arnés por overlay como g39. Parte barata, pero sin motor detrás no tiene efecto.
- **Motor**: reutilizar Apollo/MFNR **no basta**: MFNR promedia con rechazo de movimiento y no es «aclarar/oscurecer/suma». La vía realista es un **mezclador propio** (código en cueva del `.dat`, píxel a píxel con NEON sobre las 2–9 imágenes ya desarrolladas en RAM; 24 MP × 9 tomas ≈ 450 MB si se guardan a 16 bit: **no cabe**; habría que acumular en un solo búfer, lo que sirve para suma/promedio/máx/mín y para Live Composite).
- **Limitaciones**: ráfaga única por pulsación (varias pulsaciones requieren conservar el acumulador entre disparos; hay que localizar dónde se libera el búfer de captura).

## 4. Veredicto: PARCIAL (investigación; sin parche)
Hipótesis de reutilización de MFNR **no confirmada y poco probable** (HME es solo movimiento). No se escribió parche porque no hay parámetro de pocos bytes que cambie la operación. Pendiente por fases: `MULTIEXP-ACC` (F1 localizar acumulador/búfer de captura y la etapa donde acumular; F2 cueva `acc_max/add/avg` probada en Unicorn con test de bytes; F3 entrada de menú con overlay).
