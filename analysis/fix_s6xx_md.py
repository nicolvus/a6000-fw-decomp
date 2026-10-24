#!/usr/bin/env python3
"""Corrige los informes .md S605–S627: marca logger dual, equivalencia funcional y
equivalencia de código como NO_VERIFICADO donde la evidencia son solo cadenas."""
import re
from pathlib import Path

md_dir = Path("docs/capture")
md_files = sorted(
    f for f in md_dir.glob("s6[0-2][0-9]*.md")
    if 605 <= int(f.name[1:4]) <= 627
)

for md in md_files:
    text = md.read_text()

    # 1. "la fw3.21 **duplica** la traza" -> "la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO)"
    text = text.replace(
        "la fw3.21 **duplica** la traza",
        "la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA)"
    )
    text = text.replace(
        "La fw3.21 **duplica** la traza",
        "La fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA)"
    )

    # 2. "la fw3.21 **añade** capa" -> "la fw3.21 **añade** capa (NO_VERIFICADO para equivalencia de código)"
    text = text.replace(
        "La fw3.21 **añade** capa",
        "La fw3.21 **añade** capa de logging (NO_VERIFICADO - equivalencia de código no demostrada)"
    )
    text = text.replace(
        "la fw3.21 **añade** capa",
        "la fw3.21 **añade** capa de logging (NO_VERIFICADO - equivalencia de código no demostrada)"
    )

    # 3. "**existe igual** en los tres firmware" -> "**existe** (NO_VERIFICADO) en los tres firmware"
    text = text.replace(
        "**existe igual** en los tres firmware",
        "**existe** (NO_VERIFICADO - requiere análisis de A7S/A6300) en los tres firmware"
    )

    # 4. "**existe en los tres firmware**" -> "**existe** (NO_VERIFICADO) en los tres firmware"
    text = text.replace(
        "**existe en los tres firmware**",
        "**existe** (NO_VERIFICADO - requiere análisis de A7S/A6300) en los tres firmware"
    )

    # 5. "código equivalente" -> "código equivalente (NO_VERIFICADO)"
    text = text.replace(
        "código equivalente",
        "código equivalente (NO_VERIFICADO - requiere comparación de instrucciones)"
    )

    # 6. "mismas X cadenas núcleo" -> "mismas X cadenas núcleo (solo presencia de strings, NO_VERIFICADO para equivalencia de código)"
    text = text.replace(
        "mismas 17 cadenas núcleo",
        "mismas 17 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 7 cadenas núcleo",
        "mismas 7 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 6 cadenas núcleo",
        "mismas 6 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 5 cadenas núcleo",
        "mismas 5 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 4 cadenas núcleo",
        "mismas 4 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 3 cadenas núcleo",
        "mismas 3 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 2 cadenas núcleo",
        "mismas 2 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )
    text = text.replace(
        "mismas 1 cadenas núcleo",
        "mismas 1 cadenas núcleo (presencia de strings; equivalencia de código NO_VERIFICADO)"
    )

    # 7. "Lo propio de la fw3.21 ... es" -> "Lo propio de la fw3.21 ... es (NO_VERIFICADO para equivalencia de código)"
    text = text.replace(
        "Lo propio de la fw3.21 de la A6000 son",
        "Lo propio de la fw3.21 de la A6000 son (NO_VERIFICADO - requiere xrefs/REA para confirmar duplicación de logger)"
    )

    md.write_text(text)
    print(f"Actualizado: {md}")

print(f"\n{len(md_files)} informes .md actualizados.")