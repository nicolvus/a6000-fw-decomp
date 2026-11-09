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
| Claves de la A6000 | el constructor `0x4a9a56` pone en `+0x2f4…+0x36c` valores `0x107xxxx` | **descartado en §2b**: es otro objeto; la A6000 usa `0x214` como la A6300 |

Ningún `.so` de la A6000 contiene esas claves como literal: hoy ninguna vista envía Picture Profile.

## 2b. Segunda pasada con REA (VERIFICADO)

- **API de la A6300, completa para la gamma**: escritura `requestModelExecute("@M00B", 0x40, {0x214: v})`. Lectura
  `getModelInfo("model/CAMERA", 0x49)` → clave **`0x216`** (`0x3a61e8`); en modo MR, `readBackup`. La lectura usa otra clave que la escritura.
- **El elemento genérico `Normal` de la A6000 funciona solo con datos** (REA, `cmn_view_processDataMgr.so`, símbolos;
  `setModelParam` `0x75ea0`, `getModelParam` `0x75b18`, `getValueFromModel` `0x75c2a`, `getDataModel*`). El modelo del descriptor
  ocupa 0x24 B: `+0` nombre, `+8` id de evento de escritura, `+0xc` id de lectura (`getModelInfo`), `+0x10` claves de escritura, `+0x14` claves de lectura,
  `+0x18` tipos (0 = bool, 1 = número), `+0x1c` tabla opción→valor, `+0x20` nº de claves, `+0x21` nº de valores. Al escribir construye
  `ParamList{clave: valor}` y llama a `requestModelExecute(nombre, evento, lista)`. Al leer llama a `getModelInfo(nombre, id)` y busca qué opción
  coincide con el valor. Por tanto, **cada ajuste PP de la A6300 cabe en un descriptor `Normal`** (`@M00B`/0x40/`0x214` para escribir y
  `model/CAMERA`/0x49/`0x216` para leer, en la gamma) **sin portar las 25 clases**.
- **Lectura en la A6000: NO_VERIFICADO.** Ninguna función de la `libObj` de la A6000 añade la clave `0x216` con un inmediato. El
  `getModelInfo` `0x5fc3fc` devuelve `0x214` con el id `0xe` (otro uso). La notificación PP del núcleo (`0x4b4498`, mensaje `0x8577`) lee
  las claves `[this+0x468+4·i]` y guarda el estado; falta ver quién lo devuelve a la vista. Si la A6000 no responde al 0x49, el menú
  escribiría bien pero no marcaría la opción actual; la salida sería un descriptor con respaldo NVRAM en lugar de lectura del modelo.
- La clave `0x214` de la A6000 queda **a favor de la A6300** (la `libObj` de la A6000 usa `0x214`…`0x274` en sus `ParamList`); la lectura
  `0x107xxxx` del §2 era otro objeto (cerrado como INFERENCIA descartada).

## 3. Lo que falta para un menú que funcione

1. Lectura del valor actual en la A6000 (§2b): `model/CAMERA` 0x49 o, si no existe, respaldo NVRAM por perfil.
2. **ProcessId**: la tabla está llena (`0xe8`). Opción barata: reutilizar el ProcessId **`0x12`** (`AfTrackingSpeed`, oculto y `Normal`
   sin modelo ni NVRAM, [G13](g13-barrido-ajustes-a6000-a6300.md) §6) y apuntar su descriptor a uno nuevo (`@M00B`, set `0x40`, la clave
   de gamma). No se pierde ninguna función visible.
3. **Nodo de menú** en `CautionConfig.so` con 10 opciones (Movie, Still, Cine1–4, ITU709, ITU709(800%), S-Log2 y Off). Ver cuántos hijos tiene el nodo
   de `0x12`. Si son menos, hay que crear nodos nuevos, que es código en `_INIT`.
4. Textos en `string_*.uxc` (A6300 → A6000) e inserción en una página con `add_menu_entry.py`.
5. CFW sobre el 3.56 y prueba en cámara: elegir Cine1 en el menú debe dar el mismo resultado que el modo de prueba del 3.56.

Sin las curvas en RAM ([G18](g18-pp-espacio-y-cfw-355t.md)), las opciones 3 y 6–9 no tienen curva: el menú depende del gancho del 3.56.
