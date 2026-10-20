# A7S frente a A6000 — manuales de servicio Level 3 (19-10-2026)

Fuentes: `sony_ilce_7s_level3_sm.pdf` (62 págs., 2014) y
`sony_ilce-6000_..._ver.1.1_rev-1_level3.pdf` (54 págs.), convertidos con `pdftotext -layout`
(`sony-ilce-7s-level3-sm.txt`, `sony-ilce-6000-level3-sm.txt`). Solo búsquedas de texto;
no se leyeron los diagramas de bloques. Origen web de terceros, revisión oficial no verificada.

| Dato | A7S | A6000 |
|---|---|---|
| CXD90027GF | IC2001 | IC6200 |
| Rol en el manual | hoja "CAMERA SIGNAL PROCESS" | igual |
| Pares sub-LVDS SLRX / SLTX | 12 / 12 | 12 / 12 |
| Reloj 54 MHz | sí | sí (bloque imager) |
| Sensor | IMX235AQR-13 | IMX210AQL-13 |
| "DFE", "Silent", EFCS | no aparecen | no aparecen |

Límites: "DFE" es etiqueta del firmware, no del manual. Los 432 Mb/s por canal no aparecen.
El manual no documenta el modo silencioso; el mecanismo queda en el firmware (`dfe.bin`).
Web: Sony anunció Silent Shooting de la A7S por firmware en mayo de 2014 (prensa, no oficial verificado).
