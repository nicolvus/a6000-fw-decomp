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
| `CAMERA_MAIN_SYNC` | **Revisado, sin pista nueva.** Es el secuenciador VD del sensor (`VD_Drive`, `HS_Main`, `int_ADC_Handler`, `LM::GetSendTiming`); `shut/svd/shd/spl/sint` son registros del imager, no cortina. R57 §9-§11 ya mostró que el desplazamiento no sale de datos de la unidad en firmware. `pkt[2..3]` a Darwin = `[sl+0x162]` (AE), no la propiedad `0x30081`. |
| Subsistema `0x51` (`0x510013/14/20` cambian entre volcados) | Configuración de arranque/loader (UART `0x510015`, `chk adjust` `0x510011`, tipo de energía); no consta uso en cortina. |
| Origen del tipo de mecanismo de Darwin `[0x20000050+canal]` | **Abierto** (rea-tema3 §3). Sin xrefs de código a `Sens:AdjCmd DwnCamera`/`BkSyncCb CAIF` (cadenas de tabla de trazas). Cierre solo con acceso a Darwin (`CN4906`) o lectura SWD de su RAM. |

## 5. Cierre estático de las tablas `0x3` pendientes (05-11-2026, REA + Capstone Thumb)

* **`0x300ab`, `0x30103`, `0x3012c`:** código en `0x4378ba74-0x4378c528`, trazas `[CAMERA_MAIN] #####ERR!! [SetLoadData]` / `[SetLoadDataTrans]`: son **tablas «LoadData» del imager** (S61/rea-tema2: pares IMX210). Se leen con el servicio `0x435613cc(0, id, buf)`. Las funciones son Thumb que REA no reconoce (se leyeron con Capstone).
* **Valor compartido `0x1000-0x1a00` = Tv de la última velocidad (VERIFICADO por fórmula):** `Tv = 4096 − 256·log2 t` (E25-19c): `0x1600` = 1/64 s, `0x1680` ≈ 1/90, `0x1280` ≈ 0,18 s, `0x1000` = 1 s, `0x1a00` = 1/1024 s (el volcado `337-previo` se tomó tras pruebas a 1/1000). `0x30081[6..7]`, `0x30081[0x36..0x37]` y `0x3012c[0x106..0x107]` repiten ese ajuste de usuario; no es calibración ni tabla de fábrica y no influye en la sincronía.
* **`0x300ab[0x110..0x114]`:** a ceros en first/A; con `5e01 0101 0100 …` en todos los volcados posteriores, incluido 05-11 (no se restauró). Cae fuera de los 232 B de pares IMX210 (S61). Función sin determinar.
* **`+0xe0`** en `0x300ab` y `0x3012c` oscila entre `0x22/0x2c/0xa2/0xb1/0x80/0x00` según el volcado: byte de estado, sin semántica.
* **`0x30011-14`, `0x3005b/5d`:** mismo racimo de código que `ADJ::sjob_Dk_G/Hl_G_Check_Result` (YC). **`0x300ae`:** `SetSyncDevelopParam`. **`0x30002`:** callback `vfx`. **`0x30100`, `0x185…`:** `CAMERA_DSP_APL`.
* **`0x30076`, `0x30086`, `0x30102`, `0x1380000`, `0x150002`, `0x1850004/5`, `0x5f00af/b0/b2`, `0x6000a6/a8`, `0xbc000d/e`, `0xe0000/2/3/6/7`, `0x13b0001`:** solo aparecen en listas de IDs registradas y tablas de datos (`0x43ff2fd8`, `0x4400ea30`, `0x4400fee0`…); el acceso se hace por índice relativo a GOT, sin literal ni cadena propia. Agrupados por vecindad en imagen/panel/óptica. **No hay vía estática barata para nombrarlos uno a uno**; requeriría trazar el registro `0x2b0` del servicio de backup por subsistema.
* **Darwin `[0x20000050+canal]`:** las cadenas `Sens:AdjCmd DwnCamera` / `BkSyncCb CAIF` no tienen referencias de código (tabla de trazas), y la tabla de handlers de Darwin `0x2a1a0` queda fuera de `darwin_core.bin` (157 276 B), por lo que no se puede seguir el escritor desde el binario disponible.

## 6. De dónde pueden salir los tiempos de cortina y de sincronía (mapa de fuentes, 05-11-2026)

Cadena (E25-19c/d, E24-05h, R57): Tv del ajuste (`[sl+0x162]`) → `0x4382fac8` (µs) → **temporizador de host** (`cap+0x728/0x74f`) y paquete `0x0c` a Darwin (`pkt[2..3]` = Tv, `pkt[0xc]` tipo de mecanismo) → FSM de Darwin (estados 26/31, ADC-A/ADC-B de seguimiento de fases, bobinas P4D/P4E, temporizador base `0x93e6`) → aviso `0x0e` de fin → sensor (barrido electrónico, 15,2 µs/línea, `record+0x1c` del descriptor de modo).

| Fuente posible | Qué aporta | Estado |
|---|---|---|
| Código de Darwin (`darwin_core`) | FSM, umbrales (5000/50000/250000/25000/500000), duraciones de bobina | **Descartada como diferencia**: el `darwin_core` del paquete de recuperación 3.24/3.37 es **idéntico byte a byte** al 3.21 (0 de 157 276 distintos; `a6000-r1-backup/recuperacion-328`). |
| Código BIONZ (`av-cam.bin`) | Conversión Tv→µs, planificador, `record+0x1c` | Sin constante de latencia de cortina ni dato por unidad (R57 §9-§11). |
| NVRAM BK4 | — | **Ninguna propiedad contiene tiempos de cortina/sincronía** (§3, §5). |
| Área de arranque de Darwin `0x0000-0x41ff` | Código y, posiblemente, datos de fábrica del MCU; **no se reescribe** en las actualizaciones y no está en el paquete ni en ningún volcado | **Abierta, la única fuente de datos por unidad aún no leída.** Necesita lectura física (`CN4906`/SWD). |
| Celdas de Darwin `[0x20000050+canal]`, `[0x200002c0+canal]` | Tipo de mecanismo por canal; se llenan «por copias/mensajes» | Escritor no localizado; origen desconocido (BIONZ por MSS o constante de fábrica). |
| Entorno eléctrico | Darwin mide `BATT_AD_IN` (P10/AN00) y `BATT_TEMP` (P17/AN07); no consta que compensen la bobina, pero el tiempo de recorrido de una cortina depende de la tensión | **Hipótesis a descartar con una prueba barata**: repetir 1/1000 con batería nueva original y con adaptador de CA, en frío y en caliente. |
| Hardware del obturador | Recorrido y velocidad de las cortinas, sensores de posición (ADC), cable plano y contactos de bobina (tocados al abrir la cámara para la sonda SWD) | Coherente con el patrón medido en R57 §8: δ constante de 1,27 ms desde 1/250, **gradiente vertical** (≈1,2 ms arriba, ≈1,6 ms abajo) y **sin gradiente horizontal**, lo que apunta a velocidades de barrido distintas (cortina mecánica frente al barrido electrónico) más que a una latencia de mensaje (que daría desfase uniforme). INFERENCIA. |

## 7. Lectura SWD del BIONZ durante disparos EFCS (05-11-2026, MEDIDO, solo lectura)

Datos en `analysis/camera-dumps/20261105-bionz-swd-disparos/`. RAM física = virtual + `0x40000000` (validado con el bloque `0xbc0005`).

* Paquete `0x0c` a Darwin (`0x83ed4948`) y duración (`0x83eee76c`): **1/500** → `pkt[2..3]=0x1900` (1/512 s), 1953 µs; **1/125** → `0x1700` (1/128 s), 7812 µs. Coinciden con `Tv = 4096 − 256·log2 t`.
* `pkt[1]=0x02`, `pkt[0xc]=0x00`, `pkt[0xd]=0x40` y el resto del paquete son **idénticos** en ambos disparos: el BIONZ envía a Darwin lo mismo salvo el Tv. Los descriptores de modo del sensor (`0x83ea04bc`, `0x83ea13dc`) también son idénticos.
* **Consecuencia:** el BIONZ no distingue la velocidad que falla de la que funciona más que por el Tv y la duración; la diferencia no está en el paquete ni en el modo del sensor. Queda Darwin (arranque, celdas, bobinas) o el hardware.
* Sin resolver: si `pkt[0xc]=0` es el valor normal en un firmware oficial sano; Darwin no se ha podido leer (sin respuesta del DAP de su SWD).

## 8. Restauración de NVRAM sin reiniciar (05-11-2026, MEDIDO)

* `scripts/senser_backup_restore_dump.py` (nuevo; restaura y vuelca en la **misma** sesión de servicio). Volcado previo `analysis/camera-dumps/20261105-pre-restauracion/` (46 propiedades distintas del primer volcado). Restaurado `20261020-first/backup_flash.bin` (SHA-256 `60a810eb…a18b`).
* **Resultado:** `backup_mem.bin` y `backup_flash.bin` tras sincronizar = `60a810eb…a18b`, **0 bytes distintos** del primer volcado; RAM = flash. `0xd50086`, `0x3c03a3` y `0xbc0010` quedan en su valor original. La restauración sí se aplica.
* **Prueba fotográfica con la NVRAM idéntica al original (usuario):** EFCS activado a 1/1000: luz en la parte superior con gradiente; velocidades mayores, negro entero; EFCS desactivado funciona. **Mismo síntoma que antes → la NVRAM queda descartada también en funcionamiento.** (Sin determinar si salir del modo de servicio reinició la cámara.)
* **Tercer volcado tras apagado limpio y reconexión** (`20261105-post-apagado-limpio`, SHA-256 `d5f7cfd0…`): 29 propiedades distintas del primer volcado. `0xd50086` **vuelve a ceros**; `0xbc0010` se reescribe (`[1] = 0x5108` = 05-11-2026 por la fórmula de fecha de R58 §2, `[4] = 0x1f`); `0x3c03a3` cambia un byte (contador). **Confirmado:** esos módulos (medios, detector ZIT, base de contenidos) reescriben su propiedad al apagar o arrancar, por lo que ninguna restauración persiste, y ninguna es de sincronía.

## 9. Volcado total y comparación bit a bit con los originales (05-11-2026, ~20:30, MEDIDO)

* **NVRAM** (`20261105-volcado-total-nvram`, fw 3.37): `bootrom.bin` y `status.bin` **idénticos** al original (0 bytes); `backup_flash.bin` 1127 B distintos del primer volcado (36 propiedades: ajustes `0x107`, contadores, y las tres que la cámara reescribe, `0xd50086`/`0xbc0010`/`0x3c03a3`); `backup_mem.bin` 1122 B.
* **NAND** (`nand-20261105-total`, completa): ver su README. **Idénticas al original las particiones 5, 6, 7, 11, 15 y 16** (kernel, rootfs, `/usr` y sistema Android de Sony). `1`, `18` y `23` solo difieren en contadores (8, 72 y 7 B). `3` difiere solo en el relleno posterior a la imagen. Los cambios grandes están en datos de uso: `2` (Setting), `4` (MPR), `10` (logs) y `17` (Android /data con las apps y restos de pruebas).
* **Conclusión:** todo el software de Sony y todo el firmware principal están intactos; no queda nada modificado en la NAND que no sea estado de uso. Un nodo de la lista (`nflasha12-14`, `19-22`, `24-31`) no existe, igual que en el volcado original.

## 10. ¿Cierra la exposición el temporizador de host? (05-11-2026, MEDIDO, solo lectura)

Lectura SWD del BIONZ (cámara en modo normal) de los ocho canales del bloque de temporizadores `0xf2403000` (stride `0x20`, control `0x1102`, carga `0x2710` en reposo) y de la duración `0x83eee76c`. Datos en `analysis/camera-dumps/20261105-bionz-swd-disparos/` (`timers_idle.txt`, `timers_tras_1_500.txt`, `poll_1s_timers.log`).

* Tras un disparo EFCS a 1/500: ningún canal cambia; la duración vale 1953 µs.
* **Barrido continuo durante una exposición de 1 s con EFCS** (45 s, ~ms por barrido): la duración pasa de 1953 µs a **1 000 000 µs** (calculada al planificar), pero **ningún canal cambia de control ni de carga**. Un temporizador de host armado a 1 s habría sido visible.
* **Conclusión:** en fotos normales el temporizador de host (`cap+0x728`, rama `74f==0`) **no se arma**, en línea con `74f=1` y la espera de confirmaciones de Darwin (E25-19d). Retrasar `0x83eee76c` o ese temporizador **no desplaza el cierre de la segunda cortina**. Una compensación del desfase de ~1,27 ms tendría que actuar en el plan de exposición del sensor (`record+0x1c`/`sl`, R57 §10), no en el temporizador.
* Limitación: solo se vigiló el bloque `0xf2403000`; otro bloque de temporizadores no se ha descartado.

## 11. Búsqueda de `cap` por SWD (05-11-2026, MEDIDO + REA)

* `FUN_437df338` (arranque de captura) guarda su primer argumento en el global `0x43ed4cd4`. **En vivo vale 0 en reposo y pasa a `0x00000008` al disparar** (barrido a ~0,3 ms; `global_4cd4_barrido.log`): es un identificador, no un puntero.
* `FUN_437dfe4c(id)` devuelve `P+8`, con `P = [slot GOT 0x44023bbc] = 0x43ed4d28` y comprobación `*P == id` (leído `[P] = 8` ✓). Por tanto este «cap» es la estructura **estática** `0x43ed4d30` (física `0x83ed4d30`).
* Leído en reposo: `+0x5cc=5`, `+0x5d4=0x43ed5310`, `+0x5d8=+0x5dc=0x20`, `+0x5e0=0x43ed5478` (puntero, no el VTS que R57 §10 describe en `cap+0x5e0`); `+0x74c`, `+0x728`, `+0x4ad8` a 0.
* **Barrido de 90 s con un disparo EFCS dentro de la ventana (confirmado por el usuario): ningún campo de esta estructura cambió.** Por tanto **no es el objeto vivo que consulta el planificador EFCS** (`FUN_437f87ac`), que en E25-19 tenía `+0x74c..0x74f = 00 01 00 01` y `+0x4ad8 = 0x43ed4908`.
* Incidente: leer direcciones no mapeadas (`0x0`+offsets, `0x40000000`) dejó el AP atascado (`stalled AP operation`) y obligó a reiniciar la cámara dos veces. Las lecturas SWD deben limitarse a la DRAM validada (`0x83…`).
* Abierto: de dónde obtiene `cap` el planificador (E25-22 midió `cap=0x952db580`, dirección virtual sin traducción física conocida). Alternativa directa: leer el bloque P2S (`0xfc088340…`) para ver los registros de exposición que se envían al sensor.

## 12. De dónde obtiene `cap` el planificador EFCS (REA + Capstone, 05-11-2026)

* `FUN_437f87ac(cap)` (único llamador del planificador `0x43841070`) elige el camino por `[[0x44020e90]+0x24] == 1`; el selector es estático (`0x43e94ee4 + 0x24 = 0x43e94f08`, física `0x83e94f08`). Con `==1` llama al planificador EFCS `0x43841070(cap+0x1198, cap+0x20, &cap+0x5c8, [cap+0x4ad8]+0x20/+0x40…)`; si no, al normal `0x437b3b08` (EFCS desactivado = mecánico completo).
* Su llamador (`0x437f22d4`, `r6`=`M`) obtiene `cap = 0x43ae75dc(M)` (`cap=[M]`, E25-19): **`cap` sale de `M`, un nodo transitorio de cola**, y es una asignación dinámica (E25-22: `0x952db580`), no un global. Por eso no hay dirección fija que leer por SWD.
* **Consecuencia práctica:** la compensación en vivo por escritura en RAM no es viable sin una traducción virtual→física que no tenemos. La vía realista es un **parche estático** del planificador EFCS (`0x43841070`/`0x4383fa40`: añadir ≈84 líneas a `sb` solo con EFCS activado y T ≲ 1/200), construido como los paquetes de R53–R57, con instalación (reescribe firmware) y medición posterior.

