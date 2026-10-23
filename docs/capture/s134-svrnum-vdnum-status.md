# S134 — estado de writers de `svr_num` y `VdNum` (pendiente)

## Contexto

Desde S134 (imager_params.md), la función validadora `0x4381106c` del módulo `[CAMERA_MAIN_SYNC]` lee:
- `svr_num` = u8 en `[sl+0x14e]` donde `sl = [estado+8]`
- `VdNum` = u16 en `[sl+0xcc]` donde `sl = [estado+8]`
- `estado` obtenido vía singleton `0x4378f9b4` → global `0x43e99208` (cero en el blob)

Fórmula: `svd_esperado = (svd == 9 ? 1 : shut) * svr_num − 1` o `= (svd == 9 ? 1 : shut) / VdNum − 1`

## Hallazgos en la función validadora `0x4381106c`

Desensamblado clave (verificado contra bytes):

```
0x438110ae: bl    #0x4378f9b4        ; obtiene puntero de estado en r0
0x438110b4: ldr   r3, [r0, #0x24]    ; lee [estado+0x24] → sub-estructura en r3
0x438110b6: mov   r7, r0             ; r7 = estado
0x438110b8: ldm   r3, {r0-r3}        ; carga 4 palabras desde sub-estructura
0x438110ba: stm.w r6, {r0-r3}        ; almacena en stack (sp+0x18)
0x438110c6: ldr.w sl, [r7, #8]       ; sl = [estado+8] = OTRO puntero a sub-estructura
0x438110ce: ldrh.w sb, [sl, #0xcc]   ; VdNum = [sl+0xcc] (u16)
0x438110e0: ldrb.w r0, [sl, #0x14e]  ; svr_num = [sl+0x14e] (u8)
```

Hay DOS punteros diferentes desde el estado:
1. `[estado+0x24]` → usado para ldm (carga 4 palabras de sub-estructura)
2. `[estado+8]` → usado como sl para leer VdNum y svr_num

Estos pueden ser el mismo puntero o diferentes. No se ha determinado.

## Escritores de `svr_num`/`VdNum`

**NO LOCALIZADOS estáticamente:**

1. **No hay literales de dirección** `0x43e99356` (estado+0x14e relativo) ni `0x43e992d4` (estado+0xcc relativo) en el binario. El valor en `[0x43e99210]` (que sería `[estado+8]`) es 0 en la imagen estática.
2. **No hay BL directo** a `0x4378f9b4` (singleton acceso estado) desde fuera de la propia función.
3. Los campos se escriben en tiempo de ejecución, probablemente durante inicialización de cámara o selección de modo de captura.
4. `[estado+0x24]` y `[estado+8]` son punteros que se rellenan en runtime.

## Escritura indirecta de `[estado+0x24]` y `[estado+8]`

Desde `0x438110b4`: `ldr r3, [r0, #0x24]` lee `[estado+0x24]` y lo usa como puntero para `ldm`.
Desde `0x438110c6`: `ldr.w sl, [r7, #8]` lee `[estado+8]` y lo usa como sl.

No se ha identificado quién escribe `[estado+0x24]` ni quién rellena la sub-estructura con `svr_num`/`VdNum`.

## Impacto en S51

**Ninguno.** S51 sigue A=NO, B=NO, C=NO. `svr_num`/`VdNum` son parámetros de validación del imager, no selectores de mecanismo de obturación.

## Siguiente paso

Requiere trazado dinámico (prueba física P1 autorizada) o REA con `trace_native_values` para seguir el valor de `[estado+8]` y sus writers.

## Archivos relacionados

- `docs/capture/s134-imager-params.md` — hallazgo original de S134
- `docs/capture/s134-imager-params.md` — fórmula aritmética svd_esperado
- `docs/STATE.md` — política REA y restricciones
