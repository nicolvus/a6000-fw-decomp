# Backlog B — imager, estado y gates (S300–S399)

Auditado el 24-10-2026. Una casilla completada acredita el entregable indicado;
no convierte en hecho una conclusión marcada NO_VERIFICADO. Los resultados
negativos se limitan a los sitios examinados. [Auditoría vigente](../../docs/capture/repo-audit-2026-10-24.md).

## Entregables existentes

- [x] S300 — [Barrido A6000](../../docs/capture/s300-state-xref-sweep.md): 67 sitios (56 lecturas, 6 escrituras, 3 spills, 1 propagación, 1 dato). La cifra inicial de 15 xrefs estaba superada. No se identifican escritores de gates `+3/+6` en este conjunto.
- [x] S301 — [Barrido A7S y comparación](../../docs/capture/s301-a7s-state-xref-sweep.md): 79 sitios; estado candidato `0x43f7bce6`, GOT `0x440251e4`. El barrido y la tabla comparativa ya están publicados.
- [x] S302 — [Tablas de exposición](../../docs/capture/s302-drive-mode-exposure-tables.md), fórmula de S134 y vectores de registros comparados.
- [x] S303 — [Árbol de referencias](../../docs/capture/s303-ref-tree-43ff3200.md). La falta inicial de llamadores no es un resultado de ausencia; S304 añade un llamador.
- [x] S304 — [Informe del dumper y llamador](../../docs/capture/s304-rea-dumper-callers.md). Se elimina la copia duplicada de esta sección. Los 13 sitios de llamada no prueban 13 iteraciones de un bucle.
- [x] S305 — [Informe parcial publicado](../../docs/capture/s305-fun43858390-literal-pool.md). Publicación completada; análisis completo pendiente.
- [x] S306–S348 — Informes posteriores en el [README](../../README.md) y sus fuentes. La existencia del informe no cierra todos sus límites.

## Preguntas que permanecen abiertas

- [ ] Completar el análisis por tramos de `FUN_43858390` y demostrar su flujo de control y argumentos; S305 sigue parcial.
- [ ] Demostrar el acceso al GOT `0x4401f080` y al objeto `0x43ff3200`, con instrucciones y pools; no dar por cerrado un acceso solo porque exista el slot.
- [ ] Identificar escritores de `state+3/+6` o acotar su procedencia por puntero, copia o productor externo. Los barridos S300/S301 no prueban ausencia global.
- [ ] Resolver los límites del carril B (servicio ODL y significado físico de registros) con evidencia estática; consultar la [matriz S51](../../docs/capture/s51-static-coverage-and-tool-limits.md).

Sin ejecución de firmware, cámara ni flasheo. Las pruebas físicas siguen diferidas.
