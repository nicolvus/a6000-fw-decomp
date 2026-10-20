---
name: knowledge-navigation
description: Buscar símbolos, direcciones hexadecimales, conceptos o documentos del proyecto Sony A6000 sin releer toda la documentación. Úsala siempre antes de explorar manualmente docs/analysis/reports/references/research cuando busques algo específico.
---

# Navegación del conocimiento (Sony A6000)

## Cuándo se activa

El usuario o el agente necesita: localizar una dirección hexadecimal o símbolo,
entender un concepto (EFCS, SilentShutter, Darwin, GPIO...), leer el contenido
original de una sección concreta, o navegar la estructura
Repositorio→Subsistema→Documento→Sección sin cargar todo el archivo.

## Procedimiento

1. Activar el entorno del proyecto: `source .venv/bin/activate` (desde la raíz
   del repo `sony-a6000-electronic-shutter`).
2. Si no sabes qué tipo de búsqueda conviene, usa el enrutador adaptativo:
   ```bash
   python3 scripts/knowledge/search.py ask "<consulta>" --budget 2000
   ```
   Clasifica automáticamente entre dirección/símbolo exacto, ruta de documento
   o concepto libre, y combina resultados con corrección relacionada si existe.
3. Si ya sabes el tipo, usa el comando específico (más rápido, menos texto):
   - Dirección/símbolo exacto: `python3 scripts/knowledge/search.py exact "0x..."`
   - Concepto: `python3 scripts/knowledge/search.py text "concepto" --limit 10`
   - Árbol de un subsistema: `python3 scripts/knowledge/search.py tree --subsystem docs/capture`
   - Árbol de un documento: `python3 scripts/knowledge/search.py tree --doc <ruta.md>`
   - Texto original de una sección (por id de `tree`): `python3 scripts/knowledge/search.py section <node_id>`
4. Cita siempre la ruta y línea devueltas, nunca reformules sin la fuente.

## Entradas / salidas

Entrada: una consulta en texto libre, dirección hex, o ruta `.md`.
Salida: texto con ruta:línea, encabezado de sección y fragmento o cita exacta.

## Herramientas disponibles

CLI: `scripts/knowledge/search.py` (subcomandos `exact`, `text`, `tree`, `section`, `ask`).
MCP (si el cliente lo tiene configurado vía `../.mcp.json`): `search_exact`,
`search_documents`, `search_hybrid`, `find_symbol`, `get_document_section`.

## Limitaciones

- Requiere que `.knowledge-cache/knowledge.sqlite` exista (ver skill `knowledge-maintenance`
  si da error "No existe la DB").
- La búsqueda textual es BM25 sobre Markdown, no semántica: sinónimos no indexados
  pueden no aparecer. Prueba variantes del término si no hay resultados.

## Validaciones

Antes de citar un resultado como autoritativo, verifica con `search.py claim <doc>`
(skill `contradiction-audit`) si ese documento está corregido o superado.

## Referencias bajo demanda

Ver `docs/STATE.md` para el estado vigente y `knowledge/PROGRESS.md` para el estado
de implementación de este propio sistema de conocimiento.
