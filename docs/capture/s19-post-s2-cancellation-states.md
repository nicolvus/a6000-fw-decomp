# S19-13 — Cancelación y estados posteriores a S2

Alcance: Sony A6000 FW 3.21; análisis estático local de `av-cam.bin` con
`llvm-objdump -d --triple=thumbv7-none-eabi` sobre
`analysis/av-cam-analysis-view.elf` (base LIRO `0x43541000`). No se modificó
ningún binario ni proyecto Ghidra y no se usó cámara.

## Veredicto

**S19-13: PARCIAL.** Hay tres mecanismos estáticos distintos: RelMgr emite
`0x3015` al soltar una tecla; el dispatcher local toma salidas que desarma o
notifica estado; y las etapas LIRO devuelven errores/reintentos y limpian una
ranura `+0x754`. No se recuperó la arista que una `0x3015` con el dispatcher,
con una etapa LIRO, con el estado idle ni con CAIF/Darwin. Por ello no se puede
afirmar que soltar S2 cancele una captura ya comprometida, ni que exista una
ventana de cancelación segura antes de una cortina.

## Evidencia

| Clasificación | Dirección | Hallazgo | Método |
|---|---|---|---|
| VERIFICADO | `0x4379ea38..0x4379ea64` | RelMgr construye ObjMsg tipo 0, id `0x3015`, origen `0x300c`, y lo entrega mediante `0x43aeaee2`. Esto prueba emisión de transición; no identifica liberación física S2 ni consumidor. | LLVM Thumb. |
| NO_VERIFICADO | `0x3015` → `0x43807f4c` | Sigue sin receptor de `0x40193` ni adaptador demostrado entre `0x3011/0x3013/0x3015` y los mensajes locales `0x100..0x207`. | Búsqueda/recorrido estático heredado y rechecado. |
| VERIFICADO | `0x43807d80..0x43807f40` | Las rutas que no instalan `0x43809ed8` llaman combinaciones de helpers de estado y retornan; varias pasan `0` o `1` a `0x43b01a20`, y otras hacen tail-call a `0x43b01f36/40/7c`. Los nombres/efectos semánticos de esos helpers no se recuperaron. | LLVM control-flow. |
| VERIFICADO | `0x438082ce` | Sólo el mensaje local `0x100` entra directamente en `0x43807d80`; los casos vecinos (`0x101`, `0x102`, etc.) toman otros handlers. Esto separa dominios locales, no asigna significado de cancelación. | LLVM en `0x43807f4c..0x43808340`. |
| VERIFICADO | `0x437f22d4..0x437f245c` | La etapa LIRO llamada desde las filas dinámicas retorna códigos `0`, `1`, `2` o `5`; en la rama `FUN_43ae7648()==1`, si `ctx+0x754 != 0`, llama `0x437fbad8(param,ctx+0x754,0)` y escribe cero. La ruta normal también llama `0x43b00410`, repite esa limpieza condicional y cierra el objeto temporal con `0x43787180`. | LLVM Thumb; pseudocódigo local previo contrastado con el flujo. |
| INFERENCIA | `ctx+0x754`, `0x437fbad8` | El patrón «helper con valor + escritura cero» parece desvincular una ranura de solicitud/etapa. No se conoce el tipo del campo, la propiedad ni si equivale a idle o cancelación segura. | Flujo de datos estático. |
| VERIFICADO | `0x43b1bf04`, `0x43b1bfc8`, `0x43b1c034` | Las filas LIRO despachan por estado hacia `0x437f22d4`, `0x437f1c38`, `0x437f247c`, `0x43afe9f4/ea*` y `0x437ed568`; estado fuera de rango retorna `5`. Son rutas de error/reintento reales, no prueba de finalización. | LLVM Thumb, entradas pares (bit Thumb removido). |
| NO_VERIFICADO | Cadena RelMgr → CaptureManager → LIRO | No se recuperó un retorno que restablezca un estado denominado idle, ni una confirmación que vincule `0/1/2/5` con éxito, cancelación, física o disponibilidad de nueva captura. | Análisis estático. |
| NO_VERIFICADO | DMM en esta cadena | No apareció `DmmOpen`, `DmmClose`, `DmmFree`, `DmmCloseAndFree` ni una asignación/liberación de unidad DMM atribuible a estas rutas. En consecuencia no se acredita liberación de buffers. | LLVM y contraste con la evidencia DMM previa. |
| DESCARTADO | `DmmClose` | Aunque se encontrara un cierre, no demostraría liberación de asignación: en `dmm.ko:0xa430..0xa458` sólo decrementa `unit+0x2a1`. No se usa como evidencia de ownership o liberación. | Evidencia previa `s16-codex-fea-completion.md`. |
| HIPOTESIS | antes de `0x43b04730` | El único intervalo candidato para abortar antes de ejecutar el descriptor sería después de admisión y antes de `0x43b04730(Image)`. No hay vínculo de un mensaje de liberación con ese intervalo, ni prueba de que éste preceda toda orden física CAIF/Darwin. | Orden de llamadas recuperado. |

## Estados que sí se pueden separar

```text
RelMgr emite 0x3015             [VERIFICADO]
  └─ adaptación a dispatcher    [NO_VERIFICADO]
dispatcher local limpia/notifica o instala callback  [VERIFICADO]
  └─ CaptureManager selecciona descriptor y ejecuta 0x43b04730 [VERIFICADO]
       └─ LIRO devuelve/reintenta y puede limpiar ctx+0x754    [VERIFICADO]
            └─ idle, liberación DMM y borde de cortina         [NO_VERIFICADO]
```

## Consecuencias de seguridad

- Una ruta alternativa tendría que preservar la correlación de RelMgr y los retornos de etapa, realizar la limpieza que corresponda a `+0x754`, y tener un finalizador explícito de recursos propios.
- No se debe sustituir esa limpieza por `DmmClose`: no es una liberación de asignación demostrada.
- No existe una ventana de cancelación segura verificada. Cualquier propuesta entre `CaptureStart` y CAIF/Darwin permanece hipotética.

## Siguiente tarea

**S19-14 (f): `Stage_RawPlayInit` y reutilización de etapas.** Es la opción pendiente más útil: las etapas LIRO anteriores revelan contratos de retorno y limpieza (`0x437f22d4`), pero falta recuperar qué recursos/etapas inicializa o finaliza `Stage_RawPlayInit` para evaluar una reutilización sin inventar ownership ni movimiento de obturador.

SilentShutter no se declara funcional.
