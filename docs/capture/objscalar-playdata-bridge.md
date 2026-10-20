# ObjScalar como puente PlayData → ObjStillRecorder — sesión 14

Alcance: análisis estático `libObj.so` fw 3.21. ELF (Ghidra = ELF + 0x10000). Decompilados: `analysis/ghidra/libobj-recordstillimagecmd.json`, `libobj-scalar-makeplaydata-3fed34.json`, `libobj-recorder-1027.json`.

## Veredicto

**No demostrado como puente de captura.** ObjScalar sí contiene un constructor de `PlayData` (`0x2001/0x1003`) compatible con el contrato del recorder a partir de **handles DMM que aporta el cliente**, pero el mensaje que emite (`0x2001/0x1027`) lo trata el recorder como **armado + eco al cliente**, no como orden de ejecución. No se encontró un camino que convierta ese PlayData en `0x10000005`/`Execute`. Tampoco se contradice el hallazgo de la sesión 11 (el manejador de `0x1027` no toma bytes de imagen).

## Mapa de la conexión

```
ScalarDaemon::recordStillImage ──(petición con handle+dirección/ticket)──► ObjScalar
   ModelScalar [M_SCALAR][TESTCMD] INFO_TICKET_PHYSICAL_ADDR: ticket + memoryType → dirección física
ObjScalar::SequenceRecordStillImageCmd
   SetParameter 0x3e3070  : copia los parámetros 0x2001, 0x2007, 0x205a del ObjMsg entrante (this+0x54/0x58/0x5c) y el mensaje (this+0x60)
   Begin        0x3e2ef8  : MakePlayData (0x3eed34) ─► MakePlayDataMsg (0x3ee314) ─► ObjMsg(0x2001,0x1003)
                            ObjMsg(0x2001,0x1027){0x131f=ticket, 0x1320=PlayData anidado} ─► GetPin(6) vtable+0x10(0x1002)
ObjStillRecorder pin handler 0x919ca0 (sub-mensaje 0x1027)
   this+0x128 = 4 (Paint), prepara estado (0x91efb0), ObjMsg(0x3500,0x1000000f){0x1000000b=0x131f, 0x10000006=0x1320} ─► this+0x18 (cliente)
ObjScalar 0x3e2ddc (respuesta): ObjMsg{0x2001,0x2000} ─► solicitante original; pin 6 estado 1
```

Topologías relacionadas (tabla del TopologyManager): `0x85` Scalar(30) o0 → Effect(9) i0; `0x86` Effect o1 → Scalar i0. **No hay topología Scalar → StillRecorder en YC.** El `ModelScalarStillRecPatch` (`0x65efd1`) es un modelo mínimo (sin lista de topologías propia, 0x1ec B de código).

## Respuestas (1–10)

1. **Canal STM:** la imagen no llega por un canal STM en este camino; la petición del `ScalarDaemon` lleva **par (handle u16, valor/puntero)** de cada buffer (campos `sStack_e0/iStack_dc` y opcional `sStack_d0/iStack_cc` de `0x3eed34`). El «ticket» se traduce a dirección física con `INFO_TICKET_PHYSICAL_ADDR` (cadena de `ModelScalar`). Quién reserva esas unidades: el cliente (NO VERIFICADO el mecanismo exacto).
2. **Formato:** el que implique el `unitType` de la unidad aportada; no se valida en `0x3eed34` más que handle ∈ [1, 0xfffd] y puntero ≠ 0 (VERIFICADO). Formato real NO VERIFICADO.
3. **MakePlayDataMsg recibe** dos descriptores de buffer (construidos por `0x3ee1f8` a partir de handle, valor, tipo y tamaño) y el ObjMsg de metadatos (`this+0x60`); no recibe bytes. Antes `0x3eed34` toma una **asignación compartida** de cada handle con `OBJAVBBCBASECLASS::DmmCh::allocShare(dmm_comp_alc_unit*, u32, u16, u16)` (stub PLT ELF `0xdf49c`; VERIFICADO el nombre) —es decir, ObjScalar incrementa el contador `alloc` de la unidad DMM del cliente y la retiene— y calcula la geometría con `0x3edf20/0x3ed196`.
4. **Claves** `0x1017` (`0x1008`), `0x1031` (`0x1007`), `0x1041` (`0x1009`) como las que usa ObjEffect (ver `analysis/yc-pin-delivery-flow.json`); orden de campos INFERENCIA fuerte.
5. **Pin de entrega:** `GetPin(6)` de la tabla de pines de ObjScalar (`this+0x14` vtable `+0x10`, id `0x1002`). A qué objeto lo conecta el TM: NO VERIFICADO (ninguna fila de la tabla enlaza Scalar con el recorder en YC; Scalar tiene `0x85`/`0x86` con Effect).
6. **`0x1027` vs `0x1003`:** `0x1003` dentro del `0x1002` ⇒ el recorder crea `0x10000005` y ejecuta; `0x1027` ⇒ fija modo 4, devuelve ticket y PlayData al cliente por `this+0x18` y **no** ejecuta (VERIFICADO en `0x919ca0`).
7. **¿Solo arma?** Sí: arma y devuelve; el paso posterior (si existe) no se localizó.
8. **Confirmación de que el recorder recibió el YC:** el cliente recibe `0x3500/0x1000000f`; no hay callback de «YC consumido» (NO VERIFICADO otro).
9. **Operaciones posteriores:** NO VERIFICADO (no hay llamador de `RecordImage` desde ObjScalar; `0x10000005`/`0x3001` solo salen de ModelPbCap/ModelPaint/consola).
10. **Uso fuera de reproducción/edición:** el modo fijado es `Paint` (4), es decir, edición; sin evidencia de uso en disparo.

## Hipótesis (no demostradas)

- HIPÓTESIS: el cliente completa el flujo con una segunda orden (`RecordImage` modo 4) y el recorder pide el YC por `YcPinReqDeliver`; la respuesta la daría Effect reenviando hacia Scalar cuando `0x100a==10` (el parser de Effect reenvía aguas arriba en ese caso).
- HIPÓTESIS: ObjScalar permitiría inyectar un YC externo con handle+dirección, pero requiere que el cliente (ScalarDaemon, proceso externo con API Wi-Fi) esté activo; incompatible con «sin Wi-Fi».

## Conclusión para la arquitectura E2

E2 queda **sin sustento**: ObjScalar no convierte un frame existente en PlayData (solo envuelve handles ajenos), el cliente es un daemon de red y el destino de su pin 6 no está enlazado al recorder. Útil como **precedente**: (a) el recorder admite un YC con handles externos y (b) existe un patrón de retención por `DmmCh::allocShare` (refcount DMM) que evita que el productor libere la unidad.
