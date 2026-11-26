# FILM-PB-1 / sub-consola-fbm-anillo — el anillo de entrada del monitor EX-PC y cómo meterle órdenes

**Fecha:** 2026-11-26 · **Binario:** `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21) ·
**Arnés:** perfil `analysis/gui/g22/harness/live/fbm/` · **Evidencia:**
`reports/evidence/film-pb-1-sub-consola-fbm-20261127/` (`run0`…`run27`, shim, `ptcall`, `fbm_ring.sh`).

## Resumen (15 líneas)

1. El monitor («**** EX-PC Monitor Program ****» 0x90F1A0, prompt `MON>`) no lee tty ni socket: lee un anillo en RAM del MPR.
2. `X = u32*(libmpr+0xA4FD88)` (selector 0x5F7A14(1,…), uso 0x683C94–0x683C9E); **cambia en cada arranque**.
3. Objeto stream 16 B en `libmpr+0xA51AC4`, ctor **0x684A48** `{+0=&A,+4=&B,+8=buf,+C=0x400}`, hecho en 0x683CA6–0x683CAE.
4. `[X]`=A índice de lectura, `[X+4]`=B de escritura; datos en `X+0x10`, 0x400 B, un hueco libre ⇒ **0x3FF útiles**.
5. Productor **0x684ACC** (`strb r1,[r0,r2]` 0x684AD8; `B=(B+1)%0x400` 0x684ADE–0x684AE6); consumidor **0x684CBC**.
6. Vacío 0x684A64 (1 si A==B), lleno 0x684A7A, libres 0x684AAC=(A-B-1)mod 0x400. **Terminador de línea: CR 0x0D** (medido).
7. **No hay flag «línea lista»: el flag es B**; sondeo 0x683D20 → `0x5FD6E0(0x64)` (0x683D2E–0x683D30) ⇒ ~100 ms, medido ≤1 s.
8. Quién consume: getc 0x683D04 (0 llamantes `bl`: por puntero) y putc 0x683D4C (llamado en 0x683564/0x6835D0/0x683638/0x68367C); 0x683D20 como dato en `libmpr+0xBF1C4`.
9. **Run6, desde dentro**: depositando `FBM SetSMI 20 90 7 1 10` (A 0→24) queda **idx 20 (0x90) h7/s1** en `base+0xA3699C`.
10. **Run23, línea base** (8 s, sin tocar nada): **0/30** entradas con handle≠0 ⇒ lo de run6/run27 no es estado de arranque.
11. **Run27, desde FUERA por ptrace**: `fbm_ring.sh` → `X=0x8fb38000 A=0 B=0 libres=1023`, `ok B: 0 -> 24` → **idx 21 (0x91) h7/s1**.
12. Run26 igual con `BASE` explícito. `InitB 6 3` se consume (run6) pero no crea: `CreateSector32` = **0x7 FBS_INVALID_PROCESS**.
13. `tools/camera-ptrace/ptcall` (ARM estático, 9,9 KiB): `peek|poke|call|ring`; medido `peek` de la tabla, `poke`→`0x12345678` y `call GetErrorString(7)` → `ret=0xaeb03322 centinela=1 text=FBS_INVALID_PROCESS`.
14. Trampas del ABI de ptrace en ARM resueltas y medidas: PEEKDATA entrega el dato por el puntero `data` (0 ⇒ -EFAULT), siginfo 128 B, CPSR.T según el bit 0 de la VA (§3.2).
15. Procedimiento por telnet en §5 (ejecutado en el invitado salvo el propio telnet y el `/proc` real); lo no verificado, en §6.

## 1. Formato exacto del anillo

### 1.1 De dónde sale X

`0x5F7A14(idx, out0, out1, out2)` es un selector de MemInfo (`ldr r0,[pc]=0xA4FD88` en 0x5F7A3E). Para
`idx=1` (0x5F7A3E–0x5F7A4A):

```
0x5F7A3E  ldr r0,[pc,#0x98]   ; 0xA4FD88
0x5F7A40  ldr r4,[r0,#4]      ; out0 = [0xA4FD88+4]
0x5F7A44  ldr r1,[r0]         ; out1 = [0xA4FD88+0]
0x5F7A48  ldr r2,[r0,#8]      ; out2 = [0xA4FD88+8]
```

y el que se usa es **out1** (`0x683C94: ldr r3,[r7,#8]; 0x683C98: str r3,[r5]` con `r5=0xA51AC8`), es
decir **X = u32 en `libmpr+0xA4FD88`**. Medido (run6): descriptor `[0xA4FD88]=0x8f884000`, `[+4]=0x82DF9000`,
`[+8]=0x8000`, `[+C]=0`. En otros arranques X fue 0x8FC32000 (run4/run5), 0x8FA84000 (run26),
0x8FB38000 (run27): **hay que leerlo en cada arranque**.

> `0x82DF9000` es la base del anillo de *log* del MPR (las líneas de log caen en 0x82DF9300–0x82DFC400),
> no el anillo de entrada.

### 1.2 Construcción del objeto y del anillo (0x683C64–0x683CB4)

```
0x683C90  bl  0x5F7A14       ; (1, &out0, &out1, &out2)
0x683C94  ldr r3,[r7,#8]     ; r3 = X
0x683C98  str r3,[r5]        ; [0xA51AC8] = X
0x683C9A  blx new(0x10)      ; objeto stream de 16 B
0x683C9E  ldr r1,[r5]        ; r1 = X
0x683CA0  mov.w r3,#0x400
0x683CA4  str r3,[sp]        ; 5.º argumento = size = 0x400
0x683CA6  adds r2,r1,#4      ; r2 = X+4
0x683CA8  add.w r3,r1,#0x10  ; r3 = X+0x10
0x683CAE  bl  0x684A48       ; ctor(obj, X, X+4, X+0x10, 0x400)
0x683CB2  ldr r3,[pc]        ; =0xA51AC4  (se guarda el objeto)
```

ctor **0x684A48** (leído con `dis`):

```
0x684A4C  stm.w r0,{r1,r2,r3} ; +0=&A(X)  +4=&B(X+4)  +8=buf(X+0x10)
0x684A52  ldr r3,[r7,#0xc]    ; size
0x684A54  str r3,[r0,#0xc]    ; +0xC = 0x400
0x684A56  movs r3,#0
0x684A58  str r3,[r1]         ; *(u32*)X     = 0   -> A
0x684A5A  str r3,[r2]         ; *(u32*)(X+4) = 0   -> B
```

Medido en ejecución (run6): objeto `0xA51AC4 → 0x8FA2B6F0` con `+0=0x8F884000, +4=0x8F884004,
+8=0x8F884010, +C=0x400`.

### 1.3 Mapa de bytes

| VA | tamaño | contenido |
|---|---|---|
| `X+0x00` | 4 | **A** — índice de lectura (consumidor) |
| `X+0x04` | 4 | **B** — índice de escritura (productor) |
| `X+0x08` | 4 | sin uso (medido `0`) |
| `X+0x0C` | 4 | sin uso (medido `0xB41`, basura del montón) |
| `X+0x10` | 0x400 | búfer circular; un hueco libre ⇒ **0x3FF útiles** |
| `X+0x410` | — | fin del área (cabe en una página: `mincore` página 0 = mapeada, la 1 no — run6) |

### 1.4 Operaciones, instrucción a instrucción

- **Escribir un byte (0x684ACC)**: `0x684AD2 ldr r2,[r0,#4]` (ptr B) · `0x684AD6 ldr r0,[r0,#8]` (buf) ·
  `0x684AD8 strb r1,[r0,r2]` · `0x684ADE ldr r0,[r4]`, `0x684AE0 adds r0,#1`, `0x684AE2 blx 0x11FDDC`
  (`__aeabi_uidivmod`, size), `0x684AE6 str r1,[r4]` ⇒ `B=(B+1)%0x400`.
- **Leer un byte (0x684CBC)**: `0x684CC8 ldr r0,[r4]` (A) · `0x684CCA ldrb r5,[r2,r0]` ·
  `0x684CCC adds r0,#1`, `0x684CCE blx 0x11FDDC`, `0x684CD4 str r1,[r4]` ⇒ `A=(A+1)%0x400`.
- **Vacío (0x684A64)**: `0x684A6C ldr r0,[r2]; 0x684A6E ldr r3,[r3]; 0x684A70 subs r3,r0,r3;
  0x684A72 rsbs; 0x684A74 adc.w` ⇒ **1 si A==B**.
- **Lleno (0x684A7A)**: `0x684A86 subs r1,r3,#1` + `0x684A88 rsb ip,r2,r1` ⇒ 1 si `(A-1)==B` (y el caso
  `A==0, B=size-1` en 0x684A94–0x684A9A).
- **Libres (0x684AAC)**: `0x684AB8 cmp r2,r3` … `0x684AC2` ⇒ `(A-B-1) mod 0x400`.
- **Sondeo (0x683D20)**: `0x683D28 bl 0x683C54` (flag global); si 0 → `0x683D2E adds r0,#0x64;
  0x683D30 bl 0x5FD6E0` (espera de 100) y después `0x683D3C b.w 0x684A64` ⇒ **cadencia ~100 ms**.
- **Quién lo llama**: `calls 0x683D04` = 0 (getc por puntero), `calls 0x683D20` = 0 pero hay un dato en
  `libmpr+0xBF1C4` (tabla `{0x17, ptr}` en 0xBF1A0–0xBF1DC con 0x683CF4/…/0x683D20/…), y
  `calls 0x683D4C` = 0x683564, 0x6835D0, 0x683638, 0x68367C (rutinas de salida del monitor).

### 1.5 Terminador, longitud y «línea lista»

- **Terminador: CR (0x0D)**. Verificado dos veces (run6 y run27): depositando `"…10\r"` la orden se
  ejecuta; el firmware escribe el CR igual que cualquier otro byte (0x684ACC).
- **Longitud máxima**: **NO_VERIFICADO** para la línea completa. El único tope que aparece es **0x1FE
  (510)** en el constructor de la cadena de argumentos (`0x682BE6 cmp.w r8,#0x1FE`, mensaje
  **"TOO LONG STR" 0x90EC7C** en `0x682C06`, búfer 0xA5189E). Se toma como tope práctico.
- **Flag de «línea lista»: no existe**; el único indicador es `A != B`. Por eso conviene **escribir los
  bytes y publicar `B` de una sola vez** (así el monitor nunca ve media línea); es lo que hacen el shim y
  `ptcall ring`.

## 2. Verificación en el arnés

Perfil `analysis/gui/g22/harness/live/fbm/` con shim propio (`reports/evidence/…/sonyshim-fbm.c`,
compilado por `comando.sh`). Lanzador: `pb_run_fbm.py` (`PBINJECT=8` = inyectar a los 8 s,
`PBSKIP=1` = sólo la prueba de ptrace, `PBSKIP=2` = sólo volcar la tabla).

### 2.1 Desde dentro del proceso (run6) — el anillo ejecuta la orden

Sin llamar a 0x2B50D8: se depositaron bytes con la semántica de 0x684ACC y se movió `B`.

```
[FBMR] X=0x8f884000  [X]=A=0 [X+4]=B=0  buf=0x8f884010
[FBMR] escribo en el anillo: "FBM SetSMI 20 90 7 1 10"   (A=0 B=0 antes)
[FBMR] tras escribir: A=0 B=24 ;  SetSMI: A=24 B=24 a los 1 s   <- el monitor lo consumió
[FBMC] tras-anillo-SetSMI  entradas con handle!=0 = 1/30
[FBMC] tras-anillo-SetSMI [15..29] … 20:090=h7/s1 …
[FBMR] escribo en el anillo: "FBM InitB 6 3" (A=24 B=24) → A=38 B=38 a los 1 s
[FBMR] escribo en el anillo: "FBM LTC 1"    (A=38 B=38) → A=48 B=48 a los 1 s
```

`SetSMI 20 90 7 1 10` deja **idx 20 (sector 0x90) handle=7 status=1** en `base+0xA3699C`: la línea llega
al handler y se ejecuta. `InitB 6 3` se consume pero la tabla no cambia (`CreateSector32` = **0x7
FBS_INVALID_PROCESS**, medido por símbolo en run3/run6).

**Línea base sin tocar nada** (run23, `PBSKIP=2`, dump a los 8 s): `entradas con handle!=0 = 0/30`, todas
`h0/s0` ⇒ lo anterior no es estado de arranque.

### 2.2 Desde FUERA del proceso, con ptrace (run27) — el camino de la cámara

`fbm_ring.sh` + `ptcall` (los mismos ficheros que se llevarían a la cámara), ejecutados por el shim como
haría el `telnet`:

```
[FBMP] $ PID=207 TID=315 PT=/usr/bin/ptcall /bin/sh /usr/bin/fbm_ring.sh 'FBM SetSMI 21 91 7 1 10'
maps: ae301000-aecbd000 r-xp 00000000 00:02 2496       /usr/lib/libmpr.so
X=0x8fb38000 A=0 B=0 libres=1023
ok B: 0 -> 24 (24 B)
[FBMP] tabla tras fbm_ring.sh:
[FBMP]   idx 20: name=0x90 handle=0 status=0 OM=0
[FBMP]   idx 21: name=0x91 handle=7 status=1 OM=0xa      <- la orden se ejecutó
[FBMP]   idx 22: name=0x92 handle=0 status=0 OM=0
```

Es decir: leer X del descriptor, leer A/B, escribir 23 B + CR en `X+0x10+B` y publicar `B` **desde otro
proceso** basta para que el monitor ejecute la línea. En run26 lo mismo con `BASE` explícito
(`X=0x8fa84000`, mismo resultado). `fbm_ring.sh` saca la base de `/proc/PID/maps`; dentro del chroot del
arnés no hay `/proc`, así que el shim escribió un `maps` sintético con la base verdadera para ejercitar
ese parser (eco `maps: …` arriba).

## 3. La alternativa ptrace: `tools/camera-ptrace/ptcall`

ELF ARM EABI **estático, sin libc**, 9,9 KiB (`sh tools/camera-ptrace/build.sh`). Modos:

```
ptcall [--dry] [--sp DIR] PID TID peek DIR LEN
ptcall [--dry] [--sp DIR] PID TID poke DIR BYTE...
ptcall [--dry] [--sp DIR] PID TID call NARG VA [A0..A3]
ptcall [--dry] [--sp DIR] PID TID ring BASE "TEXTO"     # TEXTO+CR al anillo del monitor
```

`call`: `PTRACE_ATTACH` → `GETREGS` → `r0..r3`=args, `LR=0xDEAD0000`, `PC=VA`, `CPSR.T`=bit0 de la VA →
`SETREGS` → `CONT` → se espera el **SIGSEGV con `si_addr==0xDEAD0000`** → se lee `r0` (y si parece puntero,
24 B de texto) → se restauran los 18 registros → `DETACH`. No parchea código.

### 3.1 Medido en el invitado (run17 / run20)

```
$ ptcall 209 367 peek 0xb6f1d768 0x10   -> 11 11 11 11 ...              (global del shim: 0x11111111)
$ ptcall 209 367 peek 0xae3e1000 0x10   -> 7f 45 4c 46 ...              (cabecera ELF de libmpr)
$ ptcall 209 367 peek 0xaee1799c 0x20   -> 10 00 00 00 00 00 00 00 ...  (tabla FBM: idx0=0x10 h0 s0)
$ ptcall 209 367 poke 0xb6f1d768 78 56 34 12 -> poke ok ;  pb_scratch = 0x12345678
$ ptcall 205 363 call 1 0xae5d0115 7    -> sig=11 code=0x00000001 fault=0xdead0000 ret=0xaeb03322 centinela=1
                                           text=FBS_INVALID_PROCESS
```

### 3.2 Trampas del ABI de ptrace en ARM (todas encontradas y corregidas aquí)

1. **`PTRACE_PEEKDATA` no devuelve el dato en `r0`**: el kernel hace
   `put_user(tmp, (unsigned long __user *)data)` (`arch/arm/kernel/ptrace.c`); con `data=0` devuelve
   **-EFAULT = -14**, que es lo que salía antes (run15: `f2 ff ff ff` en todas las palabras). Ahora se
   pasa `&w`. `POKEDATA` sí usa `data` como valor (funcionaba desde el principio).
2. **`siginfo_t` son 128 B**: con un búfer de 16 B el kernel escribe fuera del marco y **el trazador se
   caía** (`system -> 35584` = exit 139, run15). `si_addr` está en el 4.º word (offset 12).
3. **CPSR.T hay que fijarlo**: si la VA objetivo tiene el bit 0 a 1 hay que poner `CPSR.T`; si no, el
   código Thumb se ejecuta como ARM y el SEGV llega con `r0` sin tocar (run17: `ret=0x7`, `fault` raro).
4. **Las VA del invitado son «negativas» como `long`**: comparar `X > 0` o `ret > 0x10000` con signo da
   falso para 0x8F…/0xAE…. Hay que comparar como `unsigned long` (run25 falló por esto).

### 3.3 Riesgos al usarlo en la cámara

- **Mutex del FlashLib** (`MutexLock` 0x2B60A1, tomado en `CreateSector_Body` 0x2B6F96 y en
  `CheckAndRepairFlashBackup` 0x2B89CA): si el hilo elegido ya lo tiene, la llamada se cuelga y deja el
  MPR muerto. Con `ptrace ring` este riesgo **no existe**: sólo se escribe memoria, el trabajo lo hace el
  hilo del monitor en su propio contexto.
- **Elección de hilo**: `PTRACE_ATTACH PID` engancha al hilo principal (el de la UI). Mejor pasar el TID de
  un hilo ocioso; en el arnés se usó un hilo propio.
- **Pila**: `call` reutiliza la pila del hilo interrumpido; para funciones profundas usar `--sp`.
- **Señales**: si el proceso tuviera un manejador de `SIGSEGV` que reanuda, el centinela no pararía la
  ejecución; `ptcall` exige `si_addr==0xDEAD0000` e informa `centinela=0` si no.
- **Root** y `/proc` del mismo namespace (el Tweak da root por telnet).

## 4. Detalles del arnés que afectan a la prueba

1. **im.elf corre con `chroot /cam`** (`im_pb.sh`: `LD_PRELOAD=/usr/lib/sonyshim.so chroot /cam
   /usr/bin/im.elf`). Por eso `system()` desde el shim ve rutas del *chroot*.
2. **`/cam/tmp` es tmpfs** (`init` del initramfs, línea 6: `busybox mount -t tmpfs tmp /cam/tmp`): lo que
   se copie ahí desaparece. `ptcall` y `fbm_ring.sh` se dejan en **`/usr/bin`** (`/cam/usr/bin`).
3. **El `/cam` de la cámara no tiene `/bin/sh`** (sólo `busybox` y 7 applets): `system()` devuelve
   **32512 (=127)** hasta que se añade un `/bin/sh` (copia de `busybox` en el overlay). El `busybox` de la
   cámara **no trae `awk`** ⇒ `fbm_ring.sh` no usa awk/sed/od/cut: todo lo hace `ptcall ring`.
4. Interruptores usados: `PBINJECT=<s>` (cuándo inyecta), `PBSKIP=1` (sólo ptrace), `PBSKIP=2` (sólo
   volcado). Se pasan como 3.er argumento de `pb_run_fbm.py` (`SHIMEXTRA`), no por entorno del host.
5. `pb_run_fbm.py` corta al ver `[FBMC] FIN`; el guion del invitado espera `WAIT=900`, así que cualquier
   salida extra debe ir a `/dev/console` (que sí llega a `consola.log`).

## 5. Procedimiento reproducible desde el PC (telnet del Tweak, sin flashear)

```sh
# --- en el PC --------------------------------------------------------------------------------------
sh tools/camera-ptrace/build.sh                                   # -> tools/camera-ptrace/{ptcall,sctrace}
base64 -w0 tools/camera-ptrace/ptcall     > /tmp/ptcall.b64
base64 -w0 tools/camera-ptrace/fbm_ring.sh > /tmp/ring.b64
# --- en la cámara (root; el Tweak levanta «busybox telnetd -l sh») ---------------------------------
telnet <IP_CAMARA>
cat > /tmp/ptcall.b64 <<'EOF'
<pegar /tmp/ptcall.b64 en una línea>
EOF
base64 -d /tmp/ptcall.b64 > /tmp/ptcall && chmod +x /tmp/ptcall
cat > /tmp/fbm_ring.sh <<'EOF'
<pegar /tmp/ring.b64 en una línea>
EOF
base64 -d /tmp/ring.b64 > /tmp/fbm_ring.sh
PID=$(pidof im.elf); PID=${PID%% *}
sh /tmp/fbm_ring.sh                                   # estado: imprime «maps: <base>-…», X, A, B y hueco libre
BASE=0x…            # la base que acaba de imprimir la línea «maps:»
sh /tmp/fbm_ring.sh "FBM LTC 1"                       # 1.ª orden pedida
sleep 2
sh /tmp/fbm_ring.sh "FBM InitB 6 3"                   # crea el sector 0x91 (OM 6, media 3 = MS1)
sleep 3
/tmp/ptcall "$PID" 0 peek $((BASE + 0xA3699C + 0x14*21)) 0x14   # idx 21: +4 = handle, +8 = status
sh /tmp/fbm_ring.sh "FBM View"                        # vuelca la tabla al log de FBM (no a la consola)
```

Notas: (a) si no hay `awk`, `fbm_ring.sh` ya saca la base con `while read`+`case`; (b) `View` escribe en el
log del MPR (0x82DF9xxx), no en la consola serie; (c) el resultado real de `InitB` se ve en el handle de
`0xA3699C` (offset `+4`) y en el log de FBM (`BackupMgr::InitBackupData…`, 0x2B440E), **no** en la consola
(InitB devuelve 1 siempre: `0x2B5B5E`); (d) si `CreateSector32` falla, el código es lo que devuelve a
0x2B40CC: en el arnés **0x7** (`FBS_INVALID_PROCESS`, tabla de textos 0x7E9488).

## 6. Límites de lo medido (NO_VERIFICADO)

1. **La cámara real**: nada de esto se ha ejecutado en ella (el encargo lo prohíbe).
2. **`/proc/PID/maps` real de la cámara**: el parser de `fbm_ring.sh` se probó contra un fichero sintético
   con la base verdadera (run27) y contra un maps de ejemplo en el PC; no contra la cámara.
3. **`/dev/mem`**: la dirección física de X no está en el descriptor (los dos valores son VAs); haría falta
   `pagemap`, no probado. El camino bueno es `ptrace` (probado).
4. **Tope de longitud de línea**: sólo consta el 0x1FE del constructor de argumentos.
5. **Línea sin CR**: no probado (todas llevaban 0x0D).
6. **Concurrencia**: si el monitor está leyendo justo cuando se publica `B`, el anillo es SPSC y basta el
   orden «bytes y luego B»; no se ha medido con el monitor a media línea.

## 7. Evidencia

`reports/evidence/film-pb-1-sub-consola-fbm-20261127/`:
`run0`…`run27/consola.log` (run6 = anillo desde dentro; **run17/run20** = peek/call de ptcall;
**run23** = línea base 0/30; run26 = `ptcall ring` con BASE; **run27** = `fbm_ring.sh` completo),
`sonyshim-fbm.c` (shim con el ensayo del anillo y la prueba de ptrace), `comando.sh`, `pb_run_fbm.py`,
`im_pb.sh`, `evidencia/tabla-comandos-fbm.txt`, `evidencia/initb-cadena-y-tablas.txt`.
Herramientas: `tools/camera-ptrace/ptcall.c`, `tools/camera-ptrace/fbm_ring.sh`,
`tools/camera-ptrace/build.sh`.
