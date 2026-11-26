# ORDEN — reglas de orden del repositorio

Reglas **vinculantes**. No son recomendaciones: un cambio que las contradiga no se acepta. Para cambiar una regla, se cambia
**primero este documento**, en un commit propio, y el resto del cambio va detrás. Versión inglesa: [ORDER.md](ORDER.md).
Comprobación automática: `python scripts/audit/check_order.py` (y `pytest tests/test_order.py`).

## 1. Una sola fuente por asunto

| Asunto | Fuente única | Todo lo demás |
|---|---|---|
| Portada pública | [README.md](README.md) / [README.en.md](README.en.md) | enlaza, no resume ni copia tablas |
| Reglas de contribución | [CONTRIBUTING.md](CONTRIBUTING.md) / [CONTRIBUTING.en.md](CONTRIBUTING.en.md) | — |
| Orden del repositorio | este documento ([ORDEN.md](ORDEN.md) / [ORDER.md](ORDER.md)) | — |
| Contexto mínimo para agentes | [knowledge/CURRENT.md](knowledge/CURRENT.md) (≤ ~150 líneas) | — |
| Conclusiones y límites vigentes | [docs/STATE.md](docs/STATE.md) | — |
| Tareas abiertas, bloqueadas y cerradas | [docs/PENDIENTES.md](docs/PENDIENTES.md) | — |
| Cronología de la investigación | [knowledge/PROGRESS.md](knowledge/PROGRESS.md) | — |
| Índice de informes por subsistema | [docs/INDEX.md](docs/INDEX.md) | — |
| Informes canónicos de una línea de trabajo | `docs/capture/` | `reports/` solo mientras el caso está vivo |
| Evidencia reproducible | `analysis/` | — |
| Verificadores | `tests/` | — |
| Guía de réplica (ES/EN) | `wiki/` | `site/` solo tablero |
| Tablero publicado | `site/` (datos generados por `scripts/build_pages_status.py`) | — |
| Lista de funciones objetivo | [FUNCIONES.md](FUNCIONES.md) | — |

Prohibido duplicar contenido: se escribe en su fuente única y el resto **enlaza**.

## 2. Dónde va cada fichero nuevo

| Tipo | Ruta | Nombre |
|---|---|---|
| Informe de una sesión o fase | `docs/capture/` | `<prefijo>-<slug>.md` |
| Informe de trabajo de un agente o subagente, caso aún abierto | `reports/` | `<caso>-<tema>-AAAAMMDD.md` |
| Evidencia (volcados, JSON, scripts de una sola vez) | `analysis/<caso>/` | libre, en minúsculas |
| Script de análisis o de cámara | `scripts/<área>/` | `snake_case.py` |
| Script del carril GUI / CFW | `scripts/gui/` | `snake_case.py` |
| Verificador de un informe | `tests/` | `test_<prefijo>_<tema>.py` |
| Página de wiki | `wiki/` | `<n>-Titulo.md` **y** `en-<n>-Title.md` |
| Documento derivado | `docs/CORRECTIONS.md`, `docs/OPEN-QUESTIONS.md`, `docs/INDEX.md` (§ generado), `knowledge/audit/*.json` | solo por script |

Prefijos en uso: `s<N>` sesión, `e<NN>` fase estática, `e25-`/`e26-` obturador y recuperación, `e26-r<NN>` informe de recuperación,
`g<NNN>` carril GUI, `p<NN>` plan físico, `og-` open gate, `usb-carga-` carga USB, `cam-` incidencias de cámara.

## 3. Nombres

- Minúsculas, guiones o `snake_case` según el tipo de la tabla anterior; sin espacios ni acentos. Los ficheros antiguos con mayúsculas se conservan para no romper enlaces; los nuevos, en minúsculas.
- Un ID, un fichero. Los IDs no se renombran ni se reutilizan jamás: un ID nuevo es el siguiente libre del prefijo.
- Si dos informes tratan lo mismo, el segundo **corrige** al primero con enlace explícito; no se duplica el análisis.
- Prohibido el sufijo de fecha en `docs/capture/` (la fecha va dentro del documento); obligatorio en `reports/`.

## 4. Orden interno de un documento

1. `# Título` con prefijo e ID cuando exista.
2. Cabecera de metadatos: fecha, estado, fuentes.
3. Cuerpo: hechos verificados → inferencias → lo que falta.
4. Sección **Límites** (qué no se ha medido y qué no prueba el informe).
5. Enlaces a evidencia y a los informes relacionados.

Todo `.md` dice la verdad **actual**; el historial está en Git. Prohibido dejar versiones antiguas, bloques «antes decía» o
secciones que ya no se sostienen.

## 5. Estados normalizados

- Evidencia de cada afirmación: `VERIFICADO`, `INFERENCIA`, `NO_VERIFICADO`.
- Tareas: `ABIERTO`, `PARCIAL`, `BLOQUEADO`, `CERRADO`, `CERRADO CON LÍMITE`, `DESCARTADO`.
- Cualquier otro estado en `docs/PENDIENTES.md` es un fallo de orden.

## 6. Orden de commits y publicación

- Un commit por fase o corrección, Conventional Commits (`tipo(ámbito): resumen`), con `docs/PENDIENTES.md` actualizado **en el mismo commit**.
- Push a `origin/main` al cerrar cada fase, con la cuenta `nicolvus`.
- Nunca se versiona firmware de Sony, binarios de Sony, `*.bin`/`*.elf` de la cámara, RAW ni datos personales.

## 7. Wiki: pares obligatorios

- Cada página `wiki/<n>-Titulo.md` tiene su gemela `wiki/en-<n>-Title.md` con el **mismo número y la misma estructura**.
- Un cambio de contenido se aplica a las dos en el mismo commit; si solo puede hacerse en una, se anota en la otra.
- Una página nueva entra en los dos bloques de `wiki/_Sidebar.md` en el mismo commit.
- Enlaces a la wiki se escriben como URL completa `https://github.com/nicolvus/a6000-fw-decomp/wiki/<slug>`; enlaces al código, como
  `https://github.com/nicolvus/a6000-fw-decomp/blob/main/<ruta>`.

## 8. Sitio

- `site/status.json` y `site/badge-*.json` son **generados**: se regeneran con `scripts/build_pages_status.py`, nunca se editan a mano.
- `site/index.html`, `site/app.js`, `site/styles.css` y `site/progress/index.html` son manuales; sus datos deben coincidir con
  `docs/STATE.md` y `README.md`.
- La portada del sitio tiene par: `site/index.html` (español) y `site/en/index.html` (inglés), con selector cruzado en las dos. El tablero `site/progress/` es generado y va solo en español hasta que se decida traducirlo.
- El sitio y la wiki se publican solos (`pages.yml`, `wiki.yml`); nadie publica a mano.

## 9. Prohibiciones absolutas

1. Enlaces a `releases/tag/...` mientras el repositorio no tenga releases.
2. Citar una versión de firmware sin su build, informe o criterio de cierre.
3. Repetir la tabla de funciones objetivo, de versiones o el estado global en más de una fuente.
4. Renombrar, mover o borrar un fichero enlazado sin actualizar todos los enlaces en el mismo commit.
5. Dejar un documento con afirmaciones que otro ya corrigió.
6. Editar a mano un derivado generado.
7. Commitear cambios en `.md` sin ejecutar `knowledge-maintenance` y `check_order.py`.

## 10. Verificación previa a cada commit

```sh
python scripts/audit/check_order.py     # reglas de este documento, de forma mecánica
python -m pytest tests/knowledge tests/test_order.py -q
CI=1 python -m pytest tests -q          # sin firmware
```

## 11. Reglas vigentes: se traen de `a6000-handoff-context`

Las reglas **nuevas sobre el orden del repo** se publican en el repositorio privado
[`nicolvus/a6000-handoff-context`](https://github.com/nicolvus/a6000-handoff-context) antes de llegar
a este documento. Al empezar cada sesión, y siempre antes de decidir algo sobre el orden del repo:

```sh
bash scripts/agent/sync_rules.sh   # trae las reglas vigentes y lista qué difiere de la copia local
```

- Manda **GitHub**: lo que traiga se aplica en la sesión y, si la copia local se quedó atrás, se
  actualiza en el mismo commit.
- Un snapshot más antiguo no borra ninguna regla local: si GitHub aún no trae una regla, sigue vigente.
- Para cambiar una regla: primero el repositorio de handoff, después este documento, y el resto del
  cambio detrás, como en cualquier regla de orden.
