# S145 — el staging IMX210 existe en un hueco de cobertura REA

**Resultado PARCIAL:** REA delimita un procedimiento de 8 bytes inmediatamente
antes de `0x43843a44`, pero no incluye la dirección candidata ni el callsite
entrante en ningún procedimiento observado. Los bytes Thumb sí contienen un
prólogo plausible en `0x43843a44` y un `BL` visible desde otro bloque no
analizado en `0x437b61d2`. Esto justifica una consulta futura con entradas
explícitas en la sesión REA; no prueba ejecución, store a `S[0]` ni contenido
de filas runtime.

## Observaciones REA

- `resolve_containing_procedure(0x43843a38)` → `FUN_43843a38`, cuerpo
  `0x43843a38..0x43843a3f`, Evidence
  `ev_5c7ff69e20724a19d3273ec66911ffab44d75d2d245c9f19b102447a114121b6`.
- `resolve_containing_procedure(0x43843a44)` → `not_in_procedure`, Evidence
  `ev_ea22a2182a4e3d23312394b402b358789ae6a158f2c91f4dd012453fd50de7ed`.
- El caller candidato `0x437b617e` y el callsite `0x437b61d2` también están
  fuera de procedimientos reconocidos: `ev_1a8bf1980c534d35a1e20f267840577c270f73f4cd59c18c6df98299d631737a` y
  `ev_bf964a553c23c814671cdfb6585c400508017bf07914746b9f4ab0cb1b420ac1`.
- REA bytes completos: entry `0x437b617e` → `2de9f34705463d4c8a465b78`
  (`ev_1341f2fcb0c98ed30d51646e21fd980c2c7fdd917c14493817665a26e707173a`);
  sitio `0x437b61d2` → `8df037fc`
  (`ev_51665d015dc585c586b3ef325ee488b0a7dbe64ea0c74cf3f7519e63649a6336`);
  candidato `0x43843a44` → `2de9f04f1d46036a87b0dc4c064601925b787c440294109c04912370eb7f85f8`
  (`ev_f6cf7574b2e3b18fcec3ebf5f5fc14bbfd36049e3fdc90b9ac37a20541919ebb`).

El código `0x43843a38` termina con `bx lr` antes del literal y del prólogo
candidato; por tanto, no se confunden esas dos entradas. El candidato de
caller está tras el cuerpo conocido `FUN_437b5f98` (`0x437b5f98..0x437b6127`)
y un pool literal, pero no se convierte por ello en función confirmada.

## Límites y siguiente paso

Una búsqueda de procedimientos no modelados y xrefs vacíos caracteriza solo
la cobertura del análisis. En particular no prueba ausencia del código, que un
camino se ejecute, ni que el `BL` sea llamado en una captura real. El siguiente
paso útil y acotado se evaluó en S146: la superficie REA actual no puede
sembrar funciones. El seguimiento pendiente debe usar recorrido estático
reproducible de los bytes, sin presentar la falta de CFG como ausencia de código.
No se atribuye significado eléctrico ni se modifica S51.

```sh
python3 analysis/s145_imager_unanalyzed_code/verify_code_gap.py
python3 -m unittest tests.test_s145_imager_unanalyzed_code -v
```

El script exporta las instrucciones desde bytes originales del binario con
`file_offset = VA - 0x43541000`; salida: `analysis/s145_imager_unanalyzed_code/code_gap.json`.
