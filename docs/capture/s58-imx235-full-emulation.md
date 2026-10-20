# S58-C — Emulación IMX235: cadena ejecutada y cobertura delimitada

20-10-2026. A7S 3.20, SHA-256 `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`. **Se ejecutan los cuatro métodos reales y el transporte P2S; la inicialización completa del sistema y la respuesta eléctrica quedan fuera.**

## Entradas verificadas en bytes de vtable

| Método | Slot de 0x43fce050 | Entrada Thumb sin bit 0 |
|---|---|---|
| SetMode | +0x20 | 0x436f3b44 |
| SetExposure | +0x28 | 0x436f4168 |
| SetRead | +0x30 | 0x436f4a94 |
| Execute | +0x38 | 0x436f5a14 |

Wrappers de servicio: `0x436f2910`/`0x436f2988`; cargador de columna `0x436f3928`; formateador `0x43ad9536`/`0x43ad95a6`/`0x43ad9666`; backend P2S `0x436f26c8`. El constructor no se recuperó ni ejecutó: objeto sintético en 0x45600000, vtable real, campos restantes a cero. No se simula una captura iniciada desde el arranque.

**CORRECCIÓN (VERIFICADO) de [S57-B](s57-ssb-pulse-analysis.md):** `0x436f4a94` es SetRead y `0x436f4168` es SetExposure. La comparación arg+2>0x1000 pertenece a ganancia. Identidad comprobada por los slots, logs y ejecución separada.

## Estructuras y formato

- Banco sombra: 98 registros en `0x44021ebc`, paso **6 B** `{u16 dispositivo,u16 dirección,u16 dato}`; la carga/emisión usa sus bytes significativos. El borrador «registro de cinco bytes» no describe el stride en memoria.
- Matriz: 69 filas de 0x14 B `{puntero_dato,16 columnas}` en `0x43fee598`. Tabla de 34 modos en `0x43fee370`; 34 índices de columna en `0x43c9c5b5`, 15 columnas usadas.
- Bus observado: `81|03|DEV|ADDR8|DATA`, terminador 00 al final de cada buffer. No se observó direccionamiento de 16 bits en estos escenarios A7S; A6000 usa otro formato.

## Escenarios y evidencia persistida

`python3 analysis/s58/reproduce.py` genera:

- `out/a7s_scenarios.json`: modos 0x0b, 0x35, 0x4c, 0x4d, 0x4e, 0x4f × ShutMode 0/1; argumentos sintéticos iguales shd=0x123, svd=0x456, spl=0x78, AGC=0x100. Todos los métodos devuelven 0.
- `out/a7s_effective_diff.json`: cinco comparaciones por etapa, valores de matriz y nueve escenarios AGC (0x1000/0x1001/0x2000 en foto y Silent).

Se conservan snapshots ordenados de los 98 registros: inicial, SetMode, SetExposure, SetRead, pre-Execute y post-Execute. Se guardan tramas, escrituras MMIO con PC/tamaño/valor, mensajes y stubs. `device_seq` conserva duplicados y dispositivo; `seq` es solo la vista compatible del dispositivo 0x81.

**Resultado:** 5 buffers P2S de longitudes 126,126,126,101,26 B; **100 escrituras**, 99 al dispositivo 0x81 y una a **0x83:0x17=0x4a**. Orden idéntico de destinos en los escenarios obligatorios. FIFO `0xf3c00340+4i`, disparo 1,0,1 en `0xf3c00808`. El decodificador inicial de Claude cortaba al encontrar DEV=0x83 y contaba 99; se corrigió y se añadió regresión y rechazo de trama truncada.

## Stubs y condiciones artificiales

Se permite ejecutar `0x436f2000..0x43700000`, `0x43ad9000..0x43adb000` y `0x43550000..0x43570000`. Fuera de esos intervalos, las llamadas retornan 0 salvo el stub de mensajes `0x438f6864`, que registra r0…r3 y devuelve 1. En los escenarios aparecen destinos stub 0, `0x439b3918`, `0x438f7114`, `0x43544270`: las llamadas indirectas a 0 evidencian servicios/objetos sin inicializar. Sus efectos no se consideran ejecutados.

Depuración `0x43de4910`: se fuerza 0xff (sin sustitución), no el BSS cero de la imagen. NTPAL/matriz alternativa quedan fuera. Memoria no mapeada se crea con 0 o 0xa5; memoria de firmware/objeto ya mapeada conserva sus valores. No hay IRQ, espera OSAL real, confirmación de receptor SIF ni modelo del sensor.

El arnés habilita VFP y conserva la mitigación ITSTATE del trabajo heredado. Su vector de regresión pasa; esto no acredita equivalencia exhaustiva ni prueba un defecto general de Unicorn. Agotar el presupuesto de instrucciones ahora lanza error: no se acepta como retorno correcto.

## Cobertura que sigue faltando

Constructor y servicios reales; origen AE de los argumentos A7S; errores OSAL/P2S; modos alternativos NTPAL; callbacks asíncronos; secuencia posterior al fin de exposición; aplicación eléctrica de los buffers. Por ello «cadena completa» significa **cuatro métodos y preparación de transporte bajo estas condiciones**, no emulación integral de Silent Shooting.

Tests: `tests/test_s58_timing_a7s.py`, clases Integrity, A7SMatrix, A7SExposure, A7SExecute y HarnessLimits. [Diferencias](s58-a7s-silent-effective-diff.md) · [ciclo](s58-exposure-cycle.md).
