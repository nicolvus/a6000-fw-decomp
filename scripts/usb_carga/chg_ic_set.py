#!/usr/bin/env python3
"""Fija los registros del cargador OZ8072 con la A6000 encendida mediante USB_CHG_IC_SET (USB-CARGA-3, vía sin parche).

Cadena (VERIFICADA en estático, docs/capture/usb-carga-encendida.md §3): senser AdjustControl bloque 0x0d20,
código 0xa0 (tabla de libsencore/adjstctl: mensaje OSAL 0x2804be) → av-cam (0x4398886c) → canal de órdenes de
Darwin (+0x22 del marco, 0x1b8cc) → despachador 0x243a4, caso 0xa0 → 0xc8bc: guarda 3 B y el OZ8072 recibe
reg4 = (reg4 & 0xf8) | d0, reg5 = (reg5 & 0x30) | d1, reg6 = (reg6 & 0xf8) | d2 (0xc660), al momento o en el
siguiente ciclo de la tarea 0x7a36 del modo encendido (0xc6dc).

Preajustes (copian lo que Darwin escribe en modo apagado, 0x8692/0xc4e8, más el bit 3 de reg5 = USB alimenta):
  carga     d1 = 0xc9, d2 = 4   (= 0xc4e8(1, 0xc0, 4) | USB PWR)
  normal    d1 = 0x0a, d2 = 0   (= «Off exit» 0xc4e8(2, 0, 0) | USB PWR: como deja Darwin la cámara al encender)
Límite de entrada (reg4[2:0], traducción VERIFICADA en 0xc6f0): 100→0, 500→1, 1500→2, 900→3, 2000→4 mA.

Sin --execute solo muestra el paquete. Con --execute entra en el modo de servicio por USB (como scripts/senser_*)
y lo envía. Reversión: `normal`, desenchufar el USB o apagar la cámara (el modo apagado reescribe reg5/reg6).
RIESGO: con la cámara encendida Darwin no supervisa la carga (temperatura, fin de carga); vigilar y no dejar
desatendido.
Uso: chg_ic_set.py {carga,normal} [--ma 500|900|1500|2000|100] [--execute]   (PYTHONPATH=references/pmca)
"""
import argparse
import os
import sys

BLOQUE, CODIGO = 0x0D20, 0xA0
LIMITE = {100: 0, 500: 1, 1500: 2, 900: 3, 2000: 4}  # mA → código de reg4 (0xc6f0)
PREAJUSTE = {'carga': (0xC9, 4), 'normal': (0x0A, 0)}  # (reg5, reg6)


def carga_util(modo: str, ma: int) -> bytes:
    """8 B que Darwin copia al búfer de la orden (0x1b8f8); solo se usan los 3 primeros."""
    if ma not in LIMITE or modo not in PREAJUSTE:
        raise ValueError(f'modo {modo!r} o límite {ma} mA no válidos')
    r5, r6 = PREAJUSTE[modo]
    d = bytes([LIMITE[ma], r5, r6])
    assert d[0] <= 7 and not d[1] & 0x30 and d[2] <= 7  # nada fuera de los campos que escribe 0xc660
    return d + bytes(5)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('modo', choices=sorted(PREAJUSTE))
    ap.add_argument('--ma', type=int, default=500, help='límite de entrada USB en mA (por defecto 500: puerto de PC)')
    ap.add_argument('--execute', action='store_true')
    a = ap.parse_args()
    datos = carga_util(a.modo, a.ma)
    print(f'USB_CHG_IC_SET bloque {BLOQUE:#06x} código {CODIGO:#04x} datos {datos.hex(" ")}')
    print(f'equivalente por telnet (formato de datos de adjstctl sin verificar): adjstctl {BLOQUE:#x} {CODIGO:#x} '
          + ' '.join(f'{b:#04x}' for b in datos[:3]))
    if not a.execute:
        print('SIMULACIÓN: no se envía nada (usa --execute)')
        return
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'references', 'pmca'))
    from pmca.commands.usb import senserShellCommand

    def enviar(cam):
        cam.readHasp()
        resp = cam._sendAdjustControlPacket(BLOQUE, CODIGO, datos)
        print('respuesta:', resp.hex(' ') if resp else '(vacía)', '→ enviado')

    senserShellCommand(complete=enviar)


if __name__ == '__main__':
    main()
