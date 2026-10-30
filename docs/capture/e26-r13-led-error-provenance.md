# E26-R13 — Procedencia del error LED 3 lentos + 2 rápidos (Loader2 / Loader3)

Fecha: 30-10-2026. Continúa [R12](e26-r12-bootrom-static-audit.md) (`2baf2378`). **Solo análisis estático y emulación/aritmética offline.** No se interactuó con la cámara, no se envió nada y no se generó ningún artefacto instalable.

Fuentes: `analysis/camera-dumps/updater-20261020-175427/bootloader.bin` (491 520 B, SHA-256 `eb420385…a327f`, original intacto) · cabeceras públicas de Sony ya presentes en el repo (`analysis/session18/main/sony-oss-extracted/linux/arch/arm/mach-cxd90014/include/mach/{regs-timer,timex}.h`) · [`r13_loader3.py`](../../analysis/e26-recovery/r13_loader3.py) (barrido Thumb, grafo, listados) · [`r13-led-provenance.py`](../../analysis/e26-recovery/r13-led-provenance.py) · pruebas `tests/test_e26_r13_led_provenance.py`.

Etiquetas: **BINARIO** = comprobado en bytes/desensamblado · **ARITMÉTICA** = cálculo sobre valores del binario · **HIPÓTESIS** = sobre la cámara real, sin prueba física.

## Resumen

1. **BINARIO.** `FUN_c01f3b74` es de **Loader3** (`0xc01f0000`, INFO 5), no de Loader2. R7 lo situaba bien; la etiqueta «Loader2» fue un error de R12. **Pero Loader2 (`0xc0030000`) contiene una copia byte a byte de la misma rutina LED en `0xc0030c7c`**, con la misma constante `d = 0x3d0900`.
2. **BINARIO.** Loader2 resta 1000 al código antes de señalizar (`c00303e4: sub.w r0, r4, #0x3e8`); Loader3 no resta nada. El grupo `LDR2` (millares) del registro `ERROR: Blinking LED[LDR2=%d LNG=%d SHT=%d]` identifica la etapa: **un error de Loader2 siempre empieza con ≥1 pulso lentísimo; un error de Loader3 menor de 1000 no tiene ninguno.**
3. **BINARIO.** Entre los códigos negativos que contienen ambos cargadores, **solo −302 de Loader3 da «3 y luego 2»** (0/3/2). Loader2 no contiene −302.
4. **ARITMÉTICA + HIPÓTESIS DE RELOJ.** Con el temporizador a 2 MHz, `d` = 2,0 s: los 3 pulsos «lentos» (LNG) duran 0,5 s encendido/0,5 s apagado y los 2 «rápidos» (SHT) 0,25/0,25 s; ciclo de 8,0 s. Encaja con «3 lentos y 2 rápidos». Depende de que la entrada del temporizador sea de 4 MHz como en las cabeceras de Sony (no medida).
5. Ninguna evidencia atribuye el fallo a NAND, a 3.25 ni a un productor concreto. Quedan **dos familias** de causa alcanzables hasta el LED: tabla de particiones BOS y lectura de configuración/FAT.

### Corrección trazable (no se alteran R7–R12)

- **Corrección de R12 §1:** «`FUN_c01f3b74` es de Loader2» es incorrecto; pertenece a Loader3. Loader2 tiene su propia copia (`0xc0030c7c`). R5/R6 ya situaban Loader2 en `0xc0030000` y Loader3 en `0xc01f0000`.
- **Corrección de R12 (corrección 4 sobre R7):** R12 afirmó que R7 tenía un «typo» y que el retorno del kernel NULL es −302. No es así: el retorno de `c01f04b6` es `mvn r0,#0x12e` = `0xfffffed1` = **−303** (patrón 0/3/3). El hexadecimal de R7 (`0xfffffed1`) es correcto; lo erróneo es solo el paréntesis `(-0x12e)`. El literal −302 existe, pero en los productores de §3.
- **Corrección de R12 §6:** los productores de −302 son **siete** funciones y **nueve** puntos de carga (tres palabras de literal), no seis; además **tres** de esos puntos (`c01f3de0`, `c01f3eee`, `c01f40ca`) hacen `subs r0,r0,#4` y devuelven **−306**, no −302. Devuelven −302 tal cual solo cuatro rutas (§3).

## 1. Identidad verificada de Loader2 y Loader3

| | Loader2 | Loader3 |
|---|---|---|
| Dirección de ejecución | `0xc0030000` | `0xc01f0000` (entrada ARM `b 0xc01f0028`) |
| Posición en `bootloader.bin` | `0x600–0x7200` (EXBL) | `0x22800–0x38000` (INFO 5, 43 páginas; INFO 6, 21 páginas, no adquirida) |
| Identificación en bytes | banner `Loader2 Ver.33.01.90 (Jan 24 2014 22:07:33)`; cadenas `LDR:` / `LDR_E:` | cadenas `LD3:` / `LD3_E:`, `BOS_E`, `CFG_E`, `FAT_E` |
| Salto entre etapas | `c00303d8: blx r5` con `r5 = 0xc01f0000`; tras volver, `LDR_E:NOTREACHED` | recibe control; `c01f01e0 → c01f11ec` (despacho) |
| Rutina LED | `0xc0030c7c` (llamadores `c00303e8`, `c0034a7a`) | `0xc01f3b74` (único llamador `c01f1264`) |
| Código pasado a LED | `err − 1000` (`c00303e4`); la rama `c0034a76` pasa −210 sin restar | `err` sin tocar |
| Constantes negativas propias | −201, −202, −210, −304, −306, −307 y códigos de capa baja (−10001…, −131073, −131078…) | −201…−209, −301…−308 y otros (§4) |

Cadena BootROM → Loader2 → Loader3 (BINARIO, R5/R6/R12 + esta tabla): BootROM `ffff013c` salta a `0xc0030000`; Loader2 lee INFO, inicializa BOSS y copia Loader3 a `0xc01f0000` (`c0030de8`, entradas INFO 5/6); salta con `blx r5`. **El prefijo Loader3 usado aquí está incompleto** (faltan las 21 páginas de INFO 6) y su integridad global no está validada (R6); las funciones citadas están todas dentro del prefijo adquirido (`c01f0000–c0205800`).

## 2. Auditoría de la rutina LED (`c01f3b74` y gemela `c0030c7c`)

BINARIO. Con `n = −código` (Loader2: `n = 1000 + |err|`):

```
c01f3b74: r7 = n/1000 (LDR2)   r8 = (n%1000)/100 (LNG)   r6 = n%100 (SHT)
          log nivel 1 "ERROR: Blinking LED[LDR2=%d LNG=%d SHT=%d]" y "ERROR: Loader boot failed."
          c01f3884, c01f5008 (UART)   d = 0x3d0900
bucle:    c01f379a (sondeo UART)
          blink(LDR2, d)  ; wait(d/2) ; blink(LNG, d/4) ; wait(d/2) ; blink(SHT, d/8) ; wait(d)
blink(c, t) = c × { reg+0x48←1 ; wait(t) ; reg+0x44←1 ; wait(t) }     (c01f6d18; reg = 0xf2910000)
wait(t)     = rearma timer0 y espera contador ≥ t                      (c01f4f88, c01f4fea)
```

- Un grupo con 0 pulsos no hace nada, pero **su pausa `d/2` sí se ejecuta**.
- Las cadenas llaman LNG («long») al grupo de centenas y SHT («short») al de unidades: concuerdan con los nombres «lentos/rápidos» del usuario.
- `c01f379a` consume UART; no altera los tiempos de forma apreciable (**HIPÓTESIS**).
- Polaridad del LED (qué escritura enciende) no determinada; el patrón no depende de ella.

## 3. Productores de −302 en Loader3 y su propagación

`c01f01e0 → c01f11ec` despacha según el modo; **todo retorno distinto de cero de `c01f0cca` (init), `c01f1de6` (modo), `c01f1312`/`c01f04b6`/`c01f03e2` (cargas) acaba en `c01f1262 → c01f3b74`** (BINARIO, listado `c01f11ec–c01f1264`). El valor por defecto si un manejador «no debía volver» es −306 (`ldr r5,=0xfffffece`).

### Grafo (aristas BL/B.W verificadas con `r13_loader3.build_graph`)

```
c01f11ec ─ c01f0cca (init)  ─ c01f3d50 "Init FAT"  ─ c01f2c92/2c98  BOS: tabla de particiones   [P1]
        │                    └ c01f159a "chk updater" ─ c01f3eb6 (mount) …  ← devuelve 0: NO propaga
        ├ c01f1de6 (modo) ─ c01f1d6a "chk adjust" ─ 3eb6/44c6/45cc …                ← NO propaga (bool)
        ├ c01f1312 ─ c01f09e4 "Normal load" ─ c01f2fe8 CFG ─ c01f2f24 ─ c01f3eb6 / c01f4654   [P2]
        │          └ c01f1378 ─ c01f068a (kernel/initrd desde FAT) ← resultado guardado en 0xc00e0000, NO propaga
        └ c01f03e2 ─ c01f2fe8 ─ c01f2f24 (rama modos 7–9, 13, 14)                           [P2]
c01f3eb6 ─ c01f3d8a (FAT, ID, tipo) [P3] ; c01f3e54 (PBR) [P4] ; c01f46a8 (raíz)
c01f44c6 ─ c01f407e (dir. entry) [P5] ─ c01f3fd0 (siguiente cluster) [P6]
```

### Matriz de productores

| Id | Función (cadenas) | Operación | Condición exacta para devolver −302 | Otros retornos | ¿Llega al LED? |
|---|---|---|---|---|---|
| P1 | `c01f2c98` (`BOS_E:Load partition error / Partition signature error`) | cargar tabla de particiones BOS en `0xc00e04ac` | `c01f2b7c` devolvió 0 y la palabra en `0xc00e04ac` ≠ `0x36343238` | error de `c01f2b7c` tal cual | **Sí**: `3d50` lo devuelve, la etapa «Init FAT» de `c0cca` lo devuelve a `c11ec`. **Se ejecuta en cada arranque que llegue a esa etapa** |
| P2 | `c01f2f24` (`CFG_E:Load file`) | cargar un archivo de la lista RAMCFG | `c01f4654` (cargar archivo) devuelve ≤ 0: fallo de apertura, de lectura **o archivo vacío** | error de montaje (`CFG_E:Mount part`) tal cual | **Sí** (`2fe8` aborta con el negativo; `09e4`/`03e2` lo devuelven) |
| P3 | `c01f3d8a` (`FAT_E:FAT ID…`, `…not supported`) | leer FAT | byte de ID de la FAT ≠ campo del BPB; o sectores/FAT16 = 0 (FAT32); o nº de clusters ≥ `0xfff5` | OOM → −306; error de `c01f4690` tal cual | Solo vía montaje en P2 (en `159a`/`1d6a` se descarta) |
| P4 | `c01f3e54` (`FAT_E:PBR…`) | leer PBR | marca final ≠ `0xAA55`; bytes/sector ≠ 512; sectores/cluster × 512 ≠ `0x4000` | error de lectura tal cual | Igual que P3 |
| P5 | `c01f407e` (`FAT_E:Unknown Fat Type`) | leer entrada de directorio | tipo de FAT guardado ∉ {12, 16} | OOM → −306; error de cluster tal cual | No como −302: `c01f4654` lo convierte en error de lectura y P2 lo colapsa en −302 de P2 |
| P6 | `c01f3fd0` (`FAT_E:End of cluster chain`) | siguiente cluster | petición de longitud 0 (`r5 ≤ 0` y `r5 % 512 == 0`): retorna el −302 inicial de `r4` | fin de cadena → **−305** | Ídem P5 |
| (P7) | `c01f3eb6` | montar partición | —; el literal se usa con `−4` → **−306** («Not initialized yet») | partición < 1 → −305 | n/a |

Hechos clave: (a) los fallos de montaje/lectura FAT **no se ven en el LED** salvo por P2; (b) P2 convierte cualquier fallo de archivo en −302 (incluido un archivo vacío); (c) la lista de archivos y particiones de P2 sale de **RAMCFG, leída del área Backup (ID `0xfa0080`, `c01f2ffc`) a `0xc005c000`**; sus rutas y números de partición **no se han resuelto estáticamente**.

Diferenciación (BINARIO por cadenas de log, **no** por el código): inicialización/alimentación → `LD3_E:Init Sync/Power…` (códigos −2xx/−301/−303 y sub-códigos de capa baja); BOS/partición → P1; configuración → P2; FAT → P3–P6; carga de imagen → `Load Image`, `Sync Ierr`. **El código −302 es compartido por BOS, CFG y FAT**, así que el LED por sí solo no distingue entre ellos.

## 4. Códigos compatibles con «3 lentos y luego 2 rápidos»

Orden temporal fijo LDR2 → LNG → SHT (velocidades 8 : 2 : 1 en semiperiodo). Enumeración exhaustiva sobre 1…9999 con grupos no vacíos = [3, 2]:

| n | (LDR2, LNG, SHT) | ¿Existe en los binarios? | Aspecto |
|---|---|---|---|
| **302** | 0 / 3 / 2 | **Sí**, Loader3 (§3) | 3 medios (1 Hz) + 2 rápidos (2 Hz) |
| 3002 | 3 / 0 / 2 | No como literal; Loader2 requeriría `err = −2002` | 3 pulsos de 2 s + 2 rápidos |
| 3200 | 3 / 2 / 0 | No como literal; Loader2 requeriría `err = −2200` | 3 pulsos de 2 s + 2 medios |

Códigos Loader3 próximos que **no** coinciden: −301 (3+1), −303 (3+3), −305 (3+5), −306 (3+6, **resultado por defecto «no debía volver»**), −307, −308; −202/−205 (2 + n). Loader2 siempre añade ≥1 pulso LDR2 (p. ej. −304 → n = 1304 → 1/3/4). Un código bruto de capa baja (p. ej. −131078) da miles de pulsos y no se parece. HIPÓTESIS: la equivalencia entre lo que ve el usuario y (0,3,2) depende de que «lentos» = LNG y «rápidos» = SHT.

## 5. Temporización

- ARITMÉTICA: unidades de `wait` = cuentas del contador `0xf2403000+0xc`. `c01f4fea` escribe `0x31` y luego `0x1031`; según `regs-timer.h`: `0x30` = `TMCS_FREERUN`, bits [2:0] = `TMCK` (1 = `DIV2`), `0x1000` = `TMST`. El BootROM usa `0x30/0x1030` (DIV1).
- Según `timex.h` (rama no FPGA): «CLK=2MHz (count up rate = 4MHz)»; el kernel usa `DIV4 → 1 MHz` y `DIV2 → 2 MHz`. Se deduce una entrada de 4 MHz. **INFERENCIA RESPALDADA**: esas cabeceras son un paquete OSS genérico de Sony (2014-02) sin nombre de modelo; no se midió el reloj de la a6000.
- Con DIV2 = 2 MHz: `d` = 4 000 000 → **2,000 s**; `d/2` = 1,0 s; `d/4` = 0,5 s; `d/8` = 0,25 s.
- Ciclo de −302: pausa 1,0 s · 3 × (0,5 encendido + 0,5 apagado) · pausa 1,0 s · 2 × (0,25 + 0,25) · pausa 2,0 s = **8,0 s**. El mismo código de Loader2 con 1000 añadido empezaría con un pulso de 2 s + 2 s.
- Límites: se ignora la latencia de `c01f379a`; la polaridad del LED; si el reloj real fuera 1 MHz o 24 MHz los tiempos serían ×2 o ÷12. La frecuencia de entrada solo se confirma con una medición (vídeo del LED con fotogramas contados, o captura lógica), que **no** se ha hecho.

## 6. Relación con el firmware 3.25

**No hay evidencia que relacione ningún productor con 3.25.** Hechos:
- La instalación 3.25 recompone `nflasha3` (TPZL; E25/E26-R2). Ningún productor del §3 lee `nflasha3`: P1 usa la tabla de particiones BOS, P3–P6 la geometría de la FAT (512 B/sector, clusters de 16 KiB, FAT12/16, marca `0xAA55`) y P2 los archivos que listan RAMCFG/Backup.
- El actualizador crea y borra `updater/uincomp` sobre `/dev/nflasha2` (R7b). Si esa FAT quedó alterada, Loader3 la monta en `159a`/`1d6a`, pero **descarta** el error. Solo cambiaría el resultado si RAMCFG listara un archivo de ese volumen (desconocido).
- Es **compatible** pero **no demostrado**: una escritura incompleta que afectara la tabla BOS, a la FAT de configuración o a RAMCFG (Backup) produciría −302; también lo haría cualquier otra causa independiente de 3.25. R5–R12 ya acotaban esto (R7b §D: «un retorno negativo de `c01f2f24` se propaga hasta `c01f3b74`»); R13 lo amplía a P1 y a las condiciones concretas.

## 7. Evidencias, incertidumbres y límites

| Afirmación | Tipo |
|---|---|
| `c01f3b74` es Loader3; `c0030c7c` es la gemela de Loader2 | BINARIO |
| Loader2 resta 1000; Loader3 no | BINARIO |
| −302: 3 palabras de literal, 9 cargas, 7 funciones; 3 cargas → −306 | BINARIO |
| Condiciones de P1–P6 | BINARIO (desensamblado; sin ejecutar) |
| P2/P1 llegan al LED; mount en `159a`/`1d6a`/`068a` no | BINARIO (aristas directas) |
| Tiempos 2,0 / 0,5 / 0,25 s | ARITMÉTICA sobre INFERENCIA de reloj |
| La cámara muestra (0,3,2) | HIPÓTESIS |
| Falta: RAMCFG real, rutas de P2, bloque `2b7c`, INFO 6, llamadas indirectas (punteros a función no resueltos), caminos por tablas `tbb` solo parcialmente seguidos | NO VERIFICADO |

El barrido de `r13_loader3.py` solo sigue BL/BLX/B.W directos y puede fallar con datos entre funciones; las aristas decisivas se releyeron con `listing`.

## 8. Recomendación para R14 (offline)

1. **Resolver RAMCFG:** localizar el registro Backup `0xfa0080` en las copias de NVRAM del repo (formato de `c01f498c`) y decodificar su tabla (partición, dirección, ruta). Discrimina P2 frente a P1.
2. Desensamblar `c01f2b7c` (carga BOS) y la firma `0x36343238` para ver de qué sector/bloque lee y qué la invalida.
3. Comprobar las condiciones P3/P4 (512 B, cluster 16 KiB, FAT12/16, `0xAA55`, ID FAT) contra las imágenes FAT de los paquetes 3.21/3.25 ya en el repo.
4. Solo después, si el usuario lo autoriza por separado: medir el LED (vídeo, sin tocar la cámara) para confirmar 0,5 s/0,25 s/8 s o descartarlo.

## Respuestas

- **Q1.** Loader3 (`0xc01f3b74`), y Loader2 tiene una copia gemela (`0xc0030c7c`); ver §1.
- **Q2.** Siete funciones: `c01f2c98` (BOS), `c01f2f24` (CFG), `c01f3d8a`, `c01f3e54`, `c01f3fd0`, `c01f407e` y `c01f3eb6` (esta última con −306 efectivo). −302 «crudo» solo en seis rutas; §3.
- **Q3.** Condiciones exactas en la matriz de §3.
- **Q4.** **Sí para P1 y P2** (aristas directas verificadas); **no** para el resto como −302 propio: `159a`/`1d6a`/`068a` descartan el error y P5/P6 se colapsan en P2.
- **Q5.** **No medidos.** Se obtiene 2,0/0,5/0,25 s bajo la hipótesis de entrada a 4 MHz (cabeceras Sony); falta medición.
- **Q6.** Solo 3002 y 3200 (§4); ninguno existe como literal; en Loader2 harían falta −2002/−2200.
- **Q7.** No. Compatible, no demostrado (§6).
- **Q8.** Mejor sustentada: **Loader3 alcanzado y fallo de lectura de metadatos/configuración (BOS o RAMCFG+FAT)** representado por −302. No se puede ordenar P1 frente a P2 sin RAMCFG; no hay base para atribuirlo a NAND, Darwin ni 3.25.
- **Q9.** Los pasos 1–3 de §8.

**Decisión:** R14 = pasos 1–3 de §8 (RAMCFG, bloque BOS, geometría FAT frente a imágenes 3.21/3.25). Ninguna acción física.
