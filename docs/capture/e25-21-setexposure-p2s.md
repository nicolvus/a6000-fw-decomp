# E25-21 — SetExposure hasta P2S (28-10-2026)

Firmware A6000 3.21, `av-cam.bin` SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`, base `0x43541000`. Análisis offline, sin cámara. REA MCP no tenía documento abierto; se usaron bytes Capstone y Unicorn. S56 ya identificó el transporte; esta sesión aporta una **prueba integrada reproducible de datos** que encadena SetExposure, preparación SSB y formateadores P2S con una misma instancia emulada, y decodifica la lista completa de vuelta. No se emula `StartExposure`, `SetRead`, `Execute` ni el sensor de extremo a extremo; se reproducen por separado sus componentes. Las esperas y varias funciones auxiliares son stubs del arnés S56.

## A. Productor y formato

`0x4383fa40` calcula el plan en `record`; en `0x4383fda6–0x4383fdb2`, `0x4383fd6c` copia cuatro palabras desde `record+0x64` al destino indicado por el primer puntero del argumento, entre ellos el bloque `cap+0x64c`. El formato **parcial** observado en la ruta es: `+0` shd u16, `+4` svd u16, `+6` spl u16, `+8` sint u8, `+9` ShutMode u8. Son offsets; no se presume semántica de todos los bytes restantes. Las cargas `ldrh` de `0x436d6faa/6fae/6fb0` y `ldrb` de `0x436d6fb6` lo verifican.

`0x438c82fe` obtiene imager; `0x438c8302–830c` pasa `cap+0x64c` a `0x436d6320`, cuyo despacho `0x436d6344–634a` carga objeto y vtable+0x28. La tabla de esta implementación apunta a `0x436d6f6c` (test S56). Con `cap+0x504==1`, `0x438c82f0` pone svd a cero antes de la llamada y `0x438c8334` lo restaura: la copia restaurada **no demuestra que se haya transmitido el valor original**. La ruta solo ocurre en el paso cero, `cap+0x4b9c==0`.

| Campo | ID sombra/dirección de trama | Codificación demostrada |
|---|---|---|
| svd +4 | 3, 4 | bits 0–7; bits 8–11 en nibble bajo, preserva nibble alto |
| shd +0 | 5, 6 | bits 0–7; bits 8–13 en 6 bits bajos, preserva 2 altos |
| spl +6 | 7, 8 | bits 0–7; bits 8–11 en nibble bajo |
| ShutMode +9 | 1 | modifica bits según modo; la identidad física del registro no está demostrada |

Las instrucciones `0x436d6fe2–6ffc`, `0x436d7000–701e` y `0x436d7022–7034` son las escrituras y máscaras. Espejo condicional: IDs `0x144–0x149`. Los IDs son direcciones de la trama, no está demostrado que sean registros nativos del chip.

## B. Despacho y sumidero

```text
record+64 → cap+64c → StartExposure 438c828c
 → SetExposure 436d6320 → vtable+28 → 436d6f6c → sombras ID 1,3–8
 → SetRead 436d6398 → SSB 43ad9116 → Execute(1) 43ad911c
 → vtable+38 → 436d839c → 436d7c08 → 436d75f8
 → lista 43fe995c → formateador 43ad8fa2 → RAM P2S fc088340…
 → config fc088800=2, disparo fc088808: 1,0,1 → hardware P2S
```

`0x438c831e/8326/8330` son las llamadas SetRead, SSB y Execute(1); `0x43ad912a–912e` despacha por vtable+0x38. En pasos posteriores `0x438c8340` usa Execute(0), vtable+0x3c, que no transmite la lista. El destino de Execute(1) está identificado por tabla y bytes, no por referencias directas. Para la instancia 0, el canal 1 conduce a P2S DFE0; la conexión eléctrica al IMX210 es inferencia, no señal medida. El modo 2 y las banderas de espera no demuestran cuándo se aplica la trama ni que la espera cubra la transferencia eléctrica completa; ver [S57](s57-p2s-vd-synchronization.md).

Reproducción: `.venv/bin/python scripts/e25_21/traza.py`. Comprueba el hash, ejecuta SetExposure de bytes reales, fuerza en Unicorn el flag SSB que fija el llamador, ejecuta `0x436d7c08`, pasa sus 119 sombras al formateador real y verifica que la decodificación devuelve los 119 pares originales. Para `shd=0x1234, svd=0xabc, spl=0x567, ShutMode=3`, la trama contiene IDs 1=`dc`, 1=`d4`, 2=`20`, 3–8=`bc 0a 34 12 67 05`. En el plan de ejemplo de 30 s (`shd=1, svd=472, spl=0`, VTS 4219 y supuestos E25-17), IDs 3–8=`d8 01 01 00 00 00`; el lote emulado ocupa 127 y 87 bytes. El resultado no demuestra que la foto real use ese plan: la lectura física E25-19 observó `svd=0` en su registro. El script imprime tramas completas y escrituras MMIO simuladas; el sensor y SetRead no están emulados.

## C. Integración, lectura y frontera

La evidencia demuestra programación de parámetros y un pulso en ID1, no que ese pulso sea reset de filas, inicio o fin de integración. `0x438c814c` calcula `cap+0x724` y prepara una operación llamada ReadExecute; su nombre no demuestra la primera transferencia RAW ni el fin electrónico de integración. La ruta de VTS selecciona `record+0xd8/da/dc` en `0x437b21b8` y escribe período calculado en `0x436ef628`; el receptor físico sigue sin resolver ([E25-18](e25-18-integracion-silent-todas-velocidades.md)). Darwin `ExposureReady` acredita mensajería de finalización del host, no cierre electrónico de filas.

La **primera frontera hardware demostrable** de esta ruta es la activación del bloque P2S en `0xfc088808`, tras cargar RAM `0xfc088340…`. La operación física que falta para Silent 30 s **no se ha identificado**: aún deben discriminarse aplicación real del plan/VTS, mantenimiento de integración y evento de fin/lectura sin cortina. Ninguno se puede declarar como primer fallo causal sin medir o seguir el consumidor hardware. Datos locales disponibles de Darwin y estudios de IMX210 no atribuyen semántica concluyente a estos IDs. No se infiere imposibilidad física.

## Validación y límites

Tests S56, E25-17 y E25-19f: 53 aprobados. Script integrado: asserts de integridad, mapeo y decodificación completa. `ruff` del script limpio; `mypy` limpio con `MYPYPATH=analysis/s56`. La revisión del commit anterior `c450733f` detectó 15 avisos Ruff y 3 errores mypy en sus archivos; por ello no se considera validado para publicar. Sin ensayo físico ni ejecución de firmware real; no se demostró inicio/fin electrónico ni inicio RAW.
