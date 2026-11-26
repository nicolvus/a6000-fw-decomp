# Auditoría independiente del paquete **3.97** (`libmpr` del parche C) y del rollback **3.98**

26-11-2026. Auditoría **desde cero**: no se ha reutilizado ningún resultado de los informes previos; se ha vuelto a
desempaquetar el `.dat`, a extraer el `libmpr.so` y a desensamblar/emular la cueva. Nada instalado, cámara sin tocar,
sin `git`, sin `mcp_rea`. Evidencia: [`reports/evidence/auditor-397-20261126/`](evidence/auditor-397-20261126/).

## Resumen (13 líneas)

1. `.dat` 3.97: sha256 **`69447a27…9a5cd9`** — coincide con el esperado; DEND correcto y descifrado == `.fdat`.
2. `firmware.tar` 3.97 = `0f2daccad5…c19fad`; `dev/nflasha15` = 86 169 600 B, `29ff5bee…c76d81`.
3. `/lib/libmpr.so` extraído **por mí** del paquete: **`831142ae…e378e`** — coincide con el esperado.
4. Gancho `0x7126E6` = `28 f2 8b fc` = `bl 0x93B000`; `0x7126EA` = `96 f5 bb f8` (`bl 0x4A8864`), **intacto**.
5. **No cuadra una cosa:** la cueva `0x93B000` **no está en una sección ejecutable: cae en `.rodata`** (`0x7A3E90..0x956750`, flags `A`), no en `.text`. Sí está dentro del primer `PT_LOAD` (`R E`, vaddr==offset), que es lo que la hace ejecutable en tiempo de ejecución. Alineada a 32 B ✔.
6. Sobrescribe 82 B de un hueco de ceros de 173 B (`0x93AFD4..0x93B081`); **0 relocaciones** y **0 literales** apuntan ahí (el único candidato del barrido es un falso positivo dentro de dos instrucciones).
7. Resto del ELF **idéntico**: cabecera, 5 `PT_*` y 25 secciones byte a byte; solo 2 zonas de diff (gancho 4 B + cueva 82 B).
8. Cueva desensamblada y **emulada**: lee `base+0xA36A64` (= `0xA3699C`+`0x14·10`), guarda `+4`, registra el stub `0x93B04F` con `(4,3)` y `(0x21,3)` vía `0x2B1DEC(userID,fn,arg,mediaID)` y llama `0x2B43F0(6,3)`; vuelve a `0x7126EA` con `r4/r5/SP` restaurados.
9. Contrato del llamante `0x712530` respetado: `r0..r3` están muertos tras el gancho y `r6..r8` no se tocan.
10. Observación menor: la cueva empuja 12 B (`push {r4,r5,lr}`) ⇒ las 3 llamadas van con `SP ≡ 4 (mod 8)`, fuera de AAPCS; `push` de 12 B es habitual en este binario (2 127), pero el marco del llamante sí está alineado.
11. `audit_package_nflasha15.py --base-dat <.dat 3.94>` → **`todo_ok: true`, 22/22**, sin flags especiales.
12. Rollback 3.98 (`b0979e03…d5c3b4`): versión 3.98, `firmware.tar` = `92dfeb6a…` **byte a byte el de la base 3.94**, `libmpr` = `9a74a3bb…` (fábrica). Correcto.
13. Conclusión: el paquete es **el esperado byte a byte**; lo único que no cumple el criterio pedido es que la cueva vive en `.rodata` (datos), no en una sección de código.

## Las 6 comprobaciones

| # | Comprobación | Resultado |
|---|---|---|
| 1 | sha256 `.dat` + desempaquetado + sha256 `/lib/libmpr.so` | **OK** · `69447a27…` / `831142ae…` |
| 2 | Gancho `0x7126E6` = `28 f2 8b fc` → `0x93B000`, y `0x7126EA` intacto | **OK** |
| 3 | Cueva dentro de sección **ejecutable** y alineada | **FALLA (sección)** · está en `.rodata`; alineada a 32 B ✔; el primer `PT_LOAD` sí es `R E` |
| 4 | Sin relocaciones a la cueva; sin literales que se rompan; no en `.data`/`.rodata` | **Relocs: OK (0)** · **Literales: OK (0 reales)** · **`.data`: OK** · **`.rodata`: FALLA (está dentro)** |
| 5 | Resto del ELF (cabecera, `PT_*`, secciones) idéntico a fábrica | **OK** (solo 2 zonas de diff) |
| 6 | Semántica de la cueva y contrato de registros del llamante | **OK** (desensamblado + emulación) |

---

## 1. Contenedor y `libmpr.so`

```
$ sha256sum build/cfw_fbm31_pkg397/pkg-3.97/package-3.97/firmware_packed.dat
69447a27c1b75efd15a83f90c373a91b2246c7c0ab64fc562df7d9e3839a5cd9  …/firmware_packed.dat

$ python3 build/aud397/work/extrae.py            # descifrado propio + fwtool (tercero) + tar + TPZL + debugfs
dat_sha256 69447a27c1b75efd15a83f90c373a91b2246c7c0ab64fc562df7d9e3839a5cd9 bytes 172662936
chunks [['DATV',16,4],['PROV',28,4],['UDID',40,92],['FDAT',140,172662784],['DEND',172662932,4]] trailing 0
dend_stored 3d1f5631 dend_computed 3d1f5631 ok True
decrypt: blocks 168616 bad_sum [] bad_flag [] bad_len [] pad_not_ff False first_mismatch_vs_fdat None
         plain_size 171987456 sha256(plano) bc5078301bf4139f74e1da6129a4c83c109ea7ff40f82b681260457c3dc1ea73
fdat_header {"magic":"UDTRFIRM","checksum_stored":"b9dbe639","checksum_computed":"b9dbe639",
             "version":"3.97","model":1090715701,"region":0,"firmware_offset":143872,
             "firmware_size":171843584,"num_filesystems":2}
fwtool_out ['config.yaml','firmware.fdat','firmware.tar','firmware.tar_unpacked','updater.img','updater.img_unpacked']
tar_sha256 0f2daccad51c6c9f76c8ad78be82c5aca79716fc1b5f19c9dfab8e35f5c19fad bytes 171843584
tar_miembros 104 resto_tar 1024
nflasha15_sha256 29ff5bee31605f5b59031740bf369a9de3df3ef1e6ff07c859ad8fc39dc76d81 bytes 86169600
tpzl_bloques 2373 bloque_size 65536 data_offset 19456
ext2_sha256 9cf86d942e4eecdd410d57b3a154667422f10f1031f5f66c4676ce4be86bd797 bytes 155516928
```

```
$ debugfs -R "dump /lib/libmpr.so build/aud397/work/libmpr-397.so" build/aud397/work/usr397.ext2
$ sha256sum build/aud397/work/libmpr-397.so
831142ae9a0c1598c179c684200d86d57a1209f4ab0349e357d7e25b016e378e  build/aud397/work/libmpr-397.so
$ debugfs -R "dump /lib/libmpr.so build/aud397/work/libmpr-321.so" build/aud397/work/usr321.ext2
$ sha256sum build/aud397/work/libmpr-321.so
9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30  build/aud397/work/libmpr-321.so
```

El de fábrica se sacó de la `nflasha15` **de fábrica** (`firmware/extracted/fw321/…`, `e3530a89…`), no de la 3.94.
El `libmpr.so` de la base 3.94 es el mismo binario (`9a74a3bb…`, `cmp` sin diferencias) y el del paquete es **byte a
byte** el de `build/cfw_fbm_sector31_c/libmpr.so` (`cmp` sin diferencias).

También comprobado por mi cuenta contra la base 3.94 (`14-compara-397-394.log`): en el `firmware.tar` cambian
**solo** `0700_part_image/dev/nflasha15` y `0701_part_image_sum/part_image.sum` (104 miembros, nada añadido ni
quitado); en el ext2 cambia **solo** `lib/libmpr.so` de 715 ficheros.

## 2. Gancho

```
$ readelf -h libmpr-397.so
  Class: ELF32   Data: 2's complement, little endian   Type: DYN   Machine: ARM   Number of program headers: 5
$ readelf -lW libmpr-397.so
  LOAD  0x000000 0x00000000 0x00000000 0x9bb1c8 0x9bb1c8 R E 0x8000     ← cubre 0x93B000
  LOAD  0x9bb1c8 0x009c31c8 0x009c31c8 0x1c640  0x11893c RW  0x8000
0x007126E6 fábrica: a2 f7 9b f0  96 f5 bb f8   →  bl 0x2B4820 ; bl 0x4A8864
0x007126E6 nuevo  : 28 f2 8b fc  96 f5 bb f8   →  bl 0x93B000 ; bl 0x4A8864
0x7126EA intacto: True
```

`bl 0x2B4820` es la **única** llamada `bl` directa a `0x2B4820` de todo `.text`, así que el efecto original (`FBM::Init`) solo se
podía conservar dentro de la cueva, y ahí está (primera instrucción tras el `push`).

## 3. Cueva: dónde está (lo que no cuadra)

```
$ readelf -SW libmpr-397.so
[10] .text    PROGBITS 00120228 120228 683c5c AX     → 0x120228..0x7A3E84
[12] .rodata  PROGBITS 007a3e90 7a3e90 1b28c0 A      → 0x7A3E90..0x956750   ← 0x93B000 cae aquí
[13] .ARM.extab …  0x956750  [14] .ARM.exidx … 0x97e1c0
```

- **Sección ejecutable: NO.** `0x93B000` está en `.rodata` (flags `0x2`, solo `ALLOC`). No hay ninguna sección con
  `X` que lo cubra: `.text` termina en `0x7A3E84`.
- **Segmento ejecutable: SÍ.** El primero de los dos `PT_LOAD` (`p_offset=0`, `p_vaddr=0`, `p_filesz=0x9BB1C8`, flags `R E`) lo
  cubre, así que la página se mapea `R+X` y el `bl` funciona. La comprobación que hace el constructor
  (`parche_fbm31_c.py`, línea 343: «la cueva tiene que ser R+X y VA==offset») es a nivel de **segmento**, no de
  sección; por eso el parche pasó su propio filtro.
- **Alineada: SÍ** a 4/8/16/32 (0x93B000 % 32 == 0).
- **Qué pisa:** un hueco de ceros de 173 B en `.rodata`, `0x93AFD4..0x93B081`; la cueva ocupa `0x93B000..0x93B051`
  (82 B) y deja 44 B antes y 47 B después sin tocar. En `0x93B081` empieza el dato `0x0000186A`.
- **Riesgo residual:** si algún código leyera ese hueco como datos (no hay ninguna evidencia de que lo haga: ver §4),
  ahora leería código. No es código ejecutándose desde `.text`, es código ejecutándose desde `.rodata`.

```
$ python3 - <<'EOF'   # volcado de .rodata (salida en 03-rodata-vecindad.log)
0x0093B000 fábrica: 00 00 00 … (0x60 B a cero)
0x0093B000 nuevo  : 30 b5 79 f5 0d f4 7c 46 24 f0 03 04 …
hueco de ceros en fábrica: 0x0093AFD4..0x0093B081 (173 bytes)
```

## 4. Relocaciones y literales

```
$ python3 build/aud397/work/elf_analisis.py
nuevo   .rel.dyn   entradas 131091  cerca_gancho_o_cueva []
nuevo   .rel.plt   entradas 930     cerca_gancho_o_cueva []
nuevo total_relocs 132021          (fábrica: idéntico)
== Simbolos .dynsym en 0x930000..0x940000 ==   (ninguno)

$ python3 - <<'EOF'   # barrido de punteros u32 (salida en 13-hueco-referencias.log)
punteros de 4 B que caen en el hueco 0x93AFD4..0x93B081: 1
    ('0x93b014', '0x495390')
```

Ese único acierto es **falso positivo**: en `0x495390` los bytes `14 b0 93 00` son parte de dos instrucciones
(`str.w fp,[r7,#0x14]` = `c7 f8 14 b0` y `lsls r3,r2,#2` = `93 00`), no un literal (`04-contexto-literal.log`).
**Ninguna** relocación (`r_offset`) cae en la cueva ni en el gancho, y **ningún** puntero de 32 bits apunta al hueco.

## 5. Resto del ELF idéntico

```
$ diff de bytes libmpr-397 vs libmpr-321 (mismo tamaño, 10 321 204 B)
num_rangos 7   total_bytes_distintos 81
off 0x007126E6..0x007126EA len 4
off 0x0093B000..0x0093B052 len 44 / 11 / 17 / 1 / 1 / 3   (82 B de cueva, 77 con valor nuevo; 4 del gancho ⇒ 81 en total)
```

```
$ python3 build/aud397/work/elf_analisis.py
e_type/e_machine/e_entry/e_phoff/e_shoff/e_flags/e_shnum … iguales -> True
Program headers: los 5 iguales (tupla a tupla) -> True ; num_ph 5 5
Secciones: num_sh 25 25 metadatos_iguales True
```

Comprobado con pyelftools (`02-elf.log`): `.init/.plt/.text/.fini` son las únicas secciones con `SHF_EXECINSTR` y
ninguna contiene `0x93B000`. Cabecera ELF, tabla de `PT_*` (está en `0x34`) y tabla de secciones (en `0x9D794C`) caen fuera de las dos zonas de
diff, así que son **byte a byte** idénticas, no solo «equivalentes».

## 6. Semántica de la cueva (desensamblado real + emulación)

```
$ python3 build/aud397/work/elf_analisis.py   (capstone, Thumb)
0x0093B000  push  {r4, r5, lr}
0x0093B002  bl    #0x2b4820                  ; el efecto original del gancho
0x0093B006  mov   r4, pc
0x0093B008  bic   r4, r4, #3
0x0093B00C  movw  r1, #0xba5c
0x0093B010  movt  r1, #0xf
0x0093B014  add   r4, r1                     ; r4 = base + 0xA36A64 = &0xA3699C[10]
0x0093B016  ldr   r0, [r4, #4]               ; campo +4 de la entrada 10
0x0093B018  cbnz  r0, #0x93b048              ; guarda: si ya hay handle, no registra
0x0093B01A  movw  r1, #0xba16 / movt r1, #0xf
0x0093B022  sub.w r5, r4, r1
0x0093B026  adds  r5, #1                     ; r5 = base + 0x93B04F (stub, Thumb)
0x0093B028  movs  r0, #4   ; userID
0x0093B02A  mov   r1, r5   ; fn
0x0093B02C  movs  r2, #0   ; arg
0x0093B02E  movs  r3, #3   ; mediaID
0x0093B030  bl    #0x2b1dec
0x0093B034  movs  r0, #0x21 / r1=r5 / r2=0 / r3=3
0x0093B03C  bl    #0x2b1dec
0x0093B040  movs  r0, #6 / movs r1, #3
0x0093B044  bl    #0x2b43f0
0x0093B048  pop   {r4, r5, pc}               ; vuelve a 0x7126EA
0x0093B04E  movs  r0, #0 ; bx lr             ; stub: devuelve 0
```

- La tabla se calcula **relativa a PC** (`(PC&~3)+0xFBA5C`), no con una constante absoluta: con `libmpr` cargado en
  `base`, `r4 = base+0xA36A64`. Correcto para una `.so` que no se carga en 0.
- Firma de `0x2B1DEC` verificada en su prólogo: `r4=r0, r6=r1, r5=r2, r8=r3`; compara `r3` con `[entrada+4]` y
  escribe `r6→[entrada+0x10]`, `r5→[entrada+0x14]` ⇒ **(userID r0, fn r1, arg r2, mediaID r3)**.
- `0x2B43F0` usa `(r0,r1)` como `(OM, mediaID)` en su prólogo ⇒ `(6,3)`.

Emulación con Unicorn del binario empaquetado (`09…/10-*.log`):

```
== guarda [0xA36A68] = 0 ==                 == guarda [0xA36A68] = 1 ==
2B4820 r0=0xAAAAAAAA SP=0x7F7FF4            2B4820 r0=0xAAAAAAAA SP=0x7F7FF4
2B1DEC r0=0x4  r1=0x93B04F r2=0 r3=3        (nada más: sale por cbnz)
2B1DEC r0=0x21 r1=0x93B04F r2=0 r3=3
2B43F0 r0=0x6  r1=0x3
PC tras el retorno 0x7126EA · SP 0x7F8000 · r4/r5 restaurados
```

**Contrato del llamante (`07-llamante-712530.log`):** `0x712530` empuja `{r4,r5,r6,r7,r8,lr}` + `sub sp,#0x10`
(marco de 8 en 8). Tras `0x7126E6` la instrucción siguiente es `bl 0x4A8864`, cuyo prólogo carga `r1` y `r0` de
literales **antes de leerlos** ⇒ `r0..r3` están muertos en `0x7126EA`. `r6/r7/r8` no los toca la cueva y `r4/r5` los
salva/restaura. `lr` lo salva el prólogo de `0x712530`.

**Observación (no bloqueante):** `push {r4,r5,lr}` son 12 B ⇒ las tres llamadas se hacen con `SP ≡ 4 (mod 8)`, fuera
de AAPCS (el llamante sí tiene marco alineado: 24+16 B). El patrón exacto `0xB530` solo aparece en la cueva, pero
`push` de 3 registros (12 B) es habitual en este `.text` (2 127 casos), así que la plataforma lo tolera. En los
primeros 0x300 B de `0x2B4820`, `0x2B1DEC` y `0x2B43F0` no hay `ldrd/strd/vldr/vstr`: sin evidencia de fallo, pero
es una desviación real.

## 7. Auditoría con el script del repo

```
$ python3 scripts/gui/audit_package_nflasha15.py \
    build/cfw_fbm31_pkg397/pkg-3.97/package-3.97/firmware_packed.dat \
    build/cfw_fbm31_pkg397/files \
    --base-dat build/cfw_avcam_limpio/firmware_packed-3.94.dat
"dat_sha256": "69447a27…", "version": "3.97", "base_version": "3.94", "todo_ok": true
22/22 comprobaciones true (contenedor ×7, tar ×3, nflasha15 ×8, ext2 ×4)
"tar_cambios_vs_base": ["0700_part_image/dev/nflasha15","0701_part_image_sum/part_image.sum"]
"bloques_recompuestos": 329 · disposición: 2373 bloques, 0 no alineados, contiguos, max_sectores 129, 0 violaciones LDEC
```

- **Flags especiales: ninguno.** Solo `--base-dat` (sin `--darwin-v3`, sin `--sin-wbi`, sin `--bionz-g22`).
- El `.dat` 3.94 usado (`build/cfw_avcam_limpio/firmware_packed-3.94.dat`, `2a6fd62f…4c1c`) es **el mismo fichero**
  (`cmp`) que el que usaron ellos (`build/cfw_avcam_limpio/pkg-3.94/package-3.94/firmware_packed.dat`).
- `e2fsck -fn` da avisos de contadores de libres/inodos, **heredados de la base 3.94** (idénticos en
  `usr394-aud.ext2`); la imagen de fábrica 3.21 sí está limpia. No los introduce el 3.97.

## 8. Rollback 3.98

```
$ sha256sum build/cfw_fbm31_pkg397/pkg-3.98-rollback/package-3.98/firmware_packed.dat
b0979e03c5cf0fead6f0acf3f4ce15fea217a0f21358b49eb78968cba1d5c3b4  …/firmware_packed.dat

$ python3 build/aud397/work/rollback398.py
3.98 dat_sha256 b0979e03… — bytes 172661912 · dend 27499e76 == 27499e76 True
descifrado: bad_sum [] bad_flag [] bad_len [] mismatch_vs_fdat None
cabecera 3.98: 3.98 0x41030035 region 0 mode U crc True
tar_sha256 92dfeb6adcf1ee247144ab7b7b5db2c231a193b98b1ff87fa3f7c928b3451e0d  (== tar de la base 3.94, `cmp` sí)
miembros 3.98 104 / 3.94 104 · miembros distintos: []          ← sin parche
nflasha15 3.98 4dceb91c…f4c4 == nflasha15 3.94 4dceb91c…f4c4
bloques 2373 · bloque 0 == Sony
/lib/libmpr.so de la 3.98: 9a74a3bb…4c30 (fábrica)
```

Versión **3.98 > 3.97**; contenido = base 3.94 **sin** el parche, tal como se pedía.

## 9. Veredicto

El contenedor, el `nflasha15`, el `libmpr.so` y el rollback son **exactamente** los esperados (un solo fichero
cambia en `/usr`, 2 miembros en el tar, 0 relocaciones y 0 literales hacia la cueva, resto del ELF idéntico), y la
cueva hace lo que dice el diseño. **Lo único que no cumple es el criterio «la cueva está dentro de una sección
ejecutable»: está en `.rodata`** (0x93B000..0x93B051), no en `.text`; se ejecuta porque el `PT_LOAD` que la contiene
es `R E`, pero es un hueco de datos de solo lectura, no código. Y el `push {r4,r5,lr}` deja `SP` desalineado 4 B en
las tres llamadas.

## 10. Evidencia

`reports/evidence/auditor-397-20261126/`: `01-extrae.log`, `02-elf.log`, `03-rodata-vecindad.log`,
`04-contexto-literal.log`, `05-desasm-cueva.log`, `06-firmas-llamadas.log`, `07-llamante-712530.log`,
`08-pila-y-2b4820.log`, `09-emulacion-cueva.log`, `10-emulacion-retorno.log`, `11-audit-397-base394.json`,
`12-rollback-398.log`, `13-hueco-referencias.log`, `14-compara-397-394.log`, `15-fsck.log`, `16-shas-libmpr.txt`
y los scripts usados (`extrae.py`, `elf_analisis.py`, `emu_cueva.py`, `rollback398.py`, `compara_397_394.py`).
