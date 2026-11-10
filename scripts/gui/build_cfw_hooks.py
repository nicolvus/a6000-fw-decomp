"""G27 — gancho de arranque de `pp_ram.sh` en `s_start_android.sh` (el mismo texto que el CFW 3.56–3.59, G18)."""

ANCLA = "insmod /usr/kmod/usbg_adb.ko"
GANCHO = ("# G18: gammas de Picture Profile en la RAM del núcleo (comprueba los bytes originales antes de escribir)\n"
          "( /usr/bin/pp_ram.sh > /android/data/pp_ram.log 2>&1 ) &\n\n")


def con_gancho_ram(script: str) -> str:
    assert script.count(ANCLA) == 1 and "pp_ram.sh" not in script, "s_start_android.sh inesperado"
    return script.replace(ANCLA, GANCHO + ANCLA)
