# Contributing

[🇪🇸 Versión en español](CONTRIBUTING.md)

Thanks for wanting to help. This project reverse engineers the Sony A6000 firmware; the first rule is not to damage cameras.
The reports, backlog and code comments are in Spanish; issues and pull requests in English are welcome.

## Before you start

1. Read the [Sony a6000 CFW Wiki](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-Home) (source in [`wiki/`](wiki/en-Home.md)): requirements, risks and glossary.
2. Environment: `scripts/agent/bootstrap.sh` (downloads official firmware 3.21 from Sony; the repository does **not** contain Sony firmware) or, for code and tests only, `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
3. Minimal context: [`knowledge/CURRENT.md`](knowledge/CURRENT.md) → [`docs/STATE.md`](docs/STATE.md) → [`docs/PENDIENTES.md`](docs/PENDIENTES.md).

## Rules

- **No camera tests without an NVRAM backup**, and no flashing without the author's explicit authorization for that case. The camera scripts use the IP in the `A6000_HOST` variable (default `192.168.1.29`).
- **Do not upload Sony material** (`firmware/`, `*.bin`, `*.elf`, `*.tar.gz`, RAW files, serial numbers or personal data). They are in `.gitignore`.
- Conventional Commits. A behavior change comes with the failing test first.
- Tests: `CI=1 python -m pytest tests -q` (those that need firmware are skipped); `ruff` and `mypy` with no new warnings.
- Every task that is done, dropped or reopened updates [`docs/PENDIENTES.md`](docs/PENDIENTES.md) in the same change; every new open item is added there with an ID, origin and closing criterion.
- After editing any indexed `.md`: `python scripts/knowledge/index_docs.py && python scripts/knowledge/build_graph.py && python scripts/knowledge/export_corrections.py` and run the first two again (see the `knowledge-maintenance` skill).
- The `.md` files are not a history log: edit them so they state the current truth; history lives in Git. Do not leave old versions or "it used to say" notes.
- To change the wiki, edit `wiki/` (Spanish pages and their `en-*` English counterparts together); a workflow publishes it to the GitHub wiki on merge to `main`.

## License

Your contribution falls under the repository's [MIT license](LICENSE), which does not cover Sony material (see [Copyright and use](README.en.md#copyright-and-use)).
