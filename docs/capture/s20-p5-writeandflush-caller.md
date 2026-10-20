# S20 — P5: nuevo llamador real de `MprFileIf::WriteAndFlush`, alcanzado solo indirectamente

Primera tarea de la línea P5 (cadena MPR/DCF/reproducción) en sesión 20.
Punto de partida: `s19-dcf-playback-completion.md` (S19-08) ya había
verificado por separado `FeaIf::WriteStill`, `MprFileIfCore::WriteAndFlush`
y las APIs DCF de pre-registro, sin arista estática entre ellas. Alcance:
`libmpr.so`, `llvm-objdump` directo. Sin Codex, sin subagentes.

## Confirmación (sin cambios): `FeaIf::WriteStill` solo encola

Desensamblado completo de `FeaIf::WriteStill` (`0x44f784`,
`_ZN5FeaIf10WriteStillEPN5MprIf15WriteStillParamEPN3MPR9StillInfoEm`):
copia el descriptor `StillInfo` a una estructura de pila y termina
llamando un método virtual (`vtable+0x20` de un objeto interno) para
encolar la petición — **confirma, sin contradecir**, el hallazgo ya
registrado en `s19-fea-encodestill-completion.md`: FEA acepta y encola,
no espera ni certifica finalización en el mismo retorno.

## Hallazgo nuevo: llamador real de `WriteAndFlush`, alcanzado solo indirectamente

Se localizaron 3 sitios de llamada reales a `WriteAndFlush` en
`libmpr.so` (`MprFileIf::WriteAndFlush@plt`, usado dos veces, y
`Fsys_WriteAndFlush@plt`, una vez). Uno de ellos (`0x13df32`) cae en una
región de `.text` **sin símbolo dinámico exportado que la cubra**
(el símbolo exportado más próximo anterior está muy lejos; mismo problema
de atribución ya documentado para `libObj.so` en P3/P4). Se desensambló
directamente el bloque que lo contiene:

```asm
13df20: push {r4,r5,r7,lr}
        *DAT_estado = 0x11          ; marca de estado antes de escribir
        *DAT_estado2 = 0x1010       ; segunda marca
13df32: blx MprFileIf::WriteAndFlush
        bl 0x13de98                 ; post-procesado (no decompilado en detalle)
        *DAT_estado2 = 0
        pop {r4,r5,r7,lr}
        b.w 0x13dbb0                ; salto a manejador de limpieza compartido
```

**VERIFICADO**: existe una función real, no exportada, que envuelve
`WriteAndFlush` con marcas de estado de diagnóstico (`0x11`→`0x1010`→`0`) y
salta a un manejador de limpieza compartido (`0x13dbb0`, probablemente
reutilizado por varias rutas hermanas, como el patrón ya visto en
`StillConverter`). **VERIFICADO**: esta función **no tiene ningún llamador
directo (`bl`) localizable** en todo `libmpr.so` — se alcanza solo de
forma indirecta (puntero a función/callback), consistente con el patrón
de despacho asíncrono ya documentado para `EncodeStill`/`WriteStill`.

## Lo que esto NO cierra

No se identificó quién **registra** esta función como callback (análogo
al bloqueo ya cerrado parcialmente para `CBID_ENCODE_STILL` en P4, pero
aquí sin tabla de registro localizada todavía). No se decompiló
`0x13de98` (post-procesado tras el `WriteAndFlush`) ni `0x13dbb0`
(manejador de limpieza compartido) — candidatos directos para la próxima
tarea. No se estableció la arista hacia el pre-registro/lookup DCF
(`0x71eafc`/`0x71eb70`) ni hacia las APIs de reproducción.

## Clasificación

- **VERIFICADO**: tercer llamador real de `WriteAndFlush` localizado,
  previamente no registrado en ningún documento anterior.
- **VERIFICADO**: ese llamador se alcanza solo indirectamente (sin `bl`
  directo en todo el binario) — mismo patrón de despacho asíncrono que
  `EncodeStill`.
- **NO_VERIFICADO**: identidad de la función/clase real (sin símbolo
  exportado cercano fiable); contenido de `0x13de98`/`0x13dbb0`; mecanismo
  de registro de este callback; arista hacia DCF/reproducción.

## Siguiente paso concreto

Decompilar `0x13de98` y `0x13dbb0` (el post-procesado y el manejador de
limpieza compartido) — son los candidatos más directos para encontrar la
arista hacia el registro DCF, continuando la misma técnica (`llvm-objdump`
directo, sin depender de símbolos exportados).

SilentShutter no se declara funcional.
