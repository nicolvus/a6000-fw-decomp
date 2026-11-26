# eye-af-nativo — ¿tiene la A6000 Eye AF nativo y por qué solo actúa al pulsar? (26-11-2026)

Fecha: 26-11-2026. Estado: **verificado en estático; sin probar en cámara**. Fuentes: `av-cam.bin`
fw3.21, `av-cam.bin` de la A6300 fw2.01, `libObj.so`/`libScalarDaemon.so` fw3.21 y `orb-server`
fw3.21. Evidencia: [`analysis/eyeaf/`](../../analysis/eyeaf) (`avcam_eye_native.md`,
`a6300_eyeaf_diff.md`, `libobj_afpoint.md`, `rc_touchaf.md`).

Etiquetas: **VERIFICADO** · **INFERENCIA** · **NO_VERIFICADO**.

## 1. Respuesta corta

La A6000 **sí tiene detección de ojos nativa** y **sí convierte el ojo en área de AF**, pero solo
dentro del **manejador de respuesta de una petición de AF**: al soltar el disparador cesan las
peticiones y el estado de ojos caduca por un temporizador de un disparo. Eso explica exactamente lo
que se observa en la cámara: Eye AF mientras se mantiene pulsado, nada al soltar.

Lo que la A6000 **no** tiene es el estado de AF continuo de la A6300 (`CPafStateEyeFocus`), que es
quien vuelve a lanzar la conversión de ojos sin petición externa.

## 2. Cadena verificada (A6000 fw3.21)

```
IDT (servicio de detección)   ◄── idt_edt_start (opcode 8)   0x43a303f8
Camera::FC::Drv::ProcessEdt::StartEdt   0x43a0a47c  (FC/Drv/fc_drv_edt.cpp, «EyeDetection»)
  ▲ único llamador: selección de objetivo AF 0x43a06428
resultado FC (bloque)  +0x56/+0x58 ojo 1, +0x5a/+0x5c ojo 2, +0x5f/+0x60 válidos
[CAMERA_MAIN_FC] 0x437b6ea4  →  ctx+0xde/0xdf (válidos), ctx+0xe0..0xe7 (coordenadas), ctx+0xe8 (nº)
0x437b7598 → 0x437b7200  convierte los ojos en los 8 registros de área (ctx+8 + (i-1)*0x14)
0x437b74a4  arma temporizador OSAL de un disparo: período = u16[cfg+6] × 1000 ms  (caducidad)
```

| Hecho | Evidencia | Estado |
|---|---|---|
| Existe motor de detección de ojos en la cámara | cadena `EyeDetection` `0x43cf7022`, `FC/Drv/fc_drv_edt.cpp` `0x43cf6fd9`, `idt_edt_start`/`idt_edt_get_result` | VERIFICADO |
| El resultado trae los dos ojos con validez propia | `0x437b6fca` lee `+0x5f`; `0x437b6fee` lee `+0x60`; coordenadas en `+0x56/+0x58` y `+0x5a/+0x5c` | VERIFICADO |
| Se copian al contexto de FC | `0x437b6fce` `86f8de10` (`strb.w r1,[r6,#0xde]`), `0x437b6ff2` `86f8df10`, `0x437b6fdc` `a6f8e010` | VERIFICADO |
| El consumidor calcula el área de AF con esos ojos | `0x437b7200` usa `ctx+0xde..0xe7`; si el flag por ojo es 0 registra «Eye data is invalid, but lc flag is true.» | VERIFICADO |
| **Entrada única**: solo se ejecuta al responder a una petición de AF | cadena `0x437b7ea0` (`ReplyForTouchShutter`) ← thunk `0x43aef72e` ← `0x437b668c`; `0x437b7598` tiene un único llamador (`0x43aef9ca`) | VERIFICADO |
| El estado de ojos caduca solo | `0x437b74a4` → temporizador OSAL de un disparo, período `u16[cfg+6] × 1000 ms` | VERIFICADO |
| Quién emite las peticiones de AF (cadencia) | fuera de `av-cam.bin`: el llamador de `0x437b6670` no está en la imagen | NO_VERIFICADO |
| La A6300 añade el seguimiento continuo | `CPafStateEyeFocus` (estado 9) presente en la A6300 y **ausente** en la A6000; `CPafStateEyeStart` y el detector están en las dos | VERIFICADO |
| **`EYE_START_AF` no es Eye AF** | es *Eye-Start AF* (sensor del visor, `[EyeSens] EYE_DET_PORT`); existe igual en la A6300 | VERIFICADO |

**Corrección a `g83`** (`docs/gui/g83-barrido-objetivos-restantes.md`, filas de Eye AF): la fila
«Eye AF en tiempo real … el “tiempo real” necesita detector en `av-cam` (no localizado)» es
incorrecta. El detector **está**: es `Camera::FC::Drv::ProcessEdt` con `idt_edt_*`, y su resultado
llega al área de AF. Lo que falta no es el detector, es el **disparador continuo**. Además
`PARAMID_CAMSETTING_EYE_START_AF` (0x5007 en la tabla de `libScalarDaemon`; la A6300 lee 0x8008
en la suya) es *Eye-Start AF*, no Eye AF.

## 3. Cómo completarlo (dos vías, ninguna aplicada)

| Vía | Qué hace | Estado |
|---|---|---|
| **A. Mantener peticiones de AF** | el eye→área se recalcula en cada petición: AF-C (o S1 mantenido) debería dar seguimiento continuo sin tocar nada | implementable con un ajuste, pero la **cadencia de peticiones no está verificada** (fuera de `av-cam`) |
| **B. Enganchar el camino por VD** | llamar a `0x437b7598` una vez por cuadro desde el copiador de áreas (`0x437b7fe4`, invocado en `0x4378f6a6` dentro de `Imaging::VD_Drive`) | diseño listo; requiere parche de código en RAM (BIONZ), con guardián y reversión, como `camera_silent.py` |
| C. Usar la orden nativa de punto de AF | `setTouchAFPosition` → `MID 0x8f` → `MID 0x3a4a` (`PARAM 0x1005` = `(x·100)<<16 | (y·100)`); el AF lo hace la cámara | VERIFICADO el canal; ya implementado en `tools/eye-af/` (lado PC) y en la app de cámara |

La vía **A** es la que hay que probar primero: es gratis y, si la cadencia de AF-C es la esperada,
la cámara ya hace Eye AF continuo sin parche. La vía **B** es la que lo garantiza aunque la cadencia
no baste.

## 4. Implementación entregada en este carril

- `tools/eye-af/camera/` — app de la cámara (`ar.eyeaf`) que lee los ojos **del propio detector**
  (`CameraEx`/`FaceInfo.leftEye|rightEye`), decide con el mismo criterio que el bucle del PC
  (banda muerta, límite de Hz, salto de sujeto, cancelación) y manda el punto de AF con el mensaje
  nativo. Compila, se firma (`out/EyeAf.apk`, 16,7 KB) y su núcleo pasa 32 comprobaciones sin
  Android. **No se ha instalado.**
- `tools/eye-af/` (lado PC) — bucle verificado que usa la orden nativa de AF de la cámara.
- `tests/test_eye_af_native_evidence.py` — 6 pruebas que fijan con bytes las afirmaciones de este
  informe (cadenas, instrucciones y el diferencial A6000/A6300).
- `tests/test_eye_af_camera_core.py` — compila el núcleo Java sin `android.jar` y ejecuta sus
  autopruebas.

## Límites

- Nada probado en cámara. La cadencia real de peticiones de AF en AF-C es **NO_VERIFICADO** (vive
  fuera de `av-cam.bin`); sin ella no se puede afirmar que la vía A dé seguimiento continuo.
- El análisis es de **fw3.21**; la cámara está en **3.93**. Las direcciones de `av-cam` pueden haber
  cambiado; las cadenas y el diferencial con la A6300 son la parte estable.
- La app de cámara usa `Camera.Face.leftEye/rightEye`: que el firmware de la A6000 los rellene es
  **NO_VERIFICADO** (el campo existe y el detector calcula ojos; el respaldo es el tercio superior
  de la cara, marcado como `shortcut`).
- El canal para que una app mande la orden de punto de AF está verificado **solo** por la API
  remota (HTTP). El socket/cola interna (`WebApiIntMsg` de 0x620 B, MID `0x8f`) no está demostrado
  desde un proceso ajeno: por eso la app registra en el log por defecto y el socket se pasa por
  extra.
- La vía B no se ha aplicado ni emulado: escribir código en RAM de BIONZ no tiene recuperación
  probada (regla del proyecto) y exige autorización expresa.

## 5. Prueba mínima para cerrar

1. Cámara en **AF-C + detección de caras**, objetivo a una cara a 1–2 m, sin pulsar nada: observar
   si el marco de AF se posa en un ojo y lo sigue. (Vía A.)
2. Repetir en AF-S y con el disparador a medio pulsar: si solo aparece entonces, queda confirmado
   que la cadencia de peticiones es la que manda y hace falta la vía B.
3. Registrar con vídeo del panel y la hora; sin escrituras.
