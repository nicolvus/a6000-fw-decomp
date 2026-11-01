# 5. Instalar el 3.23

> Hazlo solo con backup de NVRAM hecho ([paso 3](3-Backup-de-NVRAM)), hashes verificados ([paso 4](4-Construir-los-paquetes)), batería cargada y la cámara en 3.21.

```sh
pmca-console firmware -f a6000-custom-fw-3.23-b1a-silent-shutter.dat
pmca-console info          # debe mostrar la versión 3.23
```

- No desconectes ni apagues la cámara durante la actualización.
- Anota el resultado en `docs/capture/registro-pruebas-camara.md`.
- Probado por el autor el 27-10-2026 (T040/T041) desde un 3.22 intermedio; desde un 3.21 directo el guard lo acepta (verificado offline) pero el autor no lo instaló así.

## Qué esperar

El obturador mecánico queda **completamente inactivo**: no se mueve en captura ni en rearme. La cámara dispara en silencio y sin error.
Sin la [capa 2](6-Capa-2-exposicion-uniforme) la exposición **no es uniforme** (la parte inferior de la imagen recibe más luz): ver [Resultados y límites](9-Resultados-y-limites).

## Prueba mínima

Haz un disparo normal y comprueba: sin ruido de obturador, imagen completa (JPEG 6000×4000 / ARW 6024×4024), sin mensaje de error y rearme de ~0,7–1,0 s.
