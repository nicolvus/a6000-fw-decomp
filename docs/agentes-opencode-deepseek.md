# Agente B (DeepSeek flash) — Imager: estado, drive modes y gates (S300–S399)

Prompt autónomo. Lee primero `docs/agentes-opencode.md` (carta común: bucle, commits, push, límites) y
aplícala íntegra. Aquí solo lo específico de este agente.

## Política de razonamiento (elige tú, por ítem)

Por defecto **low**. Cambia a **high** solo en estos casos, y vuelve a low al terminar el ítem:

| Usa **low** (ejecución) | Usa **high** (juicio) |
|---|---|
| Enumerar xrefs, contar, volcar a tabla | Clasificar un acceso ambiguo: alias del puntero, aritmética `+3/+6` indirecta, copias `LDM/STM`/`memcpy` |
| Leer bytes/instrucciones concretas con REA | Concluir "escritor/no escritor" para un campo |
| Formatear informes, JSON, tests de reproducción | Resolver evidencia contradictoria o `CONFLICTO_PENDIENTE` |
| README, commit, push, `ruff`/`mypy`, reindexar | Diseñar el barrido o regenerar el backlog |
| Comparar campo a campo dos tablas ya extraídas | Interpretar la semántica de un campo de drive mode |

Regla de escalado: si dos intentos en low no cierran el ítem, o dos fuentes se contradicen, pasa a high.
Antes de escribir un veredicto en un informe, repásalo en high aunque el resto fuera low.

## Reglas anti-invención (críticas)

- Toda dirección, offset, instrucción o conteo del informe debe venir de una salida de herramienta de esta
  sesión (REA, Ghidra, bytes). Sin salida citada, escríbelo como NO_VERIFICADO; nunca lo completes de memoria.
- "No encontré" ≠ "no existe": una consulta vacía de REA no prueba ausencia. Verifica contra bytes.
- No uses la palabra "global" salvo que el barrido cubra todos los xrefs y lo demuestres con el conteo.
- Etiqueta cada afirmación VERIFICADO / INFERENCIA / NO_VERIFICADO.

## Backlog inicial (en este orden; regenéralo al agotarlo)

1. **Barrido único** de xrefs al state pointer `0x43f72d02` (GOT slot `0x4401f990`) en A6000 fw3.21. Primero
   obtén el total de xrefs, luego clasifica cada uno (spill, lectura, escritura, propagación de puntero) en
   **una sola tabla** con dirección, función, instrucción y veredicto. Parte de los JSON ya existentes
   en `analysis/s153_*` … `analysis/s176_*` para no repetir lo clasificado. Veredicto final: ¿algún writer
   de `+3`/`+6`? con límite explícito.
2. Mismo barrido en el homólogo de A7S fw3.20; tabla de diferencias A6000↔A7S.
3. Tablas de drive mode/exposición del imager (S124, S134, S140): extraer y comparar A7S↔A6000 campo a campo.
4. Árbol de referencias de la tabla `0x43ff3200` (pendiente de S176): xrefs exactas al vector y a la base GOT.
5. Derivados: cualquier campo del state que A7S use y A6000 no (o al revés) → nuevo ítem con prioridad.

## Cierre de cada ítem

Informe `docs/capture/s3NN-<tema>.md`, JSON + tests en `analysis/s3NN_<tema>/`, `knowledge-maintenance`
(solo reindexar; no edites `CORRECTIONS.md`/`OPEN-QUESTIONS.md`, los regenera el humano), commit y push según la
carta común. Entradas en README/`CURRENT.md` solo por append.
