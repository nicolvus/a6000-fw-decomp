# S54-C — Tipo de mecanismo 0 en Darwin A6000 (20-10-2026)

Análisis estático (capstone + diff estructural A6000 3.21 ↔ A7S 3.20). Base ROM `0x4200`. Pruebas: `tests/test_s54_p4c.py` (clases `MechanismTypeZero`).
**Prohibido y no hecho:** activar tipo 0 en cámara, tocar EEPROM o valores persistentes.

## 1. Origen del valor (PARCIAL)

- `0x20c74` = `0x1b080(0)&7` ∈ {1,2,3}; cualquier otro valor (incl. 0) → 0. A7S: `0x216e8` con `0x1b5e8` (misma forma).
- `0x1b080(ch)`: si `[0x200002c0+ch]≠0` devuelve `[0x20000000+0x50+ch]`, si no 0 (literales `0x1b0e0/0x1b0e4`, VERIFICADO).
- El indicador de validez `[0x200002c0+ch]` lo fija el manejador `0x1b0b2`, **entrada 33 de la tabla de 48 manejadores `0x2a1a0`** (categoría `0x2d`):
  mensaje `{idx<0x18, 1/0}`: pone 1 solo si `[0x20000050+idx]≠0`. Sin llamadores directos (se invoca por tabla). VERIFICADO.
- **NO localizado:** quién escribe el valor `[0x20000050+ch]`: no hay `strb …,[r,#0x50]` ni `0x20000050` literal; la estructura `0x20000000` se llena por
  copias/mensajes. **INFERENCIA/HIPÓTESIS:** el valor y su habilitación llegan de BIONZ por el enlace MSS (la familia de cadenas `Sens:AdjCmd DwnCamera`,
  `SaveUsr:Read CAM`, `Sens:BkSyncCb CAIF` de `av-cam` es compatible), o de una constante de fábrica/ajuste. No se probó.
- Por tanto el tipo 0 **no** parece un modo fotográfico: es el estado «sin configuración válida/ausencia de mecanismo» del byte de configuración (H54-6: PARCIAL a favor).

## 2. Consumidores del tipo (VERIFICADO, 19 funciones A6000 ↔ 19 A7S)

A6000: `0x201b0, 0x203b2, 0x2041e, 0x20544, 0x206ec, 0x20734, 0x207e8, 0x2081c, 0x2083c, 0x20aa4, 0x20c90, 0x20cb2, 0x20cd4, 0x20d00, 0x20d26, 0x20e0e,
0x20e98, 0x20f5e, 0x20fc0` (A7S: `0x20b84…0x21a5a`, mismo orden). Efectos con tipo 0 (A6000):

| Elemento | Efecto | Evidencia |
|---|---|---|
| P4D (`0x20c90`, `0x20cb2`) | nunca escrito (solo tipo 1/2 y ≠3) | filtro `0x20c74` |
| P4E (`0x20cd4`, `0x20d00`, y en rutas largas) | nunca escrito | íd. |
| **P4C** (`0x20d26/0x20e0e/0x20e98`) | **sí se escribe (←0)**: rama «sin mecanismo» | informe 1 |
| Temporización/espera (`0x93e6`) y marca `S+0x180` (`0x210c0`) | **se mantienen** | cuerpo `0x20dda`, `0x20e88`, `0x20f2a` |
| Seguimiento ADC de fases (`0x20734`, `0x2083c`) | **omitido** (`S+0x153←0`) | `0x2077c/0x20780`, `0x20840/0x20844` |
| Rutas de reposición/aborto (`0x203b2`, `0x206ec`, diferidos `0x20a8a/0x20aa4`) | sin acción de bobina | todas pasan por el filtro |
| Respuestas CAIF/estados | **no cambian por tipo**; no se encontró otro consumidor del byte | NO exhaustivo |

Respuesta a C.2 (de las 7 opciones): **1 y 5 sí** (solo omite bobinas y la verificación ADC/posición); 2 y 3 no hay indicios; 4 no (P4C se mantiene);
6 probable (configuración de hardware, ver §1); 7 NO VERIFICADO. «Desactiva funciones de protección o verificación»: sí, el seguimiento ADC.

## 3. Comparación con Silent de A7S (VERIFICADO por diferencia estructural)

Alineación instrucción a instrucción de `0x20d26/0x20e0e/0x20e98` ↔ `0x217b2/0x218a0/0x2192e`: el **cuerpo es idéntico llamada a llamada**
(mapa: `0x51c0→0x5200`, `0x51f2→0x5232`, `0x5c88→0x5cca`, `0x5c9e→0x5ce0`, `0x93e6→0x8ad2`, `0x202c2→0x20c98`, `0x20408→0x20dfa`, `0x20c74→0x216e8`,
`0x210c0→0x21b5a`) salvo la condición de entrada: A7S añade el argumento `no_silent` y un `beq` extra a la rama sin mecanismo (`0x217d6`, `0x217da`).
La rama sin mecanismo de A7S (`0x2186c`) y la de A6000 (`0x20dda`) ejecutan la misma secuencia: `0x20408`, `0x210c0`, espera, **P4C←0**, tick.
Los diferidos (`0x214fa` ↔ `0x20aa4`) y el seguimiento ADC (`0x2116e/0x21282` ↔ `0x20734/0x2083c`) también coinciden salvo la condición añadida.

**Diferencias que quedan (importantes):**
1. **Reposición/aborto:** A7S llama a los escritores de bobina con `no_silent=1` (`0x20db4`, `0x2112a`, `0x21130`: `movs r0,#1`) → en Silent esas rutas **sí accionan**
   las bobinas si hay mecanismo (tipo≠0). En A6000 con tipo 0 **ninguna** ruta las acciona. Tipo 0 ⊋ Silent en supresión.
2. **Selección:** Silent llega por el paquete CAIF (`pkt[+0x12]&0x20`, mecanismo presente, tipos 1/2/3 compatibles); tipo 0 es global y persistente.
3. **HIPÓTESIS:** A7S Silent mantiene el mecanismo en reposo coherente porque existe hardware; el tipo 0 de A6000 asume que no lo hay (no probado).
4. Todo lo previo a Darwin (LIRO: clase 2/3, ruta `+0x748`, IMX235 `0x4e/0x4f`) no existe en A6000 (S52/S53).

**Pregunta crítica:** la ruta tipo 0 reproduce **el protocolo Darwin de una exposición Silent A7S (P4C incl.)** pero **no** la acción completa del sistema Silent:
ni el origen del estado (BIONZ) ni la rama de reposición que mantiene el mecanismo ni la parte sensor. Equivalencia funcional completa: **NO** demostrada.

Hipótesis: H54-5 **PARCIAL→reforzada** (Darwin: sí equivalente en exposición; no equivalente en reposición ni en el resto del sistema); H54-6 **PARCIAL**.
Próxima prueba: encontrar el emisor del byte de configuración (categoría `0x2d`, entrada 33) y el escritor de `[0x20000050+ch]`.
