# S20 — P4: código real del despachador interno de `StillConverter` para "Receive CBID_ENCODE_STILL"

Continuación directa del bloqueo dejado por `s19-fea-encodestill-completion.md`
(S19-06): "no se halló el `AddCallbackFunc` cuya tabla contenga el ID
candidato ni una arista registro→instancia" para `CBID_ENCODE_STILL`
(`0xc0000004`). Alcance: `libObj.so` (fw321), vía `llvm-objdump` directo
(método ya validado como fiable en esta sesión para esta librería, a
diferencia de la decompilación Ghidra — ver `s20-p3-objcamera-pin-attempt.md`).
Sin Codex, sin subagentes, sin modificar el binario.

## Método

1. Localización de la cadena `" Receive CBID_ENCODE_STILL"` en `libObj.so`
   (offset `0xde4796`).
2. Reutilización de `scripts/thumb_pc_strings.py` sobre todo `.text`
   (`0xe2b70`–`0x1c9558c`) para resolver xrefs PC-relativas — encontró la
   instrucción real que carga esa cadena en `0x91ebe0` (antes solo se sabía
   que la cadena existía, no el código que la usa).
3. Desensamblado dirigido (`llvm-objdump`) alrededor de `0x91eb60`–`0x91ec74`.

## Resultado: localizado y desensamblado el código real (no solo la cadena)

**VERIFICADO**: la cadena `" Receive CBID_ENCODE_STILL"` se usa en un
bloque de despacho real con esta forma:

```asm
91eb60: ldr r3,[pc,#..]@0x91ecb8   ; r3 = 0x40000023 (constante local)
91eb66: cmp r1,r3
91eb6e: beq 91eb78                 ; r1 == 0x40000023 -> otra rama (log distinto)
91eb70: adds r3,#0x59              ; r3 = 0x4000007c
91eb72: cmp r1,r3
91eb74: bne 91ec72                 ; si no coincide, otra rama más
91eb76: b 91ebe0                   ; r1 == 0x4000007c -> rama "Receive CBID_ENCODE_STILL"
```

**INFERENCIA, no verificado numéricamente**: `r1` (el código comparado) es
un **ID interno traducido de StillConverter** (`0x4000007c` en esta rama),
**no** necesariamente el valor crudo `0xc0000004` de `CBID_ENCODE_STILL`
tal como lo usa FEA/`EventSwitcher`. La cadena de log asocia este camino de
código con ese nombre, pero no se demostró la igualdad numérica directa con
`0xc0000004` — esto deja constancia explícita del límite para no repetir el
error ya corregido en C1/P3 (no confundir proximidad/etiqueta con identidad
numérica demostrada).

**VERIFICADO — atribución de clase, con reserva de límites de función**: el
bloque cae en el rango `[0x91395c, 0x921d56)` entre los símbolos exportados
`ObjStillRecorder_UnregisterCommand` (inicio) y `ObjConverter_Create`
(siguiente símbolo, ~58 KB después). `llvm-objdump` etiqueta erróneamente
todo ese rango como `ObjStillRecorder_UnregisterCommand+offset` (mismo
artefacto de atribución por proximidad ya documentado en
`s20-p3-objcamera-pin-attempt.md`) — **no es la función real**. La
atribución a **`StillConverter`** (no a `ObjStillRecorder` directamente) se
apoya en evidencia más fuerte que la mera proximidad: la **densidad de
cadenas `StillConverter.cpp`** (8 referencias en 1.2 KB alrededor de
`0x91eb9a`–`0x91f368`: `ParseStillCnvCmd`, `DecodeJpgCmp`, `FreeCnvMsg`,
`CalcResizeInfo`, `CalcDstJpgImageInfo`, `SetRegionInfo`) y la cadena
`send StillConverter::MSGID_CONVERT_JPG_CMP` a solo `0xd4` bytes de
distancia — consistente con código fuente real de `StillConverter.cpp`
enlazado en este bloque, no con `ObjStillRecorder_UnregisterCommand`.

**VERIFICADO**: la rama de `0x91ebe0` construye y envía un mensaje real:

```asm
91ebe0: (log "Receive CBID_ENCODE_STILL" via MonCtrl::ConPutMessage)
91ebee: ldr r2,[pc,#..]@0x91ecc4        ; categoría de mensaje
91ebea: movw r1,#0x3a48                  ; tipo de ObjMsg = 0x3a48
91ebf4: blx MWF::ObjMsg::ObjMsg(0x3a48,...)     ; construye el mensaje
91ebfc: movs r2,#0xc; movs r3,#0x1
91ec00: blx MWF::Struct::Struct(ptr=r4,0xc,1)   ; envuelve el payload (12 B) en un Struct
91ec0c: blx MWF::ObjMsg::AddParam(msg, 0x103, &struct)  ; param ID = 0x103
91ec56: ldr r0,[r5,#0x4c]               ; r0 = objeto en ctx+0x4c (candidato a Pin)
91ec5c: ldr r3,[r0]; ldr r3,[r3,#0xc]   ; vtable, slot +0xc
91ec60: blx r3                          ; LLAMADA VIRTUAL — mismo patrón en ambas ramas
```

La rama hermana (`0x91eb78`, cuando `r1==0x40000023`) hace **exactamente el
mismo patrón**: construye `ObjMsg(0x3a48,...)`, añade un párametro distinto
(`AddParam` con el mismo helper) y llama **el mismo slot de vtable `+0xc`**
sobre el mismo objeto `*(r5+0x4c)` — confirma que es un **mecanismo de
envío genérico reutilizado por varias ramas internas de StillConverter**,
no específico de `CBID_ENCODE_STILL`.

**INFERENCIA fuerte**: el slot de vtable `+0xc` llamado sobre `*(r5+0x4c)`
es consistente con `MWF::ObjPin::Send(unsigned int, MWF::ObjMsg*)` (la
firma de envío por pin ya usada en todo el proyecto — ver
`s20-p3-objcamera-pin-attempt.md` y hallazgos de sesiones previas), pero
**no se verificó el layout de vtable de esta clase concreta** para
confirmar que el slot `+0xc` es realmente `Send` y no otro método.

## Lo que esto añade sobre S19-06

- **Antes (S19-06)**: solo se sabía que la cadena `"Receive
  CBID_ENCODE_STILL"` existía en `libObj.so`, sin código asociado.
- **Ahora**: se localizó y desensambló el bloque de código real que la usa,
  confirmando que es un despachador interno de StillConverter (clasifica
  por un ID interno traducido, no necesariamente `0xc0000004` crudo) que
  **reenvía** el resultado mediante `ObjMsg(0x3a48)` + `AddParam(0x103)` +
  una llamada virtual de tipo `Send` sobre un pin en `ctx+0x4c`.
- **Sigue NO_VERIFICADO** (sin cambios respecto a S19-06): la igualdad
  numérica entre el ID interno `0x4000007c`/`0x40000023` y el `0xc0000004`
  real de FEA; la identidad exacta de la clase (no solo "StillConverter" por
  cercanía de cadenas); el destino final del pin en `ctx+0x4c` (a qué objeto
  pertenece, a qué otro pin se conecta — sería el siguiente paso para
  avanzar hacia DCF/MPR, P5).

## Clasificación

- **VERIFICADO**: código real localizado y desensamblado para la cadena
  "Receive CBID_ENCODE_STILL"; patrón de envío genérico (`ObjMsg` + `Struct`
  + `AddParam` + llamada virtual `+0xc`) compartido por dos ramas distintas
  del mismo despachador.
- **INFERENCIA**: el bloque pertenece a `StillConverter` (por densidad de
  cadenas `StillConverter.cpp`, no por límites de función recuperados).
- **INFERENCIA fuerte, no verificada**: el slot de vtable `+0xc` es
  `ObjPin::Send`.
- **NO_VERIFICADO**: identidad numérica entre el ID interno comparado
  (`0x4000007c`) y `CBID_ENCODE_STILL` (`0xc0000004`); destino real del pin
  en `ctx+0x4c`.
- **DESCARTADO**: usar el nombre de símbolo `ObjStillRecorder_UnregisterCommand`
  que imprime `llvm-objdump` para este bloque — es un artefacto de
  etiquetado por proximidad (el siguiente símbolo exportado está a ~58 KB),
  no la función real.

## Archivos

- Método reproducible:
  ```sh
  python3 -I scripts/thumb_pc_strings.py libObj.so 0xe2b70 0x1c9558c | grep -i encode_still
  llvm-objdump -d --triple=thumbv7-linux-gnueabi \
    --start-address=0x91eb60 --stop-address=0x91ec74 libObj.so
  llvm-nm -D --defined-only libObj.so | sort
  ```

SilentShutter no se declara funcional.
