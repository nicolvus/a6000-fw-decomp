# FILM-PB-1 / sub-consola-fbm-anillo — el anillo de entrada del monitor EX-PC (27-11-2026)

## Resumen (≤20 líneas)

1. El monitor de libmpr («**** EX-PC Monitor Program ****» 0x90F1A0, prompt `MON>` 0x90EC49) **no lee de
   un tty ni de un socket**: lee de un **anillo en un área de memoria** del propio proceso MPR.
2. Puntero del área: **X = u32 en `libmpr+0xA4FD88`**. Descriptor `{+0=X, +4=0x82DF9000, +8=0x8000,
   +C=0}` (selector `0x5F7A14(1,…)`); el código usa el campo `+0` como VA (0x683C94–0x683C9E).
3. Objeto stream (16 B) en `libmpr+0xA51AC4`, ctor **0x684A48**: `{+0=ptr A, +4=ptr B, +8=buf, +C=size}`,
   construido en **0x683CA6–0x683CAE** con `A=X`, `B=X+4`, `buf=X+0x10`, `size=0x400`.
4. Cabecera: **`[X]`=A = índice de LECTURA** (lo mueve el monitor), **`[X+4]`=B = índice de ESCRITURA**
   (lo mueve quien escribe); `X+8`/`X+0xC` no se usan (medido: `0` y `0xB41` de basura). Datos en
   **`X+0x10`, 0x400 B, con un hueco siempre libre** ⇒ capacidad real **0x3FF**.
5. Productor: `buf[B]=ch; B=(B+1) mod 0x400` (**0x684ACC**, `strb r1,[r0,r2]` + `uidivmod`). Consumidor:
   `ch=buf[A]; A=(A+1) mod 0x400` (**0x684CBC**). Vacío = `A==B` (**0x684A64** devuelve 1); lleno =
   **0x684A7A**; libres = `(A-B-1) mod 0x400` (**0x684AAC**).
6. **Terminador de línea: CR (0x0D)** — verificado: depositando `"FBM SetSMI 20 90 7 1 10\r"` el monitor
   la ejecuta. No hay campo de «línea lista»: **el flag es `B`**, y el consumidor sondea (latencia medida
   **≤1 s**; el sondeo del monitor es 0x683D20 → `0x683C54`, si no hay nada `0x5FD6E0(0x64)` y
   `0x684A64`).
7. **Verificado en el arnés** (perfil `fbm`, QEMU): escribiendo el anillo a mano (sin llamar a 0x2B50D8),
   `FBM SetSMI 20 90 7 1 10` deja **`idx 20 (0x90): handle=7, status=1`** en `base+0xA3699C`; `FBM InitB 6 3`
   y `FBM LTC 1` también se consumen (A pasa de 24→38→48).
8. Alternativa si el anillo no fuese escribible: **ptrace** con `tools/camera-ptrace/ptcall` (ARM estático,
   nuevo): orden de llamadas y riesgos en §3; ejecutado y verificado **en seco en el propio invitado** (§4).
9. Procedimiento desde el PC por telnet en §5: `sh fbm_ring.sh "FBM InitB 6 3"` (deposita la línea con
   `PTRACE_POKEDATA`, sin flashear, sin reiniciar el MPR).

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
decir **X = u32 en `libmpr+0xA4FD88`**. Medido (run6): `[0xA4FD88]=0x8F884000`, `[+4]=0x82DF9000`,
`[+8]=0x8000`, `[+C]=0`. En otro arranque (run4/run5) X fue `0x8FC32000`: **cambia en cada arranque**
(heap/mmap con ASLR) ⇒ hay que leerlo siempre, no se puede fijar.

> `0x82DF9000` es la dirección base del anillo de log del MPR (las líneas de log caen en
> `0x82DF9300–0x82DFC400`, ya documentadas en `knowledge/CURRENT.md`), no el anillo de entrada.

### 1.2 Construcción del objeto y del anillo (0x683C64–0x683CB4)

```
0x683C78  ldr r3,[pc]        ; =0xA51AD4   objeto "de inicialización" de 0x1c B (new en 0x683C6C)
0x683C82  ldr r5,[pc]        ; =0xA51AC8   aquí se guarda out1 (= X)
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
0x683CB2  ldr r3,[pc]        ; =0xA51AC4   se guarda el objeto
```

ctor **0x684A48**:

```
0x684A4C  stm.w r0,{r1,r2,r3} ; +0=r1(X)  +4=r2(X+4)  +8=r3(X+0x10)
0x684A52  ldr r3,[r7,#0xc]    ; size
0x684A54  str r3,[r0,#0xc]    ; +0xC = 0x400
0x684A58  str r3,[r1]  (=0)   ; *(u32*)X     = 0   -> A
0x684A5A  str r3,[r2]  (=0)   ; *(u32*)(X+4) = 0   -> B
```

Medido en ejecución (run6): objeto `0xA51AC4 → 0x8FA2B6F0` con `+0=0x8F884000, +4=0x8F884004,
+8=0x8F884010, +C=0x400`.

### 1.3 Mapa de bytes (resumen)

| VA | tamaño | contenido |
|---|---|---|
| `X+0x00` | 4 | **A** — índice de lectura (consumidor) |
| `X+0x04` | 4 | **B** — índice de escritura (productor) |
| `X+0x08` | 8 | sin uso (medido `0x00000000` y `0x00000B41`) |
| `X+0x10` | 0x400 | búfer circular; un hueco libre ⇒ **0x3FF** útiles |
| `X+0x410` | — | fin del área (cabe en una sola página: `mincore` de la página 0 = mapeada, la 1 no) |

### 1.4 Operaciones, instrucción a instrucción

- **Escribir un byte (0x684ACC)**: `0x684AD2 ldr r2,[r0,#4]` (ptr B) · `0x684AD6 ldr r0,[r0,#8]` (buf) ·
  `0x684AD8 strb r1,[r0,r2]` · `0x684ADE ldr r0,[r4]`, `0x684AE0 adds r0,#1`, `0x684AE2 uidivmod(size)`,
  `0x684AE6 str r1,[r4]` ⇒ `B=(B+1)%0x400`.
- **Leer un byte (0x684CBC)**: `0x684CC8 ldr r0,[r4]` (A) · `0x684CCA ldrb r5,[r2,r0]` ·
  `0x684CCC–0x684CD4` ⇒ `A=(A+1)%0x400`.
- **Vacío (0x684A64)**: `r0=A, r3=B; subs r3,r0,r3` + `rsbs/adc` ⇒ devuelve **1 si A==B**.
  Usado por el «getc del monitor» **0x683D04** (`0x683D0C bl 0x684A64; 0x683D10 cbnz → -1`; si no,
  `0x683D14 bl 0x684CBC`).
- **Lleno (0x684A7A)**: `(A-1)==B` ó `(A==0 && B==0x3FF)` ⇒ 1. Usado por el «putc con control de
  espacio» **0x683D4C** (`0x683D56 bl 0x684A7A; cbnz → -1; si no 0x683D60 bl 0x684ACC`).
- **Libres (0x684AAC)**: `(A-B-1) mod 0x400` (`0x684AB8 cmp r2,r3` + `0x684AC2–0x684ACA`).
- **Sondeo (0x683D20)**: `0x683D28 bl 0x683C54` (un flag global); si 0 → `0x683D2E adds r0,#0x64;
  0x683D30 bl 0x5FD6E0` (espera de 100) y luego `0x683D3C b.w 0x684A64` ⇒ **cadencia ~100 ms**.

### 1.5 Terminador, longitud y «línea lista»

- **Terminador**: no hay campo; la línea se cierra con **CR (0x0D)**, que es lo que añade el propio
  monitor al emitir (`0x684AEA` y siguientes escriben 0x0D/0x0A/0x23 para el formateo de salida).
  Verificado en el arnés: depositando 24 B `46 42 4d 20 … 31 30 0d` la orden se ejecuta (§2).
- **Longitud máxima**: **NO_VERIFICADO** para la línea completa. El único tope que aparece en el monitor
  es **0x1FE (510)** en el constructor de la cadena de argumentos (`0x682BE6 cmp.w r8,#0x1FE`, mensaje
  **"TOO LONG STR" 0x90EC7C** emitido en `0x682C06`), con el búfer en `0xA5189E`. Se documenta como tope
  práctico, no como límite demostrado del anillo.
- **Flag de «línea lista»**: **no existe**; el único indicador es `A != B`. Publicar `B` es lo que
  «despierta» al monitor, y por eso **conviene escribir primero los bytes y después `B` de una vez**
  (así el monitor nunca ve media línea). El firmware escribe byte a byte con `B` por carácter; el
  resultado es equivalente porque sólo interpreta hasta el CR.
- **Quién consume y a qué ritmo**: el consumidor son los envoltorios del objeto stream
  (**0x683D04/0x683D20/0x683D4C**), que **no tienen ningún `bl` que los llame** (`calls` sobre
  0x683D04 y 0x683D4C = 0 resultados y `xref` de sus direcciones |1 = 0): se alcanzan por puntero. Aun
  así **el consumo es real y rápido** (medido ≤1 s, §2).

## 2. Verificación en el arnés: escribir el anillo a mano ejecuta el comando

Perfil `analysis/gui/g22/harness/live/fbm/`, shim propio con el ensayo del anillo (`sonyshim-fbm.c`,
hilo `PBINJECT`). **No se llamó a 0x2B50D8 en esta parte**: sólo se depositaron bytes con la semántica de
0x684ACC y se movió `B`. Rastro (`run6/consola.log`):

```
[FBMR] *(u32*)(libmpr+0xA4FD88)=0x8f884000  [+4]=0x82df9000  [+8]=0x8000  [+C]=0
[FBMR] mincore(0x8f884000,0x2000) -> 0 vec=0001
[FBMR] X=0x8f884000  [X]=A=0 [X+4]=B=0   buf=0x8f884010
[FBMR] objeto: +0=0x8f884000 +4=0x8f884004 +8=0x8f884010 +C=0x400
[FBMR] escribo en el anillo: "FBM SetSMI 20 90 7 1 10"   (A=0 B=0 antes)
[FBMR] tras escribir: A=0 B=24
[FBMR] SetSMI: A=24 B=24 a los 1 s          <- el monitor lo consumió en <1 s
[FBMC] tras-anillo-SetSMI  entradas con handle!=0 = 1/30
[FBMC] tras-anillo-SetSMI [15..29] … 20:090=h7/s1 …      <- ¡la orden se ejecutó!
[FBMR] escribo en el anillo: "FBM InitB 6 3"  (A=24 B=24)
[FBMR] tras escribir: A=24 B=38 ;  InitB: A=38 B=38 a los 1 s
[FBMR] escribo en el anillo: "FBM LTC 1"   (A=38 B=38) ; LTC: A=48 B=48 a los 1 s
```

- **`FBM SetSMI 20 90 7 1 10`** deja **idx 20 (sector 0x90) con handle=7 y status=1** en `0xA3699C`: es la
  prueba de que la línea depositada llega al handler y ejecuta el comando (SetSMI → 0x2B208C, escritura
  en RAM). **No demuestra creación real** (SetSMI no toca el flash, §4 del informe anterior).
- **`FBM InitB 6 3`** se consume igual (A 24→38) y la tabla no cambia: `CreateSector32` sigue devolviendo
  **0x07 = FBS_INVALID_PROCESS** en el arnés (medido por símbolo: `run3/consola.log`).
- **`FBM LTC 1`** se consume (A 38→48); su efecto no es observable sin el log de FBM.
- La escritura se hizo **desde dentro del proceso** (el shim comparte el espacio de direcciones). Desde
  fuera hace falta escribir en esa VA: **ptrace `POKEDATA`** (root) o `/dev/mem` con la dirección
  **física**, que no está en el descriptor (habría que sacarla de `/proc/PID/pagemap`, que en este kernel
  exige `CAP_SYS_ADMIN`; no verificado).

## 3. Alternativa (y complemento): llamar por ptrace dentro de im.elf

Herramienta nueva `tools/camera-ptrace/ptcall.c` (ARM EABI estático, sin libc, ~6,5 KiB; `build.sh` la
deja junto a `sctrace`). Modos: `peek`, `poke`, `call`; `--dry` imprime lo que haría sin engancharse.

Mecanismo de `call`: `PTRACE_ATTACH` al TID → `GETREGS` → se fijan `r0..r3`, `LR=0xDEAD0000`
(centinela no mapeado) y `PC=VA` → `SETREGS` → `PTRACE_CONT` → se espera el **SIGSEGV con
`si_addr==0xDEAD0000`** (`GETSIGINFO`) → se lee `r0` → se restauran los 18 registros → `DETACH`.
No parchea código (no hace falta BKPT ni memoria ejecutable).

**Lista ordenada de llamadas** (VA del ELF de `libmpr.so` 3.21; **en cámara: base + offset**, con la base
del primer mapeo `r-xp` de `/proc/PID/maps`):

| # | llamada | VA (Thumb) | args (r0..r3) | para qué |
|---:|---|---|---|---|
| 1 | `FlashLib::GetErrorString` | `base+0x2B6115` | `r0=código` | traducir el código de 4/5 (devuelve `char*`) |
| 2 | `FlashLib::CreateSector32` | `base+0x2B7081` | `r0=nombre(0x90)`, `r1=0` (`FBS_MOVEFLAG`), `r2=&handle`, `r3=&id` | **medir** el código sin tocar la tabla (es la llamada de 0x2B40C8) |
| 3 | `BackupMgr::InitBackupData` | `base+0x2B43F1` | `r0=OM(4 para 0x90)`, `r1=mediaID(7)` | **crear de verdad**: userID (0x2B385C) + índice (0x2B2E54) + CreateSector32 + alta en `0xA3699C` (0x2B40DA) |
| 4 | (opcional) handler de consola | `base+0x2B50D9` | `r0=argc`, `r1=argv` (hay que escribir antes la cadena y el vector de punteros en el tracee) | sólo si se quiere el parser completo |
| 5 | verificación | — | `peek base+0xA3699C+0x14*20`, 0x14 | `+4`=handle, `+8`=status, `+0xC`=OM |

Riesgos (todos reales, no teóricos):
- **Mutex del FlashLib**: `FlashLib::MutexLock` (0x2B60A1) se toma en `CreateSector_Body`
  (`0x2B6F96 blx 0x11EEC0`) y en `CheckAndRepairFlashBackup` (0x2B89CA). Si el hilo elegido **ya** tiene
  el mutex (p. ej. está dentro de un comando FBM), la llamada se interbloquea y deja el MPR colgado.
- **Elección de hilo**: `PTRACE_ATTACH` para **un** hilo; los demás siguen corriendo. Elegir un hilo
  ocioso (el que duerme en el bucle de la UI) y no el que atiende al monitor. `PTRACE_ATTACH` al PID
  engancha sólo al hilo principal.
- **Pila**: se reutiliza la pila del hilo interrumpido; si estaba en un marco profundo, la llamada puede
  pasarse. Usar `--sp` con una zona libre del propio proceso.
- **Reentrada**: `InitBackupData` escribe las globales de OM/media (`0xA36970`, `0xA36974`, `0xA36C08`,
  `0xA36C0C`) y ordena `FlashLib::InvalidateSync` (0x2B441A): no llamarla mientras la UI está grabando
  o reproduciendo.
- **Señales**: si el proceso tuviera manejador de `SIGSEGV` que reanuda, el centinela no pararía la
  ejecución; `ptcall` exige `si_addr==0xDEAD0000` y lo informa (`centinela=1`).
- **Root/CAP_SYS_PTRACE** y `/proc` del mismo namespace; en la cámara el Tweak da root por telnet.

## 4. Verificación «en seco» de la herramienta (en el propio invitado)

`run9/consola.log` recoge la ejecución real de `/tmp/ptcall` dentro del arnés (hilo víctima propio del
shim, `tid=224`, `pid=206`):

```
[FBMP] hilo victima tid=224 (pid=206)
[FBMP] system: /tmp/ptcall --dry 206 224 call 1 0x2b50d9 1 >>/dev/console 2>&1
[FBMP] system: /tmp/ptcall --dry 206 224 peek 0xa3699c 0x20 >>/dev/console 2>&1
[FBMP] system: echo '[FBMP] peek real de la victima:' >>/dev/console; /tmp/ptcall 206 224 peek 0x<base+0xA3699C> 0x20 >>/dev/console 2>&1
[FBMP] fin de la prueba de ptrace
```

(la salida de las tres órdenes se copia a `/dev/console`; ver `run9/consola.log` para los valores).
En el host se comprueba además: `sh tools/camera-ptrace/build.sh` produce un **ELF 32-bit ARM EABI5
estático** y `sh -n tools/camera-ptrace/fbm_ring.sh` pasa en `dash`; las funciones puras del guion dan
`"FBM View\r" → 46 42 4d 20 56 69 65 77 0d` y `le32("46 42 4d 20") = 0x204d4246`.

## 5. Procedimiento reproducible desde el PC (telnet del Tweak, sin flashear)

```sh
# --- en el PC ------------------------------------------------------------------------------------
sh tools/camera-ptrace/build.sh                                  # -> tools/camera-ptrace/ptcall
base64 -w0 tools/camera-ptrace/ptcall > /tmp/ptcall.b64          # para pasarlo por el telnet
# --- en la cámara (root; el Tweak lanza «busybox telnetd -l sh») ---------------------------------
telnet <IP_CAMARA>
paste_b64=/tmp/ptcall.b64 ; cat > $paste_b64 <<'EOF'
<pegar aquí el contenido de /tmp/ptcall.b64 en una sola línea>
EOF
base64 -d $paste_b64 > /tmp/ptcall && chmod +x /tmp/ptcall
# (alternativa: dejar ptcall y fbm_ring.sh en la tarjeta SD y copiarlos con cp)
PID=$(pidof im.elf | cut -d' ' -f1)
B=$(awk '/libmpr\.so/ && /r-xp/ {print "0x" substr($1,1,8); exit}' /proc/$PID/maps)
/tmp/ptcall $PID 0 peek $((B + 0xA4FD88)) 4        # -> X (0x........)
/tmp/ptcall $PID 0 peek 0x........ 0x10            # -> A y B del anillo
sh /tmp/fbm_ring.sh                               # estado y comprobación de libres
sh /tmp/fbm_ring.sh "FBM LTC 1"                   # 1.ª línea: registra fn para (4,3)/(0x21,3)
sleep 2
sh /tmp/fbm_ring.sh "FBM InitB 6 3"               # 2.ª línea: crea el sector 0x31 (OM 6, media 3=MS1)
sleep 2
/tmp/ptcall $PID 0 peek $((B + 0xA3699C + 0x14*10)) 0x14   # idx 10 (0x31): +4 = handle, +8 = status
sh /tmp/fbm_ring.sh "FBM View"                    # vuelca la tabla al log de FBM (no a la consola serie)
```

Notas para la cámara: (a) `B` puede cambiar entre arranques ⇒ leerlo cada vez; (b) `fbm_ring.sh` publica
`B` en un solo store tras escribir los bytes (más seguro que el orden por carácter del firmware);
(c) el sector que crea `InitB 6 3` es el **`0x31`** (idx **10**): la tabla estática `0x9D23FC` tiene
`(OM 6, media 3)` → userID `0x04`/`0x21` → `sector 0x31`; los `0x90`/`0x91`/`0x92` son de **media 7
(USB)**, no de la tarjeta (comprobado en `reports/evidence/film-pb-1-causa-fbm-20261126/tabla_pares_om.txt`);
(d) si el MPR no tiene el flash escribible, `InitB` no creará nada y la consola **no** avisará
(devuelve 1 siempre, 0x2B5B5E): la única señal es el log de FBM (`[FBM] BackupMgr::InitBackupData…`,
`0x2B440E`) y el handle de `0xA3699C`, que se lee con `peek`.

## 6. Límites de lo medido

1. **NO_VERIFICADO**: escribir el anillo desde *fuera* del proceso en la cámara (aquí se escribió desde
   dentro, misma VA); `ptrace POKEDATA` es el camino natural y `ptcall poke` está compilado y con la misma
   mecánica que `peek`, pero **no se ha ejecutado en el invitado**.
2. **NO_VERIFICADO**: que la línea funcione sin CR (todas las pruebas llevaban `0x0D`).
3. **NO_VERIFICADO**: el tope de longitud de línea; sólo consta el 0x1FE del constructor de argumentos.
4. La dirección física de X no está en el descriptor (los dos valores son VAs); para `/dev/mem` haría
   falta `pagemap`, no probado.

Evidencia: `reports/evidence/film-pb-1-sub-consola-fbm-20261127/` — `run4/`, `run5/` (X y `mincore`),
**`run6/` (anillo a mano: `SetSMI` aplicado)**, `run7/run8/run9/` (ptcall en el invitado),
`evidencia/tabla-comandos-fbm.txt`, `evidencia/initb-cadena-y-tablas.txt`;
herramientas en `tools/camera-ptrace/ptcall.c`, `build.sh`, `fbm_ring.sh`.
