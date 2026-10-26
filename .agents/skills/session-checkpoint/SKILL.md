---
name: session-checkpoint
description: Continuar una investigación o implementación anterior del proyecto Sony A6000, o registrar el estado al terminar una sesión larga. Úsala al empezar una sesión nueva sobre este repo y antes de parar tras un cambio significativo.
---

# Checkpoint de sesión (continuidad multiagente)

## Cuándo se activa

Al empezar a trabajar en este repositorio tras un reinicio, una compactación de
contexto, o un cambio de agente (Claude Code ↔ Codex); al terminar una fase de
trabajo significativa, antes de que termine la sesión.

## Procedimiento — reanudar

1. Leer `knowledge/CURRENT.md` (contexto operativo mínimo). Consultar solo los pendientes
   relevantes en `docs/PENDIENTES.md` y los informes necesarios (por tema: `docs/INDEX.md`).
2. Leer `docs/STATE.md` para las conclusiones y límites vigentes. `knowledge/PROGRESS.md` es el
   historial cronológico: consultarlo solo si hace falta el detalle de cómo se llegó al estado actual.
3. NO releer los archivos históricos (`docs/history/`, `knowledge/history/`) completos salvo
   que `CURRENT.md`/`STATE.md` no basten.

## Procedimiento — registrar checkpoint

0. Orden de actualización: informe técnico y evidencia → fila afectada de `docs/PENDIENTES.md`
   → `docs/STATE.md` si cambió una conclusión → `knowledge/CURRENT.md` solo si cambió el contexto
   mínimo → `knowledge/PROGRESS.md` → `build_subsystem_index.py`. El README no se toca por cada sesión.
1. Editar `knowledge/PROGRESS.md`: actualizar la tabla de fases, añadir una
   entrada nueva bajo la fase correspondiente con lo hecho/probado/bloqueado,
   y reescribir "Próximo paso exacto" con una instrucción concreta y ejecutable
   (no "continuar con X" vago).
2. No acumular resúmenes largos: una fase ya completa se resume en 3-6 líneas
   con referencias a archivos, no se repite el detalle de cómo se hizo.
3. Si la investigación (no el sistema de conocimiento) avanzó, actualizar
   `docs/STATE.md` y, si corresponde, mover sesiones cerradas de `CONTEXT.md`
   a `docs/history/` (ver fase 4 en PROGRESS.md para el patrón ya usado).

## Entradas / salidas

Entrada: ninguna (lectura) o el resumen de lo hecho en la sesión actual (escritura).
Salida: `knowledge/PROGRESS.md` actualizado.

## Herramientas disponibles

Edición directa de `knowledge/PROGRESS.md` y `docs/STATE.md`. No requiere la DB
ni scripts de `scripts/knowledge/`.

## Limitaciones

Esta skill no verifica que lo registrado sea cierto: quien escribe el checkpoint
es responsable de haber ejecutado/probado lo que declara completo (ver
instrucción del proyecto: "no declarar completado si queda algo esencial pendiente").

## Validaciones

Antes de marcar una fase como COMPLETA en la tabla, confirmar que los tests
relevantes (`pytest tests/knowledge`) y el lint (`ruff`/`mypy`) pasaron en esta
sesión, no en una anterior sin volver a comprobar.

## Referencias bajo demanda

`knowledge/PROGRESS.md` mismo contiene el historial completo de decisiones.
