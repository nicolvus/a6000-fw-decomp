# Revisión automática de informes

Generado por `scripts/review_reports.py` con 12 procesos sobre 757 informes (`docs/capture, analysis, wiki, reports`). Heurística léxica: cada hallazgo es un candidato, no un veredicto.

## Resumen

- Líneas `NO_VERIFICADO`: **2067**; `VERIFICADO`: **2593**.
- **Cerrables (reducen pendientes):** 130 líneas abiertas cuyas direcciones constan como VERIFICADO en otro informe; **1 de nivel A** (además comparten palabras de contenido con la línea verificada, solapamiento ≥ 0,3) y el resto de nivel B (misma dirección, otro asunto).
- **Añadibles (aumentan pendientes):** 153 líneas con «falta/por hacer/sin verificar» y sin marca `NO_VERIFICADO`.
- **Conflictos:** 4 pares de líneas del mismo informe con la misma dirección, una solo NO_VERIFICADO y otra solo VERIFICADO, con solapamiento ≥ 0,25.
- **Errores:** 18 (VERIFICADO sin evidencia: 18).

## Palabras de estado (menciones totales)

- `VERIFICADO`: 5556
- `NO_VERIFICADO`: 1276
- `INFERENCIA`: 851
- `HIPÓTESIS`: 274
- `NEGATIVO`: 179
- `CORREGIDO`: 108
- `BLOQUEADO`: 40
- `REFUTADO`: 11
- `SUPERADO`: 8
- `CONFLICTO_PENDIENTE`: 4

## Informes con más líneas NO_VERIFICADO

- `docs/capture/s21-codex-exposure-to-library.md`: 33 abiertas, 36 verificadas
- `docs/capture/s19-11-effect-modes-camera.md`: 22 abiertas, 6 verificadas
- `docs/capture/s19-camera-yc-contract.md`: 22 abiertas, 12 verificadas
- `docs/capture/s17-claude-a-topology.md`: 19 abiertas, 19 verificadas
- `docs/capture/electronic-still-low-resolution.md`: 18 abiertas, 18 verificadas
- `docs/capture/s19-12-mechanical-shutter-decision.md`: 17 abiertas, 15 verificadas
- `docs/capture/s20-codex-mpr-dcf-chain.md`: 17 abiertas, 47 verificadas
- `docs/capture/branch-claude-objeffect.md`: 16 abiertas, 12 verificadas
- `docs/capture/darwin-via-actualizacion-2026-10-26.md`: 16 abiertas, 31 verificadas
- `docs/capture/liveview-yc-to-encodestill.md`: 16 abiertas, 11 verificadas
- `docs/capture/s64-silent-ram-nvram-test.md`: 16 abiertas, 7 verificadas
- `analysis/s170_illumi/illumi.md`: 15 abiertas, 1 verificadas
- `docs/capture/rea-tema1-vd-integracion.md`: 14 abiertas, 17 verificadas
- `docs/capture/s19-sfra-linux-yc-delivery.md`: 14 abiertas, 31 verificadas
- `docs/capture/shutter-trigger-state-machine.md`: 14 abiertas, 22 verificadas

## Informes con más pendientes sin marcar (a añadir)

- `docs/capture/e25-15-shutmode0-temporizacion-nativa.md`: 10
- `analysis/s125_imaging_rel/imaging_rel.md`: 5
- `docs/capture/e26-r11-bootrom-uart-physical-access.md`: 3
- `docs/capture/e26-r6-recuperacion-bionz.md`: 3
- `docs/capture/silent-shutter-status.md`: 3
- `analysis/s101_shutter_type/pending/report.md`: 3
- `analysis/s116_sfrs/sfrs.md`: 3
- `analysis/s117_augi/augi.md`: 3
- `wiki/14-Estado-actual.md`: 3
- `docs/capture/e24-01-arranque-recuperacion.md`: 2

## Cerrables de nivel A (revisar y retirar la marca)

- `docs/capture/s17-codex-d-fea-lifetime.md:14` (solap. 0.5) → verificado en docs/capture/s16-codex-fea-completion.md

Detalle completo en `review.json`.
