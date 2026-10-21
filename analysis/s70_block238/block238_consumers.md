# S70 — ¿quién consume `+0x238` (SilentShutter) y `+0x280` del bloque `0x43edf684`? (21-10-2026)

Seguimiento de S64. Método: desensamblado Thumb con capstone sobre `av-cam.bin` (base `0x43541000`); scripts en esta carpeta.

**VERIFICADO (bytes):**
- Tabla de comandos `{ID, handler|1, 0}`: ID `0x40e3` en `0x43fffc60` → handler `0x438032d5` (`ldrb r2,[r0,#8]` → `str.w r2,[bloque,#0x238]`); `0x40e2` → `+0x234`. `+0x280` lo escribe `0x43802614` (también por comando) y ambos se reinicializan a 0 en `0x43804610`.
- Las referencias PC-relativas a `0x43edf684` son **62 y todas caen en `0x43802000–0x43805000`** (handlers, inicializador `0x43804610` y la rutina de valores por defecto `0x43804fd0…`, que llama a cada handler con un paquete sintético). Ninguna fuera de esa región.
- El bloque no aparece como palabra absoluta en ningún pool; la dirección `0x43edfbe4` (fin del bloque, `0x560`) sí.
- Accesor puro `0x43804de8` (`ldr r0,[pc]; add r0,pc; bx lr`; 40 llamadores) y accesor con retorno condicional `0x43804c38` (6 llamadores): en las 16 instrucciones posteriores a cada llamada **no hay ningún acceso con desplazamiento `0x234/0x238/0x23c/0x280`**, ni copia del bloque completo.
- Ninguna instrucción `ldr*` con `[rX,#0x238]` o `[rX,#0x280]` alcanza el bloque (las únicas son `[sp,…]`/literales PC y almacenes de otras estructuras).

**Conclusión (INFERENCIA fuerte, consistente con S64):** en `av-cam.bin` `+0x238` y `+0x280` son **solo escritura**: se guardan por comando y no tienen consumidor visible. Por eso forzarlos no cambió el obturador. S51 se mantiene.

**NO VERIFICADO / límites:** lectura vía puntero guardado en una variable y desreferenciado lejos de la llamada al accesor; lectura desde otro binario (Darwin/userland) tras un volcado del bloque; análisis lineal con capstone (puede perder código tras datos). El escritor de `[0x20000050+ch]` (tipo de mecanismo en Darwin, S54) sigue sin localizar y **el parser CAIF de Darwin A6000 ya está resuelto en S53** (descarta el bit `0x20`): el punto «MCU Darwin» no es un hueco de mapeo sino de lógica ausente.

Siguiente: seguir `str rX,[...]` del resultado de `0x43804de8` hacia globales y buscar lectores de ese global; localizar el escritor de `[0x20000050+ch]` en `darwin_core.bin`.

## Ampliación (misma fecha)

**Puntero devuelto por los accesores (`scan_pointer_flow.py`):** siguiendo hasta 80 instrucciones el registro que recibe el resultado de `0x43804de8`/`0x43804c38` (copias `mov` incluidas) no hay acceso ni suma de `0x230–0x243` / `0x278–0x28b`; los 19 destinos `bl` que reciben el puntero tampoco los tocan en sus primeros 400 B. Refuerza «solo escritura»; sigue sin cubrir punteros guardados en globales.

**Darwin, `[0x20000050+ch]` (`darwin_type_byte.py`, `darwin_core.bin` A6000, base `0x4200`):**
- Lectores localizados: `0x1b080` (devuelve el byte si `[tabla+ch]≠0`), `0x1b096` (booleano) y `0x1b0b2` (valida `ch<0x18` y copia el estado a la tabla de habilitación); todos hacen `ldrb.w r,[base+ch,#0x50]`.
- **Ningún escritor por código**: no hay literal `0x20000050…58` en el pool (solo `0x20000000`, `0x20000044/47`, `0x200002c0`), y el arranque (`reset 0x45c8 → 0x4638`) no hace carga de datos desde ROM: solo fija unos bytes sueltos (cadena `1351…_2`, etc.).
- INFERENCIA: el bloque `0x20000000…` lo rellena un agente externo (el host BIONZ por el enlace MFS5/mss-async) o una copia en bloque con destino calculado; el tipo de mecanismo no se fija por constantes de Darwin. NO VERIFICADO: qué mensaje lo escribe.
