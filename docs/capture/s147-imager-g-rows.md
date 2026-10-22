# S147 — productor parcial de filas del banco G

S147 clasifica los cinco xrefs REA a `G+0x224` (`0x43eb07fc`). **VERIFICADO**
en el camino de producción observado: el sitio `0x437b5f00` forma el segundo
argumento `G+0x224`, llama a `0x4383bf2c`; éste pasa ese argumento a
`0x4383c9dc`, que recorre cuatro filas de 16 bytes desde `+0x2c` y escribe
campos en ellas. Esto reduce la incertidumbre de S140/S145, pero no asigna modo
fotográfico ni semántica física.

## Evidencia del camino productor

- REA xrefs a `G+0x224`: `ev_7375812f6a63afe1d0db14b91c6cec50187e7d53a2f6bd7a4436500fb2ec9df0`.
- En `0x437b5f00`, bytes `06f50971` = `add.w r1,r6,#0x224`; el bloque llama
  `0x4383bf2c` en `0x437b5f1c`. REA Evidence de bytes:
  `ev_fc0267a6d9f060e72f9a2b0b4dfc0536ea93bc63bed63e799dfe28ead08357b6`;
  del rango completo: `ev_5eede5f0742fa6688a75312e9c4668bd3bc8f831c7ea46d4c6c2b698f163e88d`.
- `FUN_4383bf2c` recibe punteros en `r0/r1`; mueve el segundo argumento a
  `r4`, llama primero a `0x4383c9dc` (instrucción `0x4383bf3c`) sin cambiar
  esos registros, y luego a otros helpers. REA dossier
  `ev_5305a4dbabf37e02baec4bd8b258137d9e733c0817ce4b373defe5a8ecc12203`;
  assembly view `ev_16b1b13434d0983e1e0a4ae53f4994b39195e15b25b571189089b9bd1b208b3b`.
- `FUN_4383c9dc` pseudocódigo completo, paginado en dos vistas
  (`ev_d4653d3615add43984db5b04eb31c812b23d2a5865e6038908736caf291fd05a`,
  `ev_9caa8366dd8aa3149c26482110e5523aa6132b3fd299d39fb05de95a2003380e`):
  `iVar12` empieza en el argumento de salida, cada iteración añade `0x10`,
  realiza el cálculo sobre offsets `+0x2c..+0x3a` y termina tras cuatro
  iteraciones. Así, sobre G+`0x224`, las filas cubiertas son
  `+0x2c+16·i`, `i=0..3`.

Los offsets relativos a cada fila que escribe esta función son `0,4,6,0xA,0xC`
y `0xE`; el loop no escribe `+8/+9`. Este resultado es local a esa función; no
demuestra que esos bytes nunca sean escritos por otro helper, ni identifica el
significado de ninguno de los campos.

## Referencias restantes y límites

- `0x437b57ec` almacena el puntero calculado a la pila; su uso posterior entra
  en `0x4385743c`. La función es grande y su value-flow REA está truncado; no
  se usa este xref para declarar el efecto completo de `param_7`.
- `0x437b60e6` forma otro argumento de `0x4384d8bc`; su value-flow está
  truncado y sus callees no se resuelven aquí. No se eleva a productor.
- `0x43836a06` y `0x43836a0c` son loads `ldrh.w [r3,#0x224]`; forman parte de
  una rutina fuera de procedimiento reconocido y sus bytes cercanos también
  leen campos de cabecera `+0x22c/+0x236`. Son observaciones de lectura, no
  prueba de acceso a filas.

La relación de G con los valores en ejecución, su selección por modo y los
nombres físicos continúan abiertos. Sin captura runtime ni prueba física; S51
se mantiene sin cambios.

```sh
python3 analysis/s147_imager_g_rows/verify_g_rows.py
python3 -m unittest tests.test_s147_imager_g_rows -v
```

El script genera `analysis/s147_imager_g_rows/g_rows.json` y disambla bytes
reales por `file_offset=VA−0x43541000`. La cobertura es deliberadamente local a
los xrefs y funciones enumerados.
