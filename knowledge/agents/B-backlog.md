# Backlog B — imager, estado y gates (S300–S399)

Actualizado el 26-10-2026: los pendientes abiertos de este carril están en [PENDIENTES](../../docs/PENDIENTES.md) (E7 y E8 cerrados con límite; E13 BLOQUEADO).

Actualizado el 25-10-2026. Una casilla completada acredita el entregable indicado;
no convierte en hecho una conclusión marcada NO_VERIFICADO. Los resultados
negativos se limitan a los sitios examinados. [Seguimiento vigente](../../docs/capture/capture-static-followup-2026-10-25.md).

## Entregables existentes

- [x] S300 — [Barrido A6000](../../docs/capture/s300-state-xref-sweep.md): 67 sitios (56 lecturas, 6 escrituras, 3 spills, 1 propagación, 1 dato). La cifra inicial de 15 xrefs estaba superada. No se identifican escritores de gates `+3/+6` en este conjunto.
- [x] S301 — [Barrido A7S y comparación](../../docs/capture/s301-a7s-state-xref-sweep.md): 79 sitios; estado candidato `0x43f7bce6`, GOT `0x440251e4`. El barrido y la tabla comparativa ya están publicados.
- [x] S302 — [Tablas de exposición](../../docs/capture/s302-drive-mode-exposure-tables.md), fórmula de S134 y vectores de registros comparados.
- [x] S303 — [Árbol de referencias rev.3](../../docs/capture/s303-ref-tree-43ff3200.md): dumper real `0x43858338`, dos sitios directos en `0x43859710`, acceso GOT ya probado. Prevalece sobre S304/S305 iniciales.
- [x] S304 — [Informe histórico](../../docs/capture/s304-rea-dumper-callers.md), con entradas sesgadas +0x58 y trece llamadas invalidadas por S303. No reutilizar como resultado vigente.
- [x] S305 — [Entradas corregidas y consumidores Backup](../../docs/capture/s305-fun43858390-literal-pool.md). Eliminado el falso pendiente `FUN_43858390`; cuerpo real exportado por REA, GOT y productor indirecto localizados.
- [x] S176 — [Dos lectores reproducidos](../../docs/capture/s176-imager-state-readers.md), con verificador y tests nuevos. El primer lector usa default 6 en su bloque terminal; el segundo realiza ocho anulaciones a cero.
- [x] S306–S348 — Informes posteriores en el [README](../../README.md) y sus fuentes. La existencia del informe no cierra todos sus límites.

## Preguntas que permanecen abiertas

- [ ] Obtener el tamaño/contenido efectivos de Backup `0x3000b` y completar los productores de sus campos. Ya se conoce el destino `0x43f72d02`, la fila 18 de `0x43ff3200`, `Backup_read` y el callback de copia `0x43ae8b7a`; no repetir la búsqueda exclusiva de stores directos a gates `+3/+6`.
- [ ] Determinar condiciones de invocación y efecto de los campos del estado. S176 acredita lectores, no activación durante un disparo ni semántica física.
- [ ] Resolver los límites del carril B (servicio ODL y significado físico de registros) con evidencia estática; consultar la [matriz S51](../../docs/capture/s51-static-coverage-and-tool-limits.md).

Sin ejecución de firmware, cámara ni flasheo. Las pruebas físicas siguen diferidas.
