# G22-PBMEDIA — medición viz14: la vista ya recibe el medio, pero nadie pide ni sirve `@M010` (27-11-2026)

Perfil `viz14`, `SD_MEDIA=1 SD_MEDIA_CAB=0`, `SHIMEXTRA='PLAYVIEW=1 INSHORT=1 GMILOG=1 WAITLOG=3000 WLALL=1 IMCMDLOG=1'` (**`WLALL=1` es imprescindible**: sin él las líneas `[shim]` no llegan a `shim.log`). Arranque en frío 119 s, 30 listas; luego trazas en caliente y la tecla de reproducción. Evidencia: [`viz14-extracto.txt`](evidence/g22-pbmedia-viz14-20261127/viz14-extracto.txt).

## Medido
1. Tras abrir `view/INDEX_PLAYBACK`: `getModelInfo(@M00A,0)=1`, `(@M00A,64)=1`, `(model/MEDIA,0)=1`. Antes (informe de traspaso) eran **0**; con el índice corregido y el arranque esperando al gestor el medio ya se acepta también desde la vista.
2. Aun así: **0 listas, opacos 0,0**. En ningún momento la vista consulta `@M010` (cero líneas `getModelInfo(@M010,…)` generadas por ella).
3. Sondeo `G @M010`: el modelo **existe** y responde 1 en los códigos 3 (`[1/402]`), 4 (`[1/401]`) y 5 (`[1/12000001][1/100]`); códigos 0, 1, 2 y 6…0x17 → 0.
4. `TRACEFN=dc504` (`MprIf::GetContentInfo`) armado en caliente: **0 disparos**. El servidor de contenidos no pregunta a MPR.

## Conclusión (y límite)
El 0 de `@M010` ya no es «medio no aceptado»: el navegador no recibe la petición que lo pone en marcha. El eslabón es qué evento/acción de la vista de reproducción arranca `ModelBrowser` (condición de creación → `IssueCommandAsync`). `TRACEFN2=dc144` no se confirmó armado (el shim informó «armadas (1)»): repetir con una sola traza por orden. No se ha probado que el lector de `AVIN0001.INP` se ejecute. La reproducción **sigue negra**; el objetivo de identidad con la cámara real no está alcanzado.

## Causa de los cuelgues con dos invitados (nueva)
No es CPU (12 núcleos, carga ≈ 4,6): `/tmp` es tmpfs y los perfiles viejos de `a6viz` ocupaban 2,7 GB con ≈ 10 GB de swap en uso. Borrar `live/viz1..11` bastó para arrancar un segundo invitado en 100–119 s con el de WBI corriendo. Limpiar `/tmp/a6viz/live` antes de medir.

## Siguiente
Desensamblar la creación de `ModelBrowser` (`libObj+0x47fa78`) y qué mensaje de `view/INDEX_PLAYBACK` la dispara; armar `dc144` solo; comprobar con `IMCMDLOG` la categoría/id emitidos.

## Adenda viz15 (27-11-2026): ni el ModelBrowser ni las fábricas se ejecutan tras la tecla
Con `E TRACEFN=47fa78,598930,5d8d94,dc144,dc504` armado en caliente (5 trampas, un solo comando) y la pulsación de Reproducción (`openView(view/INDEX_PLAYBACK,0)` devolvió un puntero): **0 disparos** de `ModelBrowserToInstance` (`+0x47fa78`), `ModelIndexPbToInstance` (`+0x598930`), `ModelMediaToInstance` (`+0x5d8d94`), `IssueCommandAsync` (`+0xdc144`) y `MprIf::GetContentInfo` (`+0xdc504`). Tras la pulsación el invitado queda casi mudo (solo `vdf_if`/`UpdateStatusMonitor`).
- El demonio solo registra `createModel` de 20 modelos en el arranque (`ROOT`, `MEDIA`, `SCALAR_PB`…); **ninguno** es `INDEX_PB` ni el navegador: esos modelos no se crean al abrir la vista con este atajo.
- Hipótesis más probable (sin verificar): `PLAYVIEW=1` solo llama a `openView`; en la cámara la tecla cambia primero el modo (`model/SCALAR_PB`, categoría `ObjCamera`) y es ese cambio quien crea los modelos de la vista. El eslabón es la acción 4 de `convertViewEventToAB` → ScalarDaemon/ObjCamera, no el lector del índice.
- La pantalla tras la tecla (`viz15-despues.png`) es la de disparo con el icono de base de datos en «ERROR» y la tarjeta en «E»; **no se comprobó si ese icono ya estaba antes** de pulsar (el `viz6-before.png` previo no lo tiene): hay que capturar el antes en la misma sesión.
- Evidencia: [extracto](evidence/g22-pbmedia-viz15-20261127/viz15-extracto.txt), [captura](evidence/g22-pbmedia-viz15-20261127/viz15-despues.png).

## Adenda viz16: sondeo `G` con antes/después en la misma sesión
`G` toma el máximo en **decimal** (`G @M00A 80`; `0x48` se leía como 0). `@M00A` (instancia de `model/MEDIA`) responde 1 en los códigos 0…0x80, con parámetros de media: p. ej. `0x4a: [1/12000001/1] [1/4b/2] [1/4c/2] [1/4d/0] [1/64/0] [5/4a/ffffff01]`, `0x4b…0x4e → 0`, `0x4f → [6/53/ptr]`. `model/INDEX_PB` (`@M015`) no responde. Evidencia: `evidence/g22-pbmedia-viz16-20261127/` (antes/después y sondeo). Sin interpretar todavía: qué código y valor espera la vista para pasar de `@M00A` a pedir `@M010`; es la lectura pendiente de `viewUnified3.so` (llamador de `getModelInfo(@M00A,64)`).
