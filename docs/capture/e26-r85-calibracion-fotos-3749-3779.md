# E26-R85 — Auditoría y calibración del obturador con las fotos DSC03749–03779 (11-11-2026)

Continúa [R84](e26-r84-darwin-v3-en-camara.md) y [R56 §7](e26-r56-paquete-333-envio-inline.md). Etiquetas: **VERIFICADO** · **MEDIDO** · **INFERENCIA** · **NO DETERMINADO**.
Fotos del usuario en `~/Desktop/16161111/` (no versionadas). Medidas: `analysis/e26-r85/medidas-por-foto.json` (todas) y
`analysis/e26-r85/tabla-r85.json` (ARW, tabla calibrada). Script: `scripts/e26_r85_calibrar_fotos.py` (prueba `tests/test_e26_r85_calibracion.py`).

## 1. Material
Orden fijo por tripleta (usuario): **Silent activado → Silent desactivado + EFCS activado → Silent desactivado + EFCS desactivado** (mecánico).
`DSC03770` no existe (borrada): las horas EXIF confirman las tripletas 3767–69, **3771–73**, 3774–76 y 3777–79.

| Tripleta | Formato | Velocidad | f | Focal | ISO |
|---|---|---|---|---|---|
| 3749–51 | JPEG | 1/350 | 6,7 | 16 | 100 |
| 3752–54, 3755–57 | JPEG | 1/350 | 6,7 | 25 | 100 |
| 3758–60 | JPEG | 1/1000 | 4 | 16 | 100 |
| 3761–63 | JPEG | 1/1000 | 5,6 | 50 | 100 |
| 3764–66 | JPEG | 1/3000 | 3,5 | 16 | 100 |
| 3767–69 | ARW | 1/3000 | 3,5 | 16 | 100 |
| 3771–73 | ARW | 1/350 | 3,5 | 16 | 100 |
| 3774–76 | ARW | 1/350 | 4,5 | 27 | 100 |
| 3777–79 | ARW | 1/350 | 5,6 | 50 | 100 |

Cámara en pasos de 1/2 EV (1/350 y 1/3000). T de Darwin (`0x19a12` emulado): 1/350 → 2761 µs, 1/3000 → 345 µs.
Método ARW: lineal sin negro, mediana de cocientes por bloque 32×32 frente a la foto mecánica de la misma tripleta (bloques no saturados y con señal), global y en 8 bandas (arriba → abajo). Los JPEG solo sirven de apoyo cualitativo (curva tonal, saturación).

## 2. Resultados (MEDIDO)

| Tripleta (ARW) | EFCS on / off | Pérdida EFCS (T + 2000 − E_on) | Silent / off | Silent efectivo |
|---|---|---|---|---|
| 3767–69 (1/3000) | 3,90 | 1001 µs | ≥ 43 (90 % saturada) | ≥ 15 ms |
| 3771–73 (1/350) | 1,34 | 1067 µs | 16,9 | 47 ms |
| 3774–76 (1/350) | 1,27 | 1246 µs | 19,4 (52 % sat.) | 54 ms |
| 3777–79 (1/350) | 1,30 | 1174 µs | 11,4 (47 % sat.) | 31 ms |

JPEG, misma tendencia: EFCS on/off ≈ 1,25–1,42 a 1/350, 1,76–1,83 a 1/1000, 2,9 a 1/3000; Silent con 38–70 % de píxeles saturados en todas.

Perfil vertical (on/off por bandas): 1/350 → 1,53 … 1,23; 1/3000 → 7,9 … 2,4. Silent/off a 1/350 → 5–7 arriba … 26–27 abajo.

## 3. Auditoría de lo instalado

### 3.1 EFCS activado: el «fix» encima es la tabla de PRUEBA de R84
* **VERIFICADO (R84 §4, CURRENT):** en NVRAM `0x1850000+0x48` sigue `--test` = `{Tmax 30000, c = 2000 µs}`; el CFW 3.73 lleva Darwin v3 (`build_package_nflasha15 … darwin_v3=True`).
* **MEDIDO:** el exceso de EFCS on es casi constante, +0,8…+1,0 ms a 345 y 2761 µs: es exactamente `c − pérdida`. Pérdida real ≈ **1,0 ms a 1/3000 y ≈ 1,16 ms a 1/350**, menor que el modelo R82 en lo rápido (1,31 ms) y algo mayor en 1/350 (1,08 ms). Por eso EFCS sale +27…+34 % a 1/350 y ×3,9 a 1/3000.
* **Tabla calibrada R85** (pérdida medida en x = −1056 y +1333 µs; cola a 0 desde x = 4570 µs de R62/R74): `[(2205, 1006), (2287, 961), (2369, 1178), (4411, 1096), (5863, 733), (7008, 474), (12000, 5)]` (bytes `4efbee03a0fbc103f2fb9a04ec0348049809dd02110eda01912105000080…`). Predicción de exposición media: 0,98–1,02 de T de 1/4000 a 1/30, salvo 1/400 (0,978).
* **Límite (MEDIDO, ya en R83 §5):** el degradado vertical no se corrige con `c`. Con la tabla R85, 1/350 queda ≈ +20 % arriba / −10 % abajo; **1/3000 queda ×5 arriba y negro abajo**: la diferencia entre el barrido de reinicio electrónico y la segunda cortina varía ≈ 0,9 ms (1/350) a ≈ 1,8 ms (1/3000) a lo largo del cuadro. EFCS solo puede nivelarse en media; para ≥ 1/1000 usar mecánico o electrónico.

### 3.2 Silent (electrónico): sin calibrar en el CFW
* **VERIFICADO:** el `av-cam` del 3.73 y del 3.75 (`analysis/gui/g22/pkg-37{3,5}w/base-pp.tar`) tiene el parche de tres estados (`0x43841472 = 99f81d34`) pero los sitios de exposición **originales**: `0x436d6fb6 = 91f80990` (ShutMode) y `0x436d7000 = 28125ffa85fe` (`r5`). La calibración de R56 §7 (ShutMode 0 + `r5 = 4219 − (T/16,73 µs − 97)`) solo existe como parche de RAM por disparo (RemoteShutter v8c `/silent?v=1`, o `scripts/camera_silent.py`/`camera_silent_follow.py` por telnet).
* **MEDIDO:** sin ese parche Silent ignora la velocidad: integración 31–54 ms a 1/350 y ≥ 15 ms (saturada) a 1/3000, creciente con la fila (×5 arriba → ×26 abajo frente al mecánico a 1/350): es el modo con `r5 = 1` de E25-10/T046 (≈ 7 ms + 15,2 µs·fila). Sobreexposición de +3,5…+5,5 EV a 1/350.
* **Corregido aquí:** `scripts/camera_silent.py` usaba la constante antigua (15,2 µs sin retardo: +22 % a 1/60 frente a R56); ahora usa 16,73 µs y 97 filas como RemoteShutter v8c, y acota `r5 ≤ 4218` porque por encima de ~1/600 el modelo da ≤ 0 filas (NO MEDIDO). RemoteShutter no tiene esa cota (pendiente).

## 4. Qué queda nivelado y qué no
| Modo | Estado | Cómo nivelarlo |
|---|---|---|
| Mecánico (EFCS off) | Referencia | — |
| EFCS on | +27…+34 % a 1/350, ×3,9 a 1/3000 (tabla de prueba) | Escribir la tabla R85 (§5). Media ±2 %; degradado vertical sin solución por `c` |
| Silent | +3,5…+5,5 EV, no depende de la velocidad | Hoy: parche RAM por disparo (app o `camera_silent_follow.py`). Persistente: llevar el C3 de E25-16 §7.1 a la imagen BIONZ (E26-R85-SILENT-CFW) |

## 5. Aplicar la tabla R85 (requiere la cámara en USB, escribe NVRAM; reversible con `--zero`)
```
PYTHONPATH=references/pmca .venv/bin/python scripts/senser_efcs_table_write.py --tabla analysis/e26-r85/tabla-r85b.json            # simulación
PYTHONPATH=references/pmca .venv/bin/python scripts/senser_efcs_table_write.py --tabla analysis/e26-r85/tabla-r85b.json --execute  # escribe
```
Después, una tanda ARW EFCS on/off a 1/4000, 1/2000, 1/1000, 1/500, 1/250, 1/125 (misma escena) para el refinado con
`e26_r76_calibrar_efcs.py ajustar … --previo tabla-r85.json` (`e26_r85_calibrar_fotos.py` solo admite un `c` previo constante).

## 6. Pendientes
| ID | Pendiente |
|---|---|
| E26-R84-CALIB | Primer pase hecho (R85, 2 velocidades); falta escribir la tabla y refinar con 1/4000…1/125 |
| E26-R84-ESTADO | Sigue `--test` en NVRAM hasta escribir la tabla R85 |
| E26-R85-SILENT-CFW | Calibración del electrónico persistente en el CFW (C3 de E25-16 en `av-cam`, solo foto y `cap+0x41d = 1`) |
| E26-R85-SILENT-RAPIDO | Medir el electrónico calibrado de 1/500 a 1/4000 (el modelo R56 no cubre < 100 filas) y acotar `r5` en RemoteShutter |
| E26-R85-GRAD | Degradado vertical de EFCS ≥ 1/1000 (físico, ligado a E26-R74-FISICO) |

## 7. Segunda tanda DSC03786–03806 (11-11-2026, MEDIDO)
Solo ARW, ISO 100, misma escena por tripleta; orden Electrónico → EFCS on → EFCS off. Velocidades 1/60, 1/125, 1/500 (×2), 1/1000, 1/2000, 1/4000 (falta 1/250).
La NVRAM seguía con la tabla `--test` (c = 2000): las pérdidas rápidas salen ≈ 1 ms como en §2, lo que con la tabla R85 sería imposible (pérdida ≈ 0).

| Velocidad (T Darwin) | EFCS on/off | Bandas on/off (arriba → abajo) | Pérdida (c = 2000) | Electrónico/off |
|---|---|---|---|---|
| 1/60 (15625) | 0,99 | 0,99 … 1,05 | — | 2,7 (1,7 → 5,4) ≈ 43 ms |
| 1/125 (7812) | 1,00 | 1,00 … 1,02 | — | 4,6 (2,3 → 8,8) ≈ 36 ms |
| 1/500 (1953) | 1,51 / 1,54 | 1,63 → 1,29 | 978 µs | ≈ 10 (sat. 55–68 %) |
| 1/1000 (976) | 2,06 | 2,38 → 1,57 | 964 µs | ≈ 19 (sat.) |
| 1/2000 (488) | 3,43 | 4,82 → 2,07 | 814 µs | ≈ 50 (sat.) |
| 1/4000 (244) | 5,06 | 9,24 → 2,85 | 1008 µs | ≈ 106 (sat.) |

* **Nuevo (MEDIDO):** a 1/60 y 1/125 EFCS on = off **aunque la tabla pide +2000 µs**: en esos tiempos `c` no tiene efecto y no hay pérdida que compensar (cola del modelo confirmada). El calibrador ignora los puntos con x ≥ 4570 µs.
* **Pérdida EFCS** prácticamente plana ≈ 0,8–1,16 ms de 1/4000 a 1/350 (seis puntos). Tabla final **R85b** (`analysis/e26-r85/tabla-r85b.json`, sustituye a la R85): `[(1304, 1008), (1465, 953), (2205, 880), (2240, 1008), (2349, 899), (2457, 1116), (2609, 1008), (4411, 1023), (5863, 733), (7008, 474), (12000, 5)]`; predicción de media 0,96–1,02 de 1/4000 a 1/30. Tramo 1/350–1/160 modelado (sin 1/250 medido).
* **Degradado vertical (MEDIDO):** diferencia arriba–abajo ≈ 0,67 ms (1/500), 0,79 ms (1/1000), ≈ 1,3–1,6 ms (1/2000–1/4000). Con la tabla nivelada en media: 1/500 ±17 %, 1/1000 ≈ ±40 %, 1/2000–1/4000 arriba muy claro y abajo negro. EFCS útil y uniforme hasta 1/500.
* **Electrónico:** tomado sin el parche RAM; sigue integrando ≈ 36–43 ms a 1/60–1/125 y cada vez más en proporción a velocidades rápidas (≈ +1,5 EV a 1/60, +2,2 EV a 1/125, saturado desde 1/500), con degradado ×3–4 arriba → abajo. Confirma §3.2.
