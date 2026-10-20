# S58 — Cálculo AE y configuración efectiva A7S Silent

20-10-2026. Continuación y auditoría del trabajo interrumpido de Claude. **Cierre documental y experimental offline; integración electrónica del IMX210 sigue NO VERIFICADA. S51: A=NO, B=NO, C=NO.**

## Resultado principal

Se recuperó el productor numérico: `0x4383d4d0` descompone T; `0x4383c9dc` construye filas shd/svd/spl; `0x4383b790` produce campos A/B todavía sin semántica. La cadena desde Tv hasta argumentos de SetExposure tiene evidencia estática y tramos ejecutados, pero no una ejecución integral con entradas reales de captura.

Se ejecutan los cuatro métodos A7S reales para los cinco modos obligatorios y 0x35. **El objeto y los servicios se inicializan de forma sintética**, por lo que la emulación integral de arranque, captura, sensor y fin queda delimitada explícitamente.

## Novedades y correcciones

- **ACEPTO** productor AE numérico: 600/600 descomposiciones y 300/300 filas coinciden con instrucciones originales en Unicorn. Tv y M siguen como entradas externas no recuperadas.
- **ACEPTO** SetExposure A7S=0x436f4168 y SetRead=0x436f4a94: vtable y ejecución independiente. **CORRECCIÓN VERIFICADA de [S57-B](s57-ssb-pulse-analysis.md)**: el umbral 0x1000 es de SetRead/AGC, no exposición.
- **ACEPTO** matriz IMX235 69 filas de 0x14 B, 15 columnas usadas, selección indirecta de 34 modos. **CORRECCIÓN VERIFICADA de [S57-D](s57-imx235-silent-register-diff.md)**: 0x4c→0x4e difiere en 14 registros, 0x4d→0x4f en 11; los cuatro registros entre Silent son 01/09/0a/0b.
- **RECHAZO** igualdad universal productor/validador host del borrador S58: VdNum>1 tiene expresiones distintas; contraejemplo sintético con productor real documentado en [unidades](s58-imx210-timing-units.md).
- **RECHAZO** contar solo 99 escrituras totales: el parser inicial ignoraba DEV=0x83. Son 100, conservando dispositivo y orden; nuevo test evita la pérdida silenciosa.
- **ACEPTO** petición de ganancia→bit4 de 0x81:0x5f en `0x436f459c`, probada aisladamente en foto y Silent; no demuestra finalización de integración.
- **RECHAZO** convertir ausencia de comando final en prueba de autonomía: S58 no emula un evento final posterior A7S.

La corrección de S57 afecta sus conclusiones A7S, no invalida el transporte IMX210 ni sus 60 regresiones. Los informes y tests históricos se conservan sin alterar; la auditoría de conocimiento enlaza las correcciones actuales.

## Hipótesis

| ID | Estado | Alcance |
|---|---|---|
| H58-1 | VERIFICADO | AE contiene cálculo, no solo tablas |
| H58-2 | PARCIAL | svd cuenta pasos aritméticos; VD físico sin medir |
| H58-3 | PARCIAL | shd compatible con líneas; spl es remanente de pasos, término fino separado |
| H58-4 | INFERENCIA | parámetro temporal no demuestra fin eléctrico |
| H58-5 | PARCIAL | programación previa A7S ejecutada, fin posterior fuera de cobertura |
| H58-6 | DESCARTADO en cobertura | no se añaden diferencias Silent en SetExposure/SetRead ensayados |
| H58-7 | PARCIAL | 0x0c participa en diferencias, comparte valor con foto; exclusividad descartada |
| H58-8 | PARCIAL | 0x0a pertenece a un grupo de submodo, función física desconocida |
| H58-9 | NO_VERIFICADO | analogías estructurales, sin equivalencia eléctrica entre sensores |
| H58-10 | NO_VERIFICADO | no se demuestra una función físicamente ausente en IMX210 |
| H58-11 | INFERENCIA | VD/P2S relacionado por arquitectura; instante de aplicación desconocido |
| H58-12 | INFERENCIA | autonomía compatible, no demostrada por ausencia |

La [matriz de 24 evidencias y 12 hipótesis](../../analysis/s58-evidence-matrix.json) conserva hashes, direcciones, funciones, datos/instrucciones, método, referencias, pruebas, dependencias, evidencia favorable/contraria, confianza, límites y próximo experimento.

## Qué se cerró y qué falta

S57 dejó sin productor los valores de tiempo y comparó una matriz A7S mal dimensionada: ambos puntos avanzaron con pruebas nuevas. Se conoce la configuración efectiva ensayada y sus tramas, incluida la diferencia 45 registros estáticos frente a **43 efectivos** entre foto 0x0b y Silent 0x4e.

Faltan: origen Tv, bloque M real por modo, significado de clk, restricciones que reconcilian productor/host; constructor y servicios A7S; semántica SIF/resolución de 0x0a/0x0c; llamadores efectivos del consumidor de ganancia y receptores de mensajes; relación eléctrica de tiempos, VD y XPI con integración.

Los números de pruebas describen software offline, no fidelidad eléctrica del sensor. Ni la mitigación ITSTATE, ni los stubs, ni los patrones de memoria cubren estados arbitrarios del firmware.

## Verificación reproducible

Con el Python del sistema que ya dispone de Capstone/Unicorn (sin instalaciones):

```sh
python3 -m unittest discover -s tests -p 'test_s58_timing_a7s.py' -q
python3 -m unittest discover -s tests -p 'test_s5[67]*.py' -q
python3 analysis/s58/a6_verify.py
python3 analysis/s58/a7_verify.py 150
python3 analysis/s58/build_matrix.py
python3 analysis/s58/reproduce.py
```

Resultado: **23 tests S58 y 60 regresiones S56/S57**; campañas numéricas 600/600 y 300/300. Ruff F/E9 y mypy (`--ignore-missing-imports --follow-imports=skip`) sobre 25 archivos S58 sin avisos; no se revisan estáticamente dependencias históricas. Manifiestos: firmware 5/5, silent-liro 9/9 y directorio Ghidra 1328/1328 coinciden. También se comprueban SHA completos de av-cam A6000/A7S en tests.

La `.venv` del proyecto no ve Capstone; su fallo de colección inicial queda explicado, sin instalar paquetes. El código original se lee, no se modifica; REA se reutilizó desde las exportaciones `analysis/s58/rea-out/` del trabajo heredado, sin repetir el análisis en frío. Los comandos heredados de GPREMIUM sobre `src/` no corresponden a este repositorio: se verificó el alcance real S58 descrito arriba.

## Viabilidad y S51

**A=NO:** no se demuestra exposición completamente electrónica a resolución completa. **B=NO:** no hay ruta suficientemente comprendida para un parche. **C=NO:** tampoco se demuestra imposibilidad física. S51 no cambia; no se parchea, flashea ni toca hardware.

La respuesta final es **parcial**: se reconstruyó el cálculo y la configuración A7S bajo condiciones precisas, pero no qué configuración física suficiente falta al IMX210. El experimento estático de mayor valor es recuperar el escritor del bloque que `0x437aa65c` toma de `0x437876dc()+0xdd0`, con M/Tv alcanzables; la frontera física requiere datasheet o traza pasiva autorizada. No se prolonga el análisis estático como sustituto de esa evidencia.

Informes: [A productores](s58-ae-timing-producers.md) · [B unidades](s58-imx210-timing-units.md) · [C emulación](s58-imx235-full-emulation.md) · [D diferencias](s58-a7s-silent-effective-diff.md) · [E ciclo](s58-exposure-cycle.md).

Validación adicional de conocimiento: 61 tests pasan excluyendo `test_mcp_server.py`. Ese archivo agota 15 s en su primera llamada asíncrona `get_current_state` (asyncio/AnyIO), por lo que la suite MCP completa queda sin validar. La reindexación y las auditorías CLI sí se ejecutaron; no se modificó la infraestructura para resolver este bloqueo ajeno al código S58.

VEREDICTO: APROBADO para el hito offline delimitado, con validación MCP pendiente; Silent IMX210 permanece NO VERIFICADO.
