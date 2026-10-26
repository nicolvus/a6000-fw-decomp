"""E20: ¿puede una comprobación `[EXL]` rechazar una captura? Cadena de retorno desde las dos rutinas (0x436ca820, 0x436cafc0) hasta el llamador que aborta.
Desensambla con Capstone las instrucciones decisivas del binario A6000 y las vuelca en e20_exl.json (la prueba las compara con los bytes).
Límite estático: la salida (ancho/alto) está acotada a 2208x1242 aguas arriba, pero los rectángulos de entrada de 0x436c25d0 los arman en ejecución sus dos llamadores (0x437f5a04 y el que contiene 0x438cb7ca) con estado vivo del sensor; los valores por modo de disparo no salen del binario.
shortcut: comprueba el mecanismo (condición, bandera, propagación, destino del error, acotado de salida); no evalúa dimensiones por modo, que dependen de datos de ejecución."""
import json
from pathlib import Path

import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

SITES = {  # dirección: papel
    0x436CA9B2: "bls: hsiz_arcout <= 2240 (0x8c0) salta la comprobación; si no, registra [EXL] y sigue",
    0x436CAA0A: "movs r7,#0: valor 0 para la bandera",
    0x436CAA0C: "str r7,[sp,#0x58]: bandera de éxito a 0 tras 'arcout> arcin' o 'hsiz_arcout > 2240'",
    0x436CAB34: "bls: hsiz_sig <= 2240 salta la comprobación",
    0x436CAB56: "str r1,[sp,#0x58]: bandera a 0 tras 'hsiz_sig > 2240'",
    0x436CAF78: "ldr r0,[sp,#0x58]: la bandera es el valor de retorno",
    0x436CB216: "movs r3,#0: en 0x436cafc0, tras 'hsiz_arcout > 2240'",
    0x436CB218: "str r3,[sp,#0x60]: bandera de 0x436cafc0 a 0",
    0x436CB740: "ldr r0,[sp,#0x60]: la bandera es el retorno de 0x436cafc0",
    0x43AD5B60: "mov r5,r0: 0x43ad5b02 conserva el retorno de las dos rutinas",
    0x43AD5BBA: "mov r0,r5: y lo devuelve",
    0x43AD5AF4: "bl 0x43ad5b02 dentro de 0x43ad5998",
    0x436C2726: "cbz r0: bandera 0 -> salta a 'movs r0,#7' (código de error)",
    0x436C275C: "movs r0,#7: 0x436c25d0 devuelve 7 y no ejecuta el resto de la captura",
    0x43ACC44A: "b.w 0x436c25d0: 0x43acc424 devuelve ese código tal cual",
    0x437F6358: "mov r6,r0: 0x437f5a04 guarda el código",
    0x437F635A: "cbz r0: distinto de 0 -> registra 'snrBusThroughPrereviewParamSet Error!' y aborta",
    0x43AD5AA8: "cmp r3,#0x8a0: 0x43ad5998 acota a 2208 el ancho de salida que pasa a 0x43ad5b02 (sp+0x70)",
    0x43AD5AB8: "movw r3,#0x4da: acota a 1242 la altura de salida (sp+0x74)",
    0x437F6354: "bl 0x43acc424 con el rectángulo en sp+0x50, armado antes con el estado vivo del sensor (r4+0x568)",
    0x438CB7CA: "bl 0x43acc424 (segundo llamador) con el rectángulo en sp+0x88, también armado en ejecución",
}


def main() -> None:
    blob = pic.load("a6000")
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out = {}
    for addr, role in SITES.items():
        i = next(cs.disasm(blob[addr - pic.BASE:addr - pic.BASE + 4], addr))
        out[hex(addr)] = {"instruccion": f"{i.mnemonic} {i.op_str}", "papel": role}
    Path(__file__).with_name("e20_exl.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
