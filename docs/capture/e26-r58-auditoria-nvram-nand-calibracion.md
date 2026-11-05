# E26-R58 — Auditoría NVRAM/NAND (20-10 → 05-11) y dónde vive la calibración (05-11-2026)

Solo lectura. Método reproducible: `scripts/senser_backup_compare.py`, `scripts/senser_backup_classify.py` y `scripts/senser_backup_unidad.py PLANTILLA V1 V2…`; las particiones FAT se leen con `mcopy -s -n -i dev_nflashaN.bin ::`.

## 1. La restauración de NVRAM de R57 §7 NO quedó aplicada (MEDIDO)

`nand-20261105/dev_nflasha2.bin` → `Backup.bin` (= `Backup.bak`) frente a `20261020-first`: **23 propiedades distintas** (frente a «A»: 19). Las no contador:

| Propiedad | Original | En flash 05-11 | Igual que `337-previo` |
|---|---|---|---|
| `0xd50086` (512 B) | registros de 64 B, ids `0x1b-0x20` | ceros | sí |
| `0x3c03a3` (576 B) | tabla con datos | casi ceros | sí |
| `0xbc0010` (48 B) | `0x1e` / `0xe0` | `0x2b` / `0x1dd` | sí |

R57 dio por buena la restauración («persistió en flash») sin comparar estas tres. Como `senser_backup_restore.py` verificó la NVRAM **en memoria** (`new[0x100:] == data[0x100:]`) y la flash quedó con el valor previo a la restauración, lo más probable (INFERENCIA fuerte) es que un módulo con copia propia en RAM la reescribiera al apagar (`SaveUsr:POFF Req`, `Sens:BkWrPoffAsync`, `BkWrite End` en `av-cam.bin` `0x74ee9a-0x74f031`). **Consecuencia: «restaurar la NVRAM no arregla EFCS» no está demostrado.**

## 2. `0xbc0010` (MEDIDO la evolución; semántica NO VERIFICADA)

Campos u16: `[0]=0x0220`, `[4]`=escalar, `[8..15]`=ocho valores iguales, `[20]`=`0x57/0x59`.

| Volcado | `[4]` | `[8..15]` |
|---|---|---|
| first, A (20-10) | 0x1e | 0xe0 |
| nvram-referencia (cámara funcionando) | 0x21 | 0x10b |
| pre-T024 | 0x22 | 0x11b |
| pre-T040 (3.22) | 0x21 | 0x10b |
| 3.26 (03-11) | 0x26 | 0x165 |
| 337-previo / flash 05-11 | 0x2b | 0x1dd |

Crece de forma monótona entre volcados aunque se restaure. Los IDs `0xbc0001…0x10` son bloques de parámetros de imager (tabla de IDs `av-cam` `0xaa9210`, VA `0x43fea210`; T052-B0). Coincidencia a verificar: 0x1dd − 0xe0 = 253 unidades; a 5 µs/unidad = 1,27 ms = pérdida de EFCS de R57 §8 (la unidad de 5 µs es supuesta).

## 3. Dónde está la calibración de la unidad

`senser_backup_unidad.py` (plantilla `CX77500_E38.bin` frente a 3 volcados): **339** propiedades estables, no cero y distintas de la plantilla. Bytes por subsistema: `0xbc` 128 000 (3 props: `0xbc0001/2/0d`), `0x132` 72 704 (2), `0x3` 3 713 (12), `0xe` 1 096, `0x15` 768, `0x185` 640, `0x3e` 524, `0x107` 485 (173; ajustes de usuario), `0x59` 424, `0x13e` 373, `0xd5` 257 (`0xd50001`). Semántica NO VERIFICADA salvo `0xbc` (imager) y `0x107` (usuario).

Descartadas como calibración: `0x3c03a3`, `0x3c0373-75` (literales en `libmpr.so`: base de datos de contenidos), `0x3c032d/0x3c0339` (contador de disparos), `nflasha4` (MPR), `nflasha10/17` (logs, APK y restos de pruebas), `nflasha1/18/23` (contadores de borrado), `nflasha2` salvo `Backup.bin` (`dat4` 0x321→0x337 = versión; `.etools`, `.hasp` = uso). `nflasha3`: imagen idéntica a 3.21 y 80 KB nuevos tras su final (`0xaf4f0f`→`0xb0940f`), sin decodificar. `nflasha18`: 18 `VX91xx_lensfile.bin` idénticos.

`darwin_core.bin` (157 276 B): sin literal del controlador de flash FM3 `0x40002000` (barrido alineado), así que no hay indicio de NV propia; el escritor de `[0x20000050+canal]` sigue sin localizar (rea-tema3 §3).

## 4. Lo abierto y cómo se cierra

| Abierto | Prueba que lo cierra |
|---|---|
| ¿La NVRAM original arregla EFCS? | Restaurar «A», volcar **sin reiniciar**, apagar limpio, volcar de nuevo. Si `0xbc0010`/`0xd50086` vuelven al valor previo, la causa del fallo de la restauración es el volcado de RAM al apagar; entonces restaurar con el módulo parado o por la ruta del actualizador (`endupdate.sh` → `/setting/Backup.bin`). |
| ¿`0xbc0010` es una medida que la cámara actualiza? | Mismo ensayo: si tras restaurar y reiniciar vuelve a crecer, es auto-medida y apunta a deriva mecánica. |
| Semántica de `0xd50086`, `0x30100`, `0x132*`, `0x3*` | Ensayo diferencial: cambiar un ajuste a la vez y volcar. |
| 80 KB nuevos en `nflasha3` | Decodificar contra `darwin.sum`/cabecera del paquete 3.37. |
| NV de Darwin / hardware del obturador | Solo con acceso físico a `CN4906` (R52 §8) o medida del obturador. |
