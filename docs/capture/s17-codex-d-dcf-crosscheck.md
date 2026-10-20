# S17 — Contraste DCF/Exif y límite de la evidencia MPR

## Resultado

**VEREDICTO: CAMBIOS.** No hay evidencia para afirmar que `EncodeStill`
completado cree una entrada reproducible. El JPEG y el catálogo son etapas
distintas en la evidencia disponible.

| Hallazgo | Estado | Evidencia |
|---|---|---|
| Existe API `MprIf::WriteStill` y `FeaIf::WriteStill`. | **VERIFICADO** | símbolos dinámicos y `libmpr.so:0x44f784`. |
| `FeaCore::WriteStill` prepara datos de escritura/MPR. | **VERIFICADO** | `libmpr.so:0x440794`; construye estructuras antes del envío. |
| `libObj.so` conoce `WriteStillCmp`, `MSGID_WRITE_STILL_EVT`, `entryId` y `pAccessPath`. | **VERIFICADO** | cadenas locales del componente de grabación/MprAcsr. |
| `CBID_ENCODE_STILL` llama a `WriteStill`. | **NO VERIFICADO** | no se recuperó xref ni llamada directa desde el receptor candidato. |
| Un JPEG creado por StillConverter queda indexado en reproducción. | **NO VERIFICADO** | no se recuperó la arista convertidor→recorder→MMgr. |

## Qué tendría que ocurrir

Para una fotografía visible en reproducción se requiere, como mínimo:

1. JPEG terminado y sus metadatos/Exif válidos.
2. Entrega a `WriteStill` con un `StillInfo` aceptado por MPR/MMgr.
3. Finalización de `WriteStillCmp` sin error, con `entryId` y ruta de acceso.
4. Actualización persistente del catálogo DCF y disponibilidad para el lector de reproducción.

Los pasos 1–4 describen una **INFERENCIA fuerte** basada en las interfaces y
mensajes recuperados; el binario no prueba que la ruta de EncodeStill analizada
los recorra. Por eso no se puede convertir el requisito de DCF en evidencia de
SilentShutter.

## Estándares externos, sólo contexto

La página oficial de CIPA lista **DC-009-2010, Design rule for Camera File
system: DCF Version 2.0**, con confirmación 2020. Esto respalda que DCF es el
marco de catálogo de cámara, no que esta implementación Sony haya emitido una
entrada concreta. La misma página lista Exif por separado (DC-008), por lo que
Exif correcto tampoco sustituye el alta DCF.

La página OSS oficial de Sony ILCE-6000 ofrece `linux-kernel.tar.gz`, entre
otros paquetes GPL. No se atribuye a ese árbol una implementación de FEA,
MPR, StillConverter o DMM propietario sin una coincidencia directa verificada.

Fuentes: [CIPA Standards](https://www.cipa.jp/e/std/std-sec.html),
[Sony ILCE-6000 OSS](https://oss.sony.net/Products/Linux/DI/ILCE-6000.html).

