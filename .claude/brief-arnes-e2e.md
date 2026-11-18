# Brief común: arnés GUI de punta a punta para las funciones objetivo (desde 15-11-2026)

Repo: /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter. Responde en español. Silencio entre herramientas; ahorra contexto (head/grep/wc, nada de cat de ficheros grandes).

## Meta del usuario
Probar cada función objetivo (wiki/16-Objetivos.md) en el arnés GUI de punta a punta (menú → Backup → libObj/ObjCamera → av-cam en la LIRO VM → efecto medible) y verla funcionar o fallar ANTES de la cámara. Lo que se prueba en el arnés debe ser EXACTAMENTE lo que se instalaría: mismos binarios, mismos bytes, misma ruta de carga. Se desarrolla el arnés a la vez que se prueban/arreglan las funciones.

**Si el arnés no tiene la funcionalidad necesaria para probar una función, se desarrolla y se prueba primero en el arnés, y luego se usa para desarrollar/probar la función.** Ejemplo: si la función cambia cómo se ve la foto, se verifica hasta que la foto que produce la emulación (con lo que av-cam realmente escribe/usa: curvas, LUT, matrices, exposición) sea la correcta, para que la cámara dé lo mismo.

**Fotos de referencia** (RAW reales de esta A6000, ya usadas antes): `/home/nicolas/Desktop/16161111/` (DSC03749–03766 `.JPG` y DSC03767+ `.ARW`; `r87/` con DSC03789–03799 `.ARW`, incl. `DSC03799.ARW`) y `analysis/camera-dumps/*/` (T044 ISO100 por velocidad, T046/T047 r5, T049/T050 Silent, r64-fotos). Los JPG de fábrica sirven para validar el revelado emulado contra la salida real de la cámara.

## Reglas
- **No continuar el trabajo de la SD** (recuento STLREC, AVF_INFO, Formatear: G22-E-1g queda aparcado). Si una prueba choca con la SD, busca la vía que la cámara real tiene sin tarjeta (p. ej. «Disparo sin tarjeta») o anótalo; no la persigas.
- Emulación fiel: el arnés solo simula datos verificados que cambian en la cámara real; nada de atajos que valgan solo en el arnés. Un parche de función va en ficheros que entran en el CFW real (nflasha15 `/usr`, nflasha3 BIONZ/av-cam), nunca en el arnés.
- Sin cámara, sin flasheo, sin instalar nada. Construir artefactos locales (árbol `/usr`, `nflasha3`, incluso `.dat`) para cargarlos en el arnés está permitido; nunca se instala.
- Puedes editar `scripts/gui/harness/`, `scripts/gui/avcam/` y sus tests, salvo `scripts/gui/harness/android/` (cambios ajenos sin commit: no tocar). Tests de lo que añadas (`tests/test_gui_harness.py`, `tests/test_avcam_*.py`).
- Perfiles del arnés con nombre propio (`--perfil-dir e2eNN`), puerto libre, y cierra las VM con `POST /salir` al acabar. No mates procesos ajenos.
- REA primero para el firmware (ver memoria reference-rea-daemon-uso.md); verifica lo decisivo contra bytes.
- Git: nunca `stash`/`reset`/`checkout --`/`clean`/`add -A`/`add .`; `git add` solo de tus rutas. Commit Conventional Commits terminado en `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. NO hagas push (lo hace el orquestador).
- Documenta en `docs/gui/g75-arnes-e2e-objetivos.md` (sección por tarea, con MEDIDO/VERIFICADO/NO_VERIFICADO) y añade/actualiza IDs `E2E-*` en `docs/PENDIENTES.md` (estado, origen, criterio de cierre). Corre `scripts/knowledge/build_subsystem_index.py` tras editar `.md`.
- No te detengas en dudas: decide con criterio, prueba otra vía si algo falla.
- Contexto máximo 300k tokens: hacia ≈280k para, commit local y entrega un resumen de traspaso (hallazgos con direcciones, estado, siguiente paso exacto); el orquestador sigue con un subagente nuevo.

## Entrega (≤ 15 líneas)
Qué funciona/falla con evidencia (rutas de capturas, líneas de log, tests), hash del commit, pendientes nuevos.
