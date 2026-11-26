# Eye AF dentro del CFW (parche de `av-cam`, sin APK)

Fecha: 28-11-2026. Objetivo del usuario: «no quiero que sea una app, quiero que sea un módulo real de
la cámara … que ya venga directo en el cfw». Esto es la vía elegida: **dos bytes** de `av-cam.bin`
que el constructor del CFW aplica solo, sin `ar.eyeaf` ni nada instalado aparte.

Antecedentes: [eye-af-nativo](eye-af-nativo-a6000.md) (dónde está el detector y cómo llega a área de
AF), [eye-af-tiempo-real](eye-af-tiempo-real.md) (carril del PC, alternativa).

## 1. Qué se parchea

`0x437b7200` (módulo `[CAMERA_MAIN_FC]`) elige la fuente del área de AF según el **modo de área**
(tercer argumento, `r6`). Desensamblado real de 3.21 (bytes tal cual):

```
0x437b723a: 022e       cmp  r6, #2
0x437b723c: 38d1       bne  #0x437b72b0     ; modo != 2 -> cara / multi (sin ojos)
0x437b723e: 94f8df30   ldrb.w r3, [r4, #0xdf]   ; validez ojo 2
0x437b7242: 012b       cmp  r3, #1
0x437b7244: 0cd1       bne  #0x437b7260         ; ojo 2 no válido -> aviso + ojo 1
...
0x437b7274: ...        ; bloque del ojo 1 (ctx+0xde)
0x437b72b0: ...        ; cmp r6,#1 / si no, marco de cara
```

Parche:

| Dirección | Antes | Después | Instrucción |
|---|---|---|---|
| `0x437b723c` | `38 d1` | `00 bf` | `bne #0x437b72b0` → `nop` |

Al no ramificar, **cualquier** modo de área cae en el bloque del ojo: ojo 2 válido → ojo 2; si no,
ojo 1; si no, ceros (y se mantiene el aviso «Eye data is invalid, but lc flag is true.»). Es la
prioridad de ojo que las a6xxx tienen de fábrica, sin tocar el detector (`Camera::FC::Drv::ProcessEdt`),
ni la conversión ojo→rectángulo (`0x437b73e0`–`0x437b743a`), ni el envío al consumidor
(`0x437b7ea0`).

Sólo cambian 2 bytes; tamaño de la imagen intacto (`11 427 236 B`).

## 2. Cómo entra en el CFW

`scripts/cfw/eye_af_patch.py`:

* `PATCH = {0x437b723c: (bne, nop)}`, `allowed_addresses()`, `apply_bytes()` → `(imagen, diff por byte)`
  y `restore_bytes()` (reversión exacta), con el mismo interfaz que el resto de parches del CFW;
* CLI suelta para depurar sobre una copia: `--apply`, `--check` (0 = aplicado), `--revert`;
* `SHA_INPUT`/`TAMANO_INPUT` fijan la imagen oficial de 3.21; si los bytes del sitio no son los
  esperados, aborta en vez de escribir.

`scripts/e25_27/build.py::apply_patches` lo aplica **después** del selector y de C3-B, y comprueba:

1. que el diff cae exactamente en `{0x437b723c, 0x437b723d}`;
2. que no solapa con el selector ni con C3-B;
3. que `restore_bytes` devuelve el `av-cam` intermedio bit a bit.

Con eso, `nflasha3` que produce el constructor (E25-27) ya sale con Eye AF: no hay paso manual ni
APK. El contenedor cambia un bloque comprimido más (`{0, 48, 57}` → `{0, 39, 48, 57}`), que es el
que contiene el sitio parcheado.

## 3. Pruebas (todo estático)

```
tests/test_eye_af_cfw_patch.py .......                                    [100%]  7 passed
tests/test_e25_27_build.py tests/test_eye_af_cfw_patch.py .......s...........s........   27 passed, 2 skipped
```

`tests/test_eye_af_cfw_patch.py` cubre: estado del sitio en la imagen original, desensamblado
(`cmp r6,#2` + `bne` antes; `nop` después), que **sólo** cambian 2 bytes, idempotencia, reversión con
SHA idéntico, aborto si los bytes no son los esperados, CLI completo y rechazo de tamaños ajenos.
`tests/test_e25_27_build.py` valida la cadena completa del constructor (diff del Eye AF presente, sin
solape, reversión, build determinista y emulación integrada).

## 4. Reversión

`--revert` (o `restore_bytes` en el constructor) escribe `0x437b723c = 38 d1`: la cámara vuelve al
comportamiento de fábrica (ojo sólo en los modos de área 1 y 2). Nada más que deshacer, no hay
cueva, ni tabla, ni NVRAM.

## 5. Límites

* **Cuándo actúa**: el bloque del ojo se ejecuta cuando el firmware calcula el área de AF, es decir
  al atender una petición de AF (`ReplyForTouchShutter`, `0x437b7ea0`). El parche cambia **qué
  fuente** se usa, no **cada cuánto** se pide: la continuidad sigue dependiendo de que el AF esté
  activo (AF-C / AF-S disparando). Cadencia: NO_VERIFICADA (vive fuera de `av-cam`).
* **Efecto en cámara**: NO_VERIFICADO. En modo Wide el área pasará a ser el ojo cuando el detector
  lo dé por válido; si el detector no ve ojos, el camino ya previsto deja ceros y sigue el marco de
  cara (por eso se eligió este sitio y no forzar `r2 = 2`).
* **Instalación**: no se ha flasheado nada; hace falta autorización explícita del usuario. El
  firmware del proyecto se construye y verifica, pero no se escribe en la cámara en esta fase.
