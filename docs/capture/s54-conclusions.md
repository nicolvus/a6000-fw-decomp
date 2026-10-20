# S54 — Conclusiones (20-10-2026)

Fase cerrada por **criterios 1–5 de §16** (frontera estática documentada en P4C, alcance del tipo 0 determinado, sensor sin avance, pruebas reproducibles, incertidumbres listadas).
Pruebas: `python3 -m unittest tests.test_s54_p4c` → 21/21 OK. SHA de ROM Darwin A6000/A7S y `av-cam.bin` verificados por la propia suite (inicio y fin).
Informes: [P4C](s54-p4c-signal-trace.md) · [BIONZ](s54-bionz-darwin-sync.md) · [tipo 0](s54-mechanism-type-zero.md) · [IMX210](s54-imx210-electronic-exposure.md) · [cronología](s54-capture-timeline.md).
Matriz: [`analysis/s54-evidence-matrix.json`](../../analysis/s54-evidence-matrix.json).

## Respuesta a la pregunta central

BIONZ X recibe `CA_1ST_CURTAIN_START` en **dos pines** (`SENS_B` AA13 y `GPIO_9` AD21; A7S igual), pero **no se localizó** qué función del firmware la consume ni si actúa
sobre el sensor: los pares (canal, bit) de los lectores GPIO de la tarea CA son variables sin inicializar en la imagen (frontera). Darwin la emite **siempre** (P4C←0, nunca ←1 en
tiempo de ejecución), en ambas ROM y en todas las ramas, incluida la sin mecanismo. En A7S Silent esa escritura se conserva idéntica; lo que cambia es la omisión de P4D/P4E y del ADC.

## Hallazgos nuevos (VERIFICADO salvo nota)

1. Red P4C → `SENS_B` + `GPIO_9` de BIONZ (A6000 y A7S). **Corrige S53:** el esquema A7S sí está en el repo (`docs/references/sony-ilce-7s-level3-sm.txt`); P4B–P4E de A7S dejan de ser solo inferencia (columnas idénticas).
2. P4C: 9 sitios de escritura por ROM, todos con valor 0; ninguna escritura a 1; el único otro camino a PDOR4 (`0x51f2`) conserva b12.
3. Tipo 0 de A6000 ≡ rama Silent de A7S **dentro de las funciones de exposición, diferidos y ADC** (diff llamada a llamada). No ≡ en reposición/aborto (A7S Silent sí actúa con `no_silent=1`).
4. El tipo viene de `[0x20000050+ch]` validado por `[0x200002c0+ch]`, que habilita el manejador 33 de la tabla `0x2a1a0`; escritor del valor NO localizado.
5. Primitivas GPIO de BIONZ (`0x43b5e2bc/22e/29a`, base `0xf2910000`) y 97 puntos de llamada; tabla CAIF de trazas con `ExposureEndNotify/ExpStartComp`.

## Hipótesis

| H | Estado | Resumen |
|---|---|---|
| H54-1 | INFERENCIA | P4C←0 es la marca común de «inicio»; consumidor no demostrado |
| H54-2 | PARCIAL | Darwin A7S mantiene P4C en Silent (VERIFICADO); uso por BIONZ no comparado |
| H54-3 | NO VERIFICADO | sin consumidor localizado |
| H54-4 | NO VERIFICADO | emisión y cableado iguales; recepción no comparada |
| H54-5 | PARCIAL (reforzada) | tipo 0 = Silent en exposición/ADC; ≠ en reposición y en todo lo previo a Darwin |
| H54-6 | PARCIAL | tipo 0 es estado de configuración, no modo fotográfico (origen no cerrado) |
| H54-7 | NO VERIFICADO | sin datasheet/traza |
| H54-8 | INFERENCIA fuerte | A6000 necesitaría LIRO (clase/flags, IMX) **y** Darwin (paquete/`no_silent` o tipo 0 + manejo de reposición); S53/S52 |

## Decisión S51 (viabilidad)

**Se mantiene: NO PARCHEAR NI FLASHEAR.** Condición A (mecánica): mejor entendida —Darwin ya tiene un camino sin bobinas— pero BIONZ no está cerrado; B (sensor): NO; C (coordinación): NO;
D (seguridad experimental): no definida. Ningún firmware modificado fue generado ni ejecutado.

## Bloqueantes

1. Mapa pin→(canal, bit) de BIONZ y datos de arranque que rellenan `0x43e77298…`.
2. Escritor/emisor del byte de tipo de mecanismo (`0x20000050+ch`, categoría `0x2d` entrada 33).
3. Polaridad/reposo de P4C (perfil de pines usado por la placa) y rearme.
4. Registros/temporización del IMX210/DFE para fin de integración (datasheet o traza pasiva).

## Siguiente experimento de mayor valor

**Estático:** repetir en `av-cam` A7S 3.20 el barrido `gpio_get` y comparar con A6000 (¿lee A7S un par adicional en Silent?; H54-2/H54-4), y localizar el inicializador de las variables de pin
(proceso que escribe `0x43e77298…` desde `liro.ko`/arranque). **Pasivo autorizado:** analizador lógico en `GPIO_9` (o P4C en CN4900) y `MSS_SO_DWN` durante una foto mecánica y una EFCS
(solo lectura; confirma polaridad, flanco y relación con ID `0x0c`).
