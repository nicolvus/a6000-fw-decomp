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

## 2. `0xbc0010` es el registro del detector de defectos «ZIT», no un tiempo de obturador (REA, VERIFICADO por código)

* Buffer RAM `0x43e0a360` (48 B), cargado desde BK4 `0xbc0010` por la tabla de punteros `0x43fea1e4` / IDs `0x43fea210`.
* Getter `0x43a11420` = `u16` en `+2`. Lo usa `0x43a18454` (traza `[CAM_IMAGER]: ZIT:: DetectFlag`): convierte la fecha del RTC a un número de día `(mes-1)*30 + año*365 + día + 0x735` (16 bits), lo compara con ese `u16` y, si ha pasado el intervalo configurado (byte `+0x50` de otra estructura), devuelve 1 (hay que redetectar) y escribe la fecha actual. Comprobado con los volcados: `0x50f5` = 16-10-2026, `0x50ff` = 26-10-2026, `0x3ebc` = 01-01-2014 (reloj reiniciado). **`+2` = fecha de la última detección de defectos.**
* Los demás campos los rellenan setters `SetZitLog_*` (`0x43a112ea` DetectSequencePre, `0x43a1147e` MassiveDefectDetectNum, `0x43a11544` DefectLvAndPos, `0x43a11640` DefectPosNum; `+0x20..0x26` y `+0x28` solo con modo `0x82`). `[8..15]` (de `0xe0` a `0x1dd`) son recuentos de posiciones defectuosas (INFERENCIA fuerte) y `[4]` un contador de detecciones.
* **Queda refutada la coincidencia de «5 µs/unidad = 1,27 ms» propuesta antes: no tiene relación con EFCS.** `0xbc0010` no es calibración de sincronía.
* ZIT = módulo de detección/corrección de píxeles defectuosos: buffers `adj`/`usr`/`slow`/`mend`, `ZitZphDefectBuffer::convertBackupSaveformat`, `ZIT_releaseDefectCorrectionData`.

## 3. Qué es cada grupo de BK4 (REA: IDs ↔ consumidor y trazas vecinas; 339 propiedades de la unidad)

| Subsistema / propiedades | Qué es | Evidencia |
|---|---|---|
| `0x132`: `0x1320000/1/3` (163 840 B = `0x28000`) y `0x1320002` (11 264 B = `0x2c00`) | **Tablas de corrección de píxeles defectuosos** (DPC): 14 009 pares (fila 4–4027, columna 12–6035) ordenados por fila; las entrega `0x436d66a4` con esos tamaños al bloque de corrección | contenido + `0x436d66a4` (`+0x18=0x28000`, `+0x20=0x2c00`) · VERIFICADO |
| `0xbc0000-0x10` | Bloques del imager (`ImagerCommon`, `IIFINSEL`): `0xbc0001` 1280 B, `0xbc0002` 65 280 B (1 496 pares fila/col), `0xbc000d` 61 440 B (145 pares), `0xbc0000` 20 480 B, `0xbc0010` = registro ZIT (§2) | tabla `0x43fea1e4` (tamaños = diferencias de punteros) + `0x436d9030` · VERIFICADO el tamaño; el contenido de pares es INFERENCIA |
| `0x3…` | Ajustes del procesado de imagen (YC): `0x30011-14` (`ADJ::sjob_Dk_G/Hl_G_Check_Result`, detección oscuro/luces), `0x300ae` (`SetSyncDevelopParam` addr/valor), listas de IDs registradas por módulo (`0x43ff2fd8`). `0x300ab` = pares IMX210 (S61) | trazas `CAMERA_MAIN_YC`, `IMAGING_CAP/REL` · INFERENCIA |
| `0x30100`, `0x185…` | Parámetros de la aplicación DSP (`CAMERA_DSP_APL`) | traza vecina · INFERENCIA débil |
| `0x59…`, `0x5f0134/5`, `0x600148-154`, `0x6000c` | Panel táctil (`TP_R`), desplazamientos V/H del panel y ajuste del EVF (`PNLEVF ADJ BLOCK`) | trazas `TP_R`, `PNL`, `PNLEVF` · VERIFICADO el uso |
| `0xd0027`, `0xd003d` | Sensor de luz (`LIF_DEBUG`) | trazas · INFERENCIA |
| `0x92001a/b/c`, `0x93…` | CIPA/VDF, montura/BL, sensor de ojo (`EyeSens` ALS) | trazas · INFERENCIA |
| `0xe0…` | Corrección óptica (`EXL calCamdcvTanz`, PSF) | trazas · INFERENCIA |
| `0xd50001`, `0xd50086` | Infraestructura de medios: `libInfraMediaCommon.so` lleva una tabla de descriptores del subsistema `0xd5`; registros de 64 B con ids `0x1b-0x20` (estado por medio/ranura) | literal en la librería · INFERENCIA. **No es calibración**; se puso a ceros al reinstalar |
| `0x3c03a3`, `0x3c0373-75`, `nflasha4` | Base de datos de contenidos (MPR) | `libmpr.so` |

Sin consumidor localizado (REA no los reconoce, funciones Thumb sin sembrar): `0x30076`, `0x30081`, `0x30086`, `0x30102`, `0x30103`, `0x3012c`, `0x3005b/5d`, `0x13b0001`, `0x150002`, `0x3e…`, `0x15…`. Todos son tablas pequeñas del grupo `0x3`/imagen.

**Conclusión de calibración:** la única calibración de esta unidad que toca el sensor es el mapa de defectos (`0x132`, `0xbc0002/0d`), intacto en los nueve volcados. **Ninguna propiedad de BK4 identificada contiene tiempos de obturador, cortina ni sincronía.** El código mecánico/EFCS (módulos `Mecha`, `LIRO`, `CAMERA_MAIN_SYNC`) y los tiempos de cortina viven en Darwin y en el firmware, no en BK4 (R57 §8; rea-tema3).

## 4. Estado de lo abierto

| Tema | Estado |
|---|---|
| ¿La NVRAM original arregla EFCS? | **Abierto.** La restauración no se aplicó a `0xd50086`, `0x3c03a3`, `0xbc0010`; ya sabemos que ninguna de las tres es de sincronía (ZIT, medios, contenidos), por lo que es **improbable** que lo arreglen. Cierre definitivo: restaurar «A», volcar sin reiniciar, apagar y volcar. |
| `0xbc0010` | **Cerrado**: registro ZIT (§2). |
| `0xd50086`/`0xd50001`, `0x3c03a3` | **Cerrado** como no calibración (§3). |
| `0x132*`, `0xbc0002/0d` | **Cerrado**: tablas de defectos (§3). |
| `nflasha3` +80 KB | **Cerrado**: relleno periódico. |
| `0x30076/81/86`, `0x30102/03`, `0x3012c`, `0x3005b/5d`, `0x13b`, `0x15`, `0x3e` | **Abierto, bajo riesgo**: tablas pequeñas del procesado de imagen; falta sembrar las funciones Thumb en REA para ver su lector. |
| Causa de EFCS negro ≥ 1/1000 | **Abierto y fuera de BK4**: los tiempos de cortina/sincronía están en Darwin y `CAMERA_MAIN_SYNC`/`Mecha` (R57 §8). Siguiente paso: caracterizar `CAMERA_MAIN_SYNC` (parámetros `shut/svd/shd/spl/sint`) y la memoria de Darwin vía `CN4906` (R52 §8). |
