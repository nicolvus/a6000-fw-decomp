# Uso del agente (Claude Code, Codex/ChatGPT y DeepSeek Harness)

Este repositorio es la fuente única de reglas y skills para cualquier agente que
trabaje en la investigación. Nada de configuración vive solo en la máquina de un
agente: si algo no está aquí, no es reproducible.

## Quién lee qué

| Agente | Reglas | Skills | MCP |
|---|---|---|---|
| Claude Code | `CLAUDE.md` | `.claude/skills/*/SKILL.md` | `.mcp.json` en el directorio desde el que se lanza |
| Codex / ChatGPT (CLI) | `AGENTS.md` | `.agents/skills/*/SKILL.md` | `~/.codex/config.toml` |
| DeepSeek Harness (DSH) | `AGENTS.md` + `CLAUDE.md` | `.agents/skills/*` (o `.dsh/skills`) | no usa MCP: CLI/Python |

`.claude/skills` y `.agents/skills` son **copias byte a byte** (no symlinks, para
que Windows y los clones con `core.symlinks=false` funcionen). `tests/test_agent_skills_sync.py`
falla si se separan: editar siempre `.claude/skills/<name>/SKILL.md` y copiar.

## Skills disponibles

- `knowledge-navigation` — buscar direcciones/símbolos/documentos en el grafo.
- `contradiction-audit` — saber si un hallazgo está vigente, corregido o superado.
- `knowledge-maintenance` — reindexar y reconstruir el grafo tras editar `.md`.
- `session-checkpoint` — reanudar o registrar el estado de una sesión.

## Arranque de una sesión

1. Leer `knowledge/CURRENT.md` (resumen operativo). Solo ir a `knowledge/PROGRESS.md` para el detalle.
2. Comprobar entorno: `python scripts/agent/check_env.py` (con `--json` para agentes).
3. Respetar `docs/STATE.md` § "Política de ingeniería inversa": REA primero, Ghidra
   histórico como respaldo, verificar contra bytes, firmware y proyectos intactos,
   sin ejecutar firmware ni flashear.

## MCP (Claude Code y Codex)

Servidores: `rea` (análisis con Ghidra/Hopper) y `sony-a6000-knowledge` (grafo local).

Claude Code, `.mcp.json` en el directorio padre del repo (Linux del usuario):

```json
{
  "mcpServers": {
    "sony-a6000-knowledge": {
      "command": "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/.venv/bin/python3",
      "args": ["/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/knowledge/mcp_server.py"],
      "env": {"SONY_A6000_KB_ROOT": "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter"}
    },
    "rea": {
      "command": "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/rea",
      "args": ["mcp"],
      "env": {"REA_GHIDRA_STARTUP_TIMEOUT_MS": "900000", "GHIDRA_MAXMEM": "3G"}
    }
  }
}
```

Codex: el mismo bloque en `~/.codex/config.toml` como `[mcp_servers.rea]` y
`[mcp_servers.sony-a6000-knowledge]` (sintaxis de la Fase 6 de `knowledge/PROGRESS.md`).

## REA en Windows (DSH)

Sin WSL, sin `java` ni Ghidra preinstalados, REA no puede abrir `av-cam.bin`. Para
una run en Windows hacen falta:

- JDK 21 completo (`JAVA_HOME`, con `javac`).
- Ghidra 12.1.4 PUBLIC (`GHIDRA_INSTALL_DIR`), con el descompilador nativo de la
  plataforma en `Ghidra/Features/Decompiler/os/win_x86_64/`.
- `rea-agents@6.5.0` (ya vendorizado en `tools/rea/node_modules`).

Variables recomendadas: `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=3G`.
`analysis/rea-independent/bin/session_daemon.py` es Linux-only (socket Unix, `/proc`);
en Windows usar el CLI `rea` o el MCP directamente.

## ChatGPT web

No puede leer el repo. Pegar `docs/agent/chatgpt-pack.md` (reglas + estado + skills
resumidas) al inicio del chat; ese archivo se regenera desde las fuentes del repo.

## Commit y push

Regla del proyecto: commit local al cerrar cada fase y push a `origin` (`main`).
Si el agente no tiene credenciales de GitHub en su máquina, deja el commit hecho y
pide el push al usuario; nunca `git add -A` (el árbol tiene cambios ajenos).
