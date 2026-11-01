# 10. Repository and research map

Folder and file names are in Spanish; so are the reports, state files and backlog.

| Path | Contents |
|---|---|
| `wiki/` | Source of this wiki (a workflow publishes it on every change) |
| `site/` | GitHub Pages board (`scripts/build_pages_status.py`) |
| `projects/electronic-shutter/` | Electronic shutter subproject |
| `scripts/replicar/` | Generates the patched Darwin cores from the official firmware |
| `scripts/e25_05/` | Build and verification of the 3.23/3.24 packages |
| `scripts/e25_27/` | Build and verification of 3.25c |
| `scripts/camera_*.py` | Camera control over telnet/ADB and layer 2 |
| `scripts/senser_backup_dump.py` | NVRAM backup (read only) |
| `tools/remote-shutter/` | RemoteShutter app |
| `references/` | pmca, fwtool and Tweak (vendored), manuals |
| `docs/` | State (`STATE.md`), backlog (`PENDIENTES.md`), reports (`docs/capture/`) |
| `knowledge/` | Operational summary (`CURRENT.md`) and history |
| `analysis/` | Evidence per session (camera dumps: README, SHA256SUMS and JSON only) |
| `tests/` | Checkers; the ones that need firmware are skipped in CI |

## Reproduce and verify

```sh
source .venv/bin/activate
CI=1 python -m pytest tests -q                       # suite without firmware (as in GitHub Actions)
python3 scripts/audit/repo_audit.py                   # links, cited paths, figures and SHA-256
python3 scripts/knowledge/search.py text "concepto"  # search without re-reading the repository
```

## Reverse engineering

- REA (MCP) and the historical Ghidra project (`silent-liro.gpr`, read only). `av-cam.bin` takes ≈ 8 min cold: reuse a single session (`docs/agent/bootstrap-desde-cero.md` §4).
- Where to start: `knowledge/CURRENT.md` → `docs/STATE.md` → `docs/PENDIENTES.md`.
- Progress board: <https://nicolvus.github.io/a6000-fw-decomp/progress/>.

## Navigation

| I need… | Go to… |
|---|---|
| Minimal context to pick up the work | [knowledge/CURRENT.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/CURRENT.md) |
| Current conclusions and limits | [docs/STATE.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/STATE.md) |
| What is left (single list) | [docs/PENDIENTES.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/PENDIENTES.md) |
| 3.25 incident and recovery | [docs/capture/e26-recovery.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-recovery.md) |
| Reports by subsystem | [docs/INDEX.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/INDEX.md) |
| Camera test log | [docs/capture/registro-pruebas-camara.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/registro-pruebas-camara.md) |
| Chronological history | [knowledge/PROGRESS.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/PROGRESS.md) |
| Progress board | <https://nicolvus.github.io/a6000-fw-decomp/progress/> |
| Use by agents | [docs/agent/README.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/agent/README.md), [AGENTS.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/AGENTS.md), [CLAUDE.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/CLAUDE.md) |

## Security and contributing

- The repository code does not contain Sony firmware, `*.bin`/`*.elf`, RAW files or personal data (the serial number, the
  personal email and `libmprctrl.so` were removed from history on 2026-10-31; see R7 in PENDIENTES). The ready-to-flash `.dat`
  packages are published separately as GitHub Releases ([`fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24),
  [`fw-3.25c-experimental`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental); not in the git tree), with their copyright note. Conventional Commits.
- Every camera test has a prior NVRAM backup and is logged; every task updates [PENDIENTES](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/PENDIENTES.md) in the same commit.

How to contribute: [CONTRIBUTING.en.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/CONTRIBUTING.en.md).
