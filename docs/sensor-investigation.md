# Sensor: estado de evidencia

Actualización E018/E019: wrappers y vtable IMX210 contrastados; se siguió
SetExposure hasta una lista de119 registros y el transporte P2S. El registro
modificado por el selector está en esa lista. Sigue pendiente asignar significado
físico a sus bits y demostrar fin electrónico en foto completa.
[Informe y límites](capture/imager-exposure-p2s.md).

**Corroboración física externa:** la ficha del análisis propio de TechInsights
DEF-1412-801 identifica un sensor IMX210 extraído de una Sony Alpha a6000 y
el código de dispositivo SON-IMX210AQL. Es una fuente primaria de desmontaje,
independiente de las cadenas del firmware. No es una inspección de la unidad
del usuario y no fija todas las revisiones de producción.
[Ficha del análisis](https://www.techinsights.com/products/def-1412-801),
consultada el15-10-2026. La página pública no aporta el mapa de registros.

Actualización E017: en av-cam.bin oficial se identificaron RTTI
`Camera::Imager::IMX210::C_ImagerCtrl_IMX210` e `ImagerDrvParam_IMX210`,
con diagnósticos de exposición y lectura. Es evidencia de un controlador IMX210
incorporado y un candidato relevante, no identificación física de chip/revisión.
Funciones y hashes: [SilentShutter E015–E017](capture/silent-shutter-status.md).

[VERIFICADO documental] Sony describe sensor APS-C Exmor APS HD CMOS y EFCS en ILCE-6000. Fuentes: https://www.sony.com.hk/press/pdf/2014021201_e.pdf y https://helpguide.sony.net/mig/Z001924611/EN/contents/TP0000226634.html .

[NO VERIFICADO] Revisión física de la unidad del usuario, datasheet, mapa de
registros, bus sensor/procesador, modos de lectura completa y finalización
electrónica. El controlador IMX210 identificado en E017 no es una coincidencia
aleatoria de WBI; la atribución al modelo tiene ahora la corroboración externa
descrita arriba. No se obtuvo una hoja de datos de registros en la búsqueda actual.

| Capacidad | Qué demostraría | Estado |
|---|---|---|
| Reset electrónico | Inicio/borrado de carga | No caracteriza finalización |
| EFCS | Inicio electrónico de exposición | Documentado como ajuste de usuario |
| Live View | Lectura de previsualización | No prueba fotografía completa |
| Vídeo | Lectura en un modo de vídeo | No prueba RAW completo |
| Electrónico completo fotográfico | Inicio y finalización con lectura válida sin cortina | Sin demostrar |
| Global shutter | Inicio/final simultáneos con almacenamiento adecuado | Sin evidencia |

Se identificó un registro de tabla con campo de dirección de16 bits y byte
de valor, y su inclusión en P2S; falta atribuir sus bits a operaciones físicas
del sensor. También faltan selección de modo completa, resolución, bits por
píxel y respuesta de exposición contrastados con documentación o medición.
