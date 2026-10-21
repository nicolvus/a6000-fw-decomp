# Regiones de periféricos leídas por service mode (2026-10-20)

Leídas con `scripts/senser_regions_dump.py` (RMEM por senser, solo lectura), cada región en una sesión distinta, solo las declaradas en `/proc/iomem` del sistema en marcha (más `0xf1000000+0x100`).

| Archivo | Bytes |
|---|---|
| `arm7io_0x11000_0x1000.bin` | 4096 |
| `arm7sram_0x0_0x4000.bin` | 16384 |
| `nandreg_0x20000_0x10000.bin` | 65536 |
| `sfr_f1000000_0xf1000000_0x100.bin` | 256 |
| `uart0_0xf2000000_0x1000.bin` | 4096 |
| `uart2_0xf2002000_0x1000.bin` | 4096 |
| `usb_ehci_0xf0200000_0x1000.bin` | 4096 |
| `usb_ohci_0xf0201000_0x1000.bin` | 4096 |
| `usb_udc_0xf0210000_0x20000.bin` | 131072 |

- **No leída:** `nandc` (`0x10000000`, 64 KiB): falla en cada intento. Una primera tanda que la incluía dejó la sesión sin respuesta y la cámara se reinició; las demás regiones se leyeron una a una después.
- Valores de registros sin interpretar; leer periféricos puede tener efectos de lectura (no se observó ninguno).
- Hashes en `SHA256SUMS`.
