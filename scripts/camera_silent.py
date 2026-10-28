"""E25-11: parche de «modo silencioso» (ShutMode 0 + r5 desde la velocidad) aplicado desde el PC por telnet, con guardián en la cámara.

Por qué no desde la app: `Runtime.exec` se colgó entre las dos escrituras en T049 y dejó ShutMode 0 forzado. Aquí cada parche va en UN comando de telnet,
y antes se arranca en la cámara un guardián independiente de la app y del PC: si en 25 s no aparece su archivo de aviso, escribe los bytes originales.
Constantes: tiempo de línea 15,2 µs y exposición nula en r5 = 4219 (T044, T046, T047). Solo RAM."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST = "192.168.1.29"
SM_A, SM_O, SM_N = 0x836D6FB6, "91f80990", "4ff00009"
R5_A, R5_O = 0x836D7000, "28125ffa85fe"
LINE_US, R5_FULL, R5_MIN = 15.2, 4219, 10
GUARD_S = 25
FLAG = "/android/data/local/tmp/sg_"


def rd(addr: int, n: int) -> str:
    out = run(HOST, [f"dd if=/dev/mem bs=1 skip={addr} count={n} of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z"])[0]
    data = bytearray()
    for line in out.splitlines():
        parts = line.replace(":", " ").split()
        if parts and len(parts[0]) == 8 and all(c in "0123456789abcdef" for c in parts[0]):
            data += bytes(int(x, 16) for x in parts[1:17] if len(x) == 2)
    return data[:n].hex()


def wr_cmd(addr: int, hexs: str) -> str:
    esc = "".join(f"\\0{int(hexs[i:i + 2], 16):03o}" for i in range(0, len(hexs), 2))
    return f"echo -ne '{esc}' | dd of=/dev/mem bs=2 seek={addr // 2} count={len(hexs) // 4} 2>/dev/null"


def r5_bytes(v: int) -> str:
    return f"{v >> 8:02x}20" + f"4ff0{v & 255:02x}0e"


def r5_for(seconds: float) -> int:
    """r5 para una velocidad en segundos, o -1 si la exposición no cabe en el cuadro completo (≈ 64 ms)."""
    r5 = R5_FULL - round(seconds * 1e6 / LINE_US)
    return r5 if r5 >= R5_MIN else -1


def state() -> tuple[str, str]:
    return rd(SM_A, 4), rd(R5_A, 6)


def is_original() -> bool:
    return state() == (SM_O, R5_O)


def guard_start(token: str) -> None:
    """Guardián en la cámara: revierte solo si en GUARD_S s no existe FLAG+token."""
    flag = FLAG + token
    loop = f"i=0; while [ $i -lt {GUARD_S} ]; do [ -e {flag} ] && exit 0; sleep 1; i=$((i+1)); done"
    run(HOST, [f"rm -f {flag}; ({loop}; {wr_cmd(SM_A, SM_O)}; {wr_cmd(R5_A, R5_O)}) >/dev/null 2>&1 &"])


def apply(r5: int, token: str) -> None:
    """Comprueba el código original, arranca el guardián y aplica ambos parches en un solo comando; verifica o revierte."""
    if not is_original():
        raise RuntimeError(f"código inesperado {state()}: no se parchea")
    guard_start(token)
    run(HOST, [f"{wr_cmd(SM_A, SM_N)}; {wr_cmd(R5_A, r5_bytes(r5))}"])
    if state() != (SM_N, r5_bytes(r5)):
        revert(token)
        raise RuntimeError("parche no aplicado")


def revert(token: str) -> bool:
    """Revierte en un solo comando, avisa al guardián y verifica."""
    run(HOST, [f"{wr_cmd(R5_A, R5_O)}; {wr_cmd(SM_A, SM_O)}; touch {FLAG}{token}"])
    time.sleep(0.3)
    return is_original()
