# Brief común para subagentes de objetivos (wiki/16-Objetivos.md)

Repo: /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter (ingeniería inversa del firmware Sony A6000 y CFW propio). Responde en español.

## Antes de empezar
- Lee CLAUDE.md del repo y del directorio padre, y `knowledge/CURRENT.md` con head/grep (es grande).
- Usa el MCP `sony-a6000-knowledge` antes de investigar a mano. Firmware: REA primero (MCP `rea`; daemon `analysis/rea-independent/bin/session_daemon.py` + `q.py`; ver /home/nicolas/.claude/projects/-home-nicolas-Documents-a6000/memory/reference-rea-daemon-uso.md). Ghidra solo de respaldo. Verifica lo decisivo contra bytes.
- Comprueba primero si la función YA EXISTE de fábrica en la A6000 (como pasó con Extra Fine, G37) o si ya hay trabajo previo en el repo.

## Cómo cerrar el objetivo (elige uno, con evidencia)
1. **Implementado**: escribe el parche siguiendo los patrones del CFW (menú: AÑADIR opción, nunca sustituir; `scripts/gui/add_menu_entry.py`, `menu_tables.py`, parches `pp_*_patch.py` como modelo). **REGLA DEL USUARIO: NO construyas ningún CFW (ni `.dat` ni paquete, nada de `build_cfw_*`/`build_package_*`).** La prueba es SIEMPRE en el arnés GUI (guía `docs/gui/g22-emulador-uso.md`): aplica el parche a copias de los binarios en tu propio directorio de trabajo y ejecútalo en el arnés, con captura PNG como evidencia, sin interrumpir los cambios que otra sesión hace en el arnés. Si una parte no se puede emular, dilo y prueba lo que sí (bytes del parche, tablas, cálculos). **REGLA DEL USUARIO: si algo no se puede probar en el arnés, solo se modifican ficheros que formen parte del `.dat` del firmware y sean replicables en la A6000 real (binarios/`.so`/`.uxc` del firmware). Nada de cambios que solo valgan para el arnés o el emulador** (no se edita `ae.py` ni ninguna copia, ni el shim, ni los valores iniciales solo de prueba). La prueba de esos parches es Unicorn sobre los bytes reales, con test de los bytes originales.
2. **Ya existe de fábrica**: demuéstralo y descártalo como objetivo.
3. **Descartado**: límite de hardware/firmware verificado (medido o probado estáticamente con direcciones y bytes), como «Nivel digital» en wiki 16.
4. **Parcial**: si es factible pero excede una sesión razonable, entrega la primera pieza útil y funcionando, y deja pendientes concretos con criterio de cierre.
**REGLA DEL USUARIO: nada de apps PMCA/Android (ni oficiales de Sony ni OpenMemories). Cada función debe quedar integrada en el firmware, como opción del menú oficial de la cámara.** Una app existente puede citarse como referencia del motor que usa, pero nunca cuenta como solución.
**Cuevas y celdas de datos**: toda cueva o celda nueva debe estar a cero en el fichero Y en el volcado de RAM viva (método de g72/g74, `tests/test_g74_cuevas_seguras.py`), sin referencias, y fuera del bss declarado. Añádela a ese test. Huecos ya verificados y su ocupación: ver `docs/gui/g74-auditoria-cuevas-campana.md` y g73. Para datos grandes, usa memoria dinámica (`malloc` `0x43561164` de av-cam, patrón de reserva perezosa de g73). Nunca uses `git stash`.
No te detengas en dudas: decide con criterio y sigue hasta el cierre.

## Reglas que no puedes romper
- Sin cámara, sin flasheo, sin instalar nada en la cámara. Solo offline + arnés.
- OTRA sesión modifica el arnés en paralelo: NO edites nada bajo `scripts/gui/harness/` (hay cambios sin commit ajenos). Puedes ejecutarlo con tus propios directorios de salida/temporales, sin matar procesos ajenos ni cambiar su configuración. Si el arnés necesita un cambio, anótalo como pendiente nuevo.
- Git: nunca `stash`, `reset`, `checkout --`, `clean`, ni `add -A`/`add .`. `git add` solo de rutas tuyas. Commit Conventional Commits que termine con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Después `gh auth switch -u nicolvus`, `gh auth status`, `git push origin main` (si el remoto avanzó: `git pull --rebase --autostash` NO; usa `git pull --rebase` solo si no toca cambios ajenos; si no, deja el commit local y dilo).
- Documentación: informe en `docs/gui/` (siguiente gNN libre), ID nuevo en `docs/PENDIENTES.md` (estado, origen, criterio de cierre), actualiza la línea del objetivo en `wiki/16-Objetivos.md` (✅ solo si verificado en cámara; si no, anota «CFW 3.xx construido, sin instalar», o muévelo a Descartadas con «❌ … motivo + enlace»), y corre knowledge-maintenance (`scripts/knowledge/build_subsystem_index.py` y lo que indique CLAUDE.md). No toques README.md.
- Silencio entre herramientas. Ahorra contexto: filtra con head/grep, nada de cat de ficheros grandes.

## Entrega (mensaje final, ≤ 15 líneas)
Resultado (implementado / ya existe / descartado / parcial), evidencia clave, versión CFW y hash del .dat si construiste, hash del commit y si hubo push, límites y pendientes nuevos.
