# G22 — traspaso del modo visualización (Codex → siguiente agente), 27-11-2026

Objetivo heredado: «terminar completamente el arnés con el modo visualización idéntico y funcional a la cámara». Estado: **incompleto**. Pausado por contexto de Codex; sin cámara ni firmware ejecutado en hardware.

## Qué quedó hecho (en `main`)
- `9672657d` — la SD de prueba (`SD_MEDIA=1`) ya no pierde `AVIN0001.INP/.BNP` (128 B) ni `DSC00001.JPG` frente a homónimos de la tarjeta anfitriona (copia primero la anfitriona, luego los de prueba). Informe: `reports/g22-pbmedia-prioridad-indice-20261127.md`.
- `423bc59b` — el hilo `openviewer` espera hasta 300 s a `libObj`, `openView`, `pViewManager`, el objeto gestor y su gestor de modelos (`+0x18`) y, si se piden, los eventos iniciales. Test con dependencias tardías/ausentes. Informe: `reports/g22-arranque-espera-gestor-20261127.md`.
- Antes: G22-PBVISTA (registro de vistas y cargador), G22-PLAYVIEW (la tecla abre `view/INDEX_PLAYBACK`, capa `0x17`), G22-PBMODEL (`@M010` = ModelBrowser, lista servida por el índice AV).

## Estado medido
- 2 arranques fríos (`viz5`, `viz6`) llegan a la pantalla de disparo (24 listas, opacidad 0,0823). **No** hay 3/3.
- Reproducción: abre `view/INDEX_PLAYBACK` pero queda **negra** (0 listas, opacidad 0). `model/MEDIA` devuelve 1; `@M010` devuelve 0; `model/INDEX_PB` responde 1 en códigos 0 y 1. Crear `@M010` a mano no cambia su retorno. El invitado sigue vivo.
- Esperar solo `libObj`/`openView` no basta: abrir `view/ROOT` sin gestor listo → SIGSEGV en `libObj+0x7f25e6` (`[r0+0x10]`, r0=0). Ese intento se retiró.

## Siguiente eslabón (hipótesis, sin verificar)
Quién crea/inicializa `@M010` (ModelBrowser) y por qué su retorno sigue 0 con medio=1 e índice válido. La estructura de los registros del índice sigue siendo hipótesis: no está demostrado que el firmware la lea.

## Pasos propuestos
1. Tercer arranque en frío con el perfil `viz6` sin trampas PLT (estabilidad 3/3).
2. Con REA sobre `libObj`/`viewUnified3.so`: seguir la creación de `@M010` desde `INDEX_PLAYBACK` hasta el retorno 0; comparar contra `docs/gui/g22-pbmodel-modelobrowser.md`.
3. Medir en el invitado (`TRACE 1250c0` del shim ya imprime nombres de modelo/vista) si se lee `AVIN0001.INP`.
4. Cuando la lista se llene, validar el dibujo de la miniatura (`DSC00001.JPG`).

## Evidencia
`reports/evidence/g22-arranque-gestor-20261127/` (arranques, `viz6-before/after.png`) y `reports/evidence/g22-visualizacion-traspaso-20261127/viz7-extracto.txt` (trazas del shim en `viz7`, sin conclusión propia).

## Notas de entorno
- Cambios sin commitear en `scripts/gui/harness/im.sh` y `shim/sonyshim.c` son del trabajo WBI (`ANDROIDFS=real`), no de visualización.
- Pruebas relevantes: 20 pasan; la suite de conocimiento tiene 2 fallos de triaje ya conocidos.
