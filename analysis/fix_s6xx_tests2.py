#!/usr/bin/env python3
"""Corrige el mensaje de error en test_logger_dual: elimina referencia a tf."""
from pathlib import Path

test_dir = Path("tests")
test_files = sorted(
    f for f in test_dir.glob("test_s6[0-2][0-9]*.py")
    if 605 <= int(f.name[6:9]) <= 627
)

old_msg = "f'{tf.name}: logger_dual no es NO_VERIFICADO'"
new_msg = "'logger_dual no es NO_VERIFICADO'"

for tf in test_files:
    text = tf.read_text()
    if old_msg in text:
        text = text.replace(old_msg, new_msg)
        tf.write_text(text)
        print(f"Actualizado: {tf}")
    else:
        print(f"SIN CAMBIO: {tf}")

print(f"\n{len(test_files)} tests revisados.")