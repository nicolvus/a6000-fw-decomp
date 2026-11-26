# FILM-PB-1 / guarda B — qué clase implementa `vtable+0x58` y cuándo devuelve 0

Estático, cámara no accesible, 27-11-2026. **Espacio: VA de ELF de `libmpr.so` 3.21**
(`firmware/extracted/fw321/.../lib/libmpr.so`, sha256 en evidencia); REA = esto + `0x10000`.
Evidencia: `reports/evidence/film-pb-1-sub-guardab-20261127/`.

## 1. Veredicto

**La clase es `AviMMgr` (vtable `0x8E6E58`) y sí implementa `+0x58`=`0x61A8F0`
(`isSupportContent`).** El "par 0x5C(kind)/0x60()" no existe porque el barrido previo se hizo sobre **`libObj.so`** (su `.rel.dyn` son exactamente 81 993 relocs; es el único con
`.data.rel.ro`), DSO que **no menciona `AviMMgr`** (`grep -l AviMMgr *.so` → sólo `libmpr.so`,
`libmprctrl.so`). `libmpr.so` no tiene `.data.rel.ro`: sus 608 vtables con RTTI están en `.rodata`
con `R_ARM_RELATIVE` en `.rel.dyn` (131 091 relocs). Barrido correcto: **una sola** vtable con el
cuarteto `0x58/0x5C/0x60/0xB4`, y **una sola** con `+0x18 = 0x603BE1`.
## 2. Constructor, vtable y RTTI (prueba por construcción)

`AviMMgr::AviMMgr()` = **`0x60AA98`**; `0x64CAA0` (base) escribe `0x8F60A0` (typeinfo `14MMgrBaseThread`);
tamaño del objeto `0x8C8` (`0066b736: movw r0,#0x8c8`).

```
0060aaa0: bl   #0x64caa0       ; ctor base
0060aaa4: ldr  r3,[pc,#0x1c4]  ; [0060ac6c] = 58 6e 8e 00 = 0x008E6E58
0060aab2: str  r3,[r5]         ; <== vptr de AviMMgr  (bytes 2b 60)
0060aab4: bl   #0x5fd7a0       ; ctor de miembro this+0x70C
```
Únicos `bl` al ctor: las 5 factorías `AviMMgrIf::New{Ms,Ssd,Flash,Hdd,Usb}AviMMgr` (`0x66b768`,
`0x66b556`, `0x66b33e`, `0x66b97c`, `0x66b124`). Layout GCC: `[0x8E6E50]=0`, `[0x8E6E54]=0x8E69E4`
(typeinfo) → nombre **`7AviMMgr`**, base `14MMgrBaseThread`; **sin subclases** (ningún typeinfo con
+8 == `0x8E69E4`). `vtable[0]=0x618E0D` (D1) re-escribe el vptr: `[0061909c]=0x008e6e58`; `00618e1c: str r3,[r0]`.

## 3. Clase real de `(*(mediaObj+0x24))` — cadena corregida
`mediaObj` **no** es `[core+0x1EC]` (ése es el `EntryId`/contexto): es `[FeaCore+0xDC0]`, segundo argumento
de la guarda (`0x437C28: ldr.w r1,[r4,#0xdc0]`).

```
0x447F26: bl 0x447810(entryId,[core+0xDC0],&ent)   ; 0x447F38
0x447F42: r5 = ent ; 0x447F48: r4 = [r5] ; 0x447F52: r4 = [r4,#0x58] ; 0x447F5A: blx r4
0x447810: if (![core+0xDC0]) return 0x31000006 ; ent = 0x66D0C8([core+0xDC0])
0x66D0C8: r0 = [r0,#0x24] ; r3 = [r0] ; r3 = [r3,#0x18] ; blx r3     ; "slot 6"
```
`[core+0xDC0]` es un **`AviMMgrIf`** (vtable `0x9067A8`, RTTI **`9AviMMgrIf`**, base `6MMgrIf`:
vtable `0x907C50`, tamaño `0x2C`). Su `+0x24` es el **`AviMMgr` concreto**, escrito por su factoría:
`0x66B73C: ldr.w sb,[r5]` (facade) → `0x66B768: bl 0x60aa98` → **`0x66B770: str.w r6,[sb,#0x24]`**
→ `0x66B774: ldr r0,[r3,#0x24]` (lo relee y lo pasa a `0x60B0C4`). Slot 6 de `AviMMgr`
(`[0x8E6E58+0x18]=0x603BE1`) = **`0x603BE0`: `push{r7,lr}; add r7,sp,#0; pop{r7,pc}`**, no-op que
**no toca r0** ⇒ devuelve `this` ⇒ **`ent` = el `AviMMgr`**. Cierre independiente: el mismo `ent` lo
usa el pre-motor `0x447DA8` (`0x447DBA: ldr.w r3,[r3,#0xb4]`) y `[0x8E6E58+0xB4]=0x608699` →
`0x608698`, que loguea `"MovieReadStart : ER_SEQUENCE"` (`0x8DECD3`) y devuelve `0x31000007`
(`0x6086DC`). Misma vtable.

## 4. Desensamblado de los tres slots
### `+0x58` = `0x61A8F0` — `AviMMgr::isSupportContent` (log `0x8E52B4`)
```
0061a91a: ldr.w r0,[r4,#0x768]           ; duenio de condiciones ; 0x61a922: r1=msg[0], r2=msg[4]
0061a908: r3 = msg[8] (EntryId)
0061a92c: bl #0x3f9c7c                   ; GetContentCondition(owner,cc0,cc1,entryId,&out)
0061a930: cbnz r0 -> 0x61a938 "Can't get condition" -> 0x61aa18 -> 0x61aa6c    RET 1
0061a932: ldrb r3,[r7,#0x1cf] ; cbz -> idem                  ; byte de validez del out
0061a950: bl #0x61a764 (this,0xC4,4,&out) ; err -> "Error [%x]"                RET 1
0061a962: ldr r3,[r7,#0x13c] ; 0061a966: tst r3,#4 ; beq 0x61aa6c   ; sin bit2  RET 1
0061a980: bl #0x677fb0 (ConvEntryIdPreToPost) ; err RET 1 ; 0x61a98a: [r7+0x1c8]!=4 RET 1
0061a9e4: bl #0x6e8430                   ; GetPlayThumbnailInfo(...,sel=0x1F,&info)
0061a9ec: bne 0x61aa5c -> log "GetPlayThumbnailInfo" ; 0061aa68: mov r0,r6(=0)  **RET 0**
0061a9ee: bl #0x1eefdc                   ; TvSystem = *(u32*)0x28F850
0061a9f2: ldr.w r3,[r7,#0x124]           ; f = codigo frameRate del contenido
0061a9f6: cmp r0,#1 ; bne 0x61aa1e
 TvSystem==1 : cmp f,#9 bhi "Unknown frameRate" RET1
               tst (1<<f),#0x2A8 bne 0x61aa3a "Invalid TvSystem" -> 0x61aa46 **RET 0**
               tst (1<<f),#0x154 bne 0x61aa4a "Valid TvSystem"  -> RET 1
               tst (1<<f),#3     bne 0x61aa12 "24p/23.976p"     -> RET 1
 TvSystem!=1 : espejo (0x154 -> 0x61aa3a **RET 0** ; 0x2A8 -> RET 1 ; #3 -> RET 1)
0061aa6c: movs r0,#1                     ; todos los demas caminos: SOPORTADO
```
### `+0x5C` = `0x60945C` — `AviMMgr::GetPlayMovieStatus(unsigned contentType)`
```
00609468: log "GetPlayMovieStatus : contentType[%x]" (0x8DEF1D) ; fichero "avimmgr/AviMMgr.cpp"
00609474: switch 8 / 0x10 / 6 / 0x80 / 0x100 / 0x200 ; otro -> 0x31000001 + log       RET 0
cada rama: [this+8]->vtable+0x144/0x14C/0x154/0x15C/0x164/0x174/0x178/0x188 (estado del motor);
           incoherencia -> log linea 0x26xx (0x8DD9C0)                                RET 0
00609766: r6=0 ; 0060976a: r6=1 ; 0060976c: mov r0,r6   ; 0/1 (0x609766/0x60976A)
```
### `+0x60` = `0x603DBC` — `AviMMgr::GetPlayStillStatus()` (log `0x8E7604`)
```
00603dc4: r0=[this+8] ; blx [vptr+0x150] ; cbz -> 0x31000003 + log 0x26FE              RET 0
00603df6: blx [vptr+0x208] ; 00603dfc: bics r5,r0,#0x40000000 ; beq 0x603e28          RET 1
          si no: log "GetPlayStillStatus : playStillInh[%x]" (0x8DD9D4) -> 00603e2a     RET 0
```

## 5. Condición exacta de rechazo (únicos `return 0` de `isSupportContent`)
1. **`0x61AA68`** — `GetPlayThumbnailInfo` (`0x6E8430`, `mp4Ifo_If.cpp`, selector `0x1F`) devuelve error.
   Antes: condición obtenida, `bl 0x61A764`=0, `out[0]&4 != 0`, `ConvEntryIdPreToPost`=0, `out2[0x1C8]==4`.
2. **`0x61AA46`** — desajuste frameRate/TvSystem, con `f=[info+0x124]` y `TvSystem=*(u32*)0x28F850`:
   `TvSystem==1` y `(1<<f)&0x2A8` (f∈{3,5,7,9}) → **0**; `TvSystem!=1` y `(1<<f)&0x154` (f∈{2,4,6,8}) → **0**.
   `f ∈ {0,1}` (23.976/24p) y `f > 9` **nunca** rechazan.

**Ningún valor de los seis argumentos** (`msg[0..0x14]` = `ContentCondition`(2)+`EntryId`+contexto) produce 0
directamente: el rechazo depende de propiedades del contenido indexado por ese `EntryId` y del TvSystem global.
Corolario: **«Can't get condition» NO es rechazo** (RET 1, corrige el informe del motor §3-i). Para MAH04198
(29,97 p, conforme) lo esperable es «Valid/24p» → 1, así que H-B sólo sería cierta por (1) o por (2).
## 6. Comprobación en la cámara: un paso, y NO_VERIFICADO

Un breakpoint en **`0x447F52`** (`ldr r4,[r4,#0x58]`, `r5 = ent`): comprobar `*(u32*)r5 == 0x8E6E58`
(y `r4 == 0x61A8F1`). Alternativa en `0x61A9EE`: `0x1EEFDC == 1` (NTSC) y `[info+0x124]` en la máscara
`0x154`. **No ejecutado** (cámara sin red/USB/telnet; prohibido tocar hardware). Paso estático ya hecho:
`[0x8E6EB0]=0x61A8F1`, `[0x8E6EB4]=0x60945D`, `[0x8E6EB8]=0x603DBD`, `[0x8E6F0C]=0x608699`, `[0x8E6E58+0x18]=0x603BE1`.
NO_VERIFICADO: (a) mapeo `f`(0..9) → cadencia/sistema reales (exige la tabla de `0x6E8430`/`mp4Ifo_If.cpp`;
sólo consta que `{0,1}` se rotula «24p/23.976p» y las dos máscaras); (b) significado de `TvSystem == 1`
(¿NTSC?) y de `out2[0x1C8] == 4`; (c) identidad en ejecución de `[FeaCore+0xDC0]` —deducida del store de
la factoría `0x66B770`, no observada en RAM— y valores reales de `0x28F850` y `[info+0x124]` para el clip;
(d) que la rama de fallo sea alcanzable con un MP4 conforme: no medido en la cámara.
