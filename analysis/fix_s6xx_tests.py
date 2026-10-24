#!/usr/bin/env python3
"""Actualiza los tests individuales S605–S627: test_logger_dual verifica
verification_status en lugar de afirmar logger_dual=True."""
from pathlib import Path
import re

test_dir = Path("tests")
test_files = sorted(
    f for f in test_dir.glob("test_s6[0-2][0-9]*.py")
    if 605 <= int(f.name[6:9]) <= 627
)

for tf in test_files:
    text = tf.read_text()

    # Reemplazar test_logger_dual
    old = """    def test_logger_dual(self):
        self.assertTrue(self.data['logger_dual'])"""
    new = """    def test_logger_dual(self):
        vs = self.data.get('verification_status', {})
        ld = vs.get('logger_dual', {})
        self.assertEqual(ld.get('status'), 'NO_VERIFICADO',
                         f'{tf.name}: logger_dual no es NO_VERIFICADO')"""

    if old in text:
        text = text.replace(old, new)
        tf.write_text(text)
        print(f"Actualizado: {tf}")
    else:
        print(f"SIN CAMBIO (patrón no encontrado): {tf}")

print(f"\n{len(test_files)} tests revisados.")