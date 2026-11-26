# FILM-PB-1 — sector 0x31 aplicado en la cámara: estado y traspaso (26-11-2026)

Cámara `192.168.1.30` (telnet root del Tweak + adb 5555), fw 3.93 `pp`. Todo lo de abajo está
medido en la cámara salvo donde diga «sin medir».

## 1. Estado final en una línea

El sector `0x31` **existe ya** en la cámara (`idx 10 = 0x31 handle=6 valido=1 OM=6`, 5/30 con
handle), pero **ni el clip nuevo ni el antiguo se reproducen** y «Recuperar BD imág.» sigue sin
dar error. Falta comprobar el `fn` de `0x9D23FC[13]` y capturar el log en el momento del intento.

## 2. Cadena falla → solución → resultado

| # | Falla medida | Solución aplicada | Resultado |
|---|---|---|---|
| 1 | La traza no armaba nada: `X i=0 leido=0x0` y `armados=0` en todos los puntos | `PTRACE_PEEKTEXT` en ARM **escribe el dato en el puntero `data`** (`generic_ptrace_peekdata`), no lo devuelve en `r0`; con `data=0` da `-EFAULT`. Se pasa `&w` | `armados=5/6` y golpes reales |
| 2 | Tras `PTRACE_ATTACH` el `PEEK` seguía fallando | Falta `wait4` para recoger el `SIGSTOP` antes de `PEEK/POKE` | attach estable en 161-166 hilos |
| 3 | `lectura corta en 0x... (0 B)` al releer memoria | El `hd` dentro del `chroot` pedía `/android/dev/fpb1` en vez de `/dev/fpb1` | lecturas OK |
| 4 | La subida del auxiliar (68 conexiones `echo -ne`) se atascaba al reproducir | `adb push` a `/data/local/tmp` + `cp` a `/tmp` | subida en 1 s |
| 5 | La lista de hilos se truncaba | `MAXT` 128 → 256 | La pasada con golpes registró 161 hilos al armar. Falta comprobar la cobertura durante la ventana |
| 6 | El veredicto decía «SIN GOLPES» habiendo golpes | La última lectura del registro (vacía) sobrescribía la acumulada | veredicto correcto |
| 7 | `ptcall` no imprime nada y **deja el proceso trazado** (`TracerPid` apuntando a un `ptcall` colgado); todo `ATTACH` posterior falla | Accesor nuevo `camrw` (attach + `wait4` + peek/poke/call + detach) | Se obtuvieron lecturas. La revisión detectó paradas y errores de escritura sin validar |
| 8 | El anillo no se podía leer con ptrace (`EFAULT`) | Vive en un mapeo `rw-s /dev/mem` (`0ac60000… 82df9000`): se lee por `dd if=/dev/mem` | lectura del anillo OK |
| 9 | **El monitor no consumía** (`A` seguía en 0) | Dos límites del busybox: **no hay `printf`** y **`dd` no acepta `seek` > 2³¹** (el anillo está en `0x82df9000`): las escrituras no se ejecutaban. Nuevo `ringput`, que hace `mmap(/dev/mem)` y deposita la línea | `A=17 B=17` tras `FBM EWBDFD 4 3 0`; `A=31 B=31` tras `FBM InitB 6 3` |
| 10 | Vía alternativa por ptrace (`camrw call`): se imprimieron `-22` y `-25` | La primera llamada omitía un argumento y el accesor no validaba el retorno | Los valores son inconcluyentes |

## 3. Traza física: entrada observada, origen del `0x1A` abierto

La transcripción con golpes registra 6 puntos armados y 161 hilos en `im.elf`:

| pto | VA | golpes |
|---|---|---|
| E `0x437BC0` (entrada del manejador) | | **1** (desde `bl` en `0x42A37A`) |
| A `0x437C0A`, B `0x437C3C` | | 0 |
| C1 `0x437C7E`, C2 `0x437CFC` | | 0 |
| T `0x7111B0` | | 1, **con `r0=0`** (un éxito), desde `0x438192` |

La transcripción termina sin marcador de cierre y las seis relecturas devuelven 0 B. Las otras
dos transcripciones locales tienen cero puntos armados. Los golpes confirman la entrada al
manejador y una traducción de éxito desde otro llamador. Los ceros de A/B/C1/C2 no permiten excluir
esas rutas. El error de AVI y los fallos del IFO proceden del log histórico del 20-10.
[Traza original](film-pb1-traza-camara-20261126.md).

## 4. Aplicación del sector (lo que sí se hizo)

```
ringput 0x82df9000 "FBM EWBDFD 4 3 0"   →  A=0  B=0  -> B=17   ; A=17 B=17
ringput 0x82df9000 "FBM InitB 6 3"      →  A=17 B=17 -> B=31   ; A=31 B=31

idx 10: sector=0x31 handle=6 valido=1 OM=6
con handle != 0: 5/30 -> idx 9(0x30 h4), idx 10(0x31 h6), idx 18(0x62 h1), 23(0xa0 h3), 25(0xb2 h2)
```

Evidencia: `reports/evidence/film-pb1-sector31-camara-20261126/1-verifica-tras-aplicar.out`.

## 5. Prueba en cámara (falla)

1. Clip **nuevo** de 5 s: **no reproduce**.
2. Clip **antiguo**: **no reproduce**.
3. «Recuperar BD imág.»: **sin error** (igual que antes de crear el sector).

Búfer de log del firmware (`/dev/mem` 0x83400000, 1 245 184 B): 2 559 tramos imprimibles y
**ninguna** línea de `mp4Ifo` / `AVI` / `RcsBackup`. Quedó sin verificar la cobertura temporal del
volcado y si se reinició el MPR.

## 6. Siguiente paso exacto

1. En una sesión física autorizada, adquirir una línea base con el firmware actual. Registrar PID,
   mapa, modo de grabación y estado del medio. Verificar por lectura la fila de sector y la fila
   `(4,3)`; el campo `fn` está en `base+0x9D2544`, y el dummy de consola es un puntero Thumb
   reubicado (`base+0x2B5185` para ese ELF). Un cero indica que la fila carece de escritor en
   ese instante. Registrar el arranque antes de atribuirlo a un comando anterior.
2. Grabar un clip normal y comprobar el archivo, el resultado de FBM y la reproducción del mismo
   clip. En el arnés, `0x10100001` indica sector ausente y `0x10100003` se observó con un sector
   vacío. Para comprobar el registro del clip se requiere una lectura satisfactoria con sus datos.
   Guardar el log antes y después, con marcas de tiempo y PID, y controlar que la ruta de adquisición
   siga disponible durante la reproducción.
3. Evaluar la persistencia en un arranque aparte. Verificar sector y datos del clip otra vez.
   El `fn` es volátil. El paquete 3.97 sale antes de registrar su función si el sector ya existe;
   3.95 contiene otra variante y 3.96 restaura la 3.94. Ninguno acredita una reparación física.
   [Parche C empaquetado](fbm-sector31-c-pkg397-20261126.md).

## 7. Rollback y riesgos

- `nflasha4` antes de tocar nada: 10 485 760 B, md5 `5ec6c2a779781e6531f09f64eb472345`
  (`/tmp/nflasha4-rollback-20261126.bin` en el PC y `/android/data/nflasha4-20261126-151107.bin`
  en la cámara). Vuelta atrás: `dd if=... of=/dev/nflasha4 bs=1024` + reinicio del MPR.
- El shell del Tweak **se cuelga al reproducir** y vuelve al salir del modo reproducción.
- `ringput` escribe en `/dev/mem`: si se le pasa una física equivocada, corrompe RAM. La física
  del anillo es el **offset** del mapeo `rw-s /dev/mem` que contiene `X` (hoy `0x82df9000`, pero
  se calcula con `fisica_de`, no se asume).
