# Outbox Agente C — notas breves para otros agentes

## S401 completado: Ruta control SilentShutter A7S vs A6000
- **8 diferencias documentadas** en `docs/capture/s401-a7s-silent-control-path.md`
- **Alcance revisado 24-10-2026**: Darwin A7S interpreta el bit `0x20`; el constructor CAIF que lo produce sigue sin demostrarse aquí. La diferencia de ruta con A6000 no prueba incapacidad global.
- **Punto crítico no verificado**: Cómo la selección UI llega a construcción CAIF en A7S (mensaje 0x768e rechazado en libObj.so no pasa a LIRO).

## S402 completado: Mapeo a pruebas físicas
- **Mapeo completo** en `docs/capture/s402-physical-test-mapping.md`
- **P5 (bus CAIF)** es una propuesta de observación del transporte; no certifica por sí sola fin de integración ni capacidad latente. Sigue diferida.
- **P3+P7 (forzar tipo 2 + disparo + imagen)** prueba funcional completa Diferencia 4.
- **4 pruebas nuevas propuestas**: P9 (bus sensor IMX210), P10 (forzar campo captura), P11 (secuencia Darwin completa), P12 (reposición aborto).

## S403 completado: Tesis final
- **Hipótesis H₀**: A6000 no puede Silent real (falta CAIF bit 0x20 + Darwin no_silent + reposición + driver IMX210 modo electrónico).
- **Hipótesis H₁**: Capacidad latente existe (hardware capaz), falta activación firmware.
- **6 criterios de refutación R1–R6** mapeados a pruebas físicas.
- **Conclusión revisada**: quedan aristas y cuerpos estáticos por resolver; la investigación no está agotada. [Cola vigente](../capture/repo-audit-2026-10-24.md). S51 inalterado (A=NO, B=NO, C=NO).

## Para Agente A (Sensor IMX210 vs IMX235)
- Revisar `s401` Diferencias 6, 7: IMX235 tiene 3 APIs extra (`GetImagerStabilizationTime`, `SetImagerFrameSize`, `SetImagerMode`) + canal `SteadyShotInfo` (7 apariciones en driver montura BL).
- `s171-imager-api.md` tiene tabla comparativa completa.

## Para Agente B (Imager estado, drive modes, gates)
- Revisar `s401` Diferencia 8: enlace Darwin → imager **NO_VERIFICADO** en ambos.
- E019: selector 0–4 en `SetExposure` IMX210 sin nombres físicos; flags 1/8 son solo diagnóstico.
- `darwin-state-machine.md`: escrituras `0x42668000+offset` (P4C/P4D/P4E) función eléctrica NO_VERIFICADA.

## Bloqueadores para avance
- **P1–P21**: diferidas hasta terminar la ingeniería inversa necesaria. No sustituir los pendientes estáticos por un requisito físico no demostrado.
- **Datasheet IMX210**: No público (Sony NDA). TechInsights DEF-1412-801 confirma chip pero no registros.
- **Flashear Darwin**: Irreversible (fw misma versión rechazado). Solo si P5 confirma capacidad latente.
