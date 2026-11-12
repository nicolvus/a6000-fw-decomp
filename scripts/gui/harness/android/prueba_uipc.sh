# G22-E T5b/T6 (invitado, emulador; no cámara): carga uipc_shared.ko y ejecuta la prueba entre procesos. No se ha ejecutado aún.
# Uso dentro del invitado (p. ej. como SHIM de run.py en un DIR_TRABAJO propio, nunca en la VM interactiva de otro agente):
#   copiar DIR_TRABAJO/uipcs/{uipc_shared.ko,uipc_guest_test,prueba_uipc.sh} a /cam/t6mod/ y lanzar: sh /cam/t6mod/prueba_uipc.sh
D=${UIPCDIR:-/cam/t6mod}
rmmod uipc_stub 2>/dev/null
insmod $D/uipc_shared.ko || { echo "UIPC insmod FALLO"; exit 1; }
ls -l /dev/uipc
timeout 20 $D/uipc_guest_test; echo "UIPC salida=$?"
dmesg | grep -i uipc | tail -5
