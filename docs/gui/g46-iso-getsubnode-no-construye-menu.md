# G46 — ISO: `ISOSensitivity::_getSubNode` NO construye el menú ISO visible del arnés (H2 confirmada; 15-11-2026; PARCIAL, sin CFW)

Continúa [G44](g44-iso-arnes-inyeccion.md) §4–5 y [G43](g43-iso-lista-51200.md). Sin cambios en `scripts/gui/harness/`; perfiles propios `g46a/g46b` (puerto 8646, overlay con `CautionConfig.so` 3.21 modificado, `live.py` normal), borrados al acabar.

## 1. Corrección al diagnóstico previo (lista Type12)
`Type12` = «MFNR, AUTO, 100…25600» = 2 + 25 valores = **27 nodos**, que es exactamente el menú visible (`[ISO AUTO multi-frame]`, AUTO, 100, 125, 160 … 25600). La lista coincide con `Type12` (G43 sí contaba la entrada multi-frame). No hay otra clase `*Iso*` con `_getSubNode`: en `CautionConfig.so` solo existen `ISOSensitivity` (`0x107d7c`), `ISOButton` (`0x109d84`, botón/Fn físico: 3 listas `Default/Type01/Type02`, selector por tipos 0x15/0x1a) y `StillHighISONR` (`0x107fe8`, RR ISO alta). Ninguna otra lista contiene MFNR+AUTO.

## 2. Pruebas decisivas (verificadas en bytes y en el arnés)
Overlay confirmado en el `initrd` (los 8 B del parche aparecen en el cpio del overlay) y mismo mecanismo que G39.
* **Prueba 1** (`docs/gui/img/g46-iso-todas-las-listas-Type11-sigue-25600.png`): los 10 pares de literales GOT de `_getSubNode` (`0x107e40…0x107e8c`: AmntMid, AmntEntry, Emnt, VG, DSCEntry, 09, 10, 11, 12, Default) sustituidos todos por `Type11` (9 nodos, ≤3200). Si la función construyera el menú, este acabaría en ≤3200. **Sigue acabando en 25600.** (Forzar `Default`, como hizo G43, no discriminaba: con MIN=100 y MAX=25600 la lista filtrada de `Default` se ve igual que `Type12`.)
* **Prueba 2** (`docs/gui/img/g46-iso-getsubnode-neutralizado-misma-lista.png`): primera instrucción de `_getSubNode` (`0x107d7c`, `b0b5` push) cambiada a `bx lr` (`7047`): la función no hace nada. **El menú ISO sigue mostrando `[ISO AUTO]`, AUTO, 100, 125, 160…** idéntico.
* Conclusión: el menú ISO visible NO sale de `CmnViewSettingNodeISOSensitivity::_getSubNode` ni de las 9 listas `cmnViewSettingNodesISOSensitivity*`. Los parches `iso_list_patch.py` (G43) y cualquier variante sobre esos literales **no pueden ampliar la lista**. No se creó función nueva en `iso_list_patch.py` (no hay lista que parchear ahí).

## 3. Candidatos descartados
* `ISOSensitivity::_getSubNode` y sus 9 listas (esta prueba); `ISOButton::_getSubNode` (es el botón físico, otra lista); `StillHighISONR` (RR ISO alta, otro menú). Referencias a los GOT de las listas fuera del `_getSubNode`: solo los ctores de carga (`0x46f8`, `0x658c`, `0x65ec`, `0x70e0`), que rellenan los arrays pero no los eligen.
* Los nodos de lista llegan de otra ruta: lo más probable es la lista generada desde el modelo (libObj `getIso`/`WRAPPER_ISO` con MIN/MAX, G41/G42) o por un `.uxc` (`viewISO*`/Fn) fuera de `CautionConfig.so`; no medido.

## 4. Siguiente paso (ISO-A)
1. Localizar al constructor real del menú: `grep` de los `.uxc` de `cam/usr/share/app/` con cadenas `ISO`/`MultiFrame` y de las referencias a `cmnViewSettingNodeISOSensitivityMultiFrameNoiseReduct` (GOT `0x57d0`, solo aparece en `0x119fb4`, ctor estático) hacia atrás por `vtable`/consumidores de `CmnViewSettingNodeISOSensitivity` (quién llama a su `getSubNode` virtual: la prueba 2 sugiere que nadie en este recorrido).
2. Con `TRACELIB`+`WLALL=1` verificar qué ejecuta el menú al abrir ISO (G44 §5.2), o la comprobación inversa: neutralizar `getIso`-relacionados de `libObj`.
3. Hasta resolver esto, 50/64/80 y 32000–51200 siguen sin verse; MIN/MAX (H1) no se puede probar todavía.
