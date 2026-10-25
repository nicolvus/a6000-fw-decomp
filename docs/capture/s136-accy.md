# S136 — `[ACCY]`: el subsistema de accesorios (A6000 fw3.21)

> Línea de ingeniería inversa **general**. Bytes de `analysis/rea-independent/input/av-cam.bin`;
> convención **vaddr = 0x43541000 + file_offset**. Regla de referencias: la **estricta**
> (canónica, `analysis/s106_imaging_cap/scan_pic_refs_strict.py`).
> Informe: [`analysis/s136_accy/accy.md`](../../analysis/s136_accy/accy.md) · Datos:
> [`accy.json`](../../analysis/s136_accy/accy.json) · Tests: [`tests/test_s136_accy.py`](../../tests/test_s136_accy.py) (16)

## Cifras (VERIFICADO)

- **106 cadenas** `[ACCY]` en el bloque contiguo `0x43c24cac`–`0x43c26319`; **111 sitios**
  PIC y **61 funciones** emisoras, todas en `0x43562a08`–`0x43566f20`. Las 106 están
  referenciadas (0 muertas).
- Formato de tres niveles `[ACCY][<nivel>][<sub-módulo>]`, **15 sub-módulos**:
  `HW`(1) `Main`(9) `MAIN`(4) `SENSER`(3) `UART`(13) `UTILITY`(2) `FACTORY`(7)
  `HOUSING`(5) `AVOUT`(2) `AVR`(2) `BASE`(7) `HELLO`(16) `JIRO`(2) `NULL`(1) `REMOTE`(32).
- **9 clases RTTI** `AccyUm*` intercaladas entre las trazas (`0x43c2536d`–`0x43c26340`):
  `AccyUmDeviceBase` + 7 derivadas (`WaterHousing`, `AvOut`, `Avr`, `Hello`, `Jiro`,
  `Null`, `Remote`); `AccyUmKeyStatusMgr` **sin** clase base. Tabla de `type_info` en
  `0x43fd7c8c`–`0x43fd7dc8`.
- **Taxonomía** (`FACTORY`, `0x435646a4` / `0x435647c0`): por ID `0`=AvOut, `1`=JIRO1.5,
  `4`=HELLO, `5`=LANC-AVR, resto `UNSUPPORTED`; por máscara `0x80`=Remote, `0x40`=WaterHousing.
- **Transporte**: UART propio (`AccyUartOpen/Close/Send`) + cola OSAL
  (`osal_try_valloc_msg 0x435612d0`, `osal_snd_msg 0x4356120c`); GID emisor `0x008F0139`.
  `NotifyInput` (`0x43565814`) entrega `{KeyCode, ID, State, INFO}`.
- **Ficheros fuente: NO identificables** (la única cadena no-`[ACCY]` referenciada por el
  código del módulo es `Valloc error!` `0x43c24c9e`). El primer `%d` de muchas trazas es
  el **nº de línea** de origen (secuencias monótonas en `FACTORY` 183→209, `UART` 54→241,
  `BASE` 45→104).

## Diferencial

- `[ACCY]` = **0** apariciones en la A7S fw3.20 y en la A6300 fw2.01; **0/106** textos
  (ni siquiera su núcleo) presentes allí.
- **Corrección**: el *módulo* **sí existe** en ambos (las mismas 9 clases `AccyUm*`, bloque
  RTTI `0x43c25a23`–`0x43c25afc` en la A7S y `0x43d0c9a2`–`0x43d0ca7d` en la A6300), pero
  **sin trazas**: allí hay una tabla de nombres de comando (`accy`, `edr`, `SendCommand`,
  `RxCommand`, `SetQue`…) y **dos clases `AccyMi*`** (`AccyMiDeviceBase`,
  `AccyMiDeviceLight`) que la A6000 no tiene. Lo propio de la fw3.21 de la A6000 es el
  *logging*, no el módulo. Salvedad versión/modelo (S130 §4).

## Línea del obturador

- **0/106** trazas mencionan obturador/flash/lente/montura/batería; el código del módulo
  no referencia ninguna cadena del subsistema de obturación.
- El **disparador remoto** aparece solo como tecla del mando:
  `START STOP OFF` `0x43c260b0` → `KEY:0x0A00000D` (pool `0x43566cfc`), entregada como
  **evento de tecla genérico** por `NotifyInput` (`0x43565814`). El módulo **no decide ni
  ejecuta el disparo**.
- Montura (S66) = subsistema **distinto** (código `0x436dfe6c`–`0x436e9ea4`, otro UART y otro
  protocolo). **S51 A/B/C = NO** se mantiene.

## NO VERIFICADO / abierto

Ficheros fuente; significado de `ACCY`/`UM`, `Spinal`, `GF`, `SS`, `Tally`, `JIRO`, `AVR`, `LANC`, `AISATSU`; tabla de teclas `0x0A0000xx`→acción; cola OSAL de destino (`0x007A0020`); papel de `AccyMi*`; contenido de los comandos de 5 bytes.
## Revisión del agente principal

(vacío)
