"""Regresión del grafo: entidades Function desde JSON, correcciones desde Markdown,
y el caso límite de proximidad (el número de sesión del encabezado no debe colarse
como objetivo de una corrección que menciona OTRA sesión en el cuerpo)."""

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_SCRIPT = ROOT / "scripts" / "knowledge" / "index_docs.py"
GRAPH_SCRIPT = ROOT / "scripts" / "knowledge" / "build_graph.py"


class BuildGraphTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.proj = self.tmp_path / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "analysis" / "functions").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        self.db = self.tmp_path / "knowledge.sqlite"

    def tearDown(self):
        self._tmp.cleanup()

    def run_script(self, script):
        return subprocess.run(
            [sys.executable, str(script), "--db", str(self.db)],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )

    def test_function_calls_require_exact_name_match_same_binary(self):
        dossier = [
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x100", "original_name": "ns::A::foo()",
             "outgoing": ["bar at 0x200", "unresolved external call"]},
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x200", "original_name": "ns::B::bar()",
             "outgoing": []},
            {"binary": "lib/other.so", "sha256": "xyz", "address_space": "ELF",
             "symbol_value": "0x200", "original_name": "ns::C::bar()",
             "outgoing": []},
        ]
        (self.proj / "analysis" / "functions" / "dossier.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0], 3)
        rels = conn.execute("SELECT type, src_id, dst_id FROM relations WHERE type='CALLS'").fetchall()
        self.assertEqual(len(rels), 1)  # solo foo->bar en el MISMO binario; ns::C::bar() se descarta
        conn.close()

    def test_ambiguous_short_name_in_same_binary_is_discarded_not_misrouted(self):
        # Caso reproducido en la auditoría: X::caller() llama a A::run(), pero B::run()
        # (otra clase, MISMO binario) tiene el mismo nombre corto "run". Antes, el índice
        # por nombre corto se sobrescribía (el último insertado "ganaba"), así que el grafo
        # podía registrar X::caller() -> B::run() en vez de -> A::run(), o al revés según
        # el orden de inserción. Ahora: si el nombre corto es ambiguo en el binario y la
        # llamada no trae el nombre calificado, no se genera ninguna arista (ni A ni B).
        dossier = [
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x100", "original_name": "ns::X::caller()",
             "outgoing": ["run()"]},  # llamada SIN calificar: ambigua entre A::run y B::run
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x200", "original_name": "ns::A::run()", "outgoing": []},
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x300", "original_name": "ns::B::run()", "outgoing": []},
        ]
        (self.proj / "analysis" / "functions" / "dossier.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rels = conn.execute("SELECT type FROM relations WHERE type='CALLS'").fetchall()
        conn.close()
        self.assertEqual(len(rels), 0)  # ambiguo: ninguna arista, nunca una incorrecta

    def test_qualified_outgoing_name_disambiguates_same_short_name(self):
        # Mismo caso, pero la llamada SÍ trae el nombre calificado ("ns::A::run()"):
        # debe resolver exactamente a A::run, nunca a B::run.
        dossier = [
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x100", "original_name": "ns::X::caller()",
             "outgoing": ["ns::A::run()"]},
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x200", "original_name": "ns::A::run()", "outgoing": []},
            {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
             "symbol_value": "0x300", "original_name": "ns::B::run()", "outgoing": []},
        ]
        (self.proj / "analysis" / "functions" / "dossier.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rels = conn.execute(
            "SELECT src_id, dst_id FROM relations WHERE type='CALLS'"
        ).fetchall()
        conn.close()
        self.assertEqual(len(rels), 1)
        src, dst = rels[0]
        with sqlite3.connect(self.db) as c:
            caller_id = c.execute(
                "SELECT id FROM entities WHERE name = 'ns::X::caller()'"
            ).fetchone()[0]
            a_run_id = c.execute(
                "SELECT id FROM entities WHERE name = 'ns::A::run()'"
            ).fetchone()[0]
        self.assertEqual(src, caller_id)
        self.assertEqual(dst, a_run_id)

    def test_correction_resolves_only_from_same_line_not_section_window(self):
        # El encabezado menciona "S21"; el cuerpo corrige "S18" en una línea distinta.
        # Con solo un documento s18 existente, debe resolver a S18 y NO inventar un
        # destino a partir del número de sesión del propio encabezado.
        (self.proj / "docs" / "capture" / "s18-topic.md").write_text("# S18 — tema\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "s21-topic.md").write_text(
            "## S21 — otro tema\n\n"
            "Línea de relleno.\n"
            "Línea de relleno.\n"
            "**VERIFICADO (corrige S18):** el resultado anterior era incompleto.\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rels = conn.execute(
            "SELECT status, dst_id FROM relations WHERE src_id = 'docs/capture/s21-topic.md'"
        ).fetchall()
        conn.close()
        self.assertEqual(len(rels), 1)
        status, dst = rels[0]
        self.assertEqual(dst, "docs/capture/s18-topic.md")
        self.assertEqual(status, "VERIFICADO")

    def test_link_only_in_window_is_candidate_not_verified(self):
        # El enlace a old.md está en la línea SIGUIENTE a la del marcador "CORRECCIÓN",
        # no en la misma oración: es una relación candidata (proximidad), no demostrada.
        # Antes se le asignaba igualmente el status VERIFICADO si esa palabra aparecía en
        # la ventana; ahora una relación solo de ventana se marca CONFLICTO_PENDIENTE.
        (self.proj / "docs" / "capture" / "old.md").write_text("# Resultado original\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Resultado nuevo\n\n"
            "CORRECCIÓN VERIFICADA: el resultado cambió.\n"
            "Ver también [el resultado anterior](old.md) para contexto.\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rows = conn.execute(
            "SELECT status, extraction_method FROM relations WHERE dst_id = 'docs/capture/old.md'"
        ).fetchall()
        conn.close()
        self.assertEqual(len(rows), 1)
        status, method = rows[0]
        self.assertEqual(status, "CONFLICTO_PENDIENTE")
        self.assertIn("window_candidate", method)

    def test_duplicate_function_across_dossiers_does_not_crash_and_keeps_both_sources(self):
        # Caso de la auditoría (Fase 12.1.C): la MISMA función (misma identidad técnica:
        # sha256+address_space+symbol_value) aparece en dos JSON de análisis distintos
        # (p. ej. reanalizada o exportada por dos herramientas). Antes, el segundo INSERT
        # fallaba con "UNIQUE constraint failed: entities.id".
        common = {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
                  "symbol_value": "0x100", "original_name": "ns::A::foo()", "outgoing": []}
        (self.proj / "analysis" / "functions" / "dossier1.json").write_text(
            json.dumps([common]), encoding="utf-8"
        )
        (self.proj / "analysis" / "functions" / "dossier2.json").write_text(
            json.dumps([common]), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)  # no debe lanzar CalledProcessError (UNIQUE constraint)

        conn = sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0], 1)
        sources = conn.execute(
            "SELECT owner_source FROM entity_sources ORDER BY owner_source"
        ).fetchall()
        conn.close()
        self.assertEqual([s[0] for s in sources],
                          ["analysis/functions/dossier1.json", "analysis/functions/dossier2.json"])

    def test_contradictory_metadata_between_dossiers_is_flagged_not_silently_overwritten(self):
        # Misma identidad técnica, pero original_name DISTINTO entre dossiers (metadato
        # contradictorio real, p. ej. un símbolo renombrado entre dos exports). Debe
        # conservarse el primero como canónico y registrarse el conflicto, no sobrescribir
        # en silencio ni descartar la segunda fuente.
        base = {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
                "symbol_value": "0x100", "outgoing": []}
        (self.proj / "analysis" / "functions" / "dossier1.json").write_text(
            json.dumps([{**base, "original_name": "ns::A::foo()"}]), encoding="utf-8"
        )
        (self.proj / "analysis" / "functions" / "dossier2.json").write_text(
            json.dumps([{**base, "original_name": "ns::A::fooRenamed()"}]), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        name, extra = conn.execute("SELECT name, extra FROM entities").fetchone()
        sources = conn.execute(
            "SELECT owner_source, original_name FROM entity_sources ORDER BY owner_source"
        ).fetchall()
        conn.close()
        self.assertIn(name, ("ns::A::foo()", "ns::A::fooRenamed()"))  # la primera procesada
        self.assertIn("name_conflict", extra)
        # ambas fuentes conservan SU propio nombre, no el canónico elegido para la entidad
        self.assertEqual(dict(sources), {
            "analysis/functions/dossier1.json": "ns::A::foo()",
            "analysis/functions/dossier2.json": "ns::A::fooRenamed()",
        })

    def test_removing_one_of_two_dossiers_keeps_entity_alive_via_remaining_source(self):
        common = {"binary": "lib/a.so", "sha256": "abc", "address_space": "ELF",
                  "symbol_value": "0x100", "original_name": "ns::A::foo()", "outgoing": []}
        (self.proj / "analysis" / "functions" / "dossier1.json").write_text(
            json.dumps([common]), encoding="utf-8"
        )
        (self.proj / "analysis" / "functions" / "dossier2.json").write_text(
            json.dumps([common]), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        (self.proj / "analysis" / "functions" / "dossier1.json").unlink()
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        sources = conn.execute("SELECT owner_source FROM entity_sources").fetchall()
        conn.close()
        self.assertEqual(n_entities, 1)  # sigue viva: dossier2 todavía la aporta
        self.assertEqual([s[0] for s in sources], ["analysis/functions/dossier2.json"])

    def test_ghidra_functions_family_creates_entities_and_address_based_calls(self):
        # Fase 12.4: formato dominante de exports Ghidra ({source_sha256, functions:[...]}),
        # detectado por FORMA (no por nombre de archivo). pseudo_code de FUN_43ae0002 llama
        # a FUN_43ae0100, que SÍ tiene evidencia decompilada en el mismo binario.
        dossier = {
            "source_sha256": "deadbeef", "method": "test", "firmware_profile": "ILCE-6000 3.21",
            "functions": [
                {"entry": "43ae0002", "status": "decompiled",
                 "pseudo_code": "undefined4 FUN_43ae0002(void) { return FUN_43ae0100(); }"},
                {"entry": "43ae0100", "status": "decompiled", "pseudo_code": "return 0;"},
            ],
        }
        (self.proj / "analysis" / "functions" / "ghidra1.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        entities = conn.execute(
            "SELECT name, address, address_space, binary_sha256, extra FROM entities "
            "WHERE binary_sha256 = 'deadbeef' ORDER BY name"
        ).fetchall()
        rels = conn.execute(
            "SELECT type, status, extraction_method FROM relations "
            "WHERE extraction_method = 'ghidra:pseudo_code_call_same_binary'"
        ).fetchall()
        conn.close()
        self.assertEqual([e[:4] for e in entities], [
            ("FUN_43ae0002", "0x43ae0002", "unknown", "deadbeef"),
            ("FUN_43ae0100", "0x43ae0100", "unknown", "deadbeef"),
        ])
        self.assertIn("ILCE-6000 3.21", entities[0][4])  # firmware_profile conservado, no inventado
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0], ("CALLS", "PARCIAL", "ghidra:pseudo_code_call_same_binary"))

    def test_ghidra_call_through_thunk_is_tagged_as_indirect_not_direct(self):
        # Ghidra nombra el trampolín en una dirección como 'thunk_FUN_<addr>': sigue siendo
        # una llamada real a esa dirección, pero debe distinguirse de una llamada directa
        # (auditoría 12.6, punto 1: "distingue llamadas directas, indirectas...").
        dossier = {
            "source_sha256": "deadbeef", "method": "test",
            "functions": [
                {"entry": "100", "status": "decompiled", "pseudo_code": "thunk_FUN_200();"},
                {"entry": "200", "status": "decompiled", "pseudo_code": "return;"},
            ],
        }
        (self.proj / "analysis" / "functions" / "ghidra1.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        method = conn.execute(
            "SELECT extraction_method FROM relations WHERE type = 'CALLS'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(method, "ghidra:pseudo_code_call_same_binary_via_thunk")

    def test_ghidra_function_without_decompiled_status_is_not_an_entity(self):
        # "function_not_created"/error: ausencia de decompilación real no se convierte en
        # una entidad del grafo (no inventar evidencia donde no la hay).
        dossier = {
            "source_sha256": "deadbeef", "method": "test",
            "functions": [{"query": "43ae0002", "status": "function_not_created", "error": "x"}],
        }
        (self.proj / "analysis" / "functions" / "ghidra1.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n = conn.execute("SELECT COUNT(*) FROM entities WHERE binary_sha256 = 'deadbeef'").fetchone()[0]
        conn.close()
        self.assertEqual(n, 0)

    def test_ghidra_call_to_address_without_evidence_is_discarded(self):
        # FUN_99999999 no tiene ninguna entidad con esa dirección en el corpus: 0
        # candidatos, se descarta (no se inventa el destino).
        dossier = {
            "source_sha256": "deadbeef", "method": "test",
            "functions": [{"entry": "43ae0002", "status": "decompiled",
                            "pseudo_code": "FUN_99999999();"}],
        }
        (self.proj / "analysis" / "functions" / "ghidra1.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE extraction_method = "
            "'ghidra:pseudo_code_call_same_binary'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(n, 0)

    def test_ghidra_calls_resolve_across_different_owner_files_same_binary(self):
        # El llamante vive en un archivo de topic distinto al del llamado (caso real: el
        # mismo binario se analiza en muchos JSON temáticos separados). La resolución debe
        # ser por binary_sha256+dirección en TODO el grafo, no solo dentro del mismo archivo.
        (self.proj / "analysis" / "functions" / "caller.json").write_text(json.dumps({
            "source_sha256": "deadbeef", "method": "test",
            "functions": [{"entry": "100", "status": "decompiled",
                            "pseudo_code": "FUN_200();"}],
        }), encoding="utf-8")
        (self.proj / "analysis" / "functions" / "callee.json").write_text(json.dumps({
            "source_sha256": "deadbeef", "method": "test",
            "functions": [{"entry": "200", "status": "decompiled", "pseudo_code": "return;"}],
        }), encoding="utf-8")
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE extraction_method = "
            "'ghidra:pseudo_code_call_same_binary'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(n, 1)

    def test_rerunning_ghidra_extractor_is_idempotent(self):
        dossier = {
            "source_sha256": "deadbeef", "method": "test",
            "functions": [
                {"entry": "100", "status": "decompiled", "pseudo_code": "FUN_200();"},
                {"entry": "200", "status": "decompiled", "pseudo_code": "return;"},
            ],
        }
        (self.proj / "analysis" / "functions" / "ghidra1.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        self.run_script(GRAPH_SCRIPT)  # segunda vez: no debe fallar ni duplicar

        conn = sqlite3.connect(self.db)
        n_entities = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE binary_sha256 = 'deadbeef'"
        ).fetchone()[0]
        n_rels = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE extraction_method = "
            "'ghidra:pseudo_code_call_same_binary'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(n_entities, 2)
        self.assertEqual(n_rels, 1)

    def test_same_call_reported_by_two_owner_files_deduplicates_but_keeps_both_provenances(self):
        # Caso real detectado en auditoría 12.6: la MISMA llamada FUN_100->FUN_200 aparece en
        # el pseudocódigo exportado por dos sesiones distintas (el mismo binario reanalizado).
        # Debe quedar UNA sola relación CALLS, no una por archivo, pero sin perder qué
        # archivos la respaldan.
        (self.proj / "analysis" / "functions" / "session_a.json").write_text(json.dumps({
            "source_sha256": "deadbeef", "method": "test",
            "functions": [{"entry": "100", "status": "decompiled", "pseudo_code": "FUN_200();"},
                           {"entry": "200", "status": "decompiled", "pseudo_code": "return;"}],
        }), encoding="utf-8")
        (self.proj / "analysis" / "functions" / "session_b.json").write_text(json.dumps({
            "source_sha256": "deadbeef", "method": "test",
            "functions": [{"entry": "100", "status": "decompiled", "pseudo_code": "FUN_200();"}],
        }), encoding="utf-8")
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n_rels = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE extraction_method = "
            "'ghidra:pseudo_code_call_same_binary'"
        ).fetchone()[0]
        rel_id = conn.execute(
            "SELECT id FROM relations WHERE extraction_method = "
            "'ghidra:pseudo_code_call_same_binary'"
        ).fetchone()[0]
        n_sources = conn.execute(
            "SELECT COUNT(DISTINCT owner_source) FROM relation_sources WHERE relation_id = ?",
            (rel_id,),
        ).fetchone()[0]
        conn.close()
        self.assertEqual(n_rels, 1)
        self.assertEqual(n_sources, 2)

    def test_rea_procedure_pseudo_code_shape_creates_entity(self):
        # Forma REA 'procedure_pseudo_code': una función, dirección en locations, nombre
        # extraído del comentario /* ns::Clase::metodo() */ al inicio del pseudocódigo.
        dossier = {
            "evidence_id": "ev_1", "operation": "procedure_pseudo_code",
            "subject": {"name": "libcamera.so", "digest": {"sha256": "cafef00d"}},
            "locations": [{"kind": "address", "address": "0x270c0"}],
            "normalized_result": "\n/* ns::Clase::metodo() */\n\nvoid ns::Clase::metodo() { return; }\n",
        }
        (self.proj / "analysis" / "functions" / "rea1.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        row = conn.execute(
            "SELECT name, address, address_space FROM entities WHERE binary_sha256 = 'cafef00d'"
        ).fetchone()
        conn.close()
        self.assertEqual(row, ("ns::Clase::metodo", "0x270c0", "unknown"))

    def test_rea_batch_decompile_shape_resolves_named_call(self):
        # Forma REA 'batch_decompile': varias funciones NOMBRADAS; una llama a otra por
        # nombre (no por dirección) y ambas tienen evidencia 'ok'/'resolved' en el corpus.
        dossier = {
            "evidence_id": "ev_2", "operation": "batch_decompile",
            "subject": {"name": "osal_uipc.ko", "digest": {"sha256": "deadbeef"}},
            "normalized_result": {"items": [
                {"address": "caller_fn",
                 "procedure": {"status": "resolved", "address": "0x100", "name": "caller_fn"},
                 "status": "ok", "pseudocode": "void caller_fn(void) { callee_fn(); }"},
                {"address": "callee_fn",
                 "procedure": {"status": "resolved", "address": "0x200", "name": "callee_fn"},
                 "status": "ok", "pseudocode": "void callee_fn(void) { return; }"},
            ]},
        }
        (self.proj / "analysis" / "functions" / "rea2.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n_entities = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE binary_sha256 = 'deadbeef'"
        ).fetchone()[0]
        rels = conn.execute(
            "SELECT s.name, d.name, r.extraction_method FROM relations r "
            "JOIN entities s ON r.src_id = s.id JOIN entities d ON r.dst_id = d.id "
            "WHERE s.binary_sha256 = 'deadbeef'"
        ).fetchall()
        conn.close()
        self.assertEqual(n_entities, 2)
        self.assertEqual(rels, [("caller_fn", "callee_fn", "rea:pseudo_code_named_call_same_binary")])

    def test_rea_unresolved_batch_item_is_not_an_entity(self):
        dossier = {
            "evidence_id": "ev_3", "operation": "batch_decompile",
            "subject": {"name": "osal_uipc.ko", "digest": {"sha256": "deadbeef"}},
            "normalized_result": {"items": [
                {"address": "unresolved_fn",
                 "procedure": {"status": "unresolved", "address": None, "name": None},
                 "status": "error", "pseudocode": None},
            ]},
        }
        (self.proj / "analysis" / "functions" / "rea3.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE binary_sha256 = 'deadbeef'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(n, 0)

    def test_rerunning_rea_extractor_is_idempotent(self):
        dossier = {
            "evidence_id": "ev_4", "operation": "procedure_pseudo_code",
            "subject": {"name": "libx.so", "digest": {"sha256": "cafef00d"}},
            "locations": [{"kind": "address", "address": "0x1000"}],
            "normalized_result": "void f() { return; }",
        }
        (self.proj / "analysis" / "functions" / "rea4.json").write_text(
            json.dumps(dossier), encoding="utf-8"
        )
        (self.proj / "docs" / "capture" / "placeholder.md").write_text("# Placeholder\n")
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        n = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE binary_sha256 = 'cafef00d'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(n, 1)

    def test_negated_correction_mention_is_not_verified(self):
        # Caso de la auditoría (Fase 12.1.A): "esta revisión NO corrige [...]" generaba
        # incorrectamente CORRECTS con status VERIFICADO por la sola presencia de "corrige"
        # y "VERIFICADO" en la misma línea, ignorando la negación.
        (self.proj / "docs" / "capture" / "old.md").write_text("# Informe antiguo\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Revisión\n\n"
            "VERIFICADO: esta revisión no corrige [el informe antiguo](old.md).\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rows = conn.execute(
            "SELECT status, extraction_method FROM relations WHERE dst_id = 'docs/capture/old.md'"
        ).fetchall()
        conn.close()
        self.assertEqual(len(rows), 1)
        status, method = rows[0]
        self.assertEqual(status, "CONFLICTO_PENDIENTE")  # nunca VERIFICADO pese al texto cercano
        self.assertIn("negated", method)

    def test_negation_further_than_four_words_before_marker_is_still_detected(self):
        # Fase 12.4: la auditoría señaló que acotar la negación a 4 palabras previas no
        # demuestra cobertura completa. Aquí "no" está a 7 palabras de "corrige", dentro
        # de la MISMA oración: debe seguir detectándose.
        (self.proj / "docs" / "capture" / "old.md").write_text("# Informe antiguo\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Revisión\n\n"
            "VERIFICADO: a pesar de lo que se podría pensar inicialmente, no corrige "
            "[el informe antiguo](old.md).\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rows = conn.execute(
            "SELECT status FROM relations WHERE dst_id = 'docs/capture/old.md'"
        ).fetchall()
        conn.close()
        self.assertEqual(rows[0][0], "CONFLICTO_PENDIENTE")

    def test_adversative_hedge_after_marker_in_same_clause_is_not_verified(self):
        # "corrige ..., pero nunca de forma completa" dentro de la MISMA oración: una
        # corrección con matiz adversativo no debe quedar como VERIFICADO sin más.
        (self.proj / "docs" / "capture" / "old.md").write_text("# Informe antiguo\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Revisión\n\n"
            "VERIFICADO: esta revisión corrige [el informe antiguo](old.md), "
            "pero nunca de forma completa.\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        rows = conn.execute(
            "SELECT status FROM relations WHERE dst_id = 'docs/capture/old.md'"
        ).fetchall()
        conn.close()
        self.assertEqual(rows[0][0], "CONFLICTO_PENDIENTE")

    def test_md_link_correction_and_claim_query(self):
        (self.proj / "docs" / "capture" / "old.md").write_text("# Resultado original\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Resultado nuevo\n\n"
            "CORRECCIÓN: esto corrige [el resultado anterior](old.md) con nueva evidencia.\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        incoming = conn.execute(
            "SELECT type, src_id, evidence FROM relations WHERE dst_id = 'docs/capture/old.md'"
        ).fetchall()
        conn.close()
        self.assertEqual(len(incoming), 1)
        rel_type, src, evidence = incoming[0]
        self.assertEqual(rel_type, "CORRECTS")
        self.assertEqual(src, "docs/capture/new.md")
        self.assertIn("corrige", evidence)

    def test_removing_owner_doc_prunes_its_relations_on_rebuild(self):
        (self.proj / "docs" / "capture" / "old.md").write_text("# Resultado original\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Resultado nuevo\n\nCORRECCIÓN: corrige [lo anterior](old.md).\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        (self.proj / "docs" / "capture" / "new.md").unlink()
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)

        conn = sqlite3.connect(self.db)
        remaining = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE owner_source = 'docs/capture/new.md'"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(remaining, 0)


if __name__ == "__main__":
    unittest.main()
