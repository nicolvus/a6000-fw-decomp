# S205 — escritor de S[0] y contrato del staging de exposición

Actualizado el 25-10-2026. **Escritor y argumentos resueltos estáticamente.**
El negativo anterior de slots GOT se limitaba a `0x44010000..0x44020000`;
había omitido **`0x44020c9c → 0x43eb35d0`**. El barrido no permitía
afirmar ausencia global. [Seguimiento de los cinco puntos](capture-static-followup-2026-10-25.md).

## Contrato verificado

En el llamador `0x437b617c` (su prólogo está en `0x437b617e`), el BL
`0x437b61d2` invoca **`0x43843a44`** con estos argumentos:

| Argumento ABI | Origen verificado |
|---|---|
| r0 | Contexto original del llamador |
| r1 | `0x43ead7e0 + 0x290` |
| r2 | `G + 0x224 = 0x43eb07fc`, G desde slot `0x44020b20` |
| r3 | `0x43eb2644`, desde slot `0x44023304` |
| quinto, en [sp] | **`S = 0x43eb35d0`**, desde slot `0x44020c9c` |
| sexto, en [sp+4] | `0x43eae21c`, desde slot `0x4401efbc` |

`0x437b61ac` carga el offset GOT `0x1db8`; `0x437b61b0` obtiene S
en r7 y `0x437b61b4` lo guarda en la pila. El staging salva nueve registros
(36 B) y reserva 28 B: su `[sp+0x40]` es el quinto argumento de entrada,
no un puntero inferido por cercanía.

En `0x43843a4a/54` lee **`u8(*(ctx+0x20)+1)`**; `0x43843a5e`
lo escribe en **S[0]** mediante r4. Éste es un escritor positivo localizado.

## G → S y selección de fila

Cuando el selector vale **3**, el bloque `0x43843ad2..43843b34`:

- Carga r2 original como origen G+`0x224`.
- Ejecuta cuatro iteraciones, con contador inicial 4 y paso `0x10`.
- Copia **16 B** de `origen+0x2c+16*i` a `S+0x64+16*i`.
- Copia además bancos auxiliares de 6 B y u16; no se asigna significado
  eléctrico a esos campos.

El [productor parcial S147](s147-imager-g-rows.md) documenta
`0x437b5f00 → 0x4383bf2c → 0x4383c9dc`, que llena campos de esas cuatro
filas del banco G. El llamador recién recuperado enlaza ese banco con S.
Después llama `0x43b08750(S)`, que selecciona la fila activa mediante
`0x43b0893c` y usa S[0] también para los bancos auxiliares.

**Resuelto:** quién escribe S[0], qué argumento es S, el origen del staging
y la condición de la copia de cuatro filas. **Pendiente:** todos los
productores anteriores del selector, los valores reales por modalidad de
captura, la correspondencia funcional con IMX235 y el fin electrónico de
integración. S[0]=3 no se identifica aquí con el modo Silent del sensor.

## Método y evidencia

REA volvió a responder `not_in_procedure` para `0x43843a44` y el BL
`0x437b61d2`. Se aplicó el respaldo autorizado de Ghidra histórico
`readOnly/noanalysis`; no se modificó el proyecto ni el firmware.
`0x43b08750` sí está cubierto por REA.

- [Staging y consumidores Backup](../../analysis/s205_imager_s0_writer/staging_followup.json).
- [Llamador y argumentos](../../analysis/s205_imager_s0_writer/staging_caller_followup.json).
- [Verificador](../../analysis/s205_imager_s0_writer/verify_staging.py),
  [resultado](../../analysis/s205_imager_s0_writer/staging_contract.json) y
  [tests con mutaciones](../../tests/test_s205_staging_contract.py).
- [Cobertura REA](../../analysis/s380_libobj_map/followup_evidence/av-more.jsonl),
  [consulta al llamador](../../analysis/s380_libobj_map/followup_evidence/av-staging-caller.jsonl)
  y [selección de bancos auxiliares](../../analysis/s380_libobj_map/followup_evidence/av-mode-task.jsonl).

Los scripts históricos `s0_writer_bytes.py`/`s0_writer_deep.py` conservan
barridos parciales; sus ceros no sustituyen este contrato positivo.
S51 A/B/C=NO; sin parche ni ejecución física.
