# G19 — Menú de Picture Profile: qué espera la `libObj` de la A6000 (estático, 08-11-2026)

**Petición del usuario**: añadir el menú de Picture Profile (fase 5 de [G17](g17-picture-profile-plan-c.md)). Antes de construir nada
se ha comprobado qué mensaje tiene que enviar la interfaz y si la capa de modelo de la A6000 lo atiende. Sin cámara; bytes e
instrucciones de `libObj.so` (A6000 fw3.21) y `viewUnified2.so` (A6300 fw2.01). Desensamblador de trabajo: capstone.

## 1. Cómo pone la gamma la A6300 (VERIFICADO)

`CustomPictureProfileGamma` (vtable ranura 20, `viewUnified2.so` `0x3a6310`): si no está en modo MR, construye un `ParamList` con
la clave **`0x214`** = valor elegido y llama a `CmnViewModelIfWrapper::requestModelExecute("@M00B", 0x40, lista)`. Las otras 22
clases PP usan las claves `0x1f8 + 4·i` (ColorModeType `0x1f8` … Gamma `0x214` = índice 7 … ColorPhase `0x270`; Copy `0x274`).
En modo MR guarda el valor en NVRAM por perfil (`CmnViewPictureProfileCommon::getBackupIdCustomForModel`).

## 2. La capa de modelo de la A6000 lo atiende (VERIFICADO salvo lo marcado)

| Eslabón | A6000 `libObj.so` | Resultado |
|---|---|---|
| Despachador de mensajes del modelo | `0x4cfcda`: `cmp r0,#0x40` → `0x4d0006` → `bl 0x4c0a78` | el mensaje **0x40** llama a `pvt_ActionSetPictureProfile` |
| `pvt_ActionSetPictureProfile` (`0x4c0a78`) | lee la clave `0x274` (perfil 0–9); si falta, usa el perfil actual (NVRAM `[this+0xf8c]`) | **la A6000 ya tiene perfiles PP1–PP10 en el modelo** |
| | para los 31 parámetros: valor del perfil desde NVRAM (`[this+0x5dc + perfil·0x7c + 4·i]`), y si la lista trae la clave `[this+0x2f4 + 4·i]`, la usa | una lista con una sola clave basta: el resto sale de NVRAM |
| | convierte con `pvt_ChangePictureProfileParamApp2Obj` (`0x4b46b8`, 31 casos) y envía `ObjMsg 0x75ae` (`MSGID_SET_PICTURE_PROFILE_CMD`) | → `SequenceSetPictureProfile` → LIRO 0x4066 (G17 §1) |
| `App2Obj` caso 7 = **gamma** | valores 0–9 → `0x1b7`… (los VALUEID que el conversor pasa al selector 0–11) | mismo índice 7 que la clave `0x214` de la A6300 |
| Claves de la A6000 | el constructor `0x4a9a56` pone en `+0x2f4…+0x36c` valores `0x107xxxx` (gamma, `+0x310` = `0x10701e4`) | **INFERENCIA**: si es la misma clase, las claves de la A6000 no son las de la A6300 (`0x214`) y el código de la A6300 no serviría tal cual |

Ningún `.so` de la A6000 contiene esas claves como literal: hoy ninguna vista envía Picture Profile.

## 3. Lo que falta para un menú que funcione

1. Confirmar la clave de gamma de la A6000 (`0x214` o `0x10701e4`) y qué mensaje de lectura devuelve el valor actual (para que el menú
   muestre la opción marcada). Si el modelo pide `0x10701e4`, la clave se pone en el descriptor; no cambia el resto.
2. **ProcessId**: la tabla está llena (`0xe8`). Opción barata: reutilizar el ProcessId **`0x12`** (`AfTrackingSpeed`, oculto y `Normal`
   sin modelo ni NVRAM, [G13](g13-barrido-ajustes-a6000-a6300.md) §6) y apuntar su descriptor a uno nuevo (`@M00B`, set `0x40`, la clave
   de gamma). No se pierde ninguna función visible.
3. **Nodo de menú** en `CautionConfig.so` con 10 opciones (Movie, Still, Cine1–4, ITU709, ITU709(800%), S-Log2 y Off). Ver cuántos hijos tiene el nodo
   de `0x12`. Si son menos, hay que crear nodos nuevos, que es código en `_INIT`.
4. Textos en `string_*.uxc` (A6300 → A6000) e inserción en una página con `add_menu_entry.py`.
5. CFW sobre el 3.56 y prueba en cámara: elegir Cine1 en el menú debe dar el mismo resultado que el modo de prueba del 3.56.

Sin las curvas en RAM ([G18](g18-pp-espacio-y-cfw-355t.md)), las opciones 3 y 6–9 no tienen curva: el menú depende del gancho del 3.56.
