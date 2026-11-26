# FILM-PB-1 — traza en la cámara real: el manejador de PlayMovie corre y no produce el 0x1A (26-11-2026)

> **Revisión de la evidencia:** la captura con golpes quedó incompleta. Confirmó entrada al manejador
> y una traducción con `r0=0`. Para el alcance de esos resultados y los pasos vigentes,
> véase [el resultado auditado](film-pb-1-sector31-resultado-20261126.md#3-traza-física-entrada-observada-origen-del-0x1a-abierto).

Cámara: `192.168.1.30` (telnet root del Tweak + adb 5555), fw instalado 3.93 (`pp`).
Kit: `scripts/camera_filmpb1_trace.py` (puntos UDF 0xde00 por ptrace). Arreglo del sector:
`scripts/film_pb1_sector31.py`.

## 1. Respuesta corta

1. **El manejador `FUN_00437BC0` se ejecuta** (punto E `0x437BC0`) y **no pasa por ninguna de sus
   tres ramas productoras del `0x1A`**: A `0x437C0A`, B `0x437C3C` y las dos llamadas a la
   traducción (`0x437C7E`, `0x437CFC`) **no dispararon** en dos reproducciones del clip.
2. El único otro golpe fue la **traducción de un éxito** (`0x7111B0` con `r0=0`), llamada desde
   `0x438192`, 124 ms antes de E, en el mismo hilo.
3. Llamador del manejador: `bl 0x437bc0` en **`0x42A37A`** (despachador del hilo FeaCore,
   coherente con `FUN_00429C38`), con `r0`=this, `r2=1`.
4. **Confirmado en la cámara el diagnóstico FBM**: la tabla de sectores `base+0xA3699C` tiene
   **4/30 entradas con handle** (idx 9 `0x30` h4, idx 18 `0x62` h1, idx 23 `0xA0` h3,
   idx 25 `0xB2` h2) y **idx 10 (`0x31`, OM 6, mediaID 3) está a 0** (`handle=0 valid=0 OM=0`).
   Es exactamente el volcado del 20-10: nada la ha recreado.
5. El anillo del monitor EX-PC está vivo y vacío: `X=0x0ac60000`, `A=0`, `B=0`, 1023 B libres.
6. **El arreglo no se ha aplicado**: el depósito de la primera línea (`FBM EWBDFD 4 3 0`) no fue
   consumido (`A` siguió en 0). Nada escrito en `nflasha4`; volcado de rollback ya hecho (§5).

## 2. Cómo se midió

Dos pasadas con ventana armada (180 s y 240 s) sobre `im.elf` (PID 143 y 145), 161-166 hilos
trazados con `PTRACE_ATTACH` + `UDF 0xde00` de un solo golpe por punto, y restauración verificada
del código tras la traza.

| pto | VA ELF (libmpr 3.21) | ejecución | golpes |
|---|---|---|---|
| A | `0x437C0A` | `base+0x437C0A` | **0** |
| B | `0x437C3C` | `base+0x437C3C` | **0** |
| T | `0x7111B0` | `base+0x7111B0` | 1 (`r0=0`, `lr=0x438197`) |
| E | `0x437BC0` | `base+0x437BC0` | **1**, `lr=0x42A37F` |
| C1 | `0x437C7E` | `base+0x437C7E` | 0 |
| C2 | `0x437CFC` | `base+0x437CFC` | 0 |

Golpes literales del auxiliar (pasada con E):

```
H ms=0x7a9e i=0x2 tid=0x18a pc=0x728d1b0 r0=0x0 r1=0x0 r2=0x0 r3=0x0 lr=0x6fb4197 left=0x5
H ms=0x7b1a i=0x3 tid=0x18a pc=0x6fb3bc0 r0=0xc1de008 r1=0x0 r2=0x1 r3=0x0 lr=0x6fa637f left=0x4
```

Desensamblado de los llamadores (`libmpr.so` 3.21, Thumb):

```
00438190  2046        mov r0, r4
00438192  d9f20df8    bl #0x7111b0        ← T con r0=0 (traducción de un éxito)
...
0042a372  2046        mov r0, r4
0042a378  3146        mov r1, r6
0042a37a  0df021fc    bl #0x437bc0        ← E, el manejador
```

Consecuencia: el `MPR::ER_FAILED(0x1A)` que ve `ObjPlayerCore::PlayMovieCmp` **no sale de las
guardas del manejador de PlayMovie** en este estado de la cámara. Encaja con el traspaso del
25-11 (PlayMovie acepta 0 y el fallo llega asíncrono) y con el log real del 20-10, donde el error
nace en el motor AVI (`AviSeqPlay.cpp Error=[ER_BADARG]`) por el IFO sin cargar.

## 3. Estado de la tabla FBM y del anillo (cámara real, solo lectura)

```
== anillo del monitor ==
  X=0x0ac60000  A=0  B=0  libres=1023 de 1023
== tabla de sectores (base+0xA3699C, 30 x 0x14) ==
  idx 10: sector=0x31 handle=0 valido=0 OM=0
  con handle != 0: 4/30 -> idx 9(0x30 h4), idx 18(0x62 h1), idx 23(0xa0 h3), idx 25(0xb2 h2)
  DFB/FBS (diagnóstico) [0x9e484c]=0x01 [0x9e598c]=0x00
```

Coincide entrada por entrada con el volcado de RAM del 20-10 descrito en
[docs/STATE.md](../docs/STATE.md) (§ «causa raíz FBM»). La causa material sigue siendo la misma:
sin el sector `0x31` no se crea la BD de respaldo, `RcsBackupTblData` falla, el IFO no se carga y
el motor devuelve `ER_BADARG`.

## 4. Estado del arreglo (bloqueado)

`scripts/film_pb1_sector31.py --aplica --escribe` llegó a la fase 7 y **abortó sin escribir**:

```
== 7. línea 1: «FBM EWBDFD 4 3 0» ==
ABORTADO (no se escribe nada): el monitor no consumió «FBM EWBDFD 4 3 0» (A=0, esperaba 17)
```

Fases 1-6 completas: alcance (uid 0), PID, base `libmpr`, tabla antes, volcado de rollback de
10 485 760 B con md5 verificado.

## 5. Volcado de rollback (válido)

| copia | tamaño | md5 |
|---|---|---|
| `/tmp/nflasha4-rollback-20261126.bin` (PC) | 10 485 760 B | `5ec6c2a779781e6531f09f64eb472345` |
| `/android/data/nflasha4-20261126-151107.bin` (cámara) | 10 485 760 B | `5ec6c2a779781e6531f09f64eb472345` |

Vuelta atrás: `dd if=/android/data/nflasha4-20261126-151107.bin of=/dev/nflasha4 bs=1024` +
reinicio del MPR. (La tarjeta no es escribible desde el shell Linux: `/mnt/sdcard` es de solo
lectura y `/android/mnt/sdcard` es FUSE del lado Android; `/android/data` sí vale.)

## 6. Fallos del kit encontrados y corregidos (los tres primeros impedían medir)

1. **`PTRACE_PEEKTEXT` en ARM escribe el dato en el puntero `data`** (`generic_ptrace_peekdata`),
   no lo devuelve en `r0`: con `data=0` el kernel da `-EFAULT` y todo punto se leía como `0x0`.
   Síntoma: `X i=0 addr=... leido=0x0 esperado=0x231a` y `armados=0`.
2. **Faltaba recoger el `SIGSTOP` del `PTRACE_ATTACH`** (`wait4`) antes de `PEEK/POKE`.
3. Lectura de `/proc/PID/mem`: el `hd` dentro del `chroot` pedía `/android/dev/fpb1` en vez de
   `/dev/fpb1` → «lectura corta (0 B)».
4. Subida del auxiliar por 68 conexiones `echo -ne` (frágil, se atascaba con la cámara ocupada):
   ahora `adb push` + `cp`; el registro remoto ya no se borra.
5. El veredicto se calculaba sobre la última lectura del log (una lectura vacía borraba los
   golpes): se acumulan las líneas.
6. `MAXT` 128 → 256: la cámara tiene 161-166 hilos; antes se quedaban 34 sin trazar.

## 7. `ptcall` no sirve en esta cámara; `camrw` sí

`tools/camera-ptrace/ptcall` se queda en `wait_stop` tras el `ATTACH` (no imprime nada) y deja el
proceso trazado: el `TracerPid` queda apuntando a un `ptcall` colgado y **todo** intento
posterior falla con `ATTACH falló (... )`. Se vio con `grep TracerPid /proc/<pid>/status` = PID
del `ptcall` vivo. Accesor nuevo con el patrón que sí funciona (attach + `wait4` + peek/poke +
detach): `tools/camera-ptrace/camrw.c` → `/tmp/camrw`, misma interfaz
(`PID TID peek ADDR LEN`, `PID TID poke ADDR bb..`).

Además, **los mapeos de `/dev/mem` no se pueden leer con ptrace** (`access_process_vm` da
EFAULT): el anillo vive en `0ac60000-0acdc000 rw-s 82df9000 /dev/mem`, así que se lee y escribe
por `dd if=/dev/mem`/`of=/dev/mem` con la física `0x82df9000 + (X - 0x0ac60000)`. Eso ya está en
`film_pb1_sector31.py` (`fisica_de`, `peek_mem`, `poke_mem`), pero **sigue pendiente saber por qué
el monitor no consume** (§4).

## 7-bis. Por qué el monitor no consumió (mecanismo, con citas)

- Descriptor `u32` en `libmpr+0xA4FD88` = **X**, y **cambia en cada arranque**
  (0x8f884000 → 0x904e2000 → 0x0ac60000). Mismo descriptor: `[+4]=0x82DF9000`, `[+8]=0x8000`.
- Cabecera en X: `[X]=A`, `[X+4]=B`, datos en `X+0x10`, **0x400 B con un hueco ⇒ 0x3FF útiles**.
  A y B son **índices (`mod 0x400`)**, no punteros; el objeto de 16 B vive en `libmpr+0xA51AC4`
  (ctor `0x684A48`: `+0=&A`, `+4=&B`, `+8=buf`, `+C=0x400`).
- **B lo incrementa el productor** (`0x684ACC`, `strb` en 0x684AD8, `B=(B+1)%0x400` en
  0x684ADE-0x684AE6) y **A el consumidor** (`0x684CBC`, 0x684CCC-0x684CD4); terminador CR `0x0D`.
- **No hay flag «línea lista»: el flag es B.** Si no se publica `[X+4]` después de los bytes, A no
  se mueve nunca. El script sí lo hace (`poke_mem(X+4, B+n)`), así que quedan dos hipótesis **no
  medidas**: (a) coherencia de caché entre el `dd` sobre `/dev/mem` y el mapeo del MPR —en el arnés
  el `mmap(/dev/mem)` sale anónimo, así que la vía `/dev/mem` nunca se ejercitó allí—; (b) el
  descriptor `X` del monitor es otro objeto que el que yo toco (hay que confirmar que
  `libmpr+0xA51AC4` apunta al mismo X).
- El requisito es solo `X != 0` (monitor construido): no hay habilitación, selector, hilo propio ni
  tecla. En el arnés `A` pasó 0→17→31 con depósitos de 16+CR y 13+CR.

## 8. Siguiente paso exacto

Con la cámara encendida y el telnet activo (el shell del Tweak se cuelga al reproducir y vuelve al
salir del modo reproducción):

0. **Vía directa, sin anillo (preferente):** `camrw` ya tiene modo `call`, que ejecuta una función
   del firmware en un hilo detenido (`lr` → `UDF 0xde00` en su stack, restaura registros y hace
   detach). Llamar `camrw <pid> 0 call <base+0x2B1DEC> 4 3 0`
   (`BackupMgr::EntryWriteBaseDataFunction`, sólo escribe en `.data`) y después
   `camrw <pid> 0 call <base+0x2B43F0> 6 3` (`BackupMgr::InitBackupData`, toca flash: si el MPR se
   reinicia, no se ha perdido nada). Comprobar luego idx 10.
1. Si se prefiere el anillo: probar el depósito a mano y en este orden, para separar «no se escribe» de «no se consume»:
   `printf 'AB\r' | dd of=/dev/mem bs=1 seek=$((0x82df9010)) conv=notrunc` y releer
   `dd if=/dev/mem bs=1 skip=$((0x82df9000)) count=32`; después
   `printf '\003\000\000\000' | dd of=/dev/mem bs=1 seek=$((0x82df9004)) conv=notrunc` y releer A.
   Si A no se mueve, comprobar que el monitor tiene su hilo (el descriptor `X` no es 0) y si el
   anillo exige que la consola esté «abierta» (ver informe del anillo).
2. Con el depósito funcionando, `--aplica --escribe --destino /android/data` y comprobar idx 10 =
   `0x31 / handle válido / +8=1 / OM 6`.
3. Grabar un clip nuevo de 5 s en la cámara y reproducirlo; después los antiguos y «Recuperar BD
   imág.». El sector no rellena la BD: habilita que la cámara la reconstruya.
