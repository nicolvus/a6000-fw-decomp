# FILM-PB-1 — El fallo de reproducción es global: la cadencia queda descartada

Fecha: 26-11-2026. Sustituye como marco al título «diagnóstico cerrado» de
[film-pb-1-diagnostico-cerrado-20261127.md](film-pb-1-diagnostico-cerrado-20261127.md) §4 y
corrige la vía V1 de [film-pb-1-causa-sistema-tv-20261127.md](film-pb-1-causa-sistema-tv-20261127.md).

Cámara **no accesible** en esta sesión (sin red ni USB). Todo el contenido es estático:
desensamblado local con Capstone sobre el `/usr` de fábrica 3.21.

## 1. Hecho de control que reencuadra el problema

Observaciones del usuario con la cámara en mano, en este orden:

| # | Prueba | Resultado |
|---|---|---|
| 1 | Clip convertido a 25p (`scripts/filmpb1_convertir_clips.py`) | «No se puede visualizar.» |
| 2 | **Clip grabado por la propia cámara** | **«No se puede visualizar.»** |
| 3 | Miniaturas | no aparecen (ni la del clip modificado) |
| 4 | Menú → «Recuperar BD imág.» y reintento | sin cambio |

La prueba 2 es la decisiva: un clip grabado por esta cámara **cumple por construcción**
todo lo que la guarda de sistema de TV exige (mismo `TvSystem`, misma cadencia, mismo
contenedor, misma tabla de catálogo que acaba de escribir el propio firmware). Por tanto
**la cadencia no es la causa** y la línea «cámara PAL + clips NTSC» queda refutada como
causa única. La prueba 4 descarta además que sea una entrada obsoleta del catálogo: la
reconstrucción de la base de datos no cambia el síntoma.

## 2. Árbol completo de salidas del manejador (verificado instrucción a instrucción)

`FUN_00437BC0` (ELF) — desensamblado en `reports/evidence/film-pb-1-global-20261126/handler-437bc0.txt`.
Hay **seis** salidas y solo tres producen `MPR::ER_FAILED 0x1A`:

| Orden | Condición | Código devuelto | Log (stdout de `im.elf`) |
|---:|---|---|---|
| 1 | `[ctrl+0x1F0] != 5` (`0x437BE4`) | `0x0A` | `PlayMovie(), ErrorCode = 0A` |
| 2 | `[ctrl+0x1F0] == 5` y `arg5 == 0` (`0x437BEC`) | `5` | *(ninguno)* |
| 3 | **guarda A** `0x447A1E` devuelve 0 (`0x437BFA`) | **`0x1A`** | ` Pb Disable!! ref) dsm get` |
| 4 | **guarda B** `0x447F26` devuelve 0 (`0x437C2C`) | **`0x1A`** | ` Detect UnSupported Content ` |
| 5 | `0x447DA8` devuelve ≠ 0 (`0x437C78`) | código de `0x7111B0` | `PlayMovie(), ErrorCode = …` |
| 6 | `0x307F54` (`PbStart`) devuelve ≠ 0 (`0x437CF6`) | código de `0x7111B0` | `PlayMovie(), ErrorCode = …` |

El éxito sale por `0x437D2C` sin log. Conclusión operativa: **el mensaje de la cámara
(«No se puede visualizar.») solo puede venir de la fila 3 o de la fila 4**; las filas 1, 5
y 6 muestran mensajes distintos (código de error de motor), y la 2 no muestra nada.

## 3. Nuevo: la guarda A es una comprobación de *capacidades por bits*, no un test de TV

`0x447A1E(ctrl, obj, mask)` con `mask = [ctrl+0xDB8]` (el valor que devuelve
`MMgrMp4IfoAcsr::GetInhInfo`). Comportamiento verificado (`0x447A1E`–`0x447AE8`):

1. `0x447810` obtiene el objeto de control. **Si no hay objeto → `return 0`** (inhibido).
2. Recorre la máscara y, por cada bit puesto, pregunta si el reproductor lo admite:
   | bit | consulta |
   |---:|---|
   | 0 (`0x01`) | `vtable+0x60` sin argumento |
   | 1, 2 (`0x02`,`0x04`) | `vtable+0x5C` con `id 6` |
   | 3 (`0x08`) | `vtable+0x5C` con `id 8` |
   | 4 (`0x10`) | `vtable+0x5C` con `id 0x10` |
   | 5 (`0x20`) | `vtable+0x5C` con `id 0x20` |
   | 7 (`0x80`) | `vtable+0x5C` con `id 0x80` |
   | 8 (`0x100`) | `vtable+0x5C` con `id 0x100` |
   | 9 (`0x200`) | `vtable+0x5C` con `id 0x200` |
   (el bit 6, `0x40`, no se consulta nunca).
3. **Con `mask == 0` devuelve 1** (`0x447AC8` → `0x447AE0`): sin inhibiciones, la
   reproducción está permitida. Cualquier consulta que devuelva 0 corta en `0x447AE2`
   con `return 0`.

Consecuencia: para que la guarda A dispare tiene que haber **al menos un bit de inhibición
activo** en `GetInhInfo`, y ese bit tiene que ser uno que el reproductor no cubra. Para un
clip grabado por la propia cámara, el bit de sistema de TV no puede estar activo, así que
el bit que dispara —si dispara A— es de otra naturaleza. La etiqueta del log lo dice:
`ref) dsm get`, es decir, el fabricante remite a consultar el estado por DSM.

## 4. Hipótesis vigentes, ya sin la cadencia

> Las nueve investigaciones en paralelo del 26-11 dejaron esta tabla en **una sola** rama viva: la
> H4, porque `GetPlayThumbnailInfo` falla en el mutex del `mp4Ifo_If` antes de abrir el fichero (ver
> §7 y §9). Se conserva la tabla como registro de lo descartado y de por qué.

| ID | Hipótesis | Qué la sostiene | Qué la refutaría |
|---|---|---|---|
| **H3** | Un **bit de inhibición global** (DSM/estado de sesión, no de contenido) está activo: guarda A | log `ref) dsm get`; la guarda A es de capacidades, no de formato | leer `[ctrl+0xDB8]` en ejecución, o que el mensaje salga con el log de B |
| **H4** | **`GetPlayThumbnailInfo` falla** para todo clip → guarda B por su segundo `return 0` (`0x61AA68`) | encaja con «tampoco aparece la miniatura»: si la extracción de información del *thumbnail* falla, no hay miniatura **ni** reproducción | que la miniatura del clip recién grabado sí aparezca |
| **H5** | El **decodificador** (LDEC/DSP) no está operativo tras el arranque en frío del CFW | explica a la vez «graba, no reproduce, no miniatura»; el CFW quita `dev/nflasha5` (único cambio global) | grabación correcta + decodificación correcta en cualquier otra vía (p. ej. HDMI en vivo) |
| **H6** | **Tarjeta/lectura**: la cámara escribe pero no relee el clip | el clip propio también falla | leer los mismos ficheros en el PC funciona (ya comprobado), pero no prueba el lado cámara |

H3 y H5 son las que explican el conjunto con un solo mecanismo. H4 explica el síntoma de
la miniatura pero necesita que el fallo esté en el extractor, no en el decodificador.

## 5. Lo que hay que mirar en ejecución (una sola sesión con cámara)

1. Un breakpoint de un solo uso en `0x437C0A` y `0x437C3C` (VA del ELF de `libmpr`)
   distingue A de B en el primer intento de reproducción. Kit ya preparado:
   `scripts/camera_filmpb1_trace.py` (`--verify` exige cámara; `--autotest` pasa).
2. Si dispara A: leer `[ctrl+0xDB8]` (máscara) y `[ctrl+0x1EC]` en el mismo breakpoint.
   Ese entero es la lista de inhibiciones y nombra la causa sin más análisis.
3. Si dispara B: breakpoint en `0x61AA46` y `0x61AA68` separa desajuste de TV (imposible
   para el clip propio) de fallo del *thumbnail*.

## 6. Auditoría nueva: qué hay realmente dentro del `nflasha3` instalado

Se ha abierto el `nflasha3` del tar del paquete instalado
(`build/cfw_func393/pp/base-film.tar`, miembro `0700_part_image/dev/nflasha3`), se ha
descomprimido el TPZL y se ha leído su FAT interna, comparando cada miembro con el
`nflasha3` de fábrica 3.21. Evidencia: `reports/evidence/film-pb-1-global-20261126/bionz-cfw-vs-321.txt`.

| Miembro | 3.21 | Paquete | Bytes distintos |
|---|---|---:|---:|
| `vmlinux.bin` | 3 478 912 | 3 478 912 | **0** |
| `initrd.img` | 4 079 616 | 4 079 616 | **0** |
| `av-cam.bin` | 11 427 236 | 11 427 236 | **34 013** |

Los 34 013 bytes de `av-cam.bin` están concentrados en **33 rangos**, uno de ellos de
33 084 B en `0x00A6E300..0x00A7643B` (tablas de curvas de gamma) más ~20 parches de
código de ≤112 B (ganchos de Picture Profile, S-Log3, B/N, Silent, EFCS)
(`avcam-rangos.txt`). **Ningún rango cae en la ruta de reproducción**, el juego de
cadenas es **idéntico** al de fábrica (37 679 cadenas, cero exclusivas en cada lado:
`avcam-cadenas-321-vs-cfw.txt`) y `patch_tristate` no se puede aplicar al 3.21 sin
partir del binario integrado ⇒ **lo que el proyecto llama «BIONZ 3.38» es el mismo
`av-cam` de 3.21 con 40 B de parches ya integrados, no un binario de otra versión**.
Queda descartado el desajuste de versión `av-cam` 3.38 / kernel 3.21: el kernel y el
`initrd` son byte a byte los de 3.21.

## 7. Dónde queda el fallo tras esto: `GetPlayThumbnailInfo`

Con la guarda A descartada, el único productor del `0x1A` que sobrevive es la **guarda B**
(`0x437C2C` → `0x447F26` → `AviMMgr::isSupportContent` `0x61A8F0`). Su orden real de
comprobaciones, corregido:

1. **`0x61A9E4 bl 0x6E8430`** (`Mp4IfoIf::GetPlayThumbnailInfo`) — primero.
2. `0x61A9EE bl 0x1EEFDC` (`TvSystem`) — después.

Y `0x6E8430` no falla por el contenido: falla **antes de abrir el MP4**, en la toma del
recurso del *ifoFramework* (`0x6E845A bl 0x5BAD00`, `ifoFramework_Semaphore.cpp`). Si esa
llamada devuelve ≠ 0, `0x6E846C` carga el literal `0xB0100002` y sale sin tocar el
fichero. Eso explica a la vez los dos síntomas: **sin metadatos del IFO no hay miniatura
y no hay reproducción**, con cualquier clip, incluido el recién grabado, y
«Recuperar BD imág.» no lo arregla porque reconstruye el índice, no el recurso.

Es la única pieza del expediente que explica el cuadro completo con un solo mecanismo.

## 8. Prueba de campo gratis (30 s, sin herramientas)

**Encender la cámara y pulsar el botón de reproducción lo antes posible**, sin dar tiempo a
que la galería genere miniaturas; probar varios clips seguidos.

| Resultado | Lectura |
|---|---|
| reproduce al principio y deja de hacerlo al navegar | el mutex del `mp4Ifo_If` **se filtra** (dueño vivo): la toma la hace un camino que no lo libera, y todo lo posterior falla |
| no reproduce nunca, ni el primero | el handle está **colgante** o el `mp4Ifo_If` no se creó: hay que mirar `[handle]`/`[handle+4]` |

## 9. Cadena causal única (la que sostiene toda la evidencia junta)

```
arranque (frío, CFW sin nflasha5)  →  dmm.ko reconstruye el mapa de memoria
                                   →  pool del ifoFramework / mp4Ifo_If no operativo
                                   →  0x5BAD00 (ifoFramework_Semaphore.cpp) devuelve ≠ 0
                                   →  GetPlayThumbnailInfo (0x6E8430) = 0xB0100002, sin abrir el MP4
      ├── guarda B 0x61A9E4 → isSupportContent = 0 → 0x437C3C → 0x1A → «No se puede visualizar.»
      ├── sin miniatura de vídeo (mismo lector de metadatos)
      └── duración tomada del índice (0:02) en vez del `moov` (9,5095 s)
```

Cuatro comprobaciones independientes convergen en el lector de metadatos del MP4:
el `0x1A` sale de la guarda B, que llama primero a `0x6E8430`; `0x6E8430` no
decodifica ni abre el fichero, solo toma el recurso del ifoFramework; el fallo de ese
recurso explica a la vez la miniatura y la duración; y la emulación del propio `0x6E8430`
en el arnés (`reports/film-pb-1-sub-emu-fps-20261127.md`) reproduce el mismo
`0xB0100002` cuando el recurso no está preparado.

Lo que **no** es la causa, ya verificado: la cadencia (el clip propio falla), el
`TvSystem` (con clip propio no hay bit de inhibición), el catálogo/BD (recuperar la BD
no cambia nada y la guarda es fail-open), el decodificador H.264 (el error sería
posterior a `PbStart` y las miniaturas JPEG seguirían saliendo), un parche de código en
la ruta de reproducción (auditoría del CFW), la versión del `av-cam` (es el de 3.21 con
tablas de curvas) y la NVRAM (64 volcados sin cambio de sistema de TV).

## 10. Límites

- **NO_VERIFICADO en ejecución** cuál de las dos guardas dispara: exige cámara.
- La auditoría sigue siendo estática; no cubre NVRAM ni estado del decodificador en caliente.
- El clip «grabado por la propia cámara» no está identificado por nombre en esta sesión; si
  resultara ser un clip heredado o copiado, la prueba 2 perdería fuerza y habría que
  repetirla grabando uno nuevo y reproduciéndolo sin sacar la tarjeta.
