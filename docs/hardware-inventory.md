# Inventario físico inicial

Es un inventario funcional documental, no una lista de materiales de una placa
inspeccionada. No se abrió ni conectó una cámara. Las referencias exactas de
chips de la unidad del usuario, revisiones y conexiones eléctricas permanecen
sin inspección propia; se distinguen abajo las corroboraciones externas.

Fuente S-HW-01: [especificaciones Sony α6000, 12-02-2014](https://www.sony.com.hk/press/pdf/2014021201_e.pdf), páginas 1 y 5–9 del PDF.

Fuente S-HW-02: [desmontaje de sensor a6000, TechInsights DEF-1412-801](https://www.techinsights.com/products/def-1412-801).
La ficha identifica IMX210 y código SON-IMX210AQL; consulta15-10-2026.
No suministra en su contenido público un mapa de registros ni caracteriza la
unidad del usuario. Véase [estado del sensor](sensor-investigation.md).

| ID | Componente funcional | Evidencia | Identificación física pendiente |
|---|---|---|---|
| HW01 | Sensor APS-C CMOS, 24,3 MP efectivos; IMX210 corroborado externamente | [VERIFICADO documental] S-HW-01 y S-HW-02 | Revisión de la unidad del usuario |
| HW02 | Procesamiento BIONZ X | [VERIFICADO documental] S-HW-01 | Encapsulados y bloques internos |
| HW03 | Obturador de plano focal y EFCS | [VERIFICADO documental] S-HW-01 | Actuador, realimentación y señales |
| HW04 | Montura E | [VERIFICADO documental] S-HW-01 | Protocolo eléctrico |
| HW05 | Visor OLED | [VERIFICADO documental] S-HW-01 | Controlador y bus |
| HW06 | Pantalla TFT abatible | [VERIFICADO documental] S-HW-01 | Controlador y bus |
| HW07 | Flash integrado | [VERIFICADO documental] S-HW-01 | Circuito y temporización |
| HW08 | Wi-Fi y NFC | [VERIFICADO documental] S-HW-01 | Chips y antenas |
| HW09 | USB y HDMI micro | [VERIFICADO documental] S-HW-01 | Controladores |
| HW10 | Ranura SD/Memory Stick | [VERIFICADO documental] S-HW-01 | Controlador |
| HW11 | Micrófono estéreo y altavoz mono | [VERIFICADO documental] S-HW-01 | Codec |
| HW12 | Batería NP-FW50 | [VERIFICADO documental] S-HW-01 | PMIC |
| HW13 | CPU que ejecuta ELF ARM | [INFERENCIA] 679 cabeceras ARM | Modelo, núcleos y frecuencia |
| HW14 | Almacenamiento interno | [INFERENCIA] particiones y módulos extraídos | NAND/otra memoria, chip, capacidad y geometría |
| HW15 | RAM | [NO VERIFICADO] | Chip, capacidad y mapa |
| HW16 | Interfaz sensor–procesador | [NO VERIFICADO] | Bus de datos y control, pines, temporización |

`CXD90014` está verificado como descifrador del paquete; no identifica por sí
solo el fabricante del SoC ni un encapsulado de placa. Los 172998656 bytes de
secciones WBI no son una medición de RAM instalada. Los nombres de particiones
y módulos no demuestran la tecnología física del almacenamiento.

Próxima evidencia requerida: fotografía legible de placas con procedencia,
manual de servicio autorizado o identificación técnica del sensor. Se debe
registrar variante de cuerpo/placa para evitar mezclar revisiones.
