# S20 — `libmpr.so`: diagnóstico y conversión tras WriteAndFlush

**VERIFICADO:** `0x13de98` trata el retorno de escritura como condición de
diagnóstico; `0x13dbb0` convierte el error MPR al dominio AVI. Ninguna registra
DCF ni escribe un archivo en el camino examinado. La escritura sigue siendo
la llamada previa a `MprFileIf::WriteAndFlush` en `0x13df32`; el destino final
del gestor de medio continúa **NO_VERIFICADO** para este still.

## Alcance y reproducción

- Análisis estático local con LLVM y Python stdlib; sin cámara, flasheo,
  instalaciones, ejecución del firmware ni modificación del ELF original.
- Leídos `CONTEXT.md`, `s20-p5-writeandflush-caller.md` y
  `s20-rtti-tooling-p3-objid53.md`; revisados `analysis/` y `scripts/`.
- Reutilizados `scripts/rtti_vtables.py:Elf` para ELF/relocaciones y
  `analysis/session19/evidence/dcf-playback-completion.json` para la frontera
  anterior. No se reextrajeron tablas ni el desensamblado completo.
- Binario: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`.
- SHA256: `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`.
- Direcciones VA ELF, sin sesgo de Ghidra; código Thumb salvo PLT ARM indicado.
- Reproducción: `python3 -B analysis/session20/evidence/codex-mpr-13de98-13dbb0-check.py`.
  El script solo lee y emite stdout; conserva los comandos LLVM exactos.

Evidencia nueva acotada: [desensamblado y comprobaciones](../../analysis/session20/evidence/codex-mpr-13de98-13dbb0-disassembly.txt),
[script](../../analysis/session20/evidence/codex-mpr-13de98-13dbb0-check.py).

## Hallazgos y evidencia

| Clasificación | Hallazgo | Evidencia VA / líneas del desensamblado |
|---|---|---|
| VERIFICADO | El wrapper conserva el error original en `r5`, llama al diagnóstico con `r1=0x789`, `r2=0`, borra la marca secundaria y entrega el error original al conversor. | `0x13df32..0x13df4c`; líneas 94–106. |
| VERIFICADO | `0x13de98` retorna inmediatamente si `r0==0`; solo prepara diagnóstico si es distinto de cero. No modifica el resultado usado después, porque el wrapper lo conserva en `r5`. | `0x13dea0..0x13dea6`, `0x13df10`; líneas 28–30, 73–74. |
| VERIFICADO | El diagnóstico selecciona ID mediante el estado global `0x9e0b78` (1..18); si queda fuera usa `0x105c`. Empaqueta marca secundaria, error y `0x789`. | `0x13dea8..0x13ded6`, `0x13df00..0x13df0e`; líneas 31–53, 65–72. |
| VERIFICADO | En el wrapper se fija estado `0x11` y marca secundaria `0x1010`. El nombre opcional es NULL, por lo que no se ejecutan `strlen` ni el diagnóstico `0x105d` del sufijo de hasta 20 caracteres. | `0x13df22..0x13df30`, `0x13df3a`, `0x13deda`; líneas 54–64, 85–93, 96. |
| VERIFICADO | `0x13dbb0` solo tiene prólogo/epílogo y salto a `0x11e3f8`. Es una entrada Thumb de PLT hacia `CS_AviMprIf::MPR2AVIErr`, no limpieza. | `0x13dbb0..0x13dbb8`; líneas 11–14 y 371–392. |
| VERIFICADO | El conversor local `0x143fb0` busca el error en 63 pares de 8 bytes en `0x7a8774`, devuelve el segundo valor si coincide y `0x2116` si no encuentra coincidencia. No tiene llamadas ni escrituras de memoria. | `0x143fb0..0x143fd2`; líneas 345–362. |
| INFERENCIA | El wrapper pertenece a una capa de adaptación AVI/MPR; lo respalda el conversor exportado, pero falta un símbolo o registro que atribuya exactamente `0x13df20` a clase/método. | Salto a `CS_AviMprIf::MPR2AVIErr`; no se usa el símbolo anterior por proximidad. |
| DESCARTADO | Interpretar `0x13dbb0` como limpieza compartida, cierre de archivo, liberación o commit DCF. | Su cuerpo completo y el conversor no realizan esas operaciones. |
| NO_VERIFICADO | Registro/commit/rollback DCF, medio SD, durabilidad y publicación en reproducción para el still; tampoco queda identificado el registro del wrapper como callback. | No se recupera aquí ninguna arista a las APIs DCF `0x71eafc` / `0x71eb70`. |

### Corrección de la etiqueta PLT

**VERIFICADO:** LLVM presenta el destino `0x11e3f8` como
`CancelPlayHighlightMovie@plt+0xc` al desensamblar el salto desde `.text`.
Esa etiqueta por proximidad es engañosa: bytes `78 47 c0 46` equivalen a
`bx pc; nop` en Thumb. El `bx pc` entra en ARM en `0x11e3fc`.
Sus tres instrucciones calculan el slot GOT `0x9c3934`; `.rel.plt` lo asocia a
`_ZN11CS_AviMprIf10MPR2AVIErrEN3MPR5ErrCdE`, exportado como Thumb
`0x143fb1` (código en `0x143fb0`). La comprobación decodifica los inmediatos
ARM y contrasta la relocación, sin depender del texto de la etiqueta.

## Qué hacen los auxiliares del diagnóstico

**VERIFICADO:** `0x13ded6` llama a `0x13f0cc` con segundo argumento `0xc8`.
En este ELF, `0x13f0cc` llama a `0x13ef58`, que escribe cero en la variable
de salida (`0x13ef5a/0x13ef5e`). Ese cero pasa como segundo argumento a
`0x13ef64`, cuyo `cmp r1,#0; beq 0x13f07e` retorna antes de llegar a sus
sumideros. Después `0x13f0cc` compara el segundo argumento original con
`0xcd` (`0x13f13a`) y salta al epílogo `0x13f34a` porque recibió `0xc8`.
Por tanto, en esta llamada ni siquiera se alcanza un sumidero diagnóstico.

**VERIFICADO:** el auxiliar opcional `0x13f08c` también obtiene cero de
`0x13ef58` y llama a `0x13ef64` con ese cero. Además, el wrapper estudiado
no lo alcanza, porque pasa nombre NULL. Esta conclusión es de flujo estático,
no una prueba dinámica ni una afirmación sobre otras llamadas de los auxiliares.

**INFERENCIA:** los parámetros e IDs corresponden a instrumentación de errores
deshabilitada en esta compilación. La ausencia de efectos externos en la rama
concreta sí está **VERIFICADA** por sus guardas; el propósito del diseño sigue
siendo una interpretación.

## Pseudocódigo reconstruido

Reconstrucción manual de LLVM; nombres locales descriptivos, no símbolos recuperados.

```c
void post_13de98(uint32_t err, uint32_t site, const char *name) {
    if (err == 0) return;
    uint32_t state = load32(0x9e0b78);
    uint32_t id = (state - 1u <= 17u)
        ? load16(0x7a6cfe + 2u * (state - 1u)) : 0x105c;
    diag_13f0cc(id, 0xc8, 0, 4,
               state, load32(0x9e0204), err, site, /* once ceros */);
    if (name != NULL) {
        // El bucle firmado conserva como máximo los últimos 20 caracteres.
        const char *suffix = suffix20(name);
        diag_13f08c(0x105d, 0xc8, 0, suffix);
    }
}

uint32_t convert_13dbb0(uint32_t err) {
    return CS_AviMprIf_MPR2AVIErr(err); // tabla de 63 pares; default 0x2116
}

uint32_t wrapper_13df20(/* argumentos de WriteAndFlush */) {
    store32(0x9e0b78, 0x11);
    store32(0x9e0204, 0x1010);
    uint32_t err = MprFileIf_WriteAndFlush(/* argumentos originales */);
    post_13de98(err, 0x789, NULL);
    store32(0x9e0204, 0);
    return convert_13dbb0(err);
}
```

**VERIFICADO:** el wrapper no restaura el estado `0x9e0b78` a cero;
solo limpia `0x9e0204`. **NO_VERIFICADO:** que `0x789` sea un número de
línea de fuente; aquí se conserva únicamente como identificador constante.

## Validación y siguiente paso

**VERIFICADO:** script finalizado con `PASS`; hash del ELF igual antes y
después, interworking Thumb→ARM y relocación PLT comprobados, instrucciones
del stub cero y guardas contrastadas con bytes originales. Se conservaron
los registros previos del checkpoint y se añadió una sola entrada JSON.
No se ejecutaron ruff/mypy de otro proyecto: no se modificó `src/` ni `tests/`.
Sin commit ni push: el directorio no es un repositorio Git utilizable
(`git status`: «not a git repository»); no se pudo ejecutar `git diff --check`.
El alcance solicitado permite únicamente este documento, el append al
checkpoint y temporales `codex-*`.

**DESCARTADO:** buscar el registro DCF en estas dos funciones como operación
posterior a WriteAndFlush. **NO_VERIFICADO:** que no exista registro DCF antes
de escribir o en otro nivel de la pila.

Siguiente paso concreto: resolver el destino del slot virtual `+0x290` del
gestor de medio al que delega `MprFileIfCore::WriteAndFlush` (`0x726138`,
ya documentado en S19-08), reutilizando su evidencia. Seguir desde ese destino
las operaciones de archivo y contrastarlas con las APIs DCF conocidas;
identificar quién referencia/registra
`0x13df21` permitiría atribuir el wrapper a su contexto AVI.

SilentShutter no se declara funcional.
