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

1. Leer `knowledge/CURRENT.md` (resumen operativo), luego los pendientes relevantes de `docs/PENDIENTES.md` y solo los
   informes necesarios (por tema: `docs/INDEX.md`). `knowledge/PROGRESS.md` solo para el detalle histórico.
2. Comprobar entorno: `python scripts/agent/check_env.py` (con `--json` para agentes).
3. Respetar `docs/STATE.md` § "Política de ingeniería inversa": REA primero, Ghidra
   histórico como respaldo, verificar contra bytes, firmware y proyectos intactos,
   sin ejecutar firmware ni flashear.

## Cierre de una sesión

Informe en `docs/capture/` (+ evidencia en `analysis/`, prueba en `tests/`) → fila de `docs/PENDIENTES.md` → `docs/STATE.md` si cambió una
conclusión → `knowledge/CURRENT.md` si cambió el contexto mínimo (≤ ~150 líneas) → entrada en `knowledge/PROGRESS.md` →
`python scripts/knowledge/build_subsystem_index.py` + `knowledge-maintenance`. El README no recibe un párrafo por sesión.

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

## REA en Windows

Sin WSL, sin `java` ni Ghidra preinstalados, REA no puede abrir `av-cam.bin`. Para
una run en Windows hacen falta:

- JDK 21 completo (`JAVA_HOME`, con `javac`).
- Ghidra 12.1.4 PUBLIC (`GHIDRA_INSTALL_DIR`), con el descompilador nativo en
  `Ghidra/Features/Decompiler/os/win_x86_64/`.
- `rea-agents@6.5.0` (vendorizado en `tools/rea/node_modules`) y Node 22/24.

Instalación usada en esta máquina: `C:\tools\jdk-21.0.12.1+1`,
`C:\tools\ghidra_12.1.4_PUBLIC`, venv de tests `C:\tools\venv-s63`
(`pytest`, `capstone`, `unicorn`, `pyyaml`). Variables en el perfil de usuario.
`rea doctor` da `ghidra*` y `ghidra-java` en `healthy` (Hopper/IDA/JADX pueden
faltar: no se usan).

**Límite real (verificado 2026-10-20):** el bridge Windows de REA es P0 y acepta
solo PE nativo y 6502 crudo (`target_format_unsupported` para ELF/ARM). Con
`av-cam.bin` o `libmprctrl.so` (ARM ELF) el proveedor Ghidra no está disponible,
así que la run REA completa sigue siendo Linux. En Windows quedan como vía:
Ghidra headless directo (`support/analyzeHeadless.bat`, sí soporta ARM) y
Capstone/Unicorn para bytes e instrucciones (`C:\tools\venv-s63`).


`analysis/rea-independent/bin/session_daemon.py` es Linux-only (socket Unix,
`/proc`). En Windows/macOS usar el demonio portátil, que mantiene UNA sesión
MCP viva y atiende lotes (evita los ~8 min de autoanálisis por consulta):

```bash
# 1) abrir el binario una vez (bloquea hasta acabar el autoanálisis)
REA_NODE=/ruta/node python scripts/agent/rea_daemon.py \
  --binary firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin \
  --args '{"path": "...", "base_address": "0x43541000"}'

# 2) consultar por lotes (lee el puerto de analysis/rea-independent/run/rea-win.json)
python scripts/agent/rea_client.py --tools
python scripts/agent/rea_client.py --calls guion.json --out out/respuestas.jsonl

# 3) cerrar
python scripts/agent/rea_client.py --shutdown
```

Variables: `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=3G` (el demonio
las fija si no están). El log de la sesión queda en
`analysis/rea-independent/run/rea-win-session.jsonl`.


## ChatGPT web

No puede leer el repo. Pegar `docs/agent/chatgpt-pack.md` (reglas + estado + skills
resumidas) al inicio del chat; ese archivo se regenera desde las fuentes del repo.

## Commit y push

Regla del proyecto: commit local al cerrar cada fase y push a `origin` (`main`).
Si el agente no tiene credenciales de GitHub en su máquina, deja el commit hecho y
pide el push al usuario; nunca `git add -A` (el árbol tiene cambios ajenos).
