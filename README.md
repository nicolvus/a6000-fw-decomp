# Sony A6000 Hardware & Firmware Reverse Engineering Project

Ingeniería inversa de hardware y firmware de la Sony A6000 (fw 3.21): arquitectura, arranque,
recuperación y pipeline de captura. El obturador electrónico es un
[subproyecto](projects/electronic-shutter/README.md). No se ejecutó firmware ni se flasheó la cámara;
las pruebas históricas sobre la cámara están documentadas en S64.

## Estado en una mirada

| Área | Estado | Fuente |
|---|---|---|
| Obturador totalmente electrónico | No demostrado; decisión vigente: **no parchear** | [S51](docs/capture/s51-decision.md), [S101](docs/capture/s101-conclusions.md) |
| Pruebas físicas P1–P8 | **0 de 8** ejecutadas según el plan | [Plan de pruebas](docs/capture/physical-test-plan.md) |
| Última sesión documentada | **S102**, menú principal | [Informe S102](docs/capture/s102-menu-principal.md) |

Los números Sx identifican sesiones de investigación, no una escala de porcentaje completado.
[GitHub Pages](https://nicolvus.github.io/a6000-fw-decomp/) ofrecerá, tras activarlo, un índice público y un
verificador para localizar informes por número de sesión. El índice se genera con
`scripts/build_pages_status.py` a partir de documentos versionados; si no encuentra
una sesión, eso no significa que no exista.

## Navegación por tema

- **Estado y decisiones:** [estado operativo](knowledge/CURRENT.md) · [restricciones](docs/STATE.md) · [S51, decisión sobre el parche](docs/capture/s51-decision.md) · [viabilidad](docs/feasibility-report.md).
- **Obturador y captura:** [subproyecto](projects/electronic-shutter/README.md) · [S101, selector de mecanismo](docs/capture/s101-conclusions.md) · [pruebas P1–P8](docs/capture/physical-test-plan.md) · [índice de captura](docs/capture/README.md).
- **Ingeniería inversa general:** [catálogo de hitos](docs/capture/linea-general-re.md) · [S102, menú](docs/capture/s102-menu-principal.md) · [S100, contrato ADF](analysis/s100_adf_contract/adf_command_contract.md) · [S99, userland](analysis/s99_userland/userland_architecture.md).
- **Historial:** [README anterior S19–S100](docs/history/README-historial-2026-10-21.md) · [progreso completo](knowledge/PROGRESS.md) · [continuidad](CONTEXT.md).

## GitHub Pages

El sitio está en `site/`; el flujo `.github/workflows/pages.yml` genera
`site/status.json` y publica **solo** esa carpeta al actualizar `main`.
Para activarlo en GitHub: **Settings → Pages → Build and deployment → GitHub Actions**.
La publicación requiere push explícito; este repositorio no incluye firmware en el sitio.
El verificador muestra el informe localizado, sin atribuir «completado» ni
capacidad física a una sesión.

## Agentes (Claude Code, Codex/ChatGPT, DeepSeek Harness)

Reglas en `AGENTS.md` y `CLAUDE.md`; skills en `.claude/skills/` y `.agents/skills/`
(copias idénticas, verificadas por `tests/test_agent_skills_sync.py`). Instalación de
REA/Ghidra, MCP y arranque de sesión: [docs/agent/README.md](docs/agent/README.md).
Para ChatGPT web: [docs/agent/chatgpt-pack.md](docs/agent/chatgpt-pack.md).
Entorno: `python scripts/agent/check_env.py`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | Documentación: arquitectura, captura (`docs/capture/`), historial, referencias |
| `analysis/` | Un directorio por hito (`sNN_*`), con informe y datos |
| `tests/` | Un test por hito + utilidades |
| `scripts/` | Herramientas, conocimiento (`scripts/knowledge/`), agente |
| `knowledge/` | Estado (`CURRENT.md`), progreso e índices derivados |
| `site/` | GitHub Pages: portada, verificador e índice público de sesiones |
| `src/` | Inventario, atlas, LIRO |
| `tools/`, `reports/`, `references/`, `research/`, `work/` | REA/Ghidra, informes, fuentes públicas, notas |
| `firmware/` | Firmware Sony original/extraído (en `.gitignore`, no se publica) |

## Subproyecto: obturador electrónico

- Pruebas físicas pendientes (no ejecutadas): [docs/capture/physical-test-plan.md](docs/capture/physical-test-plan.md).
- Decisión vigente: **no parchear** (S51, [decisión SÍ/NO](docs/capture/s51-decision.md)); categoría E, evidencia insuficiente; ni viabilidad ni imposibilidad demostradas.
- Conclusiones: [S50](docs/capture/s50-parallel-conclusions.md) · [S52 viabilidad A6000](docs/capture/s52-a7s-a6000-feasibility.md) · [EFCS](docs/capture/efcs-capture-selector.md) · [estado Silent](docs/capture/silent-shutter-status.md) · [traza](docs/silent-shutter-trace.md).
- Referencia comparativa: A7S 3.20 ([A6300 vs A6000](docs/capture/a6300-silent-comparison.md)).

## Documentos generales

[Alcance](docs/project-scope.md) · [Arquitectura](docs/architecture/README.md) · [Captura](docs/capture/README.md) · [Inventario físico](docs/hardware-inventory.md) · [Atlas ELF](docs/elf-classification.md) · [Dependencias](docs/subsystem-dependencies.md) · [Arranque y recuperación](docs/boot-and-recovery.md).

## Reproducción local sin instalar paquetes

Desde este directorio:

```sh
python3 -m src.inventory firmware/extracted/fw321 reports/inventory.json
python3 -m src.inventory firmware reports/firmware-inventory.json
python3 -m src.atlas
python3 -m src.liro firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin reports/silent-liro-dispatch.json --base 0x43541000 --table 0xabe30c --count 220
python3 -m unittest discover -s tests -v
/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/ruff check src tests
/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/mypy --ignore-missing-imports src
```

Extracción: `7z x firmware/original/Update_ILCE6000V321.dmg -ofirmware/extracted/updater` y `/home/nicolas/.local/share/pmca-venv/bin/python references/fwtool/fwtool.py unpack -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat -o firmware/extracted/fw321`.

La CLI real necesita `-f` y `-o`: el ejemplo posicional del proyecto base no corresponde a esta versión.
La extracción WBI por CLI falla al intentar interpretar recursivamente una sección como ext2. La alternativa ejecutada fue iterar `fwtool.sony.wbi.readWbi`, guardar `chunk.contents.read()` y registrar `physicalAddr`, `virtualAddr`, tamaño y SHA-256 en `reports/wbi-sections.json`. Véase el procedimiento completo en `docs/firmware-analysis.md`.

679 ELF ARM confirmados por readelf; 45 archivos con coincidencias de palabras
clave en la búsqueda inicial. El inventario total incluye contenedores,
derivados y duplicados: sus tamaños no deben sumarse como memoria del dispositivo.
El atlas reutiliza metadatos por hash y productor; se comprobaron 679 aciertos
en la segunda pasada. Los snapshots REA conservan evidencia, pero no sustituyen
un proyecto persistente de Ghidra ni garantizan evitar una nueva importación.

## Validación

La suite está en `tests/`; ejecutar las pruebas pertinentes antes de reutilizar
un hito. El trabajo inicial aplicó TDD a inventario, atlas, símbolos versionados,
roles ELF, dependencias, referencias Thumb y extracción LIRO. Registro histórico:
reports/shutter-validation.md; registro previo: reports/atlas-validation.md. Dos archivos
auxiliares del DMG no legibles se registran como errores; el payload y el
firmware están inventariados y los 679 ELF se analizaron sin errores.

Repositorio publicado en `github.com/nicolvus/a6000-fw-decomp` (rama `main`).
`firmware/` está en `.gitignore`: los artefactos de firmware no se publican.
REA, Ghidra y JDK están instalados localmente; no se ejecutaron programas del firmware.

## REA operativo

REA 6.5.0 instalado en `tools/rea` con versión y dependencias fijadas en package-lock.json. Ghidra 12.1.4 y Temurin JDK 21 portables, sin modificar paquetes del sistema. Descargas y hashes verificados: `reports/rea-provider-downloads.json`. Registro MCP aplicado a `/home/nicolas/.codex/config.toml`, con respaldo `.rea.backup`; reiniciar Codex para cargarlo.

```sh
./scripts/rea doctor --client codex --provider ghidra --json
./scripts/rea analyze "$PWD/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha16_unpacked_unpacked/lib/libcamera.so" --provider ghidra --json
```

Comprobado: protocolo MCP initialize, 207 herramientas, binary_session, diagnóstico Ghidra/Codex y análisis ARM real. En este sandbox, la comprobación Java desde Node requiere ejecución autorizada fuera de la restricción EPERM; no confundir ese fallo con ausencia del JDK. Binwalk, Unblob y JADX siguen pendientes; no son necesarios para el ELF ya extraído.

## Empezar desde cero (clon nuevo + firmware 3.21 recién descargado)

**Para agentes de IA:** ejecutar `scripts/agent/bootstrap.sh` (idempotente, `--dry-run` disponible) y seguir el runbook [docs/agent/bootstrap-desde-cero.md](docs/agent/bootstrap-desde-cero.md) (verificación, orientación, REA, ciclo de fase y límites). Lo siguiente es el desglose manual de esos mismos pasos.

Los binarios (firmware, Ghidra, JDK, `node_modules`, `.venv`) no están en Git: se reconstruyen así.
Todo desde la raíz del repo; Linux x86_64.

```sh
# 1. Clonar y entrar
git clone https://github.com/nicolvus/a6000-fw-decomp.git sony-a6000-electronic-shutter && cd sony-a6000-electronic-shutter

# 2. Firmware oficial 3.21 (Mac updater) y verificación
mkdir -p firmware/original && cd firmware/original
curl -L -o Update_ILCE6000V321.dmg "https://support.d-imaging.sony.co.jp/download/NEX/AcicwqgUEQ/Update_ILCE6000V321.dmg?fm=am"
sha256sum Update_ILCE6000V321.dmg   # esperado: 844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e
cd ../..

# 3. Entorno Python (herramientas, tests, grafo de conocimiento)
python3 -m venv .venv && . .venv/bin/activate && pip install pytest ruff mypy pyyaml capstone unicorn

# 4. Desempaquetar con fwtool (vendorizado en references/fwtool; necesita sus dependencias Python, ver su README)
7z x firmware/original/Update_ILCE6000V321.dmg -ofirmware/extracted/updater
python references/fwtool/fwtool.py unpack \
  -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat \
  -o firmware/extracted/fw321
# Si falla la extracción WBI anidada: procedimiento alterno en docs/firmware-analysis.md
# Comprobación: firmware/extracted/fw321/firmware.fdat debe tener SHA-256
#   603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90 (firmware/hashes/sha256.json)

# 5. Inventario y atlas ELF (679 ELF ARM esperados)
python3 -m src.inventory firmware/extracted/fw321 reports/inventory.json
python3 -m src.atlas

# 6. REA + Ghidra + JDK locales (versiones y hashes en reports/rea-provider-downloads.json)
(cd tools/rea && npm ci)                      # rea-agents 6.5.0 (Node 22/24)
mkdir -p tools/providers   # descomprimir aquí ghidra_12.1.4_PUBLIC y jdk-21.0.12.1+1 (URLs en el JSON)
./scripts/rea doctor --client codex --provider ghidra --json

# 7. Binario principal para REA: av-cam.bin (base 0x43541000, ARM)
mkdir -p analysis/rea-independent/input
cp firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin analysis/rea-independent/input/

# 8. Comprobar todo y arrancar el grafo de conocimiento
python scripts/agent/check_env.py --sha
python3 scripts/knowledge/index_docs.py && python3 scripts/knowledge/build_graph.py
python -m pytest tests -q
```

Después de instalar:

1. Leer [knowledge/CURRENT.md](knowledge/CURRENT.md) y [docs/STATE.md](docs/STATE.md) (restricciones y política de RE).
2. Registrar los MCP `rea` y `sony-a6000-knowledge` ([docs/agent/README.md](docs/agent/README.md#mcp-claude-code-y-codex)); ajustar las rutas absolutas de `.mcp.json` a tu clon.
3. Abrir **una sola** sesión REA (`av-cam.bin` tarda ~8 min en frío): `python analysis/rea-independent/bin/session_daemon.py <sock> "$(cat analysis/rea-independent/exp2-open-args.json)"` (ajustar `path` al clon) y consultar por lotes con `bin/q.py <sock> guion.json`; cerrarla al acabar el hito.
4. Antes de reutilizar un hallazgo: skill `contradiction-audit`; antes de buscar a mano: `knowledge-navigation`; tras editar `.md`: `knowledge-maintenance`.
5. Reglas que no cambian: sin ejecutar firmware, sin flasheo, REA primero y verificar lo decisivo contra bytes. Foco actual: obturador electrónico (decisión vigente S51: no parchear).
6. Para saber qué falta, ver [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) y los «Próximo» del final de [knowledge/PROGRESS.md](knowledge/PROGRESS.md).
