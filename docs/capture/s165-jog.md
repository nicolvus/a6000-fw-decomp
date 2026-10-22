# S165 — `[JOG]`: el subsistema de rueda/joystick (A6000 fw3.21)

**14 trazas · 24 sitios de referencia (regla PIC estricta) · 12 funciones · 4 clases RTTI.**
Detalle: `analysis/s165_jog/jog.md` · datos: `analysis/s165_jog/jog.json`.

## Qué es

`[JOG]` es la instrumentación de traza del **control de la rueda**. Flujo:

```
JogFg / JogTpu / JogVGrip  --(timer OSAL)-->  posición
        -> JogKey::SendKeyEvent  --(key_code + delta en grados)-->
        -> JogMain::SendEvent    --(mensaje de 12 B)-->  cola de eventos de cámara
```

## Las 14 trazas (vaddr)

| vaddr | texto | sitios | función |
|---|---|---|---|
| `0x43c40eb4` | `[JOG]JogMain::%s:%d` | `0x435ae5d4`, `0x435ae6ce` | `JogMain::Exit` / `::Init` |
| `0x43c40ef2` | `[JOG]ERR. osal_try_valloc_msg…` | `0x435aeb42` | `JogMain::SendEvent` |
| `0x43c40f23` | `[JOG]<Send Event> key_code = 0x%x, deg/sec = %d` | `0x435aeb74` | `JogMain::SendEvent` |
| `0x43c40f53` | `[JOG]ERR. osal_snd_msg…` | `0x435aebb4` | `JogMain::SendEvent` |
| `0x43c40f85` | `[JOG]ERR. osal_free_timer…` | `0x435aeda6`, `0x435af1da`, `0x435af5f6` | `JogFg/Tpu/VGrip::Exit` |
| `0x43c40fb2` | `[JOG]JogFg::%s:%d` | `0x435aee00`, `0x435aef18` | `JogFg::Start` |
| `0x43c40fc4` | `[JOG]ERR. osal_alloc_timer…` | `0x435aeeac`, `0x435af2e0`, `0x435af6fc` | los tres `::Start` |
| `0x43c40ff2` | `[JOG]ERR. osal_set_timer…` | `0x435aeee6`, `0x435af31a`, `0x435af736` | los tres `::Start` |
| `0x43c410a2` | `[JOG]JogTpu::%s:%d` | `0x435af234`, `0x435af34c` | `JogTpu::Start` |
| `0x43c410fe` | `[JOG]JogVGrip::%s:%d` | `0x435af650`, `0x435af768` | `JogVGrip::Start` |
| `0x43c41113` | `[JOG]UpdateDataFromVgrip SndErr, line=%d` | `0x435af890` | `JogVGrip::UpdateDataFromVgrip` |
| `0x43c41184` | `[JOG]JogKey::%s:%d:0x%x,%d` | `0x435af990` | `JogKey::SetDev` |
| `0x43c4119f` | `[JOG]JogKey::%s:%d,pos:%d->%d` | `0x435afa0c` | `JogKey::SendKeyEvent` |
| `0x43c411bd` | `[JOG]JogKey::%s:%d,Deg=0,Not Send` | `0x435afa66` | `JogKey::SendKeyEvent` |

Ninguna cadena muerta. Además 10 referencias `__PRETTY_FUNCTION__`
(`void JogMain::Exit()`, `virtual void JogTpu::Start(void (*)(), __uint32_t, __uint32_t)`, …).

## Clases (RTTI)

`JogDev` (abstracta, 6 ranuras → `__cxa_pure_virtual` @`0x439b4145`) →
`JogFg` / `JogTpu` / `JogVGrip` (herencia pública única).
Typeinfo: `0x43fdaaf4` / `0x43fdaafc` / `0x43fdab08` / `0x43fdab14`.
Vtables: `0x43fbb640` / `0x43fbb660` / `0x43fbb680` / `0x43fbb6a0`.
`JogMain` y `JogKey` no son polimórficas (sin typeinfo).

## Hallazgos con dirección

- **Tabla de key codes**: `0x43fdab20` = `0x11, 0x12, 0x16, 0x17, 0x14, 0x15` (6 × `u32`,
  única en la imagen). La indexa `this[0xc]` (`0x435af9c2`).
- **Mensaje de evento**: 12 B `{u32 key_code, u32 deg, u32 err}` (`0x435aeb64`-`0x435aeb68`).
- **Identificador de módulo/diagrama**: `0x106` (262), en `0x435ae47c`, `0x435aea70`, …
- **Descriptor de entrega**: 40 B, `type = 2`, `id = 0x106` (`0x435aea9c`-`0x435aeaa4`).
- **Entrada del grip vertical**: 12 B desde la cola `Vgrip_Snd` (`0x43c8fb2f`).
  `VGrip` = "V Grip" (etiqueta `V Grip S1` @`0x43c8fbbe`).

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[JOG]` | **14** | 0 | 0 |
| clases `Jog*` RTTI | Dev, Fg, Tpu, VGrip | Dev, Fg, Tpu, **VGrip** | Dev, **Caif**, Fg, Tpu |
| texto `JogKey` | sí | no | no |

→ El subsistema de rueda **existe en las tres fw** (mismo RTTI); lo **propio de la A6000
fw3.21 es la instrumentación `[JOG]`** y la clase `JogKey`. La A6300 sustituye
`JogVGrip` por `JogCaif`.

## Obturador

**El módulo no habla de obturación, disparo, sensor ni tiempos de exposición** (0
coincidencias). Su interés es otro: es **la fuente de eventos de la rueda**.

## Verificación

34 pares PIC verificados a mano en `0x435ae400`–`0x435afb00` (24 de `[JOG]` + 10 de
`__PRETTY_FUNCTION__`): literal del pool, `destino = literal + (add+4)` y ausencia de
reutilización del registro → los 34 correctos. Scripts en `analysis/s165_jog/`.
Tests: `tests/test_s165_jog.py`.
