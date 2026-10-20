# S64 — prueba en cámara: SilentShutter en RAM, NVRAM y consumidores

20-10-2026. Cámara ILCE-6000 fw 3.21 en service mode (PMCA, `scripts/senser_*.py`); análisis estático con REA (una sesión, cerrada) y barrido Capstone de `av-cam.bin` (SHA `b60c845c…6bb9`). Sin flasheo, sin parche; la única escritura fue una palabra de RAM, restaurada.

## Hechos medidos en la cámara (VERIFICADO)

1. **Acceso:** service mode lee memoria física (`readMemory`) y el shell escribe con `dd of=/dev/mem` (`scripts/senser_write_poll.py`). Física = virtual de `av-cam` − `0x40000000`.
2. **Campo Silent** `0x43edf684+0x238` = física `0x83edf8bc`: `0→1→0` con lectura confirmada. Con la sesión abierta el valor se mantuvo 60 s (48 977 lecturas). La primera observación (a 0 unos 40 s tras escribir y releer en otra sesión) **no está explicada**.
3. **NVRAM:** backups `mem` y `flash` (852 647 B) en tres estados (base, Silent=1, revertido). `flash` idéntica en los tres; `mem` difiere en 3 bytes (33, 237 673, 613 374) y esos cambios están ya en «Silent=1» y siguen en «revertido» ⇒ no dependen del modo. `analysis/camera-dumps/silent-nvram-20261020/` (no versionado).
4. **RAM 4 MB** (`0x83c00000–0x84000000`), 4 ciclos off/on: 9 palabras cambian de forma consistente (la escrita + 8 punteros/banderas). **Control** idéntico escribiendo en `0x83dab230` (zona a cero, sin relación): la palabra escrita + 7 del mismo tipo ⇒ esas palabras son artefacto del procedimiento (`dd` en el shell), no del modo.
5. Escribir el campo directamente **no ejecuta el handler `0x40e3`**: no prueba nada sobre su efecto, solo que no hay cambios colaterales visibles en esas regiones.

## Hallazgos estáticos (`av-cam.bin`)

- El bloque `0x43edf684` tiene 5 referencias directas (`0x43803f14`, `0x43803f56`, `0x438045c0`, `0x43804c52`, `0x43804dea`). Getter `0x43804de8` (22 llamadoras) y `0x43804c38` (4): ninguna llamadora carga/guarda con `#0x238` o `#0x280` (VERIFICADO sobre desensamblado).
- Copia de 0x560 B bloque → objeto de trabajo `0x43ed4d28+0x48` en `0x437dfd58` (llamadoras `0x43808774`, `0x43b02206`); el campo queda en `+0x280`. Los 15 usos del puntero GOT `0x44023bbc` no tienen cargas `+0x280/+0x238`.
- **`0x43804610`** (no reconocida por REA, Thumb): lee un byte con `Backup_read` (wrapper `0x435613b0`, slot `0x298` de la tabla de servicios) y **reinicializa el bloque a valores por defecto, poniendo `+0x238` y `+0x280` a 0** (`0x438047b6`, `0x43804810`). Única llamadora: `0x437881a8`. El byte de backup no fija `+0x238`.
- `0x43802614`: handler hermano que escribe `+0x280` (otro comando, patrón «un campo por comando»; sin estudiar).
- Escritura de backup en `av-cam`: wrappers `0x43561420` (write), `0x43561458` (write_multi), `0x43561474` (async), `0x43561494` (multi_async). Única llamadora cercana al bloque: `0x43809148` (despachador de mensajes `0x3000–0x3034`): escribe un byte 0 en los mensajes `0x3000/0x3003/0x3006/0x3007/0x300c`; sus campos del bloque son `+0x40a/+0x4cc/+0x450…/+0xd0`, no `+0x238`.

## Conclusión

**No se encontró** ruta que persista el modo Silent en NVRAM; la inicialización lo deja a 0. No se puede «fijar» el modo por backup. Sin consumidor de captura demostrado. S51 A/B/C = NO VERIFICADO; «electrónico completo» NO VERIFICADO.

## Límites

Barrido lineal de `av-cam`: 882 sitios `+0x238/+0x280` (872 Thumb, 10 ARM); solo se trataron los de la zona del bloque. Slots de backup sin wrapper (`write_vsize`, `setting_attr_async`, `sync_subsystem`) no cubiertos. Lecturas indirectas (copias en bloque a otras estructuras) no vistas. Solo 4 MB de RAM comparados.

## Ampliación: cuándo se reinicializa y tabla de comandos «de estado»

- `0x43804610` se llama desde la secuencia de arranque de `av-cam` (`0x437881a8`, entre `0x437e18b4` y `0x4378f9b4`, junto a otras inicializaciones de módulo). Es una inicialización de arranque, no una reposición periódica. Que ocurra también al cambiar de sesión de service mode: NO VERIFICADO.
- Tabla de entradas `{ID, handler|1, 0}` en `0x43fffbb8…` (IDs `0x40d7…0x40f3`, VERIFICADO por bytes). Cada handler guarda un único campo del bloque `0x43edf684`: `0x40e2→+0x234`, **`0x40e3→+0x238`**, `0x40ed→+0x23c`, `0x40ee→+0x240`, `0x40ef→+0x242`, `0x40f0→+0x244/248/24c`, `0x40f1→+0x250`, `0x40e4→+0x35c`, `0x40e6→+0x360`, etc. El bloque es un espejo de ajustes enviados por UIPC; ningún handler hace más que almacenar.
- `+0x280` lo escribe otro handler (`0x4380260c`), fuera de esa tabla (tabla no localizada).
