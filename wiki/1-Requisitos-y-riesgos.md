# 1. Requisitos y riesgos

## Qué necesitas

| Elemento | Detalle |
|---|---|
| Cámara | Sony A6000 (ILCE-6000) con firmware **oficial 3.21** (versión `pmca info`) |
| Batería y cable | Batería cargada y cable USB de datos |
| PC | Linux (probado en Arch/CachyOS), Python 3, `git`, `curl`, `7z`, `unzip`, `tar` |
| `pmca-console` | [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE) (también incluido en `references/pmca/`) |
| Solo para la capa 2 | Wi-Fi de la cámara en tu red, OpenMemories Tweak (telnet/ADB) y la app RemoteShutter ([página 6](6-Capa-2-exposicion-uniforme)) |

El 3.22 **no** es requisito: era un paquete intermedio del autor (solo bobinas apagadas) y el 3.23 ya incluye ese cambio.

## Riesgos (léelos)

- **Sin recuperación independiente.** Darwin también controla la energía; un Darwin o BIONZ que no arranca no tiene vuelta atrás demostrada por USB.
- **El 3.24 nunca se instaló en una cámara real.** Solo funciona si la cámara conserva acceso al actualizador y está en 3.23.
- **Lo verificado offline no garantiza el arranque.** El 3.25 pasó todas las comprobaciones offline y aun así bloqueó la cámara del autor.
- **Escenarios sin medir con el 3.23:** operación 5 de Darwin (P40/P41=3) y P4B/P4C siguen activos; su efecto físico no se midió. Flash, vídeo y Live View con los parches activos tampoco.
- El actualizador solo acepta versiones **estrictamente mayores** que la instalada: no se puede «bajar» de versión.

## Reglas de seguridad del proyecto

1. Backup de NVRAM antes de tocar nada ([página 3](3-Backup-de-NVRAM)).
2. Verificar SHA-256 de cada `.dat` antes de flashear.
3. Medir el guard del actualizador sin flashear (`fdat_guard_probe.py`).
4. Registrar cada prueba en cámara en `docs/capture/registro-pruebas-camara.md`.
5. **Este proyecto no te da garantía ninguna.** Hazlo bajo tu propio riesgo ([Copyright y uso](11-Copyright-y-uso)).
