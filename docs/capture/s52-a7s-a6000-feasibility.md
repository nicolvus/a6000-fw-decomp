# S52 — Viabilidad A6000 (consolidado, 19-10-2026)

Ningún resultado de S52 autoriza parchear: **S51 se mantiene** (A=NO, B=NO, C=NO). S52 sustituye la hipótesis «la clase 0 apaga la
cortina» por un mecanismo más preciso y desplaza la incógnita decisiva al MCU de obturador y al sensor.

## Mecanismo Silent A7S frente a A6000, componente a componente

| Componente A7S | Dirección A7S | A6000 | Estado A6000 |
|---|---|---|---|
| Comando `0x40e3` → estado | `0x437a9cb0` (+0x250) | `0x438032d4` (+0x238) | existe |
| Conversor ajuste → tipo {0,2} | `0x4379ec04` | — | **falta** |
| Tipo en captura `+0x78c`, bandera `+0x748` | `0x43813e94..ea2` | campo `+0x740` con lectores, sin escritor | **latente** |
| Esperas condicionadas por la bandera (S3, S5, S7) | `0x438b1cba`, `0x438b726c`, `0x438b8054` | en parte compartidas (S7 `0x438c8ac8` misma forma); S3/S5 esperan siempre | **difiere** |
| Espera CAIF 3 reordenada (S4) | `0x43b1c92e` | solo CAIF 5 | **falta** |
| Marca Silent en paquete CAIF (S1 bit `0x20` en +0x12, S2 modo 2 en +0xd) | `0x4386329a`, `0x43863258` | `0x4384149c` / `0x43841468` sin rama | **falta** |
| Clase 0 → byte +1 = 2 (como clase 3) (C2) | `0x4386315c` | `0x4384137c` daría 0 | **difiere** |
| Política tipo 2 ⇒ clase 0 | `0x438649bc` | `0x43842158` sin rama | **falta** |
| Clase → `param+9` → SetExposure | cadena VERIFICADA ([doc](s52-shutmode-propagation.md)) | mismo contrato `0x4383fd6c`/`0x436d6320` | existe |
| ShutMode 0 en driver | IMX235 caso 0 | IMX210 caso 0 (bits distintos) | existe, semántica NO VERIFICADO |
| Modos de sensor `0x4e/0x4f` (48 campos propios) | matriz col 12/13 | sin equivalente; `0x0b`/`0x2f` lectura completa | **falta** |
| Tipos de mecanismo Darwin 1/2/3 | `0x216e8` | `0x20c74` | igual |
| Consumidor de la marca Silent en el MCU | NO localizado | NO localizado | **desconocido** |

## P5 — ¿vía técnicamente plausible para A6000?

**NO VERIFICADO.** A favor: todas las piezas que faltan en LIRO son de software y están localizadas (conversor, bits del paquete, esperas,
rama de política, codificación del byte +1); el contrato clase→ShutMode y la rama ShutMode 0 existen; el selector de tipo Darwin es igual.
En contra / bloqueantes: (1) no se sabe si el **firmware Darwin de la A6000** interpreta el bit `0x20`/modo 2 — es la condición necesaria para
que la cortina no se mueva y no hay evidencia ni a favor ni en contra; (2) no se sabe si el IMX210 con ShutMode 0 y un modo de lectura
completa termina la integración electrónicamente con calidad fotográfica (sin datasheet; bits distintos al IMX235); (3) el IMX210 no tiene
modos dedicados equivalentes a `0x4e/0x4f`. Un port requeriría portar ≥7 cambios en LIRO **y** dependería de (1) y (2).

## Experimentos siguientes (de mayor valor, estáticos primero)

1. **Darwin**: localizar el parser CAIF en `darwin_core.bin` A7S y A6000 (vía la recepción del paquete de 22 B y el byte +0x12) y comparar
   el tratamiento del bit `0x20`. Es la pregunta decisiva para P2/P5. Sin riesgo.
2. Receptor del mensaje tipo 3/`0x22` (C1) y tarea CA A7S (tag `0x12`) — cierra el único efecto directo de la clase 0.
3. Contrato de los aplicadores IMX (`0x436f2d10`, `0x43ad9ec6`, `0x4355de98`) hasta el empaquetado serie → frontera B5.
4. Consumidores posteriores de los 48 campos de la matriz IMX235 para clasificarlos.
5. Con datasheet IMX235/IMX210 o traza pasiva autorizada del bus del sensor: semántica de ShutMode y de las columnas 12/13.
