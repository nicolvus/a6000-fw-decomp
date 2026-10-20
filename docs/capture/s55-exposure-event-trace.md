# S55-D — Eventos de exposición BIONZ/Darwin y P4C (20-10-2026)

Método: barrido de trazas con código inmediato (`events_mmio.py`) sobre ambos `av-cam.bin`; tabla de nombres `0x43fe8138+12·i` (146 entradas). Pseudocódigo REA de `0x436ba710`.

## Productores de las trazas (A6000 | A7S)
| Evento | Sitios | Notas |
|---|---|---|
| `ExposureEndNotify` 0x12a | `0x436b8b20` (fn `0x436b8aec`) \| `0x436d8424` | **único** sitio; construye paquete de 2 B y llama `0x436ba234` (CAIF); **sin GPIO** |
| `ExposureEndRes` 0x12b | `0x436b8a38` (fn `0x436b89e6`), `0x439d8538`, `0x439dc3f0` | fn `0x436b89e6` envía mensaje OSAL (`0x4356120c`) |
| `ImageReadStartNotfy` 0x12d | `0x436b8ad8` (fn `0x436b8abc`) | **clear** del pin (7,15) |
| código 0x128 (sin nombre) | `0x436b8aa8` (fn `0x436b8a8c`) | **set** del pin (7,15) |
| 0x12c / 0x12f | `0x436b8b48` / `0x436b8b78` | set/clear (7,13) |
| `ExposureReady` 0x129 | `0x436b8f2e`, `0x4379705a`, `0x43941666`, `0x439d734c` | |
| `ExpBefore` 0x135 | `0x436b9398` (fn `0x436b935c`, lee pin C), `0x4399db3c` | |
| `ExpStartComp` 0x136 | `0x435a55ea`, `0x435a5736`, `0x435a586c`, `0x4399db7a`, `0x43a036a0` | **ninguno** en el clúster de pines `0x436b8a00–0x436bd000` |
| `ReleaseLock` 0x131 | `0x436bc914`, `0x4399d74a` | |
| `S2REQ HI` 0x13a | `0x436b9424` | tras `gpio_set` de la salida S2REQ |
Estructura equivalente en A7S (direcciones desplazadas: p. ej. `0x436d8424`, `0x436d833c`, `0x436d83dc`, `0x436d8d28`).

## P4C frente a mensajes CAIF (D.2)
- Escenarios 2 y 3 (IRQ/polling de P4C): no hay lector de `GPIO_9` (ver [inicialización](s55-gpio-initialization-trace.md)); `ExpStartComp` se emite en funciones fuera del clúster de pines.
- Escenario 1 (indicador complementario) no se puede descartar ni demostrar: `SENS_B` es dedicado y sin rastro.
- **Sí hay una relación GPIO↔exposición**, pero en sentido BIONZ→Darwin: al iniciar/terminar la lectura de imagen BIONZ conmuta salidas (7,15)/(7,13).
- H55-6: **NO VERIFICADO / sin soporte**: ni el manejador de `ExposureEndNotify` ni `ExpStartComp` leen P4C en las rutas recuperadas.

## Mecánica vs Silent (D.3)
Los productores son los mismos en A7S y A6000 (sin ramas Silent en la tarea de pines). La distinción Silent está en LIRO (clase 0, S52) y Darwin (`no_silent`, S53), no en esta tarea.
Orden *dentro* de una función verificado; el orden entre tareas asíncronas (OSAL) **no** se reconstruyó.
