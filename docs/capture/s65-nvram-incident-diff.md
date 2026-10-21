# S65 — NVRAM antes / durante / después del incidente (2026-10-20)

Tres volcados `backup_flash.bin` (BK4, 852 647 B, checksum de cabecera válido, 16 102 propiedades, región `CX77500_E38`), leídos en service mode (solo lectura) con `scripts/senser_backup_dump.py`, comparados propiedad a propiedad con `scripts/senser_backup_compare.py` y `scripts/senser_backup_classify.py`:

- **A** `silent-nvram-20261020/1-base_flash.bin` (18:48, antes de las pruebas de obturador/`CameraSequence`).
- **F** `post-incidente-20261020-213936/` (tras el fallo; el usuario había formateado la tarjeta en cámara y se le recomendó «Inicializar»).
- **R** `post-restauracion-20261020-214352/` (tras escribir A con `scripts/senser_backup_restore.py`).
- Preset de fábrica: `0110_backup/…/CX77500_E38.bin` del firmware 3.21. (Los volcados no versionados están en `analysis/camera-dumps/`.)

## Resultados (VERIFICADO por relectura de los tres volcados)

| Comparación | Bytes distintos | Propiedades distintas |
|---|---|---|
| A → F | 1 079 | 237 (207 en subsistema `0x107`) |
| F → R | 1 025 | 232 |
| A → R | 325 | 24 |

- De las 237 propiedades que cambian A→F, **220 tienen en F exactamente el valor de fábrica** (2 de ellas ya coincidían en A): F es, en esencia, «ajustes de usuario reiniciados a fábrica». Es compatible con el «Inicializar»/formateo de la cámara; no con un daño de hardware. (Que el usuario ejecutara Inicializar es lo que se le recomendó; no se verificó en la cámara.)
- Tras la restauración, 215 propiedades vuelven al valor de A. Quedan 24 distintas de A: 15 con valores que **no coinciden ni con A ni con F** (R los cambió después: contadores/estado en marcha, p. ej. `0x3c032d`/`0x3c0339` `e20b→e30b` (+1; en F valían 0), `0x590013`, `0x930003`, bloques de 256–1 024 B `0x300ab`, `0x30100`, `0xa10003`, `0xbc000e`, `0x1250005`, `0x1850005`) y **7 con R=F (no restauradas)**: `0x510014`, `0x900001`, `0x92001c`, `0x1070140`, `0x1070774`, `0x1070b74`, `0x6000c`.
- Esas 7 no se pueden atribuir con certeza: o la cámara las recalcula al guardar (p. ej. `0x510014`/`0x900001` son valores con signo de 16/32 bits que cambian −240→−300, −2602→−522; semántica NO VERIFICADO), o son propiedades gestionadas por el sistema (atributos `0x2/0x40/0x60`). Ninguna tiene semántica conocida de obturador/objetivo.
- Nada indica que alguna propiedad con significado conocido de obturador, objetivo o sensor cambiara de forma anómala (no hay mapa semántico de las 16 102 propiedades: NO VERIFICADO).

## Verificación

- Cada volcado se abrió con `BackupFile` (valida magia, revisión BK4 y checksum): válidos.
- La restauración se verificó en memoria tras escribir (bytes desde `0x100` idénticos a A); la comparación A→R de la flash relevó los 24 restos arriba.
- No se pudo comparar la tabla de subsistemas/cabecera (`0x100` B): la escritura de `setBackupPresetData` no la modifica (`cabecera igual: False` antes de escribir; el checksum de R, `0x579cd31`, difiere del de A, `0x57a0c33`).

## Conclusión y límites

La NVRAM del fallo difiere de la de antes sobre todo por ajustes reiniciados a fábrica (explicable por «Inicializar»); no muestra una corrupción evidente. Tampoco demuestra que el fallo mecánico esté o no en la NVRAM: sigue sin haber causa verificada del obturador/objetivo. La comprobación final es física (encender y apagar tras la restauración).

## Resultado físico (2026-10-20)

Tras la restauración de A y desconectar el USB, el usuario informa: **la cámara enciende y apaga correctamente** (objetivo y obturador). Esto indica que el fallo estaba en el estado guardado y no en el hardware; **qué propiedad concreta lo causaba NO VERIFICADO** (se restauraron 215 propiedades juntas; no se aisló ninguna). Causa raíz (pruebas con `CameraSequence`, el formateo o «Inicializar») NO VERIFICADO.
