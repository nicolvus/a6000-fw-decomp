# S50 — conclusiones conjuntas (Claude + Codex, investigación paralela)

19-10-2026. Dos procesos independientes (Claude Code en esta sesión; `codex exec` en proceso aparte), cada uno con **su propia sesión
REA/Ghidra** (`analysis/s50/<nombre>/run/`: socket, logs, tmp y métricas propios; arranques en frío escalonados con `flock`).
Informes: [Claude](s50-claude-electronic-config.md) · [Codex](s50-codex-exposure-curtains.md).
Sin firmware ejecutado, sin cámara, sin flasheo, sin git.

## Respuesta a la pregunta final

**NO_VERIFICADO.** No se ha demostrado una foto de resolución completa con inicio y fin electrónicos de exposición sin cierre de cortina
mecánica, y **tampoco se ha demostrado imposibilidad** (ninguna evidencia concreta del mapa de registros/píxel del IMX210 la excluye).

## Hallazgos coincidentes (dos métodos independientes: Claude por LLVM/bytes, Codex por REA+histórico+LLVM)

1. Los nombres `CURTAINMODE`, `*_ELEC_SHUT` no prueban efecto eléctrico; ambos investigadores lo rechazan como inferencia.
2. Cadena `C+0x94/+0x95 → bloques del coordinador (B/G) → 0x43842158` (selector de modo): confirmada por ambos.
3. REA no recupera las funciones Thumb impares clave; las afirmaciones se apoyan en bytes (LLVM) y, en Codex, en el histórico de solo lectura.
4. Ninguno halló una ruta de fin electrónico de exposición ni una escritura MMIO derivada de la configuración electrónica.

## Resultados nuevos y correcciones

| Resultado | Origen | Estado |
|---|---|---|
| `0xb6 A_LINEAR_ELEC_SHUT` es inerte en `av-cam`: sin fila de callback en todo el binario y sin caso en el conmutador `C+0x60` de `0x4382dd78` | Claude | VERIFICADO |
| `0x4382dd78` = constructor del bloque B desde C: consumidor de `C+0x60` (id activo), `C+0x94/95`, `C+0x9e/0xa0 (0xed)`, `C+0xa1/0xa2` | Claude | VERIFICADO |
| `0x43842158`: `C+0x94==1` sobrescribe el modo global `0x43eefb1c+0x60` con `{0→1,1→3,2→2,3→0,4..7 id,>7→1}`; ese modo solo se exporta a registros de estado (`obj+0xf9 = modo+1`) | Claude | VERIFICADO (sin MMIO hallado) |
| `0xb7` guarda 16 B de parámetros en `B+0xb20…`; único lector `0x438d5eb4` (pipeline de registro de estado) | Claude | VERIFICADO |
| **CORRECCIÓN de S49:** el tercer campo `1/2/3/6` de las filas `{clave,slot,·}` es la **cantidad de callbacks** de la lista (`0x43af6870/0x437da2d8`), **no** una clase de captura | Codex | VERIFICADO |
| Bypass diagnóstico de la petición CA (`captura+74f=0` por `D=0x43e95950`, `D+7e/7f`) omite peticiones pero marca estados no normales; no es una foto silenciosa | Codex | VERIFICADO / rechazo de la inferencia |
| Fila externa `+0x12c`→`0x43b1c0e3`→`438d0d30` (evento 12): colocación resuelta; compatible con reproceso (INFERENCIA) | Codex | VERIFICADO / INFERENCIA |
| `43b5e2b0` escribe `1<<bit` en `0xf2910048+banco*0x100` (acción MMIO, no trama serie) | Codex | VERIFICADO |
| IMX210 `SetExposure` acepta selector 0–4; clase2 (`436d7114..`) añade máscara94 y dos bytes (ID100/101); fin eléctrico | Codex | VERIFICADO el código / NO_VERIFICADO el significado |

## Contradicciones y su resolución

- **Claude usó el vocabulario «clase 1/2/3/6» de S49** al describir filas. Codex demuestra que es *cantidad*. Se acepta la corrección de
  Codex; lo verificado por Claude (ausencia de fila `0xb6`; casos de `C+0x60`) no depende de esa lectura. Las 7 filas de claves de obturador
  (`0xb5,0xb7×2,0xba×2,0xce,0xed`) reflejan listas de 1, 3, 1, 6 callbacks, no modalidades.
- Claude afirmó para `0x4382dd78` que el conmutador cubre un conjunto de inmediatos: es la lista de inmediatos comparados, no una enumeración
  semántica de casos; la conclusión sobre `0xb6` (ausente) se mantiene por la doble evidencia (sin fila + sin comparación).
- Sin contradicciones técnicas sobre datos: ambos informes coinciden en bytes y direcciones.

## Hipótesis descartadas

«`0xb6` tiene handler pendiente que activa el obturador electrónico lineal»; «las filas 1/2/3/6 son modalidades de captura»; «el bypass `+74f`
es una toma silenciosa válida»; «Vídeo/LiveView prueba 24 MP electrónicos»; «la ausencia de global shutter impide toda obturación electrónica».

## Qué falta para demostrar exposición totalmente electrónica

Una combinación alcanzable que una: modo de resolución completa, **programación de inicio y fin por filas con efecto eléctrico identificado**
(significado de los bits ID1/ID100/ID101 del IMX210, frontera MMIO `0xf3120220`), ausencia de cierre mecánico en ese intervalo, lectura completa
nueva y rearme. Mecanismo concreto sin localizar: el **consumidor físico** del modo `0..7` (`X+0x60`) —o su equivalente— y el paso
B/G → `ModeRsvParam` → `C_Imager::SetMode/SetExposure/SetRead`. Evidencia necesaria: traza pasiva en cámara (fuera de alcance aquí) o el
mapa de registros del sensor.

## Dependencias mecánicas

Demostradas (heredado): cortinas Darwin P4D/P4E (`1ST/2ND_CURTAIN_MG`) por estático y esquema; MMIO `0xf2910048+banco*0x100` en la ruta de
evento 3. Pendiente: enlace temporal completo LIRO/MMIO → Darwin → bobina → sensor.

## Tiempo y recursos

| | Claude | Codex |
|---|---|---|
| Trabajo | ~35 min | ~27 min |
| Espera `flock` / frío REA | 0 s / 468 s | 341 s / 490 s |
| RSS REA máx | 2 880 MB | 2 333 MB |
| `GHIDRA_MAXMEM` | 4 G | 4 G (histórico 3 G aparte) |

RAM disponible mínima observada 2,9 GB; swap ~7,2 GB (ya en uso antes de S50, sin crecimiento). Sin paginación intensa. Watchdog nuevo
(`analysis/s50/shared/daemon.py`): límite por instancia `S50_RSS_MAX_MB` (8000 por defecto), corte además si `MemAvailable<1000 MB`; métricas
cada 10 s. No se modificó swap/kernel. `libObj.so` no se analizó (no hizo falta en S50): el límite ya no es de 3,8 GB.

## Fallos y límites

REA no cubre Thumb impar (rea#1048 y funciones sembradas): la exploración se hizo por LLVM. Índice PC-relativo/GOT de Claude heurístico.
Primer `nohup` de Codex no persistió (corregido). Sin validación en cámara: todo es estático.

## Integridad

`sha256sum -c analysis/s50/shared/sha256-initial.txt`: **1490/1490 OK** (`silent-liro.gpr/.rep`, `av-cam.bin`, firmware `fw321`, informes S1–S49).
Auditoría de Codex: PASS (1490 protegidos).

## Próximo hito recomendado (S51)

1. Seguir el modo `0..7` hacia `ModeRsvParam`/`C_Imager::SetMode` y localizar el escritor de `[0x43f76342+0x7e]`.
2. Dar significado eléctrico a ID1/100/101 y a `0xf3120220` (documentación del IMX210 o traza pasiva).
3. No reabrir `0xb6` ni las filas «1/2/3/6» como modalidades.
