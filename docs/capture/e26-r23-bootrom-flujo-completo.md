# E26-R23 — Flujo completo de `main` y `serial_entry`, pasos de traza y códigos de error (30-10-2026)

Cierra el BootROM «de principio a fin»: completa [R22](e26-r22-bootrom-mapa-completo.md) con el cuerpo línea a línea de `main` (`0xffff1062`) y `serial_entry` (`0xffff0fa0`), y resuelve **todos** los pasos de traza `(etapa,paso)` y **todos** los códigos de error del ROM a su sitio emisor exacto. Datos: `analysis/e26-recovery/r22-trace-steps.json` (109 pares, 111 sitios), `analysis/e26-recovery/r22-error-codes.json` (25 códigos). Test: `tests/test_e26_r23_bootrom_flujo_completo.py`.

## 1. `main` (`0xffff1062`) — BINARIO, línea a línea

> **Corregido por [R33](e26-r33-veracidad-clave-nflasha0.md):** las condiciones de `storage_init` y `load_header` están invertidas (con 0 **continúan**; `cbz` en `0x110e`/`0x1120`). `find_key` (`0x39c`) va antes de la recepción (`0x1130`) y lo de `0x1226` es `load_payload`/`0x44e`/`0x486`. R12 §3 sigue vigente.

```
ctx_reset(); snprintf("Musashi Loader1 Ver.01.00 Dec  2 2011 10:45:17\n"); console_puts
trace(0,0)
timer_init(); led_gpio_init(); nand_ctrl_timing()
[0xc0005000+0x20] = 6                       ; motivo de reinicio por defecto
sel = MODEREG(0xf2915010).bit0; [0xc0010010] = sel

si sel == 0:                                 ; ---- ruta de almacenamiento ----
  trace(1,0); r = storage_init()
  si r != 0: trace(1,1); error_blink(r)
  trace(1,2); r = load_boot_main()           ; block_read(0,3,0xd,6) -> 0xc0030000
  si r == 0: trace(1,3); error_blink(r)
  trace(1,4); jump_main_image()              ; bx 0xc0030000 (Loader2)         ── FIN (no retorna)

; sel == 1 (o llega aquí tras `block_read` dañado, R12 §3): ---- ruta de servicio ----
trace(2,0)
serial_profile_select()                      ; perfil GPIO4.21 -> 0xc0010218 (R21)
svc = GPIO4(0xf2910410).bit22; [0xc0010010+4] = svc
si svc != 0: trace(2,1); serial_entry()       ; salto directo a servicio          ── (no retorna si acepta)
trace(2,2); r = storage_init()
si r == 0: trace(2,3); serial_entry()
r = load_header()                             ; block_read(0,0,3,6) -> 0xc0000600
si r == 0: trace(2,4); serial_entry()
trace(2,5)
clave = 0; byte_status = block_read_byte(&clave)   ; lee 1 byte a pila (0x876, uso #1)
si byte_status == 0x3001: trace(2,6); serial_entry()  ; error de sincronismo -> reintenta por serie
si byte_status != 0:
  si byte_status != 0: trace(2,8); r = byte_status; ir a REGISTRO_MOTIVO
  si no: trace(2,9); r = byte_status
trace(2,7)
si [0xc0010004] (get_flag0) == 0: trace(2,10); r = 0x2004; error_blink(r)
tabla_ok = crc32_check(&pila, 8) + 1          ; `0xc52` sobre los 8 B de cabecera en pila
si tabla_ok != 1:
  trace(2,14); registrar_cabecera(clave); error_blink(0x2003)
si no: trace(2,11)
si campo_lo == campo_hi (comparación de 32 b en pila): trace(2,12); serial_entry()
si no: trace(2,13); registrar_cabecera(clave); error_blink(0x2002)

REGISTRO_MOTIVO:
r = find_key_entry()                         ; primera entrada != 0xFFFFFFFF en 0xc0001200
si r != 0: trace(2,15); error_blink(r)
si check_loaded() == 1: trace(2,16); error_blink(0x2001)   ; 0xc0000000 vacío (sin clave)
r = load_payload()                            ; cabecera -> 0xc0005000, block_read
si r != 0: trace(2,18); error_blink(r)
trace(2,17); jump_serial_image()              ; bx [0xc000500c+0xc]              ── FIN si acepta
```

**Corrige R12 §3** («observación estática, no probada» de que un error de `load_header` distinto de `0x3005`/`0x3006` cae en «éxito aparente»): en `main` ese resultado (`r == 0`, es decir, cabecera dañada sin ser recuperable por ECC) desvía a `serial_entry`, no sigue la ruta normal. El flujo verificado es: **almacenamiento sano → Loader2; almacenamiento no apto o GPIO4.22=1 → `serial_entry`.** *Corregido por [R32](e26-r32-moderreg-valor-real.md): esta cámara arranca con `MODEREG` bit 0 = 1 (dato del backup), así que no pasa por la rama `sel == 0`. Su arranque normal es la rama de servicio con clave presente: ventana serie → `0x3001` → `load_payload` → salto.*

## 2. `serial_entry` (`0xffff0fa0`) — BINARIO, línea a línea

```
trace(2,1)
si [0xc0010010+4] (copia de GPIO4.22) != 0: trace(2,2); ir a RECEPCION
trace(2,3)
si get_flag1() == 1: trace(2,4); ir a RECEPCION
si no, si get_flag1() == 0:
  si get_flag0() != 0: trace(2,6); error_blink(0x1001)      ; ni clave en tabla ni bandera
  si no: ir a SIN_RECEPCION
si no (get_flag1() no es 0 ni 1): ir a SIN_RECEPCION

RECEPCION:
r = serial_receiver(&motivo)                  ; tren de 60 flancos + trama 8O1 (R21)
si r != 0:
  trace(2,7)
  si r == 0x3001 (fallo de sincronismo): trace(2,8); r = 0x1001
  r -> REGISTRO_MOTIVO (igual que en main)
si no: ir a SIN_RECEPCION

SIN_RECEPCION:
si get_flag1() != 0: ir a REGISTRO_MOTIVO
si no: trace(2,5); ir a RECEPCION             ; (bucle: get_flag1==0 reintenta sin reclasificar)

REGISTRO_MOTIVO:
trace(2,9/2,10); trace(2,11); jump_serial_image()  ; bx [0xc000500c+0xc]
```

**Hallazgo nuevo:** `serial_entry` no recibe directamente — delega en `serial_receiver` (`0x876`, R21) y en la bandera `get_flag1()` (`[0xc0010004+4]`), que decide si ya hay un motivo de arranque fijado (p. ej. por un intento anterior) antes de volver a esperar en el UART software. Si no hay clave ni bandera (`get_flag0()==0`), el código es `0x1001` y el LED parpadea sin reintentar.

## 3. Pasos de traza — BINARIO (109 pares, 111 sitios; 0 sin resolver)

Formato `(etapa,paso)`: etapa 0 no aparece (`main` usa 1–2), 1 = inicio/selector, 2 = ruta de servicio (`main`+`serial_entry`), 3 = receptor serie (`serial_receiver`/`serial_recv_bytes`/`sample_confirm`/`serial_profile_select`), 4 = almacenamiento/bloques (`storage_init`…`load_payload`, `block_read`, `nand_ctrl_timing`). Tabla completa (dirección, función) en `analysis/e26-recovery/r22-trace-steps.json`; ejemplo por etapa:

| Etapa | Pasos | Rutinas |
|---|---|---|
| 1 | 0–4 | `main` (selector/almacenamiento) |
| 2 | 0–18 | `main` (ruta de servicio) + `serial_entry` |
| 3 | 0–33 | `serial_profile_select`, `serial_receiver`, `serial_recv_bytes`, `sample_confirm` |
| 4 | -1–38 | `nand_ctrl_timing`, `storage_init`, `block_read`, `load_boot_main`, `load_header`, `find_key_entry`, `load_key_target`, `check_loaded`, `load_payload` |

## 4. Códigos de error — BINARIO (25/25 resueltos)

Añade a la tabla de R22: **`0x1002`** (manejador de excepción ARM, `0xffff004c`, modo ARM — fuera del escaneo Thumb de R22, localizado aparte). Todos los demás códigos de la tabla de R22 (`0x1001, 0x1003–0x100e, 0x2001–0x2005, 0x3001–0x3006`) tienen ahora su sitio emisor exacto en `analysis/e26-recovery/r22-error-codes.json`; ninguno queda sin emisor conocido.

## 5. Estado del BootROM

Con R20–R23, el BootROM (24 576 B, `0xffff0000`–`0xffff1a80`) queda **completo en estático**: 57 rutinas nombradas (R22), flujo completo de las dos rutinas de decisión (`main`, `serial_entry`, este informe), los 109 pasos de traza y los 25 códigos de error resueltos a su sitio exacto, el receptor serie con tren de sincronismo y reloj de 4 MHz verificado (R21/R22), el selector `MODEREG`/GPIO4 (R20), y el límite documentado del contenido de la tabla de claves (`E26-R20-KEYTABLE`, físico). No queda código del ROM sin identificar.

## 6. Límites

Nombres de rutinas y de pasos son propios (el ROM no tiene símbolos). El pseudocódigo de §1–2 es traducción directa del desensamblado, no hay emulación instrucción a instrucción de todo el flujo (sí la hay para el receptor serie, R21). El contenido real de la tabla de claves (`nflasha0`) y el pin físico de GPIO(4) bit 21/22 siguen sin poder determinarse sin hardware (`E26-FISICO-BOOT`).
