# S150 — referencias directas a los huecos +8/+9 de las filas

**Resultado acotado:** para las ocho direcciones exactas `+8/+9` de las cuatro
filas G, REA devuelve cero xrefs entrantes. Esto significa **sin referencias
directas clasificadas en el análisis**, no “nadie escribe estos bytes”.
Además, una búsqueda completa encuentra dos palabras de datos cuyo primer
campo apunta justo a `0x43eb0850` (gap +8/+9 de la tercera fila, índice 2).
Esos literales son una pista de consumidor de tabla, no una referencia de
código ni prueba de acceso efectivo.

## Direcciones y evidencia REA

Filas base relativas a G+`0x224`: `+0x2c`, `+0x3c`, `+0x4c`, `+0x5c`.
Los gaps analizados son:

| fila (índice) | `+8` | `+9` | xrefs REA |
|---:|---:|---:|---|
| 0 | `0x43eb0830` | `0x43eb0831` | `[]` en ambas direcciones |
| 1 | `0x43eb0840` | `0x43eb0841` | `[]` en ambas direcciones |
| 2 | `0x43eb0850` | `0x43eb0851` | `[]` en ambas direcciones |
| 3 | `0x43eb0860` | `0x43eb0861` | `[]` en ambas direcciones |

Evidence IDs por orden de la tabla: `ev_c42a7d7fd9a1e599c8d0b74992d387d3f1e7164896d259abe3a6ef0f7e68f68c`,
`ev_c1664bce2a3920c0c801a1aaff003ca91ccc4b4b8633f708cba8bdb44b125d34`,
`ev_fbcf9d3ee8809bd2b72d2e50e7052aa6f06e982d175373f0d17886c1686255d6`,
`ev_59e95069b0a10c85cd584c28412ab5fe83867491a6b91797175eaad10f6f1856`,
`ev_77d3f4ce807b15caecfc43cf8a05b1d15042431081d2c73161bdcf6783d672af`,
`ev_0c07447897f2035e5bde864612e549695f004dd7d302f953b2c89004188583d8`,
`ev_5fb7233ea97b868884f119553adfa2a46f25bf15aab56f3e5e2129d56116f6e6`,
`ev_55c7c05551f922a8af96f3b4d7dbae64da5be5e55e55eacc780eb55d0149416b`.

## Control positivo y pista de tabla

El mismo análisis sí resuelve referencias al inicio de la tercera fila
`0x43eb0848`: `0x43836910`/`0x43836916`, ambas cargas `ldr.w` desde offset
`0x270` respecto de G (`ev_afcfff7678cf182ee835cd1ed4dfd1b2f55fdb0872a6bfc51817b3a9ab9f3b55`).
Los bytes de ambas cargas se guardaron en la salida estructurada y se
recalcularon con el script.

La búsqueda de patrón completo `50 08 eb 43` en la imagen (`complete=true`)
encuentra dos ocurrencias: `0x4400812c` y `0x4400b27c`, ambas comienzan con el
puntero `0x43eb0850`. Sus 16 bytes difieren después del primer word. Evidence
de la búsqueda: `ev_201b0a5e0f16fe153da29642e861f41b0a7cebeb611865db65540927452d7668`;
lecturas de las dos celdas: `ev_cd9ec49fc2ce6e6b4cda2a52e4f0cca930246ce9b9225b2afc46fa079b265647` /
`ev_bc1a632a726cff2e6b8e5ad401ab8fed6c3654d17d6ed420fe0bd35adcd7e949`.
No se identificó el consumidor de estas celdas ni el layout/criterio de
selección; por tanto, **no** se eleva el literal a acceso real al hueco.

Los ocho bytes de gap están a cero en el blob, consistente con el BSS de S140;
eso no informa de sus valores durante una captura. Los accesos por alias,
puntero calculado o parámetros recibidos permanecen fuera de lo que prueba una
consulta `xrefs` a ocho destinos exactos. No cambia S51 ni asigna significado
físico a los campos.

```sh
python3 analysis/s150_imager_row_gaps/verify_gap_refs.py
python3 -m unittest tests.test_s150_imager_row_gaps -v
```
