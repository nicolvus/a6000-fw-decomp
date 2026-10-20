# SilentShutter: consumidores y llamadas IMX210 — E018

Continuación de [E015–E017](silent-shutter-status.md). Análisis estático del
av-cam.bin oficial 3.21, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Todas las direcciones de este documento usan la base lógica 0x43541000.

## Entradas del controlador contrastadas con su tabla virtual

El nombre RTTI IMX210 apunta a typeinfo 0x43fea0a4. La tabla con cabecera
{0, typeinfo} está en 0x43fcc088; su punto de métodos es **0x43fcc090**.
La asociación no depende solo de proximidad de cadenas: los punteros están
en los bytes originales. La tabla de la clase base usa typeinfo 0x43fea23c
y punto de métodos 0x43fcc170.

Los wrappers C_Imager validan el argumento y llaman al slot virtual indicado.
Sus diagnósticos contienen las firmas completas de los métodos.

| Operación | Wrapper C_Imager | Slot | Puntero Thumb IMX210 | Entrada |
|---|---|---|---|---|
| SetMode | 0x436d62e4 | +0x20 | 0x436d6b51 | 0x436d6b50 |
| SetExposure | 0x436d6320 | +0x28 | 0x436d6f6d | 0x436d6f6c |
| SetExposure_ZAF | 0x436d635c | +0x2c | 0x436d67e5 | 0x436d67e4 |
| SetRead | 0x436d6398 | +0x30 | 0x436d7e09 | 0x436d7e08 |
| SetRead_ZAF | 0x436d63d4 | +0x34 | 0x436d74b9 | 0x436d74b8 |

Corrección de E017: 0x436d67ec y 0x436d74bc eran candidatos interiores;
el primero omitía carga/comparación previas al PUSH. No deben tratarse como
entradas, ni la condición `in_ZR` de aquel pseudocódigo como un argumento real.
Además corresponden a variantes con sufijo ZAF. No se atribuye un significado
físico a ese sufijo sin evidencia adicional. Para exposición normal, continuar
desde **0x436d6f6c**, no desde el candidato interior 0x436d67ec.

En la tabla base, los slots +0x20/+0x28/+0x30 apuntan a 0x439b4145;
en la tabla IMX210 se sustituyen por métodos propios. Eso prueba una
implementación diferenciada en el binario; no identifica la revisión física
del sensor ni demuestra que cada modalidad esté habilitada en A6000.

## Identidad de la copia de trabajo

En 0x437dfd58, el cálculo PIC usa literales:

- [0x437dfddc] = 0x83f17a.
- PC usado = 0x437dfd6a; [0x437dfde0] = 0x4cd8.
- La suma es **0x44023bbc**; la palabra original allí vale **0x43ed4d28**.

Por tanto, el puntero de trabajo tiene una inicialización estática concreta.
Esto no garantiza que conserve ese valor durante toda la ejecución. La copia
de 0x560 bytes comienza en objeto+0x48: Silent queda en +0x280 y EFCS en
+0x258. El getter 0x437dfe4c devuelve objeto+8: relativos a su retorno,
Silent queda en +0x278 y EFCS en +0x250. Las búsquedas de consumidores deben
conservar estas transformaciones y la identidad del puntero.

El lector 0x43792fb4 carga +0x238 de otra cadena de punteros:
estructura global 0x43e99208, campo +8. **Se descartó como lectura Silent**:
0x4378fa70 llama a 0x43ae8eae con base 0x43e9b548 y tabla 0x43e99208;
0x43ae8d56 enlaza tabla[0] = base y tabla[2] = base+0x5a4. El campo leído
pertenece por tanto a base+0x7dc, fuera de los 0x560 bytes copiados de los
comandos. Su entrada candidata de función es
0x43792a0c; una consulta inicial creada en la instrucción interior 0x43792fb4
se retiró del proyecto.

En cambio, 0x43792a0c sí llama a 0x43804c5c con **0x43e9b548**. En la rama
normal esta última copia 0x560 bytes desde **0x43edf684**; la rama alternativa
usa 0x43b00d06 para copiar objeto+8. Esto resuelve otra propagación del bloque
completo, sin convertir el lector de la subestructura en consumidor Silent.

También se siguió 0x43afa0ce: getter de trabajo 0x437dfe4c → retorno+0x40
(objeto de trabajo+0x48) → 0x438b83a0 → configuración de captura+0x20.
La conversión explícita inspeccionada no carga los offsets de entrada
0x238/0x210. Contiene una tabla de salto no recuperada por el decompilador;
no usar esa observación acotada para afirmar ausencia total de consumidores.

## Método reproducible y límites

Se reutiliza `analysis/ghidra/silent-liro.gpr`. `SeedSilentLiro.java`
incorpora las 220 filas de la tabla de despacho; `QuerySilentLiro.java`
consulta funciones sin borrar las anotaciones existentes y verifica el hash
completo antes de exportar. `RepairImagerEntries.java` corrige las dos entradas
con respaldo en la vtable; `QuerySilentReferences.java` exporta referencias.

Para plegar literales PIC, QuerySilentLiro marca el bloque anterior a
0x43bc0000 como no escribible **en el proyecto de análisis**. Es una hipótesis
sobre código/pools constantes, no un mapa de permisos medido en la cámara.
Los bytes no se modifican; la región posterior sigue escribible. Contrastar
las conclusiones de pseudocódigo contra instrucciones y literales originales.

Las evidencias REA previas se importaron de nuevo mediante
`import_evidence_bundle`: 61 registros validados, sin reimportar el binario.
El registro de la copia 0x437dfd58 conserva su ID
`ev_2891468c7e58b36bf94978e5efba0b1e1fa1f51fa7a24925d942d6fd2d4c46de`.
Ese registro no contiene un dossier de flujo de valores; no atribuirle esa
cobertura. Los nuevos exports Ghidra son artefactos separados.

Se conservan 35 exports de funciones con el mismo hash de origen. El análisis
amplio llegó a300s y terminó por tiempo; no se considera completo. El proyecto
registra más de37000 funciones tras consultas y correcciones. Tres consultas
no encontraron función y conservan ese estado explícito. Las entradas
provisionales descartadas se enumeran en `analysis/ghidra/rejected-queries.json`;
sus exports históricos no se borraron. Cinco consultas finales se verificaron
decompiladas y el proyecto quedó guardado.

## SetRead IMX210 decompilada íntegra (18-10-2026)

Objetivo: buscar en `SetRead` (0x436d7e08) y en el switch de configuración
0x438b83a0 un lector real de Silent +0x238/+0x210 o de su copia
trabajo+0x280 (ver sección anterior), y ver si conecta con fin de exposición,
MechaCommon o un productor YC/DMA.

| Clasificación | Hallazgo | Evidencia |
|---|---|---|
| VERIFICADO | `SetRead` 0x436d7e08 decompilada completa hasta el retorno 0x436d8004. Rechaza estado 0x11 (resultado 2); en la ruta normal calcula parámetros, actualiza estado y devuelve 0. El tramo final solo tiene diagnósticos: no hay espera de fin de lectura ni producción explícita de buffer YC/DMA. | `analysis/ghidra/imx210-setread-config-static-20261018.json`, `imx210-setread-config-instructions-20261018.json` |
| VERIFICADO | Las cuatro llamadas 0x436d7ec0/7ed0/7ee0/7ef0 → 0x43ad9262 reparten el valor calculado en ocho bytes de registros sombra; 0x436d7de8 escribe 0x40/0x48 en 0x4401c73a; los flags 1/8 de 0x436d9f70 solo habilitan diagnósticos. | `imx210-setread-config-instructions-20261018.json`, `imx210-setread-callees-static-20261018.json` |
| VERIFICADO | 0x436d7f30 → 0x436d6450 es `GetImagerTemperature` (vtabla +0x68 → 0x43ad91c6 → +0x6c → 0x435434a8, calcula y escribe un float); no relacionado con Silent. | `imx210-setread-temperature-static-20261018.json`, `imx210-setread-temperature-leaf-20261018.json` |
| VERIFICADO | Switch 0x438b8902 (tabla en 0x438b8906, selector 0x43e95950+0x75): casos 1→11, 2→8, 4→12, 8→13 escritos en salida +0x50; el resto conserva el valor previo. **Ningún caso ni el conversor cargan la entrada +0x238/+0x210/+0x280.** | `imx210-setread-config-static-20261018.json` |
| PARCIAL | `SetRead` y sus auxiliares examinados no tienen lectura identificada de Silent ni enlace a MechaCommon o productor YC. No cierra la cadena transitiva completa (quedan llamadas indirectas/auxiliares sin resolver); el objeto de temperatura parte nulo en 0x43e7f858. | `imx210-setread-runtime-object-refs-20261018.json`, `imx210-setread-callees-static-20261018.json` |
| NO_VERIFICADO | Que los registros sombra de 0x43ad9262 programen el fin electrónico de exposición, o que Silent llegue por estas rutas a un registro, orden mecánica o buffer de captura. | Frontera de los exports anteriores. |

Dato que falta y procedimiento no destructivo para resolverlo: identidad completa
de los objetos desde la inicialización de 0x43e7f858 y los llamadores de
`SetRead` (análisis estático adicional, sin tocar el dispositivo); semántica
física de los registros sombra y origen real del buffer, que requeriría
documentación IMX210 o una traza pasiva (bus/registro) en hardware, no solo
el binario. Análisis realizado con el proyecto persistente
`analysis/ghidra/silent-liro.gpr` en modo solo lectura (`-readOnly -noanalysis`),
verificando el SHA-256 del blob antes de exportar; no se modificó el proyecto
ni los binarios originales.

## Estado de la conclusión

**ACEPTO:** wrappers, slots y entradas anteriores están contrastados con
instrucciones y bytes de tabla. **RECHAZO:** asignar cortina electrónica trasera
a una variante ZAF, al modo 0x11 o a los flags de diagnóstico 1/8 solo por sus
nombres o números. La ausencia de referencias automáticas tampoco demuestra
que Silent esté muerto. El enlace al fin electrónico de integración sigue
necesitando evidencia del consumidor y de la secuencia de captura completa.
`SetRead` queda ahora descartada como ese consumidor: está decompilada íntegra
y no lee Silent ni su copia (ver sección anterior, 18-10-2026).
