# S51 — cobertura estática y límites de herramientas (24-10-2026)

Auditoría de las tareas 6 y 7. Es una matriz de **rutas relevantes**, no un
porcentaje de funciones descompiladas. `133/372` en S178 cuenta etiquetas
documentadas y `363/464` en el hito REA cuenta coincidencias de una muestra
histórica; ninguno mide cobertura integral del firmware. Se usaron informes
con instrucciones/bytes originales y el inventario REA existente. No se
ejecutó firmware ni se hicieron pruebas físicas.

| Tramo | Código recuperado y evidencia | Hueco que impide cerrar S51 |
|---|---|---|
| `CURTAINMODE` → registro de captura | `0x43842158`, `0x4384031c`, `0x43841070`, `0x437f7ff4` y `0x437f7ef6` reconstruidos en [S51](s51-decision.md). La ruta conocida no entrega el modo `0..7` a `SetMode/SetExposure/SetRead`. | Receptores del mensaje de `0x437b0390` y todas las entradas indirectas del control; el negativo está acotado al barrido documentado. |
| Configuración IMX210 A6000 | `SetMode=0x436d62e4`, `SetExposure=0x436d6320`, `SetRead=0x436d6398`, llamadas en `0x438c79bc/79fc/7a40` ([S51](s51-decision.md)); transporte P2S con bytes y [Unicorn](s56-imx210-register-transport.md). | Correspondencia eléctrica de ID1/100/101, significado de drive modes y fin de integración por filas. La emulación no aporta semántica del sensor. |
| Temporización/modelo A7S | [S58](s58-imx235-full-emulation.md) ejecutó cuatro métodos y el transporte, bajo objeto sintético y stubs declarados. | No equivale a inicialización/captura real, ni valida por sí misma la A6000. Constructor, callbacks y respuesta eléctrica quedan fuera. |
| 2ª cortina | S51/T3 sigue `0x43b5e2b0 → 0x4398f9a4`, con guardas `captura+0x74f` y `0x43ae7648`: ninguna guarda configurable demostrada para omitirla. | Traducción física banco/bit `0xf2910048`→P4E y rutas alternativas de fin de exposición; no inferir imposibilidad del hardware. |
| Mensaje `0x40193` | [Informe de cola](queue-40193-flow-2026-10-23.md): construcción, 16 B OSAL, receptor `0x4381d16c`, descriptor `0x43ea048c` e inicializador `0x4379e93c` verificados; fila 189 de 372 punteros Thumb. | Consumidor de arranque del descriptor, registro del callback concreto en Linux y enlace Linux↔LIRO siguen `NO_VERIFICADO`. |
| Foto fija Linux | [Auditoría de contrato](recordstill-contract-audit-2026-10-23.md): A6000 `0x90b248` es RecordImage; `0x908afc` corresponde a RecordStill; `StateMgr::CallFunc` consume `call_fn` indirecto. | Activación de la entrada concreta durante disparo, correspondencia completa con A7S y vínculo con `0x40193`. |
| Ruta YC/archivo | [Tareas de investigación](RESEARCH_TASKS.md) y [puente SFRA–MPR](sfra-mpr-buffer-bridge.md) delimitan formatos, pin `0x2a` y propiedad de buffers. | Creador de `0x2a` en disparo, alcanzabilidad de los escritores de modo 1, formato YC y ciclo terminal de propiedad. No hay cadena íntegra sensor→archivo demostrada. |

## Auditoría REA, Ghidra histórico y Unicorn

- [Hito REA](rea-independent-milestone.md): en `av-cam.bin`, REA reconoció
  363 de 464 entradas históricas exactas, nueve dentro de otra función y 92
  no encontradas. Son **entradas de la muestra**, no 101 funciones ausentes del
  binario. Las entradas Thumb sembradas manualmente y los gaps requieren el
  proyecto Ghidra histórico de solo lectura o desensamblado de bytes con LLVM.
  Una consulta REA vacía no prueba ausencia de código.
- REA y Ghidra histórico comparten motor; una coincidencia entre ambos no es
  validación independiente. Para afirmaciones decisivas usar bytes originales
  y LLVM/Capstone, registrar base/offset y diferenciar función reconocida,
  cuerpo reconstruido, flujo entre funciones y semántica física. El arranque
  REA del original ronda ocho minutos y la sesión no persiste: reutilizar una
  sesión para consultas relacionadas, sin reimportar el binario por cada caso.
- [Unicorn S58](s58-imx235-full-emulation.md) ya tiene mitigación ITSTATE y VFP;
  el límite de instrucciones falla explícitamente. Sus stubs, objeto sintético,
  memoria fabricada y ausencia de IRQ/OSAL/sensor son **límites de cobertura**,
  no un defecto general probado de Unicorn. Repetir el arnés no cerrará el
  efecto eléctrico ni la alcanzabilidad del disparo real.
- En este entorno, `.venv/bin/python -m pytest tests/test_s58_timing_a7s.py -q`
  no llega a colectar casos: `ModuleNotFoundError: unicorn` al importar
  `analysis/s58/wtrace.py`. Es un bloqueo local de reproducibilidad del arnés,
  no una refutación de sus resultados históricos. No se instalaron paquetes.

## Cola de trabajo antes de cualquier prueba física

1. Resolver las tres aristas abiertas de `0x40193` con llamadas, tablas de
   punteros y registro OSAL; mantener negativas acotadas a las regiones
   examinadas.
2. Seguir las entradas indirectas de RecordImage/RecordStill y la ruta de
   disparo hasta el consumidor de YC, cierre de cortina y salida MPR/DCF.
3. Reconstruir los cuerpos ausentes en los tramos decisivos del IMX210 y
   comparar sus argumentos/efectos con bytes A6000; no extrapolar A7S.
4. Resolver, hasta donde permita la evidencia estática, productor de modo 1,
   pin `0x2a`, formato y propiedad del buffer. Registrar explícitamente lo
   que exija semántica eléctrica o una observación real.

La regla vigente del usuario pospone **todas** las pruebas físicas hasta
terminar la descompilación/ingeniería inversa necesaria de esta ruta. La
matriz documenta trabajo pendiente; no autoriza parche ni cambia las tres
respuestas NO de [S51](s51-decision.md).
