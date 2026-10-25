# S176 — reproducción de los dos lectores del estado del imager

Reproducido el 25-10-2026. Los entregables históricos anunciados no se
recuperaron del historial: **este informe, el verificador y el test son nuevos**.
Se reconstruyen las dos lecturas a partir del firmware A6000 fw3.21 original,
REA y bytes. No se restaura como cierta toda la conclusión histórica.

## Objeto y lectores comprobados

Ambas rutas forman GOT `0x4401eee4` por LDR/ADD PC, cargan offset `0xaac`
y leen el slot **`0x4401f990 → 0x43f72d02`**. Este objeto de configuración
es distinto del banco de exposición S de S205 (`0x43eb35d0`).

| Lector | Operación verificada | Alcance |
|---|---|---|
| `0x43861400` | `0x4386140a` carga el puntero; `0x43861410` lee byte +`0xac` | Salta a `0x438fec38`; su bloque de inicialización sustituye cero por **6** en `0x438fec74` y lo guarda en `0x43f04cec`. |
| `0x438690dc` | `0x438693ec` carga el puntero; `0x438693ee..43869434` lee +`0x30..0x37` | Cada `cbnz` omite una escritura cuando el byte es no nulo. Si es cero, se escribe **cero** en ocho palabras del destino. No introduce un default 6 en este bloque. |

Las ocho palabras de salida del segundo lector son +`0x664`, `0x66c`,
`0x674`, `0x67c`, `0x684`, `0x68c`, `0x690` y `0x694`, relativas a r6.
REA reconoce dos rangos en el segundo lector y, en el primero, un cuerpo
no contiguo que incluye el salto a `0x438fec38`. Leer solo el bloque inicial
habría omitido el default 6 del primer lector.

## Evidencia y límites

- [Verificador](../../analysis/s176_imager_state_readers/readers_audit.py),
  [resultado](../../analysis/s176_imager_state_readers/readers.json) y
  [regresiones con mutaciones](../../tests/test_s176_imager_state_readers.py).
- [Resolución y pseudocódigo REA](../../analysis/s380_libobj_map/followup_evidence/av-initial.jsonl)
  y [instrucciones del cuerpo no contiguo](../../analysis/s380_libobj_map/followup_evidence/av-more.jsonl).
- SHA-256 de av-cam: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
- [S300](s300-state-xref-sweep.md) ya había contrastado las dos lecturas;
  se conserva su conclusión local sobre ceros en el segundo lector.
- Lectura y copia verificadas estáticamente. Unidades de +`0xac`, significado
  físico de los ocho campos y activación durante un disparo: **NO_VERIFICADO**.

**ACEPTO** los dos lectores y el default 6 únicamente en la ruta indicada.
**RECHAZO** atribuir default 6 a las ocho anulaciones del segundo lector.
El pendiente de reconstruir estos entregables queda completado; S51 no cambia.
