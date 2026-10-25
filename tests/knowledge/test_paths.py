"""Regresión de _paths.find_root (Fase 12.2.A).

Caso de la auditoría: ejecutar un script del sistema de conocimiento desde un
directorio ajeno al proyecto (p. ej. /tmp) producía cero documentos porque la
búsqueda de CLAUDE.md ascendiendo desde cwd no encontraba nada y el fallback
devolvía ese mismo cwd ajeno. Ahora, si no hay marcador sobre cwd, se busca también
ascendiendo desde la ubicación de INSTALACIÓN del propio script."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS_SCRIPT = ROOT / "scripts" / "knowledge" / "_paths.py"

spec = importlib.util.spec_from_file_location("_paths", PATHS_SCRIPT)
assert spec and spec.loader
_paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_paths)


class FindRootTest(unittest.TestCase):
    def test_ascends_from_cwd_when_marker_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            nested = proj / "a" / "b"
            nested.mkdir(parents=True)
            (proj / "CLAUDE.md").write_text("")
            self.assertEqual(_paths.find_root(nested), proj.resolve())

    def test_falls_back_to_install_location_when_no_marker_above_cwd(self):
        # Bug reproducido: cwd ajeno al proyecto (sin CLAUDE.md en ningún ancestro)
        # debe resolver a la raíz REAL instalada, no a ese cwd ajeno.
        with tempfile.TemporaryDirectory() as tmp:
            unrelated = Path(tmp)
            # tmp no tiene CLAUDE.md ascendiendo (salvo coincidencia improbable del sistema)
            self.assertEqual(_paths.find_root(unrelated), ROOT.resolve())

    def test_env_override_wins_when_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            proj.mkdir()
            (proj / "CLAUDE.md").write_text("")
            os.environ["SONY_A6000_KB_ROOT"] = str(proj)
            try:
                self.assertEqual(_paths.find_root(Path(tmp)), proj.resolve())
            finally:
                del os.environ["SONY_A6000_KB_ROOT"]

    def test_env_override_rejects_path_without_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["SONY_A6000_KB_ROOT"] = tmp
            try:
                with self.assertRaises(SystemExit):
                    _paths.find_root()
            finally:
                del os.environ["SONY_A6000_KB_ROOT"]


if __name__ == "__main__":
    unittest.main()
