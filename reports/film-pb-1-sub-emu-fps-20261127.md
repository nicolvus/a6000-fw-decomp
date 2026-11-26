# FILM-PB-1 — Emulación con E/S real de la ruta de cadencia: **no concluyente**, con el punto exacto de parada

27-11-2026 · cámara **no accesible**, sin red · **emulación Unicorn sobre `libmpr.so` real** (fw 3.21,
`…/nflasha15_unpacked_unpacked/lib/libmpr.so`, SHA-256 `9a74a3bb…4c30`) con E/S real sobre
`/tmp/orig198.mp4` (SHA-256 `148c204c…dba6`) y `/tmp/conv198-25p.mp4` (`475f75f0…34a3`), 14 545 696 B cada
uno. **V** verificado en esta sesión · **D** deducido · **NV** no verificado. VA = VA del ELF.
Evidencia y script reproducible: [`evidence/film-pb-1-sub-emu-fps-20261127/`](evidence/film-pb-1-sub-emu-fps-20261127/).

## 1. Método (V)

`emu_fps.py` carga la librería **tal cual** en su VA de ELF (`LOAD 0x0 R E` de 0x9BB1C8 B y `LOAD 0x9C31C8 RW`
de 0x1C640 B + `.bss` hasta 0xADB704), sin parchear ni una instrucción. Base 0 ⇒ las 128 507 `R_ARM_RELATIVE`
de `.rel.dyn` quedan aplicadas por construcción (el *addend* está en el sitio); las 2 580 `R_ARM_ABS32` y 4
`R_ARM_GLOB_DAT` (datos de otros módulos) no se resuelven y **no** se modelan (§5). Los 930 `JUMP_SLOT` de
`.rel.plt` se rellenan: símbolos **definidos** en la librería → su VA interno
(`MprFileIf::*`, `MprIf::*`…); **importados** → un trampolín propio en `0x5F000000+4i` (242 símbolos,
`simbolos-importados.txt`) atendido por Python, con retorno por `LR` y sin ejecutar bytes falsos.

Entrada: **`0x6E0AB8` (`mp4Ifo_AVISequence::GetPlayThumbnailInfo`)**, con el grafo mínimo que el código
exige —`this` → `[this+0x208]` (`AviIf*`) → `[+0xC]` (acsr)—, descriptor de secuencia en `r1` y 12
argumentos de pila para sus punteros de salida. Se entra en el **destino** del despacho virtual de
`0x6E8430`: `0x6E849C ldr r5,[r2,#0x18]` / `0x6E84A0 blx r5` (V, estático); entrando por el wrapper
`0x6E8430` con vtable sintética, éste se queda antes en `ER_FAILED_ACQUIRE_SEMAPHORE`
(`transcripcion-orig198-wrapper6E8430.txt`, R0 `0xB0100002`): exigiría el semáforo real de `[this+4]`
(`0x5BAD00`/`0x5BACB0`, con `gettimeofday`/`getpid`/`pthread_self`). Se declara y se mide desde `0x6E0AB8`.

## 2. Hooks (V)

| grupo | símbolos | comportamiento |
|---|---|---|
| fichero | `open/read/lseek/close/fopen/fread/fseek/ftell/fclose/feof` | E/S **real** sobre el fichero del ensayo (tabla de descriptores propia) |
| memoria | `malloc/_Znwj/_Znaj/_ZdlPv/_ZdaPv/memcpy(_memmove)/memset/strlen/strcmp/strncmp` | modelo fiel |
| log | stub `0x65062C` + `0x6F0A54/0x1DC9E0/0x1DC98C/0x68323C/0x6831F8` | se emite la cadena y los argumentos |
| formato | `vsnprintf/snprintf/sprintf/printf` | formatea de verdad (`%s` resuelto en el guest) |
| IPC | `osal_valloc_msg_wait/osal_snd_sync_direct/osal_snd_sync_msg` | bloque de mensaje real + registro del envío |
| resto | `pthread_*`, `Fsys_*`, `Backup_*` | valor neutro + registro |

**Control positivo** (`control-es.txt`): los **stubs reales** de `.plt` `open@0x11E834` y `read@0x11FEE0`
sobre `/tmp/orig198.mp4` devuelven `fd=3`, 8 B = `0000001c66747970` = `….ftyp`, idénticos al fichero. Los
hooks de E/S están vivos y devuelven bytes reales.

## 3. Resultado (V) — **la cadencia no se puede medir: el camino no llega a abrir el fichero**

`transcripcion-orig198-r1.txt` y `transcripcion-conv198-25p-r1.txt` son **idénticas** salvo la línea del
hash del fichero (los 2 bytes `0xDDE20C/0xDDE20D`):

```
hitos        ['mp4Ifo_AVISequence::GetPlayThumbnailInfo',
              'AviIf::GetPlayThumbnailInfo (thunk)', 'CS_FlashAcsr::(metodo)']
log libreria [' *** mp4Ifo_AVISequence::GetPlayThumbnailInfo ***']
             [' [SEQ]AviIf::GetPlayThumbnailInfo Call !']
formateos    ['[CS_AviMainState][CheckState]:Error:%s.']  ← 'Invalid State' (sources/avi_if/AviSeqPlay.cpp)
R0           0xb0800001     E/S fichero 0     mensajes IPC 0
buffer out   +0x100=0   +0x124=0
```

- Se ejecuta código real de la cadena: `0x6E0AB8` (con `memset(r7+8,0,0x110)` en `0x6E0B02` y ese buffer
  pasado como argumento de pila en `0x6E0B72`–`0x6E0B76`) → `0x1D7022` (`0x1D7050 ldr r0,[r0,#0xC]`,
  `r3=4`) → **`0x21F1F4`**, que entra, comprueba sus punteros de salida y registra «GetPlayThumbnailInfo»
  (`0x21F21A`). Los hitos son los VA reales ejecutados, no réplicas.
- **Cero E/S**: `open/read/lseek/close/fopen/fread` instalados y **nunca invocados**; tampoco `MprFileIf::*`
  (van a su VA interno y habrían fallado por falta de `MMgrIf`). Sólo `pthread_mutex_lock/unlock` y
  `vsnprintf`.
- `0x21F1F4` aborta en su comprobación de estado: `CS_AviMainState::CheckState` → **`Invalid State`**, código
  `0xB0800001`. Como el buffer sigue a cero, `+0x100` no se escribe nunca y `0x6E0CD6` (`1..10 → 0..9`) no
  llega a ejecutarse.
- **Mismo valor para los dos ficheros: `+0x100 = 0`, `+0x124 = 0`.** Es decir, en el tramo instanciable no
  hay **ninguna** dependencia del contenido del MP4: ni 25 ni 29,97.

## 4. Reproducibilidad (V)

`sh reports/evidence/film-pb-1-sub-emu-fps-20261127/ejecutar.sh` (dos corridas por fichero):

| transcripción | MD5 r1 | MD5 r2 |
|---|---|---|
| `transcripcion-orig198-r1/r2.txt` | `6ed12997b91cb26a0420ee38545a7eb9` | **idéntico** |
| `transcripcion-conv198-25p-r1/r2.txt` | `d84fdecbf37c4e43ab33eb258d8cbe71` | **idéntico** |
| `transcripcion-orig198-wrapper6E8430.txt` | `cafc1ce50a3a650f5185b348fd7cb459` | — |

Deterministas (sin fecha ni direcciones de heap); `diff` entre los dos ficheros: **sólo** la línea 2.

## 5. Límites — dónde se para exactamente y qué haría falta (V/D)

1. **Parada exacta (V):** `0x21F1F4` → `CS_AviMainState::CheckState` = `Invalid State`, con `this+0x208`
   fabricado. No es un artefacto del arnés: es la respuesta de la librería ante un objeto sin estado; ese
   objeto lo crea la máquina de estados de reproducción (motor de play + gestor de medios), **fuera de
   `libmpr`**.
2. **No modelado (V):** la implementación registrada de `MMgrIf` (= `dfs_If`, otro `.so`) y el `AviIf` de un
   clip de tarjeta (`MMgrMp4IfoAcsr`: ctor `0x67B0CC`, consulta `0x67B598` → `0x6E8430`). Sin ellos no hay
   `handle` de fichero ni `moov` que interpretar.
3. **Para cerrarlo** haría falta: (a) `libInfraFsys`/`dfs_If` (o su vtable) sirviendo
   `open/read/lseek/close` del `MMgrIf`; (b) el estado `CS_AviMainState` como en play, o el objeto de la
   cámara en ese momento; (c) el `AviIf` real de un clip de tarjeta. Con (a)+(c) los hooks de §2 ya
   servirían los bytes reales del `moov` sin tocar el arnés.
4. **No se firma ni se refuta** que la cadencia salga de `mdhd.timescale/stts.delta` (sigue en **D**,
   [informe previo](film-pb-1-sub-framerate-20261127.md) §4): lo medido es que el tramo alcanzable **no toca
   el fichero**. El `NV` de §8 de aquel informe queda así: *ejecutado; se para en el gestor de medios, no en
   un parser*.
5. Sin cámara no se contrasta con el menú. Sólo se crean este informe y `reports/evidence/film-pb-1-sub-emu-fps-20261127/`
   (nada de `docs/`, `knowledge/`, `build/`, `tests`, código, scripts, red ni git).
