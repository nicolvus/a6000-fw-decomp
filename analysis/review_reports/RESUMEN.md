# Revisión automática de informes

Generado por `scripts/review_reports.py` con 12 procesos sobre 757 informes (`docs/capture, analysis, wiki, reports`). Heurística léxica: cada hallazgo es un candidato, no un veredicto.

## Resumen

- Líneas `NO_VERIFICADO`: **1801**; `VERIFICADO`: **2593**.
- **Cerrables (reducen pendientes):** 112 líneas abiertas cuyas direcciones constan como VERIFICADO en otro informe; **1 de nivel A** (además comparten palabras de contenido con la línea verificada, solapamiento ≥ 0,3) y el resto de nivel B (misma dirección, otro asunto).
- **Añadibles (aumentan pendientes):** 503 líneas con «falta/por hacer/sin verificar» y sin marca `NO_VERIFICADO`.
- **Conflictos:** 3 pares de líneas del mismo informe con la misma dirección, una solo NO_VERIFICADO y otra solo VERIFICADO, con solapamiento ≥ 0,25.
- **Errores:** 18 (VERIFICADO sin evidencia: 18).

## Palabras de estado (menciones totales)

- `VERIFICADO`: 5290
- `NO_VERIFICADO`: 1010
- `INFERENCIA`: 851
- `HIPÓTESIS`: 274
- `NEGATIVO`: 179
- `CORREGIDO`: 108
- `BLOQUEADO`: 40
- `REFUTADO`: 11
- `SUPERADO`: 8
- `CONFLICTO_PENDIENTE`: 4

## Informes con más líneas NO_VERIFICADO

- `docs/capture/s21-codex-exposure-to-library.md`: 29 abiertas, 36 verificadas
- `docs/capture/s19-11-effect-modes-camera.md`: 22 abiertas, 6 verificadas
- `docs/capture/s19-camera-yc-contract.md`: 22 abiertas, 12 verificadas
- `docs/capture/s17-claude-a-topology.md`: 18 abiertas, 19 verificadas
- `docs/capture/electronic-still-low-resolution.md`: 17 abiertas, 18 verificadas
- `docs/capture/s19-12-mechanical-shutter-decision.md`: 17 abiertas, 15 verificadas
- `docs/capture/s20-codex-mpr-dcf-chain.md`: 17 abiertas, 47 verificadas
- `docs/capture/branch-claude-objeffect.md`: 16 abiertas, 12 verificadas
- `docs/capture/s64-silent-ram-nvram-test.md`: 16 abiertas, 7 verificadas
- `analysis/s170_illumi/illumi.md`: 15 abiertas, 1 verificadas
- `docs/capture/liveview-yc-to-encodestill.md`: 14 abiertas, 11 verificadas
- `docs/capture/rea-tema1-vd-integracion.md`: 14 abiertas, 17 verificadas
- `docs/capture/s19-sfra-linux-yc-delivery.md`: 14 abiertas, 31 verificadas
- `analysis/s68_power/battery_power.md`: 14 abiertas, 11 verificadas
- `docs/capture/rea-tema2-imx210-parametros.md`: 13 abiertas, 13 verificadas

## Informes con más pendientes sin marcar (a añadir)

- `docs/capture/darwin-via-actualizacion-2026-10-26.md`: 11
- `docs/capture/e25-15-shutmode0-temporizacion-nativa.md`: 10
- `docs/capture/e25-04-recuperabilidad-y-decision.md`: 8
- `docs/capture/e25-19-verificacion-fisica-exposicion-larga.md`: 8
- `docs/capture/e26-r5-loader3-servicio.md`: 8
- `docs/capture/t052-a-parametros-reales.md`: 8
- `docs/capture/e26-r11-bootrom-uart-physical-access.md`: 7
- `docs/capture/s21-claude-button-to-shutter-order.md`: 7
- `docs/capture/silent-integration-design.md`: 7
- `docs/capture/e25-11-r5-bionz-analisis.md`: 6

## Cerrables de nivel A (revisar y retirar la marca)

- `docs/capture/s17-codex-d-fea-lifetime.md:14` (solap. 0.5) → verificado en docs/capture/s16-codex-fea-completion.md

Detalle completo en `review.json`.
