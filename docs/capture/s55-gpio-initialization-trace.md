# S55-B — Origen de los pares (canal, bit): base de backup BK4 (20-10-2026)

**Resultado principal:** la frontera de S54 («valores inyectados por el entorno, no recuperables») queda **resuelta**: los valores salen de la base de backup y el
escritor **sí** está en `av-cam.bin`.

## Cadena (VERIFICADO)
1. Tabla de servicios `0x435410b4` (rellenada por `liro.ko`, S49): slot `+0x2e0` (wrapper `0x43561508`; A7S `0x4355f7c8`) = `Backup_read_4Byte`
   (relocación de `liro.ko .init.data` offset `0x2bc` = `0x2e0-0x24`; ancla `+0x200 = osal_dynamic_id` coincide con S49).
2. `backup.ko`: `Backup_read_4Byte(id)` → subsistema = bits 16..23 (aquí `0xf9`), `Data_SearchId` → tabla SID (6 B/entrada `{u16 cuenta, u32 base}`) → tabla de entradas
   (6 B `{u16 tam, u32 off|flags}`, base `0x100+6·nsid`) → valor en `archivo + (off&0xffffff) + {0:4, 0xff:2, resto:0}`.
3. Datos: **`0110_backup/SYSMUSASHI-DSLR/DM_UUD3/CX77500_*.bin`** (A6000) y `…/ICV/CX78500_*.bin` (A7S), formato «BK4» (`analysis/s55/bk4.py`). Las 11 variantes regionales de A6000 coinciden
   en los pines comprobados. Son el *preset*; los valores por unidad viven en `/Backup.bak` (no disponible).
4. Inicializador: **`0x436bcef4`** (A6000) / **`0x436dc054`** (A7S) ejecuta 16×`id→Backup_read_4Byte→ *GOT[off]` y 6 stores de bytes. Las 16 celdas son exactamente
   `0x43e77298…0x43e772d4` (A6000) / `0x43e84f38…0x43e84f74` (A7S). S54 no lo vio porque el store es indirecto vía GOT. REA no reconoce la función (Thumb sin sembrar); verificado por capstone.

## Variables y valores (idénticos en ambos modelos)
| Variable A6000 | ID | valor | rol |
|---|---|---|---|
| `…77298` / `…772c8` | `0xf904cb` / `0xf904ca` | 17 / 3 | pin lector A = (3,17) |
| `…772a4` / `…772ac` | `0xf90455` / `0xf90456` | 10 / 3 | pin lector B = (10,3) |
| `…772b0` / `…772cc` | `0xf90465` / `0xf90466` | 0 / 12 | pin lector C = (0,12) |
| `…7729c` / `…772a0` | `0xf9045f` / `0xf90460` | 0 / 7 | pin lector D = (0,7) |
| `…772bc` / `…772d0` | `0xf900b1` / `0xf9006d` | 5 / 14 | pin lector E = (5,14) |
| `…772c0` / `…772c4` | `0xf9045d` / `0xf9045e` | 7 / 15 | salida (7,15) |
| `…772b4` / `…772a8` | `0xf90457` / `0xf90458` | 7 / 13 | salida (7,13) |
| `…772b8` / `…772d4` | `0xf90200` / `0xf90201` | 0 / 16 | sin lectores en el blob |
Orden: el primer ID del par es el canal, el segundo el bit.

## Identidad de las estructuras (B.2) y GPIO_9 (B.4)
Son **enteros de canal y de bit** (no punteros). Calibración del mapa pin↔esquema: `nfc.ko` lee `(0xf904da,db)=(0,4)` (IRQ) y `(0xf904dc,dd)=(0,8)` (RFDET); el esquema
da `NFC_IRQ=GPIO_S_4`, `XNFC_RFDET=GPIO_S_8` ⇒ **banco 0 = `GPIO_S_n`, bit = n** (PARCIAL: 2 anclas). Refuerzo: `(0,7)` ⇒ `CA_RELEASE_LOCK_MSS=GPIO_S_7` (la tarea CA lo comprueba al arrancar,
`0x436bc0a0`) y `(0,12)` ⇒ `DWN_CSREQ_MSS=GPIO_S_12`. Los lectores de la tarea CA son por tanto **líneas de handshake SIO** (REQ/RELEASE_LOCK…), no la cortina.
**`GPIO_9` (sin «S») no está calibrado:** el banco de los `GPIO_n` simples es desconocido. Hecho acotado: ningún par usado por el código tiene bit 9 salvo `(0,9)=GPIO_S_9=LENS_XDETECT`;
si bit==n también en ese banco, `GPIO_9` no es leído por `gpio_get` (INFERENCIA).

## Frontera restante
Valores por unidad (`Backup.bak`) frente al preset; IDs dinámicos (`0x43716dd0`); banco de `GPIO_n`. Todo ello se cierra con el SoC TRM o una traza pasiva.
