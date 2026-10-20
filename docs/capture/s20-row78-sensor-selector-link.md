# S20 — Fila LIRO `0x78`: enlace real con el selector de modo de sensor y con RawDevInit

Continuación directa de `s20-rawplay-stage-reuse.md`. Alcance: Sony A6000
FW 3.21, `av-cam.bin`, proyecto Ghidra `silent-liro` (solo lectura). Sin
Codex, sin subagentes.

## Hallazgo principal: la fila `0x78` llama al selector real de modo de sensor

**VERIFICADO** (decompilación completa de `FUN_43b1bdb4`, entrada Thumb de
la fila `0x78` ya catalogada en S19-07, `analysis/session20/evidence/s20-liro-rows-dec.json`):

El caso `0` (estado inicial) de esta fila, cuando `FUN_43ae7648(ctx) != 1`
(es decir, fuera de la rama de cancelación), ejecuta:

```
FUN_437286bc(); FUN_43728614(); FUN_437284b4(); FUN_437284c0();  # NO_VERIFICADO su función
FUN_437f7ff0(ctx);   # == selector de modo IMX210 ya confirmado en CONTEXT.md:813
                      #    ("produce 0x0b/0x2f/0x01/0x0c/0x17/0x1b/0x35")
si ctx+0x1d8==0 || ctx+0x1e0==0x17:      # 0x17 == modo vídeo 1080 (CONTEXT.md:818)
    FUN_43796484(); FUN_4395e320(); ...
```

**Esto es VERIFICADO, no inferencia**: la fila `0x78`, ya catalogada por
S19-07 como "convencional, sin marca Silent/EFCS", llama directamente al
selector real de modo de sensor IMX210 (`0x437f7ff0`) en su estado inicial.
**Esta fila no es independiente del sensor.** No se puede usar como base de
una ruta Silent sin reemplazar explícitamente esta llamada.

## Hallazgo secundario: el patrón de cancelación de S19-13 está en la MISMA función que la fila `0x78`

**VERIFICADO**: el mismo caso `0` de `FUN_43b1bdb4`, cuando
`FUN_43ae7648(ctx) == 1`, ejecuta exactamente el patrón ya documentado en
S19-13 (`s19-post-s2-cancellation-states.md`) para `0x437f22d4`:

```c
if (*(int *)(iVar3 + 0x754) == 0) {
    uVar5 = 0;
} else {
    FUN_437fbad8(param_1, *(int *)(iVar3 + 0x754), 0);
    *(undefined4 *)(iVar3 + 0x754) = 0;
    uVar5 = 0;
}
```

**Precisión sobre S19-13 (no contradicción, extensión directa)**: los
rótulos `LAB_437f2452`/`FUN_437f2228` que aparecen en la decompilación de
Ghidra de `FUN_43b1bdb4` caen dentro del rango `0x437f22d4..0x437f245c` que
S19-13 ya identificó como una **etapa compartida** a la que "despachan
varias filas LIRO" (S19-13 cita explícitamente `0x43b1bf04`, `0x43b1bfc8`,
`0x43b1c034` como filas que llegan a `0x437f22d4`). **Esta tarea confirma y
extiende ese hallazgo**: la fila `0x78` (`0x43b1bdb4`) también despacha a
esa misma etapa compartida — es un salto a una implementación común, no
código duplicado dentro de `FUN_43b1bdb4`. Lo genuinamente nuevo aquí es la
**rama no-cancelación** de esa etapa compartida (cuando
`FUN_43ae7648()!=1`), que S19-13 no decompiló: ahí es donde aparecen el
selector de sensor `0x437f7ff0` y la espera "RawDevInit_WAIT_IMG_PARAM"
sobre `ctx+0x4b70`.

## Hallazgo terciario: nueva cadena RawDevInit y conexión con Stage_DevLater

**VERIFICADO**: en la misma rama (gate `!=1`), si `ctx+0x4b70 != 0`, el
código entra en un bucle de espera:

```c
while (FUN_4372a73c(0x1b) != 0) {
    FUN_43560cc8(100);              // sleep 100 (unidad NO_VERIFICADA)
    log "RawDevInit_WAIT_IMG_PARAM" // cadena nueva, no documentada antes
}
```

**Esto conecta directamente con `s20-rawplay-stage-reuse.md`**: el campo
`ctx+0x4b70` es el MISMO campo que `FUN_437edaf8` (Stage_DevLater) escribe
desde `ctx2+0x27e4` cuando se le llama con `param_3==0`. Es decir, **el
resultado del "develop" de un `.ARW` desde tarjeta (Stage_DevLater) se
comunica a la máquina de estados de la fila `0x78` a través de `ctx+0x4b70`**,
que esta fila usa como condición de espera llamada "RawDevInit" antes de
continuar. Esto es un enlace real y nuevo entre la cadena S20-RAWPLAY ya
cerrada (desarrollo de ARW de tarjeta) y la máquina de estados principal de
captura — pero sigue sin demostrar una vía Silent: la fila `0x78` solo espera
a que ese campo esté listo antes de llamar al selector de sensor real
`0x437f7ff0`, no en lugar de él.

## Funciones gemelas confirmadas (mismo patrón, filas `0x50`/`0x64`/`0x78`)

`FUN_43b1bd12` (fila `0x50`) y `FUN_43b1bd5e` (fila `0x64`) tienen el mismo
caso `3`/`4` (según la fila) con idéntico patrón:

```c
iVar3 = FUN_43840f58(ctx+0x20);
ctx+0x718 = iVar3;
si iVar3 != 0: ctx+0x71c = FUN_43b08ffe(ctx+0x20);
FUN_43782f10(ctx);
...
iVar3 = FUN_437dd400(ctx);
si iVar3 == 0xffff: FATAL "Stage_Raw.cpp" (0x109)   // cadena Stage_Raw.cpp, nueva
sino si (ctx+0x774==1 && FUN_437dd4dc(ctx)==0xffff): return 2
sino: si ctx+0x4fc0 != 0: FUN_43afb276(ctx)
```

Esto confirma que las filas `0x50`/`0x64`/`0x78` son variantes de la MISMA
plantilla de "preparación convencional" ya señalada por S19-07 como una
familia compartida (campos `+0x718/0x71c/0x774/0x4fc0`), con una tercera
cadena nueva: **`Stage_Raw.cpp`** (diagnóstico FATAL si `FUN_437dd400`
devuelve `0xffff`).

## Hallazgo adicional: `FUN_43afe11a` caso 0 rellena los campos de dimensión que lee Stage_Apollo

**VERIFICADO** (misma decompilación, `analysis/session20/evidence/s20-rawplay-dec2.json`,
función `43afe11a` completa): el caso `0` (fallthrough) de este dispatcher
—hermano de `43afe9f4`, también llamado desde filas LIRO— obtiene un puntero
de configuración vía `FUN_4379a320()` y copia sus campos `+0x280/+0x284/
+0x2b0/+0x2b2/+0x2b4/+0x2b6` hacia `ctx+0x4afa/+0x4ec0/+0x4efa/+0x4efc/
+0x4efe/+0x4f00` (más derivados en `+0x4f02..+0x4f08`). **Estos son
exactamente los mismos campos que `FUN_43b1bb4c` (Stage_Apollo) lee** para
construir su estructura de 0x18 B (`uStack_44=ctx+0x4efa`,
`uStack_42=ctx+0x4efc`, etc. — ver `s20-rawplay-stage-reuse.md` §2). Esto
confirma que `FUN_43afe11a` caso 0 es la etapa de **preparación de
dimensiones** que antecede a Stage_Apollo, no una ruta independiente.

Dentro de ese mismo caso 0 aparece una cadena de diagnóstico nueva y no
documentada antes: **`GOLFSHOT_FREE_ERR...SSP_IMAG...`** (función
`FUN_43902df8`, candidata `SSP_IMAG`). No se investigó su significado; se
registra como hallazgo léxico nuevo, sin clasificación de comportamiento.

**VERIFICADO**: `FUN_43afe11a` caso 3/7 usa los mismos patrones de
guardar/recuperar sobre `ctx+0x4ad0+0x16cc/+0x16e0` ya vistos en
`FUN_43afe9f4`/`437ef8cc`/`43b1ad32`, confirmando que es la misma familia de
mecanismo de descriptor, aplicada a un campo de imagen (`ctx+0x6e4/0x6e8/0x6ec`)
distinto del de `437ef8cc` (`ctx+0x4b54/58/5c`). **Esto es una pista real de
que el mecanismo de guardar/recuperar NO es único — hay al menos dos
instancias paralelas** (una para `ctx+0x4b54..5c`, otra para `ctx+0x6e4..ec`)
operando sobre el mismo objeto secundario `ctx+0x4ad0`.

## Clasificación y límites

- **VERIFICADO**: fila `0x78` llama al selector real de sensor `0x437f7ff0`;
  no es independiente del sensor.
- **VERIFICADO**: `ctx+0x4b70` conecta Stage_DevLater con la espera
  "RawDevInit" de la fila `0x78`.
- **NO_VERIFICADO**: significado de `FUN_437286bc/43728614/437284b4/437284c0`
  (llamadas previas al selector de sensor).
- **DESCARTADO**: que la fila `0x78`, o sus gemelas `0x50`/`0x64`, ofrezcan
  una vía de captura sin sensor — las tres llegan a selectores/funciones de
  sensor reales cuando el gate de cancelación no está activo.

SilentShutter no se declara funcional.

## Archivos

- `analysis/session20/evidence/s20-dispatcher-callers.json` — llamadores
  reales de `FUN_43afe9f4` (filas `0x50/0x64/0x78/0xf0/~0x118`).
- `analysis/session20/evidence/s20-liro-rows-dec.json` — decompilación real
  de `0x43b1bd12, 0x43b1bd5e, 0x43b1bdb4`.
- `analysis/session20/evidence/s20-ctx-getter-dec.json` — decompilación de
  `0x43ae75dc` (getter trivial: `*param_1`), `0x43ae769a`, `0x43ae7c80`.
