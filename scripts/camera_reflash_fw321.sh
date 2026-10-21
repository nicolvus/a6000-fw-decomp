#!/bin/sh
# Reinstala el firmware oficial ILCE-6000 v3.21 por USB con pmca-console (Sony-PMCA-RE). NO se ejecuta solo: lo lanza el usuario.
# Requisitos: batería >50 %, cámara en modo MTP o almacenamiento masivo (Ajustes > Conexión USB), cable directo, PC sin suspensión.
# NO desconectar ni apagar durante la actualización. Verifica primero el archivo (solo lectura) y pide confirmación.
set -e
cd "$(dirname "$0")/.."
DAT=firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat
SHA=29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f
PY=${PMCA_PY:-$HOME/.local/share/pmca-venv/bin/python}
echo "$SHA  $DAT" | sha256sum -c -
lsusb | grep -i "054c" || { echo "No se ve ninguna cámara Sony por USB"; exit 1; }
printf 'Esto FLASHEA el firmware 3.21 en la cámara. Escribe SI para continuar: '
read r; [ "$r" = "SI" ] || { echo cancelado; exit 1; }
exec "$PY" references/pmca/pmca-console.py firmware -f "$DAT"
