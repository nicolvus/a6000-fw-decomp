# S321 — Matriz real de 69 filas y consumidor por modo (resumen; ver canónico)

> **Aviso D4 (25-10-2026):** [S325](s325-position-map.md) y [S329](s329-mode-timing-tables.md) retiran «`0x4e`/`0x4f` comparten la columna 1»: el mapa es posición→columna y `0x4e`→columna 12, `0x4f`→13.

**Documento canónico:** [`docs/capture/s321-matrix-rows.md`](s321-matrix-rows.md)
(evidencia completa en `analysis/s321_matrix_rows/matrix_rows.json`, 138 comprobaciones
del verificador y 14 tests).

**Resultado:** la matriz A7S empieza en `0x43fee598`, no en `0x43fee5ac`, que es su
**fila 1**. Contiene **69 filas** de `0x14` B (`u32 destino | u8 valores[16]`) y termina
en `0x43feeafc`. El método `0x436f3928` (vtable `0x43fce050`, slot `+0xa0`) traduce el
código de modo con el mapa `0x43c9c5b5` y ejecuta, por fila:

```text
*fila.destino = fila.valores[mapa_modo[modo]]
```

Los 69 destinos son el byte `data` de registros de seis bytes (`{dev,0,reg,data,0}`) del
pool contiguo `0x44021ec2..0x44022108` (98 registros; 97 × `0x81` y 1 × `0x83`). La A6000
usa el mismo mecanismo con **59 filas** desde `0x43fe9b74` y **sin** mapa modo→columna:
recibe la columna ya resuelta, y sus registros son de 4 B (`{reg:u16,data,0}`).

**Evidencia REA (aportada en esta sesión):** `xrefs(0x43fee5ac)` devuelve
`0x436f3942`, interior del bucle consumidor; REA **no** reconoce como función la entrada
Thumb `0x436f3928` (la identidad se fija por bytes: vtable `0x43fce0f0 = 0x436f3929`,
GOT `0x44028844 = 0x43fee598` y el bucle `0x436f393a..0x436f3946`). Una consulta vacía no
prueba ausencia (regla del proyecto).

**Modos:** `0x4e` y `0x4f` comparten la columna **1** con otros 35 códigos; no existe
columna exclusiva de silent → esta matriz no distingue el modo silencioso ni demuestra su
semántica física. La segunda matriz (`0x43e8de00`, puerta `[obj+0x2b0]`) está a cero en el
blob: **NO_VERIFICADA**. S51 sin cambios.

> Este archivo se conserva por los enlaces existentes; el contenido autorizado y
> reproducible es el del documento canónico.
