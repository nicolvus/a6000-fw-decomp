# G22-ARR2 — El Puente (LIRO VM) arranca en paralelo: restauración 4,75 s → 1,22 s (26-11-2026)

Cierra la parte (2) de [G22-ARR2](g22-emulador-uso.md#arranque-más-rápido-18-11-2026): «arrancar la LIRO VM cuesta 5–6 s y al
restaurar va en el camino crítico porque el lector espera al `Puente`». **Medido: no era la CPU del arnés ni la sobrecarga
Python↔Unicorn, era el orden de arranque.** La LIRO VM se arrancaba dentro de `Vm.__init__`, antes de que el hilo lector
conectara con QEMU, así que la restauración no podía dar el primer fotograma antes de que la VM acabara de arrancar.

## 1. Qué se cambió

- **`scripts/gui/harness/live.py` — el Puente arranca en un hilo** (`Vm.arranca_puente`). `Vm.__init__` vuelve en 0,3 s (QEMU ya
  restaurando y el lector conectando) y la LIRO VM termina de arrancar en paralelo. **En frío se sigue esperando al Puente dentro
  de `__init__`** (`if not restaurar: self.puente_listo.wait()`): el orden del arranque no cambia — los avisos de
  `reenvia_arranque()` salen antes de la «R», como antes — y si la VM no arranca el error se relanza ahí, igual que antes. Al
  restaurar, un fallo queda anotado en `puente_error` y se informa en la consola en vez de matar el proceso.
- **Un solo hilo, en orden, para lo que manda el invitado** (`Vm.avq_hilo`). Antes el `AVH` (campos de libObj del encabezado del
  anillo de av-cam) se aplicaba en el hilo lector y solo `if self.puente`, así que **se perdía** si llegaba antes de que la VM
  estuviera lista; ahora `AVH` y `AVQ` comparten cola y se entregan en orden en cuanto el Puente está listo (sin carrera en el
  primer mensaje).
- **`scripts/gui/avcam/puente.py` — la VM de `colas_avcam` se reutiliza en el `Puente`** (`arranca(vm=…)`, `vm_de_colas`). Con la
  caché de colas fría (cualquier cambio de `scripts/gui/avcam/*.py` o de av-cam, idt, `bk.tbl`, `liro.ko`) la LIRO VM arrancaba
  **dos veces** en el mismo inicio; ahora arranca una.
- **`live.py: configuracion()` se cachea por `mtime` y tamaño**: validar el `config.json` del configurador cuesta ≈15 ms (§4) y
  `/config` se pide en cada carga de página.

## 2. Medido (antes / después)

8 núcleos, QEMU 8 vCPU TCG, perfil `optA`, estado de 117 MB. Método: `live.py analysis/gui/g22/harness --perfil-dir optA --puerto
8620` con un cronómetro externo (`pgrep -c qemu-system-arm` antes de arrancar, `GET /estado` cada 100 ms hasta `fotogramas > 0`,
cierre con `POST /salir`). El `estado.zst` se copiaba antes de cada repetición: **las seis restauraciones parten del mismo
estado**. «Puente listo» = instante en que `Puente.__init__` termina.

| restauración (mismo estado, 117 MB) | Puente listo (s) | **1.er fotograma (s)** | guardado (s) | líneas nuevas en `avcam.jsonl` |
|---|---|---|---|---|
| antes 1 | 4,64 | **4,75** | 8,21 | 11 |
| antes 2 | 4,52 | **4,63** | 8,21 | 11 |
| antes 3 | 6,93 | **6,99** | 8,21 | 11 |
| después 1 | 4,61 | **1,25** | 8,01 | 11 |
| después 2 | 4,39 | **1,22** | 8,21 | 11 |
| después 3 | 4,85 | **1,22** | 8,21 | 11 |

- **Antes, el primer fotograma salía 0,11 s después de «Puente listo» (3 de 3)**: la restauración estaba encadenada a la LIRO VM.
  Después, el fotograma sale a 1,22 s mientras la VM sigue arrancando (lista a los 4,4–4,9 s): ya no está en el camino crítico.
  Mediana **4,75 s → 1,22 s (−74 %, 3,9×)**.
- La carga del anfitrión no fue igual en las dos tandas (media de carga 11–17 en «antes», 7 en «después»), así que el ahorro se
  comprueba también por su mecanismo, dentro de la misma tanda: **antes** el fotograma = Puente + 0,11 s; **después** el
  fotograma llega 3,2 s *antes* de que el Puente esté listo.
- **El invitado no cambia**: las 11 líneas que cada restauración añade a `avcam.jsonl` son la **misma secuencia** (quitando `t`,
  que es tiempo virtual y depende del reloj real) antes y después, y su sha256 coincide en las seis
  (`a99638feda71bf86…`). Mismo estado guardado (117 MB, ±0,2) y mismo tiempo de guardado (8,2 s).
- Arranque en frío: 148,4 s (antes) y 144,2 s (después), dentro del ruido de la carga; el camino en frío es el mismo por
  construcción (se espera al Puente antes de la «R»).
- Caché de colas de av-cam, medido aparte: **4,22 s con la caché fría → 0,036 s con la caliente** (117×), y desde este cambio la
  fría solo arranca la VM una vez (§1).

## 3. Dónde está el tiempo de verdad (descompuesto)

| tramo | medido | nota |
|---|---|---|
| `puente.arranca()`, LIRO VM | 3,0–3,3 s en reposo; 4,4–4,9 s con QEMU restaurando | `L.carga` 0,14 s + `entry_pre` `planifica(20 M)` 0,07 s + **`planifica(200 M)` 2,9–6,4 s** + sensor 0,00 s |
| `zstd -dc estado.zst` (117,7 MiB) | 0,46–0,54 s (≈220 MiB/s) | ~40 % de lo que queda hasta el fotograma |
| QEMU: lanzar → `GET /estado` responde | 0,30 s | restaurando |
| QEMU: lanzar → 1.er fotograma | 1,22 s | incluye el `zstd -dc` y el invitado pintando |
| guardado (`migrate` + `zstd -1 -T0`) | 8,0–8,2 s | ahora el tramo más largo del ciclo |

**El cuello no era «42 690 trampas Python↔Unicorn», como decía [G22-ARR](g22-emulador-uso.md#arranque-más-rápido-18-11-2026)**:
el 95 % del arranque de la VM son 200 M de instrucciones emuladas (`planifica`), o sea trabajo *del firmware de av-cam*, no
del intérprete de Python. Un núcleo nativo aceleraría cada instrucción pero no eliminaría esas 200 M; lo único que quitaría el
arranque entero es un *snapshot* de la VM ya arrancada (memoria + contexto de Unicorn). Queda como pendiente (§5).

## 4. Trabajo repetido por petición (medido: no estaba donde decía la ficha)

- `GET /estado` (lo pide la página cada segundo) **no lee la configuración**: `sensor_web.maneja` devuelve `False` antes de
  `_cfg` para cualquier ruta que no empiece por `/sd/` o `/sensor/`. Ahí no había nada que optimizar.
- Lo que sí cuesta es `emu_config.valida_config`, que `sensor_web._cfg` llama en **cada** `/sd/*` y `/sensor/*`: **≈15 ms por
  petición** porque `botones_conocidos()` hace `ast.parse(live.py)` entero cada vez (`valida_config({})` 16 ms, `carga_config`
  de un fichero 15 ms). Está fuera del camino de la restauración (una foto de 100 ms no lo nota), y `sensor_web.py` lo lleva otro
  agente: **handoff al agente principal** (caché por `mtime` en `botones_conocidos`, o en `_cfg`).
- `live.py: configuracion()` (una vez por carga de página) tenía el mismo coste y **sí se ha cacheado aquí**: ≈15 ms → ≈0,02 ms.

## 5. PARA PENDIENTES.md

| ID | Estado | Origen, motivo y criterio de cierre |
|---|---|---|
| G22-ARR3 | ABIERTO (26-11-2026) | Origen: [G22-ARR2](gui/g22-arranque-paralelo.md) (restauración 4,75 s → 1,22 s al sacar la LIRO VM del camino crítico). (1) El arranque de la LIRO VM sigue costando 3,0–4,9 s de CPU y el 95 % son 200 M de instrucciones emuladas de `planifica(200 000 000)` (`L.carga` son 0,14 s): no baja con un núcleo nativo, solo con un *snapshot* de la VM ya arrancada (montón de 240 MiB + contexto de Unicorn a fichero), que además acortaría el arranque en frío. Cierre: medir snapshot/restauración de la LIRO VM y decidir (objetivo: Puente listo < 1 s). (2) El `zstd -dc` del estado son 0,46–0,54 s de los 1,22 s que quedan hasta el primer fotograma: `lz4` (o estado sin comprimir con `migrate` a `exec:cat`) debería bajar ~0,4 s; medirlo antes de cambiar el formato. (3) El guardado (`migrate` a `zstd -1 -T0`, 117 MB) son **8,0–8,2 s**, ahora el tramo más largo del ciclo guardar→restaurar, y `POST /salir` lo mete en el camino de salida. (4) `sensor_web._cfg`/`emu_config.valida_config` validan la configuración en cada `/sd/*` y `/sensor/*` (≈15 ms por `ast.parse` de `live.py`): caché por `mtime` en `botones_conocidos` (handoff al agente principal: `sensor_web.py` no es de esta rama). (5) Sigue abierta la parte (1) de G22-ARR2 (`GUARDA_MIN=190`). |

## 6. Reproducirlo

```sh
# antes: código de main; después: rama harness/g22-opt
pgrep -c qemu-system-arm                     # no arrancar con 2+ en el sistema
.venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir optA --puerto 8620
# 1.er arranque en frío (≈145 s), POST /salir guarda estado.zst; luego, por cada restauración:
cp /tmp/estado-base.zst analysis/gui/g22/harness/live/optA/estado.zst
# lanzar y cronometrar GET /estado hasta "fotogramas" > 0, y el cierre con POST /salir
```

Pruebas del cambio: `tests/test_gui_harness.py -k "al_restaurar_vm or antes_del_puente or no_arranca or configuracion or
arranca_puente_con_la_vm_real or sin_avcam"` (6: no bloquea al restaurar, entrega en orden lo que llega antes, error relanzable en
frío, sin `--no-avcam` no se espera al cerrar, caché de la config y la cadena real `arranca_puente`+`avq_hilo` contra av-cam) y
`tests/test_avcam_puente.py` (8, con la reutilización de la VM de colas y la petición dataflow real).

## 7. Límites

- Las dos tandas de restauración no corrieron con la misma carga del anfitrión (otros agentes usaban 1–2 QEMU); por eso el
  resultado se apoya también en la relación «fotograma vs Puente listo», que es independiente de la carga.
- El arranque en frío se midió con `nvram.json` distinto en cada tanda (el perfil `optA` se creó en la primera), así que sus
  secuencias de `avcam.jsonl` no son comparables línea a línea (175 vs 270 líneas); el camino en frío no cambia por construcción.
- No se probó el *snapshot* de la LIRO VM (§5.1): no está implementado.
- Con el código final no se pudo repetir la tanda de restauraciones: los otros agentes mantuvieron los dos huecos de
  `qemu-system-arm` ocupados y no se arranca un tercero (política del arnés). Un intento a las 00:50 cayó en arranque en frío
  porque otro agente recompiló `sonyshim.so` (cambia la huella y borra el estado): sirvió de todos modos para ver la reutilización
  de la VM en vivo (`puente_listo dt=0,012 s` en vez de 3,4 s), y esa ejecución terminó con **SIGSEGV al cerrar** (código −11)
  *después* de guardar el estado — la clase de aborto de Unicorn durante el cierre del intérprete que ya documenta `Puente.cierra`;
  no se reprodujo en las otras tres y no afecta al invitado ni al estado guardado.
- El `k` de la caché de colas depende del contenido de `scripts/gui/avcam/*.py`: cualquier cambio ahí hace un arranque en frío
  (ya documentado en [G22-ARR](g22-emulador-uso.md#arranque-más-rápido-18-11-2026)).
