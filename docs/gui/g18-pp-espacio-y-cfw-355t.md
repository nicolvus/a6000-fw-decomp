# G18 — Dónde meter las curvas PP (salidas 3 → 2 → 1) y CFW de prueba 3.55t (08-11-2026)

**Orden pedido por el usuario**: estudiar la salida 3 (ampliar `av-cam.bin`), luego la 2 (demostrar que el hueco de 40 KB está libre),
luego la 1 (escribir en RAM) y probar con un CFW. **Restricción del usuario**: el parche se ejecuta **en la propia cámara**, nunca
desde el PC. Sigue a [G17](g17-picture-profile-plan-c.md) §2.1. Herramientas: `scripts/gui/pp_curves_patch.py`,
`analysis/gui/g18/emu_gamma.py`; `build_nflasha15.py` y `audit_package_nflasha15.py` aceptan ahora ficheros nuevos (`MANIFEST` «nuevos»).

## 1. Salida 3 — ampliar `av-cam.bin`: **descartada** (VERIFICADO)

- Loader3 carga `av-cam.bin` en `0x83541000` con una ventana de **12 MiB** ([R14](../capture/e26-r14-ramcfg-bos-analysis.md) §5).
  El fichero ocupa 11 427 236 B, así que el cargador admitiría ~1,1 MiB más.
- Pero el fin del fichero (`0x44026da4`) es `__JCR_LIST__`: lo carga `frame_dummy` en `0x439cc67c` (`movw/movt 0x44026da4`).
  Lo que va detrás es **`.bss`** hasta `~0x4409ce00`, y luego buffers fijos con punteros estáticos en casi todos los bloques de
  64 KiB hasta la pila (`0x44140ffc`, que es el fin de la ventana; está en la cabecera «LIRO» en `+0xd0`). Ampliar el fichero pisaría memoria en uso.

## 2. Salida 2 — el hueco `0x43faf28c`–`0x43fb8ee0` (40 020 B): **sin referencias estáticas** (VERIFICADO, con límite)

Se buscó cualquier referencia al rango por siete métodos, todos con un control positivo:

| Método | Control que sí da positivo | Resultado en el hueco |
|---|---|---|
| PIC corto (`ldr rX,[pc]` + `add rX,pc`, ventana 400 B) | cadena `[Sync]GammaReg` → `0x4389bc4a` | 0 |
| PIC ancho (`ldr.w`) y `movw/movt` absolutos | `__JCR_LIST__` → `0x439cc67c` | 0 |
| Punteros absolutos alineados (incluido el GOT) | — | 1, un falso positivo: bytes de código en `0x4365f814` |
| GOTOFF (dirección − base del GOT `0x4401eee4`) | — | 12 literales `0xfff954xx`, que ninguna instrucción carga (datos) |
| REA/Ghidra `xrefs` (sesión sobre `av-cam.bin` de la A6000) | tabla de curvas `0x44001404` (19 sitios), bloque `cfg` (5) | 0 en 8 puntos del hueco |
| Último dato referenciado antes del hueco | — | solo referencias internas de una tabla que termina en `0x43faf20c` |

**Límite**: un acceso por dirección calculada en tiempo de ejecución no se puede excluir de forma estática. Por eso el CFW
de prueba (§4) **vuelve a comprobar las curvas a los 60, 600 y 3600 s**: si el núcleo usara el hueco, se vería.

## 3. Salida 1 — escritura en RAM desde la cámara: **elegida para la prueba**

- **Dónde se ejecuta**: `/sbin/init` (initrd) lanza `/usr/bin/s_start_android.sh` como root en cada arranque. Tras montar
  `/android/data` se añade una línea: `( /usr/bin/pp_ram.sh > /android/data/pp_ram.log 2>&1 ) &`. No interviene el PC.
- **Qué hace `pp_ram.sh`**: (1) comprueba con `md5sum` que los 19 sitios tienen los bytes originales de la imagen. Si alguno
  no coincide, sale sin escribir nada. (2) Escribe por `/dev/mem` (física = virtual + `0x40000000`), en este orden: 7 curvas (de la A7S, con `+0x1012 = 4`), 5 punteros de vídeo (`0x16`, `0x18`–`0x1b`) y 7 entradas del selector (3–9).
  (3) Relee cada escritura. (4) Hace la comprobación diferida del §2. Cada arranque parte del `av-cam` original de la flash, así que el
  parche no es persistente y no toca `nflasha3`, que es la partición que bloqueó la cámara en el 3.25 (R36).
- **Busybox 1.13.4 de la cámara**: no tiene `printf` (se usa `echo -ne`) y su `dd` no acepta `conv=`. Sin `conv`, con `seek>0` hace
  `ftruncate`, que en `/dev/mem` falla y se ignora (no es un fichero regular), como en los scripts del R56. La aritmética `$(( ))` es
  de 32 bits, así que los desplazamientos van ya calculados en medias palabras.

### Verificación sin cámara

| Prueba | Resultado |
|---|---|
| `pp_curves_patch.py`: comprobaciones de la imagen base (hueco a cero, punteros nulos, selector `(0,0x0a)`), curvas iguales a las de la A7S salvo `+0x1012`, tabla selector igual a la de la A7S en 3–9 | OK; 28 389 B distintos; tamaño igual |
| Emulación Unicorn de la selección de gamma de la A6000 (`0x43853ec0`) sobre la imagen parcheada, en modo vídeo | selector 0 → `0x0a` (sin cambio); **3 → `0x16`, 6–9 → `0x18`–`0x1b`**; 10/11 → `0x0a` (fase 4) |
| `pp_ram.sh` con el **busybox de la cámara** bajo `qemu-arm`, sobre memoria simulada | comprobación previa, escritura y relectura correctas; **19/19 rangos** iguales a la imagen; una segunda pasada se niega a escribir |

## 4. CFW de prueba 3.55t (construido; instalación NO autorizada)

- Base: el **3.53** instalado (menú, Darwin v3, sin `nflasha5`). Solo cambian `nflasha15` (los ficheros del 3.53 +
  `s_start_android.sh` + `pp_ram.sh` 0755 + `pp_curvas.bin` 0644) y `part_image.sum`. **`nflasha3`/`av-cam` sin tocar.**
- `.dat` SHA-256 `381e189a247cff125453b8bc342171b9b1577ddb6f7f81eb1e6208bc0c8245cd`; auditoría independiente
  [`audit-3.55t.json`](../../analysis/gui/audit-3.55t.json) **25/25**; regresión del 3.53 con la auditoría ampliada **25/25**.
- **Modo de prueba**: no hay todavía interfaz PP (fase 5). A los 20 s el script fuerza el selector a **6 (Cine1)** en el bloque de ajustes
  `0x83edf7d7` y en su copia de trabajo `0x83ed4ec3` (S64). Así la vista en directo de vídeo debería verse con la curva Cine1.
  Si `libObj` reenvía el 0x4066, el valor puede volver a 0 sin que eso indique un fallo de la curva.
- **Qué mirar tras instalarlo**: (1) que arranca como el 3.53; (2) `/android/data/pp_ram.log` con «pp_ram: OK», sin «alterada» a los 60/600/3600 s;
  (3) en modo vídeo, el contraste más suave de Cine1 frente al 3.53; (4) que las fotos no cambian.
- **Vuelta atrás**: reinstalar un paquete de versión mayor sin el gancho, o borrar el gancho. El parche desaparece al apagar.

## 4b. CFW combinado 3.56 (construido; instalación NO autorizada) — el que se instalará

A petición del usuario se juntan las dos novedades en un solo paquete: el 3.55t (gancho y script PP) + el `CautionConfig.so` del
**3.54**, que es el selector On/Off de «Silent Shooting» ([G11](g11-auditoria-307-nflasha15.md) §13; nunca probado en cámara).
Los otros 26 ficheros del 3.54 son idénticos a los del 3.53 (comprobado por hash). Frente al 3.54 solo cambian `nflasha15` y `part_image.sum`;
Darwin v3 está incluido y no hay `nflasha5`. `.dat` SHA-256 `ebb7ee825b87a07f4afc485f2681a2b0df52d7333b33a0e21943c98237926728`;
auditoría [`audit-3.56.json`](../../analysis/gui/audit-3.56.json) **25/25**. Qué mirar: lo del §4 más que «Silent Shooting» abra el selector
y On/Off conmuten entre EFCS y electrónico. Si algo falla, el registro `pp_ram.log` separa la parte PP de la del menú.

## 5. Pendiente

Instalar el 3.55t (requiere autorización expresa). Después, la fase 2 definitiva (sin el modo de prueba), la fase 3 (campos PP)
y las fases 4–7 de G17.
