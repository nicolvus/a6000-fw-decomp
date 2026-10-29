# E25-24c — Protocolo físico del selector EFCS / Electronic (pendiente de autorización)

28-10-2026. **No ejecutado.** Este documento no autoriza escrituras, flasheo ni pruebas en
cámara; describe qué habría que medir y con qué criterios, para una autorización separada.
La implementación offline está en [E25-24b](e25-24b-implementacion-selector.md).

## 0. Qué se quiere demostrar

| Afirmación | Cómo se demuestra |
|---|---|
| EFCS acciona la segunda cortina mecánica | Sonido/movimiento del mecanismo y RAW correcto con EFCS ON |
| Electronic no acciona ninguna cortina | Ausencia de sonido/movimiento mecánico y RAW completo con EFCS OFF |
| La modalidad no se mezcla entre disparos | Secuencia repetida EFCS→Electronic→EFCS con RAWs y estados |
| La reversión funciona | Restaurar imágenes originales y verificar hashes/arranque |

No basta con que el menú cambie ni con que `pkt[0x0e]` valga 0/1: eso ya está verificado
offline. La prueba física debe separar **selección** de **efecto**.

## 1. Precondiciones

1. Identificar cámara, IP, firmware, modelo y hashes; comprobar Telnet/RemoteShutter.
2. Copia de NVRAM y de los originales `av-cam.bin` y `darwin_core.bin`; verificar SHA-256.
3. Confirmar la vía de recuperación disponible (3.24) y el estado del actualizador. Sin
   recuperación demostrada, no se instala nada (E24-04).
4. Localizar de nuevo `M`, `cap` y los objetos dinámicos; no reutilizar direcciones
   históricas.
5. Escena fija, luz continua, apertura/ISO/encuadre constantes; RAW en tarjeta.
6. Instrumentación mínima: micrófono junto al cuerpo (cortinas) y, si es posible, registro
   de audio sincronizado con el disparo. No se abre la cámara.

## 2. Matriz mínima

Con EFCS ON y OFF, tres disparos por velocidad:

| Velocidad | Objetivo |
|---|---|
| 1/4000 | Régimen rápido; comparar uniformidad y sonido |
| 1/250 | Control intermedio |
| 1/60 | Control lento dentro del cuadro |
| 1/30 | Límite del cuadro (64,9 ms) |
| 1 s | Solo si Electronic ya tiene C3-B; si no, documentar el límite |

Secuencia de aislamiento: EFCS ×3 → Electronic ×3 → EFCS ×3 → Electronic ×3. Entre bloques,
comprobar que la cámara vuelve a `ready` y que no hay error.

## 3. Medidas y criterios

* **Audio:** energía y picos en la ventana del disparo. EFCS debe mostrar el segundo golpe;
  Electronic no debe mostrar ninguno atribuible a cortinas. Un solo micrófono no distingue
  motor de cortina: registrar también el motor de enfoque/estabilizador y usar controles.
* **RAW:** 6024×4024, sin recorte; media y uniformidad por filas tras nivel negro; comparar
  con el control de la misma sesión. Electronic con `ShutMode 3` puede conservar el sesgo de
  E25-10; no confundirlo con fallo del selector.
* **Estado:** `pkt[0x0e]` (si se puede leer), `cap+0x41c`, `record+0x6d`, `cap+0x655`,
  `cap+0x64c`, mensajes `0x0c`/`0x0e`. Solo lectura; no escribir RAM.
* **Reversión:** restaurar imágenes, verificar SHA y repetir un disparo mecánico de control.

Criterio de éxito del selector: EFCS conserva segunda cortina y exposición; Electronic no
acciona cortinas y entrega RAW de 24 MP; la secuencia repetida no acumula estado. Criterio de
exposición: solo se declara si el RAW cumple ±5 % y uniformidad ±5 % (para Electronic, tras
C3-B).

## 4. Abortos

* Error de disparo, `shooting` > 90 s o cámara que no vuelve a `ready`.
* Sonido anómalo, olor, temperatura anormal o batería inestable.
* Cualquier indicio de que el mecanismo quedó a medio recorrido.
* Fallo de comunicación con Darwin (sin `0x0e`).

Ante un aborto: apagar, no insistir, restaurar imágenes originales si se llegó a instalar, y
documentar el estado antes de cualquier otro intento.

## 5. Lo que no se puede demostrar offline

El movimiento físico de P4D/P4E, la ausencia de rebote, la integridad del RAW en todas las
velocidades, el comportamiento del cargador con el relleno parcheado y la recuperación tras
un fallo de arranque. Todo eso queda fuera de E25-24b y requiere esta sesión física
autorizada.
