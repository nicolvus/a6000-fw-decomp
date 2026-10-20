# S20 — P3 (contrato YC real de `ObjCamera.out0`): intento con `llvm-objdump`, resultado limitado por atribución de clase

Continuación del bloqueo de herramienta registrado en la sesión anterior
(`S20-P3-ATTEMPT`, Ghidra/`scripts/libobj_dec.sh` producía pseudocódigo
inválido para `libObj.so`). Esta tarea reintenta P3 con `llvm-objdump`
directo, como ya hizo S19-04/05. Alcance: `libObj.so` SHA-256 ya verificado
en sesiones previas, sin modificar el binario.

## Resultado: sin cierre, limitado por falta de límites de función/clase fiables

**VERIFICADO** — `MWF::ObjPin::Send(unsigned int, MWF::ObjMsg*)` tiene
exactamente **464 sitios de llamada** en todo `libObj.so` (enumeración
completa vía `llvm-objdump` + PLT, `/tmp` de trabajo, lista reproducible).
**Ninguno cae dentro del rango de código ya verificado por S19-04 como
construcción/inicialización de `ObjCamera`** (constructor `0x98c380`, y los
auxiliares de pines `0x987788/0x987d6c/0x987dc6/0x9880a4`). Esto es un
hallazgo negativo real, más fuerte que el de S19-04 (que solo inspeccionó el
constructor): **en todo el código de construcción de ObjCamera no hay una
sola llamada directa a `Send`.**

**INFERENCIA, no verificado**: existe un sitio de llamada a `Send` en
`0x98f974`, físicamente dentro del rango atribuido por el símbolo exportado
más cercano (`ObjCamera_Destroy`, offset `+0x35d72`) — pero esta atribución
es **débil**: el binario está *stripped* y solo tiene símbolos exportados
para `ObjCamera_Create`/`ObjCamera_Destroy`; el rango entre un símbolo
exportado y el siguiente puede contener código de **otras clases locales no
exportadas** del mismo archivo fuente, sin que `llvm-objdump` pueda
distinguirlo sin un análisis de límites de función (el que Ghidra debería
dar, pero que en esta sesión produjo resultados inconsistentes para esta
librería — ver bloqueo de la tarea anterior).

### Lo que sí se decompiló del sitio `0x98f974` (quien sea su clase real)

```
GetCategoryId(ctx+0x18)              -> r5   # inspecciona un ObjMsg ENTRANTE
si 0x991948(r9, ctx+0x18) == 0:
    ObjMsg::SetCateIdMsgId(&msg, r5, 0x100e)
sino:
    ObjMsg::SetCateIdMsgId(&msg, r5, 0x100f)
ObjMsg::AddParam(&msg, 0x1011, &param)   # uno o dos parámetros según rama
pin = GetPin(r4, 6)                      # 0xa15fb4(r4, 6) -- INFERENCIA de nombre
pin->Send(0x1003, &msg)
```

Esto es un patrón real de **manejador de mensaje entrante → construcción de
respuesta → envío por el pin de índice 6** con los códigos `0x100e/0x100f`
(selección de rama) y `0x1003` (mensaje de salida — el mismo código `0x1003`
ya visto en `s20-rawplay-stage-reuse.md` §2, construido por `FUN_43b1ad32`
en el lado LIRO). **No se verificó que este sea un método de la clase
`ObjCamera`** ni que el pin de índice 6 corresponda a `Camera.out0` (que es
el pin de índice 0 según la construcción de nueve pines ya verificada por
S19-04). Si esta atribución fuera correcta, el pin 6 sería una salida
distinta de `out0`, por lo que **incluso en el caso más favorable esto no
cerraría el contrato de `Camera.out0`**.

## Clasificación

- **VERIFICADO**: 0 llamadas a `ObjPin::Send` dentro del código de
  construcción ya verificado de `ObjCamera` (constructor + 4 auxiliares de
  pines).
- **NO_VERIFICADO**: a qué clase pertenece realmente el manejador en
  `0x98f974`; si el pin de índice 6 es relevante para `Camera.out0`; el
  significado de los códigos `0x100e/0x100f/0x1003/0x1011` en este contexto.
- **DESCARTADO**: usar la proximidad a un símbolo exportado como prueba de
  pertenencia de clase en un binario *stripped* sin límites de función
  recuperados — es el mismo error que ya se evitó en C1 (sesión 20) al
  distinguir origen/destino de una fila de topología.

## Bloqueo real para cerrar P3

Se necesita recuperar los límites de función reales de `libObj.so` (RTTI /
vtable walking, o un análisis Ghidra que SÍ funcione para esta librería —
pendiente de depurar por qué `scripts/libobj_dec.sh`/`DecompAt.java` falla
aquí cuando sí funciona para `av-cam.bin`) antes de poder atribuir con
confianza el manejador de `0x98f974` a una clase concreta. Sin eso, P3 sigue
NO_VERIFICADO tal como lo dejó S19-04/05.

## Archivos

- `/tmp/.../send-callsites.txt` (fuera del repo, trabajo de sesión): lista
  completa de 464 direcciones de llamada a `ObjPin::Send` en `libObj.so`,
  reproducible con `llvm-objdump -d --triple=thumbv7-linux-gnueabi libObj.so`
  y grep sobre `ObjPin4SendEjPNS_6ObjMsgE@plt`.

SilentShutter no se declara funcional.
