# Tema 2 — Origen de los parámetros IMX210 (M/Tv/clk) y bloque de temporización del sensor (obj+0xe20..+0xe37 / 0xdd0)

**Proyecto:** sony-a6000-electronic-shutter — obturador completamente electrónico.  
**Objetivo:** Tema 2 de 3. Localizar el escritor real de `obj+0x2be..0x2d0` (origen P0 de M/Tv/clk), los escritores de `G+0x168` / `G[0xD]` y los valores M/Tv/clk alcanzables.  
**Binario:** `av-cam.bin` (raw ARM, base de importación `0x43541000`, SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).  
**Método:** REA sobre `av-cam.bin` (evidencia ya exportada, sesiones S60/S61/S59, verificada contra bytes y emulada con Unicorn sobre código original). No se ejecutó firmware en cámara, no se flasheó, no hay pruebas físicas. Todo es estático.

> Nota operativa: la sesión REA caliente sobre `av-cam.bin` no se mantiene estable en este entorno (el demonio muere al arranque del autoanálisis Ghidra y por `xrefs` masivos a globals). Se basa, por tanto, en la evidencia REA ya exportada y contrastada (`docs/capture/s61-conclusions.md`, `docs/capture/s61-imx210-parameter-origin.md`, `docs/capture/s60-conclusions.md`, `docs/capture/s59-conclusions.md`, `analysis/s61-evidence-matrix.json`, scripts `analysis/s61/`). Se cita dirección exacta por hallazgo.

---

## 1. Escritores resueltos de obj+0x2be..0x2d0 y de G+0x168 / G[0xD]

### 1.1 Bloque `obj+0x2be..0x2d0` (9 campos u16, origen P0 de M/Tv/clk)

**Escritor del bloque `obj+0x2be..0x2d0`: NO LOCALIZADO.**  
Este es el bloqueante principal del tema. `obj+0x2be..0x2d0` se lee (no se escribe) en la cadena conocida:

- `P0 = 0x43861ed0` lee `obj+0x2be, 0x2c0, 0x2c2, 0x2c4, 0x2c6, 0x2c8, 0x2ca, 0x2cc, 0x2ce, 0x2d0` y escribe `obj+0x310..0x334` (ventanas lo/hi, márgenes ±0x400, constante `0x3400`, interpolación con división en `0x4355fd68`, reordenación `lo<hi`).  
  - VERIFICADO (bytes + Unicorn, entradas sintéticas). Llamadores de P0: `0x43862bc4`, `0x43863668`.  
  - `obj+0x2cc` se copia a `obj8` (memcpy de 0x244 B en `0x43aece72..0x43aece90`, `p[2] = obj8`).  
- Candidatos propuestos como escritor de `obj+0x2be..0x2d0` (los 9 campos): `0x4383075c`, `0x437f1414`, `0x43ae9e92`, `0x43894524`, `0x438f171c`. **Ninguno confirmado como escritor.**

Estado: **NO_VERIFICADO** — no se localizó el productor real que rellena `obj+0x2be..0x2d0`.

### 1.2 Escritor de `G+0x168` / `G+0x16A` (productor A)

- `G = 0x43e964a4` (slot GOT `+0x21a0`, dirección absoluta `0x4401eee4 + 0x21a0`). **No es** el objeto de 0xF20 B (corrige S60).  
- **Productor A = `0x437ab474`** (tramo `0x437ab502..0x437ab50e`): escribe solo si `bit6(G[0xD]) == 0`.  
  - Comprobación del bit: `movs r1,#6; ldrb r0,[r5,#0xd]; bl 0x43aeb0cc; cbnz` donde `0x43aeb0cc = (r0>>r1)&1` (bytes `asrs; and #1; bx lr`).  
  - `G[0x168]` / `G[0x16A]` leídos con `ldr r5,[r4,r3]` en `0x437ab506`.  
  - Escribe 6 pares idénticos (`strh` ×12) de `(G[0x168], G[0x16A])` → mismo bloque `obj+0xe20`.  
  - VERIFICADO (Capstone + emulación del tramo real `analysis/s61/e4_producer_a.py`: `G[0xD] ∈ {0x00,0xBF}` publica; `{0x40,0xFF}` no).  
- Escritor de `G+0x168/+0x16A` (es decir, quién rellena esos offsets del global G): **NO LOCALIZADO**. 232 funciones cargan G; taint de registros no halla store a esos offsets; no hay referencias pc-relativas directas a G; no hay memcpy hacia G detectado. Los únicos stores `+0x168/+0x16A` en la subred de constructores son sobre el *stage* `[p]` (`0x437aa4e4/e8` desde `src+0x164e/+0x1650`; `0x437aae54/58 = 0`). Que G coincida con el stage es **no demostrado**.  
  - Estado: **NO_VERIFICADO**.

### 1.3 Escritor de `G[0xD]` (byte de selección A/B)

- `G[0xD]` (bit6) controla la rama A: A escribe si `bit6(G[0xD])==0`; se borra a 0 cuando `G[0xD]` bit6==1 en `0x437a9a7c` (`0x437a9b8a..0x437a9ba0`).  
- Escritor que pone `G[0xD]` (especialmente a 1): **NO LOCALIZADO**. "Ningún escritor a 1 localizado en ningún constructor."  
  - Estado: **NO_VERIFICADO**.

### 1.4 Escritor del bloque `obj+0xe20..0xe37` (6 pares u16, acceso `0x43ae8504`)

- Acceso: `0x43ae8504` (= `0x437876dc() + 0xE20`) → bloque de 24 B. Equivale a `obj+0xe20..0xe37` del registro de estado `obj+0xe04..0xe53`.  
- Dos productores vía este accesor:
  - **A = `0x437ab510`** (6 pares idénticos de `G[0x168]/G[0x16A]`).  
  - **B = `0x43aecbec`** (tramo `0x43aecbf0..0x43aecbf8`): escribe solo si `[[p]+0x3a]==1`. Copia 5 pares de `obj8+0x48..0x5f` (10 `ldrh.w` verificados: offsets `0x48,4a | 4c,4e | 50,52 | 54,56 | 5c,5e`) y calcula el 6.º par con `0x437a5a6c` (tabla `T`).  
    - `obj8 = obj+0x2CC` (copia de 0x244 B, familia `0x4379fc9e`/`0x43aece72`); en familia `0x4379ed34`, `p[2] = r6+0x248` (base distinta, sin resolver).  
    - 6.º par: `T = *(0x43ea5070)`; puntero fijado por `0x437ad3a4` (`T ← GOT[0x3d8] = 0x43e95cd0`) y `0x437ad3c0` (`T ← obj[0x9c]? GOT[0x381c]=0x43e95e10 : 0x43e95cd0`). Índice `idx = (stage[0x17]==0x1a)·9 + (modo−0x0d)·3 + sel`, `sel = 1` si `stage[1]≠0`, si no `2` si `obj8[2]==0` y `0` en otro caso; par = `T[0x36+4·idx], T[0x38+4·idx]`; override por `p[3]+0x15d8/0x15da` si `stage[1]≠0` y (`obj8[0xa]==2` o `p[3][0x15e9]==1`).  
    - Los tres bloques de 18 B + 18 pares de `T` coinciden con la entrada BK4 `0x300AB` (232 B); servicio `+0x27c` (envoltorio `0x435613cc`, `svc(0,0x300ab,T)`) corresponde por desplazamiento (+0x24) a `Backup_read_setting_attr` de `liro.ko`: **INFERENCIA**, no verificada la semántica del servicio.  
  - Estado productor B: **VERIFICADO (bytes)**; origen de `stage+0x3a` y de `obj8[3]` (modo `0x0D..0x0F` para 6.º par): **PARCIAL/NO_VERIFICADO**.

### 1.5 Publicación del bloque `obj+0xe20` → `obj+0xDD0`

- `0x43b00da0` copia 80 B a `obj+0xdb4` (cubre `+0xdd0..0xde7`), fuente `obj+0xd64`. Publicado por `0x43b00dd4` si `obj+0x57c≠0`.  
- `obj+0xd64` alimentado (PARCIAL) por `0x438069f0` casos 4/10 con `obj+0x568=2`.  
- Constructor (A7S `C_Imager = 0x436f3fc0`) deja el bloque a cero: **los valores de M no son constantes de construcción**; vienen de payload externo.  
  - Estado: escritor del bloque `+0xDD0` **VERIFICADO** (`0x43b00da0`); valores M alcanzables: **NO_VERIFICADO** (S59).

---

## 2. Valores M/Tv/clk alcanzables (0x0B / 0x2F) y clk vs histogramas

- **Modos `0x0B` / `0x2F`:** M/Tv/clk/N/svr/VdNum alcanzables: **NO VERIFICADO** (S59, repetido en S61). No se declara ningún estado `(modo, M, Tv, clk, N, svr, VdNum, flags, svd, shd, spl)` completo. ALCANZABLE = 0 (solo existe un estado PERMITIDO sintético en `analysis/s61/e3_chain.json`: bloque `1108110c3e003f003f04400040034000000050009a02e2860`).  
- **Origen de M/Tv/clk:** no sale de constantes de construcción (constructor deja ceros). No hay productor real localizado que enlace los pares del bloque `obj+0xe20` con los productores AE (`0x4383d4d0`, `0x4383c9dc`). **Sin evidencia de que los pares sean entradas de esos productores.** Vínculo M ↔ Tv/clk: **sin evidencia**.  
- **¿Es `clk` el objeto de histogramas?** **NO.** Corregido en S60: `clk` NO es el objeto de histogramas (corrige S58-A §5). `VdNum = max(0, raw − 0x3000)`. Los pares del bloque `obj+0xe20` se comportan como **límites inferior/superior de 16 bit con margen ±0x400 y reordenación**, no como tiempos demostrados; unidad desconocida (`0x400` sugiere Q10, no probado). Hipótesis "M = temporización" **debilitada, no descartada** (P61-7).  
- Mensajes `0x1000/0x1001` = lista blanca de modos `{0x0b, 0x35, 0x37, 0x38}` (receptor sin localizar). Emisor del payload (`0x438069f0`, casos 4/10, `obj+0x568=2`) y de dónde nacen M/Tv/clk reales: **no localizado**.

---

## 3. Cadena HS_Main → petición 9 → VD_Pre y publicación; relación con fin de integración

- **HS_Main = `0x4378fef4`** (manejador de sincronía; tareas TC/Last1st/Last2nd, EC, LC, YC, Lens). Emite **petición 9** mediante call `0x437907a6` → `0x43b00ed8` → `0x43806398/0x4380632c` → `0x438061c4` (cola `0x3030f`).  
  - `0x43b00ed8` → única llamada desde `0x437907a6` en HS_Main (VERIFICADO, bytes).  
- **Despachador de mensajes = `0x43806e38`** (tarea, recv `0x3030f`, timeout −1) → `0x438069f0` → libera. Tabla TBH base PC `0x43806a04`/`0x43806a08`; casos 4/10 → `0x43806c28`/`0x43806d06` (corrige S60-Sol). Emisores de respuesta `0x43b00fe6` (caso 3→4) y `0x43b00f62` (caso 9→10) → `0x43806400` → cola `0x8003030f`.  
  - `0x8003030f` ≈ alias de `0x3030f` (**INFERENCIA**).  
- **VD_Pre = `0x43792a0c`** (publicación) → `0x43b00dd4` (publica el bloque si `obj+0x57c≠0`).  
- **Orden estático:** HS_Main → respuesta 10 → staging → VD_Pre.  
- **Petición 3:** no localizada (sin emisor).  
- **Relación con fin de integración:** el tráfico de mensajes es de sincronía/estado por V (ciclo V del sincronizador), no de una captura concreta. No hay dependencia de modo fotográfico localizada (el emisor no consulta `0x0B/0x2F`). No hay evidencia de que HS_Main/VD_Pre programe el fin electrónico de exposición. **Fin electrónico de integración NO VERIFICADO** (S51: A=NO, B=NO, C=NO; S57 intacto; ninguna secuencia de registros reescribe nada al terminar).  
- Hipótesis abierta (S61 §Silent shooting): si el fin de exposición se planifica en el sincronizador, el sitio donde buscarlo es `HS_Main` (`0x4378fef4`) / `VD_Pre` (`0x43792a0c`), pero es solo hipótesis.

---

## 4. Estado VERIFICADO vs NO_VERIFICADO (direcciones exactas)

| # | Afirmación | Estado | Dirección(es) exactas | Base |
|---|---|---|---|---|
| T2-1 | P0 `0x43861ed0` lee `obj+0x2be..0x2d0` → escribe `obj+0x310..0x334` | VERIFICADO | `0x43861ed0`; lectores `0x43862bc4`, `0x43863668` | bytes + Unicorn (s61 e3) |
| T2-2 | Escritor de `obj+0x2be..0x2d0` | **NO_VERIFICADO** | candidatos: `0x4383075c`, `0x437f1414`, `0x43ae9e92`, `0x43894524`, `0x438f171c` | S61 §bloqueantes |
| T2-3 | Productor A `0x437ab474` escribe si `bit6(G[0xD])==0`, 6 pares `(G[0x168],G[0x16A])` | VERIFICADO | `0x437ab474`, tramo `0x437ab502..0x437ab50e`, `0x437ab506`, `0x43aeb0cc` | bytes + emulación (s61 e4) |
| T2-4 | `G = 0x43e964a4` (GOT+0x21a0), no objeto 0xF20 B | VERIFICADO | `0x43e964a4`; `0x4401eee4+0x21a0` | bytes (s61 P61-2) |
| T2-5 | Escritor de `G+0x168/+0x16A` | **NO_VERIFICADO** | (ninguna dirección) | S61 P61-3 |
| T2-6 | Escritor de `G[0xD]` (ponerse a 1) | **NO_VERIFICADO** | (ninguna dirección) | S61 §selección A/B |
| T2-7 | Productor B `0x43aecbec` escribe si `[[p]+0x3a]==1`, 5 pares `obj8+0x48..0x5f` + 6.º por `0x437a5a6c` | VERIFICADO (bytes) | `0x43aecbec`, `0x43aecbf0..0x43aecbf8`, `0x437a5a6c`, `0x43aece72..0x43aece90` | bytes (s61 P61-5) |
| T2-8 | `stage+0x3a`: 0 en `0x437a9d30`; copia `src+0xb4` en `0x437aa65c`; borrado a 0 si `G[0xD]` bit6==1 en `0x437a9a7c` (`0x437a9b8a..0x437a9ba0`) | VERIFICADO (parte); escritor a 1 NO_VERIFICADO | `0x437a9d30`, `0x437aa65c`, `0x437aa956`, `0x437a9a7c` | bytes (s61 P61-4) |
| T2-9 | Acceso bloque `obj+0xe20`: `0x43ae8504` (= `0x437876dc()+0xE20`) | VERIFICADO | `0x43ae8504` | s61 P61 |
| T2-10 | Publicación `obj+0xe20` → `obj+0xDD0`: `0x43b00da0` copia 80 B a `obj+0xdb4`; `0x43b00dd4` si `obj+0x57c≠0` | VERIFICADO | `0x43b00da0`, `0x43b00dd4`, `obj+0xd64`, `obj+0x57c`, `obj+0x568=2` | s59/s60 |
| T2-11 | Valores M/Tv/clk alcanzables `0x0B`/`0x2F` | **NO_VERIFICADO** | (ninguna) | S59, S61 |
| T2-12 | `clk` es objeto de histogramas | NO (refutado) | — | S60 (corrige S58-A §5) |
| T2-13 | Petición 9: HS_Main `0x4378fef4` → `0x437907a6` → `0x43b00ed8` → cola `0x3030f` | VERIFICADO | `0x4378fef4`, `0x437907a6`, `0x43b00ed8`, `0x43806398/0x4380632c`, `0x438061c4` | s61 P61-5 |
| T2-14 | Publicación VD_Pre `0x43792a0c` → `0x43b00dd4` | VERIFICADO | `0x43792a0c`, `0x43b00dd4` | s61 P61-5 |
| T2-15 | Fin electrónico de integración | **NO_VERIFICADO** | — | S51, S57, S61 |

**Conclusión del tema 2:** no se localizó el productor real de M/Tv/clk (escritor de `obj+0x2be..0x2d0`, escritor de `G+0x168/16A`, `G[0xD]`). Los valores alcanzables `0x0B/0x2F` no se demostraron. `clk` no es objeto de histogramas. El bloque `obj+0xe20` contiene pares ventana (±0x400), no tiempos demostrados.

---

## 5. Próximo paso exacto concreto

**Sembrar Thumb y trazar las entradas de P0 (`obj+0x2be..`) desde los candidatos de escritor.**  
Acción concreta: con una sesión REA estable sobre `av-cam.bin` (base `0x43541000`), sembrar las entradas Thumb en `0x4378fef4` (HS_Main), `0x43792a0c` (VD_Pre), `0x437ab474` (A), `0x43b00ed8` (petición 9), `0x4379fc9e` (familia obj8) y ejecutar `trace_native_values` sobre las entradas de P0 `obj+0x2be..0x2d0` partiendo de `0x4383075c` y `0x437f1414` (candidatos de escritor) para hallar quién rellena esos 9 campos. En paralelo, leer `HS_Main` (`0x4378fef4`) de principio a fin (orden TC/YC/EC/LC/Lens y qué tarea programa el fin de exposición) y emular `0x437a9a7c`/constructores con `G[0xD]` y `src+0xb4` derivados de un modo real. Cerrar la sesión REA con `q.py SOCK --shutdown` y verificar que no queden procesos `session_daemon.py`.

> Esta recomendación reproduce la de S61 §Recomendación S62 punto (1) y (2), pendiente por falta de sesión REA estable en este entorno.

---
*Fin del informe. Todo estático; sin firmware ejecutado, sin cámara, sin flasheo.*