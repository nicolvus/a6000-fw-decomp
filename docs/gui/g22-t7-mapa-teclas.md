# G22-E T7 — Mapa completo de teclas (estático, 12-11-2026)

Fuentes (fw 3.21, `nflasha15_unpacked_unpacked/lib` y `nflasha16 …/framework`), sin VM ni REA:
- `libScalarDaemon.so` `0x1cb50c–0x1cb6f4`: tabla de 61 pares `{evento InfraInput, código ScalarInput}` (8 B por par), que traduce los eventos del núcleo a las teclas de las apps.
- `com.sony.scalar.sysutil.ScalarInput` (decompilado en `analysis/decomp-apk/src/ScalarInput/…/ScalarInput.java`): nombres `ISV_KEY_*`/`ISV_DIAL_*` de esos códigos.
- `libObj.so` (`eb12512e…`) `0x109df4c–0x109e350`: tabla `{clave, nombre}` de 131 `KEY_TACT_*`/`KEY_*`/`SLIKEY_*` (la de §5.18z′).
- Mensaje del driver (`libObj` `0x806f88`, hilo `I-InputMain`, cola `0x7a0020`): 0x18 B `w0` clave, `w1`, `w2` valor, `w3`, `w4` índice físico (si `w4 < 0` se descarta; `0x807044`), `w5` indicadores (bit 0 → compara 0x10 B con la tabla física `this+0x24`, 0x24 B por índice, y descarta repeticiones; `0x807072`).

## 1. Coherencia con las 7 teclas medidas (VERIFICADO)

La tabla de `libScalarDaemon` reproduce **7 de 7** eventos medidos en el arnés (§5.18z′):

| Tecla | Clave `w0` (medida) | Índice `w4` (medido) | Evento | ScalarInput |
|---|---|---|---|---|
| arriba | `0x3` `KEY_TACT_UP` | `0x1` | `0x15010070` | `0x67` `ISV_KEY_UP` |
| abajo | `0x30` `KEY_TACT_DOWN` | `0x5` | `0x15010080` | `0x6c` `ISV_KEY_DOWN` |
| izquierda | `0x15` `KEY_TACT_LEFT` | `0x3` | `0x150100a0` | `0x69` `ISV_KEY_LEFT` |
| derecha | `0x1af` `KEY_TACT_RIGHT` | `0x14` | `0x15010090` | `0x6a` `ISV_KEY_RIGHT` |
| menu | `0x1ab` `KEY_TACT_MENU` | `0x11` | `0x15010110` | `0x202` `ISV_KEY_MENU` |
| intro | `0xe000000` (CEC) | `0x1bc` | `0x15010060` | `0xe8` `ISV_KEY_ENTER` |
| disparador (S2) | `0xa7` `KEY_TACT_CAP` | `0xe` | `0x15010030` | `0x206` `ISV_KEY_S2` |

## 2. Teclas nuevas: evento VERIFICADO, clave e índice NO_VERIFICADO

El **evento** sale de la tabla de `libScalarDaemon` (mismo método que valida las 7). La **clave** `w0` y el **índice físico** `w4` no están en ningún binario estático: la lista de 150 entradas de `InfraInput` (dispositivo 4) la construye `InputService::UpdateInputTable` (`libObj` `0x113c1c` → `SetEventKeyList`) en tiempo de ejecución; ni `0x15010070` ni `0x15010030` aparecen como constante en `libObj`. Donde hay un nombre `KEY_*` que encaja se da como **candidato**.

| Tecla A6000 | Evento | ScalarInput | Clave `w0` candidata | `w4` |
|---|---|---|---|---|
| Fn | `0x15010120` | `0x208` `ISV_KEY_FN` | sin nombre `KEY_*` | NO_VERIFICADO |
| Reproducción | `0x150100f0` | `0xcf` `ISV_KEY_PLAY` | `0x1f7` `KEY_TACT_PLAY` | NO_VERIFICADO |
| MOVIE | `0x15010050` | `0x203` `ISV_KEY_STASTOP` | `0x1f0` `KEY_TACT_STARTSTOP` | NO_VERIFICADO |
| C1 | `0x150103a0` | `0x26e` `ISV_KEY_CUSTOM1` | `0x66` `KEY_TACT_CUSTOM` | NO_VERIFICADO |
| C2 / Borrar (A6000: mismo botón) | `0x15010100` | `0x253` `ISV_KEY_DELETE` | `0x1f8` `KEY_TACT_DELETE` | NO_VERIFICADO |
| AEL | `0x15010140` | `0x214` `ISV_KEY_AEL` | sin nombre `KEY_*` | NO_VERIFICADO |
| Semipulsación S1 | `0x15010020` | `0x204` `ISV_KEY_S1_1` | NO_VERIFICADO | NO_VERIFICADO |
| S1 (2.º) | `0x150102b0` | `0x205` `ISV_KEY_S1_2` | NO_VERIFICADO | NO_VERIFICADO |
| Dial 1: estado / horario / antihorario | `0x15070030` / `0x1507003a` / `0x1507003b` | `0x20c` / `0x20d` / `0x20e` | NO_VERIFICADO | NO_VERIFICADO |
| Dial 2: estado / horario / antihorario | `0x15070040` / `0x1507004a` / `0x1507004b` | `0x20f` / `0x210` / `0x211` | NO_VERIFICADO | NO_VERIFICADO |
| Dial de modo (posición) | `0x15070050` | `0x23c` `ISV_KEY_MODE_DIAL` | `0x7025` `KEY_POS_MODE_DIAL` | NO_VERIFICADO |
| Objetivo montado | `0x15050010` | `0x212` | — | — |

Notas:
- **Rueda de control y dial de control:** el A6000 tiene una rueda (alrededor de la cruceta) y un dial superior. La tabla trae dos diales (`DIAL_1`, `DIAL_2`), y **cuál es cuál está NO_VERIFICADO**. `ISV_DIAL_KURU_*` (`0x209–0x20b`, «kuru» = rueda) no aparece en la tabla de la A6000. El candidato `KEY_OTHER_KURU_PON` (`0x7023`) es la pulsación, no el giro.
- **Giro de los diales:** los eventos `…3a`/`…3b` (horario/antihorario) sugieren que el núcleo los genera desde un evento de estado con valor (`w2` = paso o contador). Formato de `w2` NO_VERIFICADO; `InputService::callback_dial_signed_speed` (`libObj` `0x111c81`) es el que lo interpreta.
- **Dial de modo:** posiciones `ISV_KEY_MODE_*` (`0x216`–`0x227`: Auto `0x217`, Auto sup. `0x218`, P `0x219`, A `0x21b`, S `0x21a`, M `0x21c`, Película `0x220`, Barrido `0x21e`, SCN `0x221`…). La conversión del valor `w2` del evento `0x15070050` a posición la hace `InputService::callback_mode_dial` (`libObj` `0x112041`); los valores de `w2` son NO_VERIFICADO.

## 3. JSON para el mapa de teclas

Formato de `TECLAS` de `live.py`, `nombre: [clave w0, índice w4]`. Las 7 primeras están medidas. El resto lleva `null` donde falta el dato y el evento esperado para comprobarlo.

```json
{
  "medidas": {
    "arriba": [3, 1], "abajo": [48, 5], "izquierda": [21, 3], "derecha": [431, 20],
    "menu": [427, 17], "intro": [234881024, 444], "disparador": [167, 14]
  },
  "pendientes": {
    "fn":           {"clave": null,  "indice": null, "evento": "0x15010120", "isv": "0x208"},
    "reproduccion": {"clave": "0x1f7", "indice": null, "evento": "0x150100f0", "isv": "0xcf"},
    "movie":        {"clave": "0x1f0", "indice": null, "evento": "0x15010050", "isv": "0x203"},
    "c1":           {"clave": "0x66",  "indice": null, "evento": "0x150103a0", "isv": "0x26e"},
    "c2_borrar":    {"clave": "0x1f8", "indice": null, "evento": "0x15010100", "isv": "0x253"},
    "ael":          {"clave": null,  "indice": null, "evento": "0x15010140", "isv": "0x214"},
    "s1":           {"clave": null,  "indice": null, "evento": "0x15010020", "isv": "0x204"},
    "dial1":        {"clave": null,  "indice": null, "evento": "0x15070030", "giro": ["0x1507003a", "0x1507003b"]},
    "dial2":        {"clave": null,  "indice": null, "evento": "0x15070040", "giro": ["0x1507004a", "0x1507004b"]},
    "dial_modo":    {"clave": "0x7025", "indice": null, "evento": "0x15070050", "isv": "0x23c"}
  }
}
```

## 4. Cómo cerrar lo NO_VERIFICADO (para el agente de la VM)

Con el arnés, en una sola ejecución:
- volcar las 150 entradas de 0x44 B (`TRACEFN=8058ce TRACEDEREF=0:2c:a00`, §5.18w): `+0` clave, `+4` evento, `+0x24` (palabra 9) índice físico;
- filtrar por los eventos de §2. Eso da `w0` y `w4` exactos para cada tecla.

Para los diales, inyectar el evento de estado con `w2` = 1 o −1 y ver si gira la selección.
