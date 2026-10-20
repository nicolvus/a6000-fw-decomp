"""Verificación real del protocolo MCP: descubrimiento de herramientas y llamadas,
en memoria (sin subproceso), contra la implementación real de mcp_server.py."""

import asyncio
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "knowledge"))

spec = importlib.util.spec_from_file_location("mcp_server", ROOT / "scripts" / "knowledge" / "mcp_server.py")
mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_server)


class McpServerProtocolTest(unittest.TestCase):
    def test_tools_are_discoverable(self):
        tools = asyncio.run(mcp_server.server.list_tools())
        names = {t.name for t in tools}
        expected = {
            "search_exact", "search_documents", "search_hybrid", "find_symbol",
            "get_document_section", "query_graph", "trace_relations", "find_corrections",
            "get_open_questions", "get_current_state", "check_index_freshness",
        }
        self.assertEqual(expected, names)

    def test_call_tool_search_exact_returns_real_result(self):
        result = asyncio.run(mcp_server.server.call_tool("search_exact", {"query": "0x932a44"}))
        text = result[0].content[0].text if hasattr(result, "__getitem__") else str(result)
        self.assertIn("932a44", text)

    def test_call_tool_get_current_state_reads_real_file(self):
        result = asyncio.run(mcp_server.server.call_tool("get_current_state", {}))
        text = result[0].content[0].text if hasattr(result, "__getitem__") else str(result)
        self.assertIn("Estado vigente", text)

    def test_get_current_state_respects_global_mcp_char_limit(self):
        # Bug de la auditoría (Fase 12.2.D): get_current_state devolvía el archivo
        # COMPLETO sin pasar por MCP_MAX_CHARS, a diferencia de toda otra tool.
        big = mcp_server.ROOT / "docs" / "STATE.md"
        original = big.read_text(encoding="utf-8")
        try:
            big.write_text("X" * (mcp_server.MCP_MAX_CHARS + 500), encoding="utf-8")
            text = mcp_server.get_current_state()
            self.assertLessEqual(len(text), mcp_server.MCP_MAX_CHARS + 100)
            self.assertIn("límite MCP", text)
        finally:
            big.write_text(original, encoding="utf-8")

    def test_get_current_state_offset_paginates(self):
        text1 = mcp_server.get_current_state(offset=0)
        text2 = mcp_server.get_current_state(offset=10)
        self.assertNotEqual(text1, text2)
        self.assertEqual(text1[10:], text2[:len(text1) - 10])

    def test_call_tool_with_invalid_input_does_not_crash_server(self):
        result = asyncio.run(mcp_server.server.call_tool(
            "query_graph", {"direction": "sideways"}  # fuera de los choices válidos del CLI
        ))
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
