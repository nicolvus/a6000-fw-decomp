# Tema 2 — Origen de los parámetros IMX210 (M/Tv/clk) y bloque de temporización del sensor

**Proyecto:** sony-a6000-electronic-shutter — obturador completamente electrónico.  
**Objetivo:** Tema 2 de 3. Localizar el escritor real de `obj+0x2be..0x2d0` (origen P0 de M/Tv/clk), los escritores de `G+0x168`/`G[0xD]` y los valores M/Tv/clk alcanzables.  
**Binario:** `av-cam.bin` (raw ARM, base de importación `0x43541000`, SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).  
**Método:** REA estática sobre `av-cam.bin` (Ghidra 12.1.4, `-readOnly`, sin análisis mutante). No se ejecutó firmware en cámara, no se flasheó, no hay pruebas físicas. Todo es estático.

## Estado de la sesión REA (este informe)

El demonio `analysis/rea-independent/run/rea-tema2.sock` (`.ready` a las 23:22, `cold_s=901.2`) murió entre las 23:22 y las 23:35 (watchdog; al finalizar hay 0 procesos `session_daemon.py`/`AnalyzeHeadless`/decompile/`q.py`). El lote `/tmp/opencode/tema2-calls.json` (8 `analyze_function`, 2 `xrefs`, `get_call_graph` de `HS_Main`, 2 `trace_native_values`) **no se ejecutó contra una sesión viva**: `tema2-out.jsonl` quedó vacío (0 bytes). No se relanzó el demonio por instrucción expresa.

La evidencia REA cruda que sí se obtuvo proviene del log compartido `analysis/rea-independent/out/exp2-session-log.jsonl` (mismo binario, mismo digest): de las llamadas de este lote, solo `procedure_pseudo_code(0x43aecbec)` devolvió resultado (confidence `observed`, autoridad `shipped-artifact`, `untrusted_content`). El resto de direcciones se citan como conocimiento previo verificado (S60/S61/S59) o se marcan NO_VERIFICADO.

---

## 1. Escritores resueltos de `obj+0x2be..0x2d0` y de `G+0x168` / `G[0xD]`

### 1.1 Escritor de `obj+0x2be..0x2d0` (origen P0 de M/Tv/clk) — NO LOCALIZADO

`analyze_function(0x43861ed0)` y `xrefs(0x43861ed0)` no devolvieron resultado (daemon caído). El productor real que rellena los 9 campos de `obj+0x2be..0x2d0` **no se localizó en esta sesión**.

Conocimiento previo (S61, conocimiento previo verificado, no REA esta sesión):
- `P0 = 0x43861ed0` lee `obj+0x2be, 0x2c0, 0x2c2, 0x2c4, 0x2c6, 0x2c8, 0x2ca, 0x2cc, 0x2ce, 0x2d0` y escribe `obj+0x310..0x334` (ventanas lo/hi, márgenes ±0x400, constante `0x3400`, división en `0x4355fd68`, reordenación `lo<hi`). Llamadores de P0: `0x43862bc4`, `0x43863668`. `obj+0x2cc` se copia a `obj8` (memcpy de 0x244 B en `0x43aece72..0x43aece90`, `p[2] = obj8`).
- Candidatos propuestos como escritor de los 9 campos: `0x4383075c`, `0x437f1414`, `0x43ae9e92`, `0x43894524`, `0x438f171c` — **ninguno confirmado como escritor**.

Estado: **NO_VERIFICADO** (productor real de `obj+0x2be..0x2d0` no localizado).

### 1.2 Escritor A de `G+0x168` / `G+0x16A` (gate `bit6(G[0xD])==0`)

- `G = 0x43e964a4` (slot GOT `+0x21a0`; absoluta `0x4401eee4 + 0x21a0`). **No es** el objeto de 0xF20 B (corrige S60). **VERIFICADO** (S61 P61-2).
- Productor A = `0x437ab474` (tramo `0x437ab502..0x437ab50e`): escribe solo si `bit6(G[0xD]) == 0`. Comprobación del bit: `movs r1,#6; ldrb r0,[r5,#0xd]; bl 0x43aeb0cc; cbnz` donde `0x43aeb0cc = (r0 >> r1) & 1` (bytes `asrs; and #1; bx lr`). Lee `G[0x168]` / `G[0x16A]` con `ldr r5,[r4,r3]` en `0x437ab506`. Escribe 6 pares idénticos (`strh` ×12) de `(G[0x168], G[0x16A])` → bloque `obj+0xe20`. **VERIFICADO** (S61 P61-3; bytes + emulación del tramo real: `G[0xD] ∈ {0x00,0xBF}` publica; `{0x40,0xFF}` no).
- Escritor que rellena `G+0x168/+0x16A` (quién pone esos offsets del global G): **NO LOCALIZADO**. 232 funciones cargan G; el taint de registros no halla store a esos offsets; no hay referencias pc-relativas directas a G; no hay memcpy hacia G detectado. **NO_VERIFICADO**.

### 1.3 Escritor B de `G[0xD]` / bloque (gate `[[p]+0x3a]==1`) — EVIDENCIA REA de esta sesión

**VERIFICADO (evidencia REA cruda: `procedure_pseudo_code(0x43aecbec)` del log compartido, misma binary).**

```c
void FUN_43aecfac(int *param_1)   // 0x43aecbec
{
  /* 9 llamadas previas: 0x43aec79a, 43aec7b8, 43aec87a, 437ab5c4,
     437ab6e4, 437abd3c, 43aecbd6, 43aed11e, 43aec8ba */
  if (*(char *)(*param_1 + 0x3a) == '\x01') {          // [[p]+0x3a]==1  (gate B)
    u16 *puVar2 = FUN_43ae8504();                      // acceso 0x43ae8504 -> destino u16*
    int iVar5 = param_1[2];                            // p + 8  (= obj8)
    puVar2[0] = *(u16 *)(iVar5 + 0x48);                // *(u16*)(p+0x50) = obj8+0x48
    puVar2[1] = *(u16 *)(iVar5 + 0x4a);                // obj8+0x4a
    puVar2[2] = *(u16 *)(iVar5 + 0x4c);                // obj8+0x4c
    puVar2[3] = *(u16 *)(iVar5 + 0x4e);                // obj8+0x4e
    puVar2[4] = *(u16 *)(iVar5 + 0x50);                // obj8+0x50
    puVar2[5] = *(u16 *)(iVar5 + 0x52);                // obj8+0x52
    puVar2[6] = *(u16 *)(iVar5 + 0x54);                // obj8+0x54
    puVar2[7] = *(u16 *)(iVar5 + 0x56);                // obj8+0x56
    puVar2[8] = *(u16 *)(iVar5 + 0x5c);                // obj8+0x5c
    puVar2[9] = *(u16 *)(iVar5 + 0x5e);                // obj8+0x5e
    u32 uVar4 = (u32)*(byte *)(iVar5 + 3);             // *(byte*)(p+0xB)
    if (2 < uVar4 - 0x0d) uVar4 = 0x0d;                // índice acotado <= 0x0D (G[0xD]=13)
    u32 uVar3 = FUN_437a5a6c(param_1, uVar4,
                              *(byte *)(iVar5 + 2), iVar5, ...);
    puVar2[10] = (u16)uVar3;                           // 6.º par, lo
    puVar2[11] = (u16)(uVar3 >> 16);                   // 6.º par, hi
  }
  return;
}
```

- Escritor B = `0x43aecbec` (tramo `0x43aecbf0..0x43aecbf8`): escribe solo si `[[p]+0x3a]==1`, vía acceso `0x43ae8504`. Escribe 12 u16 (24 B = bloque `obj+0x2be..0x2d0` ≡ `obj+0xe20..0xe37`): 10 valores directo de `obj8+0x48,0x4a,0x4c,0x4e,0x50,0x52,0x54,0x56,0x5c,0x5e`; el par final (`dest[10],dest[11]`) desde `FUN_437a5a6c` indexado por `byte(p+0xB)` acotado a ≤0x0D. `obj8 = obj+0x2cc` (copia de 0x244 B, familia `0x4379fc9e`/`0x43aece72`).
- Escritor que pone `G[0xD]` (especialmente a 1): **NO LOCALIZADO**. "Ningún escritor a 1 localizado en ningún constructor." Borrado a 0 cuando `G[0xD]` bit6==1 en `0x437a9a7c` (`0x437a9b8a..0x437a9ba0`). **NO_VERIFICADO**.

### 1.4 Escritor del bloque `obj+0xe20..0xe37` (acceso `0x43ae8504`)

- Acceso `0x43ae8504` (= `0x437876dc() + 0xE20`) → bloque de 24 B. Equivale a `obj+0xe20..0xe37` del registro de estado `obj+0xe04..0xe53`. **VERIFICADO** (S61 P61).
- Dos productores vía este acceso: **A** (`0x437ab510`/`0x437ab474`, 6 pares idénticos de `G[0x168]/G[0x16A]`) y **B** (`0x43aecbec`, arriba).
- 6.º par ← tabla BK4 `0x300AB` (entrada `0x300AB`, 232 B; idéntica en 5 `CX77500`: 18×`(0x2EA0,0x6028)`). Servicio `+0x27c` (envoltorio `0x435613cc`, `svc(0,0x300ab,T)`) corresponde por desplazamiento (+0x24) a `Backup_read_setting_attr` de `liro.ko`: **INFERENCIA**, semántica del servicio no verificada.

---

## 2. Valores M/Tv/clk alcanzables (0x0B / 0x2F) y `clk` vs histogramas

- **Modos `0x0B` / `0x2F` — alcanzables: NO_VERIFICADO** (S59, repetido en S61). No se declara ningún estado completo `(modo, M, Tv, clk, N, svr, VdNum, flags, svd, shd, spl)` demostrado. El único estado "alcanzable" declarado es 0 (estado PERMITIDO sintético en `analysis/s61/e3_chain.json`: bloque `1108110c3e003f003f04400040034000000050009a02e2860`).
- **Origen de M/Tv/clk:** no sale de constantes de construcción (el constructor deja el bloque a cero). No hay productor real localizado que enlace los pares del bloque `obj+0xe20` con los productores AE (`0x4383d4d0`, `0x4383c9dc`). **Sin evidencia de que los pares sean entradas de esos productores.** Vínculo M ↔ Tv/clk: **sin evidencia**.
- **¿Es `clk` el objeto de histogramas? NO.** Corregido en S60: `clk` NO es el objeto de histogramas (corrige S58-A §5). `VdNum = max(0, raw − 0x3000)`.
- Los pares del bloque `obj+0xe20` se comportan como límites inferior/superior u16 con margen ±0x400 y reordenación `lo<hi`; unidad desconocida (`0x400` sugiere Q10, no probado). Hipótesis "M = temporización" **debilitada, no descartada**.
- Mensajes `0x1000/0x1001` = lista blanca de modos `{0x0b, 0x35, 0x37, 0x38}`; receptor sin localizar. Emisor del payload (`0x438069f0`, casos 4/10, `obj+0x568=2`) y el origen real de M/Tv/clk: **no localizado**.

---

## 3. Cadena HS_Main → petición 9 → VD_Pre y publicación; relación con fin de integración

- `HS_Main = 0x4378fef4` (manejador de sincronía; tareas TC/Last1st/Last2nd, EC, LC, YC, Lens). Emite **petición 9** mediante `call 0x437907a6` → `0x43b00ed8` → `0x43806398/0x4380632c` → `0x438061c4` (cola `0x3030f`). `0x43b00ed8` tiene una única llamada desde `0x437907a6` dentro de HS_Main (VERIFICADO, bytes, S61 P61-5). `get_call_graph(0x4378fef4)` **no obtenido esta sesión** (daemon caído).
- Despachador de mensajes = `0x43806e38` (tarea, recv `0x3030f`, timeout −1) → `0x438069f0` → libera. Tabla TBH base PC `0x43806a04`/`0x43806a08`; casos 4/10 → `0x43806c28`/`0x43806d06`. Emisores de respuesta `0x43b00fe6` (caso 3→4) y `0x43b00f62` (caso 9→10) → `0x43806400` → cola `0x8003030f`. `0x8003030f` ≈ alias de `0x3030f` (**INFERENCIA**).
- `VD_Pre = 0x43792a0c` (publicación) → `0x43b00dd4` (publica el bloque si `obj+0x57c≠0`; fuente `obj+0xd64`). `procedure_callers(0x43792a0c)` falló esta sesión.
- **Orden estático:** HS_Main → respuesta 10 → staging → VD_Pre. **Petición 3:** sin emisor localizado.
- **Relación con fin de integración:** el tráfico de mensajes es sincronía/estado por VD (ciclo V del sincronizador), no de una captura concreta. No hay dependencia de modo fotográfico localizada (el emisor no consulta `0x0B/0x2F`). No hay evidencia de que HS_Main/VD_Pre programe el fin electrónico de exposición. **Fin electrónico de integración: NO_VERIFICADO** (S51: A=NO, B=NO, C=NO; S57 intacto; ninguna secuencia de registros se reescribe al terminar).
- Hipótesis abierta (S61): si el fin de exposición se planifica en el sincronizador, el sitio donde buscarlo es `HS_Main` (`0x4378fef4`) / `VD_Pre` (`0x43792a0c`), pero es solo hipótesis.

---

## 4. Tabla VERIFICADO vs NO_VERIFICADO (direcciones exactas)

| # | Afirmación | Estado | Dirección(es) exactas | Base |
|---|---|---|---|---|
| T2-1 | P0 `0x43861ed0` lee `obj+0x2be..0x2d0` → escribe `obj+0x310..0x334` | VERIFICADO (conocimiento previo S61) | `0x43861ed0`; lectores `0x43862bc4`, `0x43863668` | bytes + Unicorn (S61 e3) |
| T2-2 | Escritor real de `obj+0x2be..0x2d0` | **NO_VERIFICADO** | candidatos: `0x4383075c`, `0x437f1414`, `0x43ae9e92`, `0x43894524`, `0x438f171c` | S61 §bloqueantes |
| T2-3 | `G = 0x43e964a4` (GOT+0x21a0); no objeto 0xF20 B | VERIFICADO | `0x43e964a4`; `0x4401eee4+0x21a0` | bytes (S61 P61-2) |
| T2-4 | Escritor A `0x437ab474` escribe si `bit6(G[0xD])==0`; 6 pares `(G[0x168],G[0x16A])` | VERIFICADO | `0x437ab474`; `0x437ab502..0x437ab50e`; `0x437ab506`; `0x43aeb0cc` | bytes + emulación (S61 P61-3) |
| T2-5 | Escritor de `G+0x168/+0x16A` | **NO_VERIFICADO** | (ninguna dirección) | S61 P61-3 |
| T2-6 | Escritor de `G[0xD]` (ponerse a 1) | **NO_VERIFICADO** | (ninguna dirección; borrado a 0 en `0x437a9a7c`) | S61 §selección A/B |
| T2-7 | Escritor B `0x43aecbec` escribe si `[[p]+0x3a]==1`; 5 pares `obj8+0x48..0x5e` + 6.º por `0x437a5a6c` vía `0x43ae8504` | **VERIFICADO (REA esta sesión)** | `0x43aecbec`; `0x43aecbf0..0x43aecbf8`; `0x437a5a6c`; `0x43ae8504`; `0x43aece72..0x43aece90` | pseudocódigo REA (log compartido, mismo digest) |
| T2-8 | Acceso bloque `obj+0xe20`: `0x43ae8504` (= `0x437876dc()+0xE20`) | VERIFICADO | `0x43ae8504` | S61 P61 |
| T2-9 | Publicación `obj+0xe20` → `obj+0xDD0`: `0x43b00da0` copia 80 B a `obj+0xdb4`; `0x43b00dd4` si `obj+0x57c≠0` | VERIFICADO | `0x43b00da0`, `0x43b00dd4`, `obj+0xd64`, `obj+0x57c`, `obj+0x568=2` | S59/S60 |
| T2-10 | Valores M/Tv/clk alcanzables `0x0B`/`0x2F` | **NO_VERIFICADO** | (ninguna) | S59, S61 |
| T2-11 | `clk` es objeto de histogramas | NO (refutado) | — | S60 (corrige S58-A §5) |
| T2-12 | Petición 9: `HS_Main 0x4378fef4` → `0x437907a6` → `0x43b00ed8` → cola `0x3030f` | VERIFICADO | `0x4378fef4`, `0x437907a6`, `0x43b00ed8`, `0x43806398/0x4380632c`, `0x438061c4` | S61 P61-5 |
| T2-13 | Publicación `VD_Pre 0x43792a0c` → `0x43b00dd4` | VERIFICADO | `0x43792a0c`, `0x43b00dd4` | S61 P61-5 |
| T2-14 | Fin electrónico de integración | **NO_VERIFICADO** | — | S51, S57, S61 |

**Conclusión del tema 2:** no se localizó el productor real de M/Tv/clk (escritor de `obj+0x2be..0x2d0`, escritor de `G+0x168/16A`, `G[0xD]`). Los valores alcanzables `0x0B/0x2F` no se demostraron. `clk` no es objeto de histogramas. El bloque `obj+0xe20` contiene pares ventana (±0x400), no tiempos demostrados. Escritor B (`0x43aecbec`) es el único hallazgo REA nuevo de esta sesión.

---

## 5. Próximo paso exacto concreto

Reiniciar el demonio `analysis/rea-independent/run/rea-tema2.sock` (el anterior murió por watchdog: RSS ≈2 GB vs pico Ghidra ~2,3 GB; considerar `REA_DAEMON_RSS_MAX_MB>2048` o `GHIDRA_MAXMEM` mayor), esperar `rea-tema2.sock.ready` y ejecutar el lote pendiente:

```
q.py run/rea-tema2.sock /tmp/opencode/tema2-calls.json /tmp/opencode/tema2-out.jsonl
```

Consultas prioritarias para cerrar las brechas: `analyze_function(0x437ab474)` (escritor A), `xrefs(0x43e964a4)` y `xrefs(0x43861ed0)` (escritores de G y de P0), `get_call_graph(0x4378fef4)` (forward, HS_Main), y `trace_native_values` sobre `0x43861ed0` y `0x437ab474` (`max_depth` suficiente) para hallar quién rellena `obj+0x2be..0x2d0`. Sembrar Thumb en `0x4378fef4` (HS_Main), `0x43792a0c` (VD_Pre), `0x43b00ed8` (petición 9) y emular `0x437a9a7c`/constructores con `G[0xD]` y `src+0xb4` derivados de un modo real. Cerrar la sesión con `q.py run/rea-tema2.sock --shutdown` y verificar que no queden procesos `session_daemon.py`.

---

*Fin del informe. Todo estático; sin firmware ejecutado, sin cámara, sin flasheo. Hecho = evidencia REA/bytes citada con dirección; Inferencia = marcado como tal; NO_VERIFICADO = sin evidencia que lo demuestre (una consulta REA vacía no prueba ausencia).*
