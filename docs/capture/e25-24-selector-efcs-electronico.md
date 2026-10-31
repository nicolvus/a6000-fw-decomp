# E25-24 — Selector EFCS / electrónico: auditoría y bloqueos

28-10-2026. Investigación offline, sin acceso a la cámara. Base `1edcf13a`; el
commit solicitado `c6faf44d` está contenido en esta base. Este informe es un
avance parcial de E25-13, no una implementación ni una validación física.

## Cadena y alcance

La evidencia previa identifica en `libObj.so` un conversor que acepta los
modelos `0x2b4` y `0x2b5`, genera respectivamente los bytes 0 y 1 y envía el
selector LIRO `0x4099`; la acción y la ruta completa del menú no están cerradas
([investigación](shutter-investigation.md)). El manejador `0x43802e4c` copia el
byte a `+0x210` ([estado](silent-shutter-status.md)); T012 observó 0 con EFCS
activado y 1 con EFCS desactivado ([registro](registro-pruebas-camara.md)).
La identificación de las opciones visibles, persistencia, validación, todos
los escritores y consumidores sigue pendiente. No se ha demostrado que el
almacenamiento completo sea exclusivamente binario.

En la ruta de captura ya estudiada, `+0x210` alimenta el banco `+0x41c`, una
instantánea, `0x43842158`, `record+0x6d`, `0x4383fd6c`, `cap+0x655` y
`StartExposure` → `SetExposure` ([E020](efcs-capture-selector.md)). Las
condiciones y anulaciones del selector impiden identificar toda clase con una
modalidad física sin más pruebas. `SetExposure` / `SetRead` / `Execute(1)`
producen y despachan parámetros hacia P2S; esto no prueba su transmisión
eléctrica ni identifica el inicio y fin de integración
([E25-21](e25-21-setexposure-p2s.md), [E25-22](e25-22-protocolo-transporte-fisico.md)).

## Decisión provisional

La alternativa de dos estados EFCS / Electronic es la candidata de menor
alcance: reutiliza un conversor binario conocido. Todavía no es una selección
implementable con seguridad. El valor 1 significa EFCS desactivado en la ruta
original y no puede simplemente reinterpretarse como Silent dejando sus
consumidores intactos. No se conocen todos los puntos a modificar, ni si
existe un tercer valor persistente compatible. La alternativa de tres estados
tampoco está descartada como imposible; su coste y seguridad aún no se conocen.

El firmware experimental 3.23 combina tipo 0 y B1a: el salto fijo
`0x1fe6a: 28 46 → 0a e0` fuerza la compuerta en Darwin. Cambiar solo BIONZ
no demuestra que vuelva la segunda cortina para el EFCS de referencia. Falta
un canal y una política por captura para el mecanismo, verificar el tipo y el
rearme, y demostrar recuperación ([E25-02](e25-02-validacion-candidato-y-via-volatil.md),
[E25-04](e25-04-recuperabilidad-y-decision.md)). Condicionar B1a por sí solo
tampoco demuestra que el tipo 0 restaure EFCS. No se proponen bytes nuevos ni
un parche de menú instalable con estas incógnitas.

## Correcciones al informe de referencia

La auditoría de [EFCS + Darwin + Silent](efcs-darwin-silent-integracion.md)
detecta afirmaciones que no deben reutilizarse como verificadas:

* Su fórmula `r5 × período` contradice el modelo rápido `(VTS − r5) × período`
  de [E25-18](e25-18-integracion-silent-todas-velocidades.md). Ambos son
  modelos condicionados; no son una medición universal del sensor. VTS 4219 y
  período 3891 Q8 no se deben generalizar: E25-19 midió 4176 y 4096 en otro
  contexto.
* `0x438c82a0` no está después de la llamada situada en `0x438c82dc`;
  E25-18 propone `0x438c82fe` para el caso rápido, con dependencias y límites.
* EFCS original no equivale a tipo 0/B1a sin cortinas; afirmar que el primero
  no mueve P4D/P4E confunde el baseline con el experimento. Tampoco está
  demostrado que B1a intacto permita seleccionar ambos comportamientos.
* La recepción de `0x0e` y la programación de `SetExposure` no demuestran
  respectivamente el fin y el comienzo físicos de integración. Un RAW o un
  sonido reducido no acreditan una exposición silenciosa uniforme y correcta.

El índice de contradicciones es incompleto y no sustituye esta revisión. El
informe de referencia llama «alternativa B» a un enganche C3; no es la
alternativa B del usuario, que significa selector binario EFCS / Electronic.

## Plan de implementación y validación pendiente

1. Censar GUI, validación y persistencia; seguir ambos valores y consumidores
   con REA y bytes del binario original. Identificar la selección y restricciones
   por modo, vídeo y flash sin modificar NVRAM.
2. Trazar la decisión y el canal BIONZ → Darwin para preservar EFCS original y
   seleccionar supresión mecánica por captura. Exigir estado inactivo, confirmar
   fin de escritura RAW y rearme, y rechazar transiciones ambiguas o valores
   inválidos. Sin mecanismo comprobado, no construir un parche ejecutable.
3. Resolver cuándo se calculan y restauran `shd`, `svd`, `spl`, `ShutMode` y
   temporización, incluyendo el campo calculado antes de C3; verificar
   aislamiento y reversión con pruebas sobre instrucciones reales. El modelo
   de [E25-18](e25-18-integracion-silent-todas-velocidades.md) y sus pruebas
   son reutilizables, pero emulan componentes, no la captura ni el sensor.
4. Demostrar inicio y fin electrónico y entrega P2S; no extender conclusiones
   de un cuadro a velocidades largas o BULB. El incidente E25-23 de 30 s sigue
   abierto; no repetirlo. El informe y datos de E25-23 fueron retirados en el
   historial remoto previo a esta base, aunque su descripción sigue en
   PENDIENTES; se conservan en Git antes de la integración remota.

## Protocolo físico y baseline, aún sin autorización

Antes de proponer una instalación: identificar cámara, firmware, hashes, IP,
estado, objetos dinámicos, B1a/C3/T050 y respaldos; establecer recuperación
comprobada y guardar bytes originales exactos, puntos de enganche, mecanismo
de restauración, tiempos de espera y criterios de aborto. Verificar en reposo,
captura, escritura RAW y error antes de permitir cambios de modo. Una prueba
física requiere autorización separada y no queda autorizada por este documento.

La comparación prevista es EFCS original frente a Electronic, con cámara fija,
misma escena e iluminación continua, apertura, ISO, enfoque y procesado;
conservar RAW y medir exposición tras nivel negro, Bayer, saturación, filas,
columnas, ruido y repetibilidad con incertidumbre. 1/4000, 1/250, 1/60 y
1/30 s son objetivos de ensayo, no velocidades certificadas seguras para esta
implementación inexistente. EFCS no es un baseline de dos cortinas mecánicas.

---

## Actualización 28-10-2026 — implementación offline (E25-24b)

La auditoría anterior identificaba los bloqueos; ya hay una implementación
offline verificada en [E25-24b](e25-24b-implementacion-selector.md):

* Selector binario EFCS↔Electronic reutilizando el campo `+0x210` (EFCS ON/OFF),
  sin añadir una entrada de menú.
* B1a y tipo 0 sustituidos por una compuerta por captura: BIONZ copia
  `cap+0x41c` a `pkt[0x0e]` y Darwin decide con ese byte si ejecuta la ruta
  original (`0x20c74`/`0x1fe66` → `0x1b080`) o devuelve 0.
* Parches con bytes originales, manifiesto, reversión y 36 pruebas; emulación
  Unicorn de las dos compuertas y del cave de BIONZ.
* Sigue pendiente la exposición electrónica C3-B (E25-26) y toda la validación
  física (E25-27, protocolo en [E25-24c](e25-24c-protocolo-fisico-selector.md)).

La frase «no se proponen bytes nuevos» de las secciones anteriores queda
superada por esta actualización; se conserva como registro de la auditoría.
