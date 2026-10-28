"""E25-17 — comprueba contra los bytes de `av-cam.bin` (fw 3.21) cada hecho estático citado en el informe y
escribe `analysis/e25-17/evidencia.json`. Solo lectura. Etiqueta V = verificado por bytes/desensamblado."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fw import ROOT, SHA, cstr, rd

# (dirección, bytes esperados en hex, mnemónico, hecho)
SITIOS = [
    (0x436D6FAA, "8e88", "ldrh r6,[r1,#4]", "SetExposure lee svd = u16[param+4]"),
    (0x436D6FBA, "c0f8a863", "str.w r6,[r0,#0x3a8]", "SetExposure guarda svd en obj+0x3a8"),
    (0x436D6FE2, "8ef802b0", "strb.w fp,[lr,#2]", "svd[7:0] -> registro ID3"),
    (0x436D6FF8, "61f3030e", "bfi lr,r1,#0,#4", "svd[11:8] -> ID4[3:0]"),
    (0x436D70C6, "dfe809f0", "tbb [pc,sb]", "SetExposure ramifica por ShutMode (0..4)"),
    (0x438C82E4, "b4f85076", "ldrh.w r7,[r4,#0x650]", "StartExposure guarda svd del cap"),
    (0x438C82F0, "a4f85066", "strheq.w r6,[r4,#0x650]", "con cap+0x504==1 el svd pasado a SetExposure es 0"),
    (0x438C8334, "a4f85076", "strh.w r7,[r4,#0x650]", "svd restaurado tras SetExposure"),
    (0x438C83C4, "a4f85036", "strh.w r3,[r4,#0x650]", "con cap+0x740==0 el svd del cap se pone a 0 tras StartExposure"),
    (0x43B1E7F8, "b0f85046", "ldrh.w r4,[r0,#0x650]", "paso con contador: lee svd; svd==0 -> mensaje de fin sin exposición"),
    (0x43B1E842, "9142", "cmp r1,r2", "paso con contador: compara svd con cap+0x4b9c"),
    (0x43B1E84A, "c3f89c20", "str.w r2,[r3,#0x9c]", "paso con contador: incrementa cap+0x4b9c"),
    (0x4383FA9A, "d3f105f9", "bl 0x43a12ca8", "productor: predicado de cuadro extra"),
    (0x4383FAA0, "b044", "add r8,r6", "productor: cuadro extra suma un VTS"),
    (0x4383FAB6, "20f549f9", "bl 0x4355fd4c", "productor: resto de líneas totales / VTS"),
    (0x4383FABA, "c9eb080a", "rsb sl,sb,r8", "productor: shd(r5) = líneas totales - líneas de exposición"),
    (0x4383FAC0, "a4f86870", "strh.w r7,[r4,#0x68]", "productor: record+0x68 = svd = cuadros enteros - 1"),
    (0x4383FADC, "8919", "adds r1,r1,r6", "productor: VTS del cuadro con resto = resto + VTS"),
    (0x4383FAE8, "a4f8d810", "strh.w r1,[r4,#0xd8]", "productor: record+0xd8 (VTS del primer cuadro)"),
    (0x437B22A4, "b4f8d820", "ldrh.w r2,[r4,#0xd8]", "planificador por VD: elige VTS del primer cuadro"),
    (0x437B22A8, "a4f86020", "strh.w r2,[r4,#0x60]", "planificador por VD: record+0x60 = VTS del cuadro actual"),
    (0x437B22B4, "b4f8dc30", "ldrh.w r3,[r4,#0xdc]", "planificador por VD: VTS del último cuadro"),
    (0x437B22BE, "b4f8da10", "ldrh.w r1,[r4,#0xda]", "planificador por VD: VTS de cuadros intermedios"),
    (0x437B2258, "b4f86810", "ldrh.w r1,[r4,#0x68]", "planificador por VD: compara svd con el índice de cuadro record+4"),
    (0x438C7528, "631c", "adds r3,r4,#1", "temporizador: (bulbFrameCount+1)"),
    (0x438C753E, "47f61223", "movw r3,#0x7a12", "temporizador: periodo = fotogramas * 31250 ticks"),
    (0x438C7522, "d5f82c47", "ldr.w r4,[r5,#0x72c]", "temporizador: lee bulbFrameCount"),
    (0x43B1E42A, "d0f82c37", "ldr.w r3,[r0,#0x72c]", "bulbFrameCount++ (lectura)"),
    (0x43B1E440, "c0f82c37", "str.w r3,[r0,#0x72c]", "bulbFrameCount++ (escritura)"),
    (0x43B1E4E4, "07b5", "push {r0,r1,r2,lr}", "callback de temporizador: fotograma completo (flag 0x2000)"),
    (0x43B1E4C0, "07b5", "push {r0,r1,r2,lr}", "callback de temporizador: último tramo (flag 0x100000)"),
    (0x438C78DE, "5b68", "ldr r3,[r3,#4]", "LongObMode = u32[req.sub+4] (solo se registra y se empaqueta)"),
    (0x438C796C, "4ff21301", "movw r1,#0xf013", "LongObMode viaja en el mensaje 0xf013 (con 0x43b1e57c)"),
    (0x438C82AC, "0228", "cmp r0,#2", "clase 0x43a12c64==2 -> bloque de exposición forzado"),
    (0x438C82C4, "c4f84c16", "str.w r1,[r4,#0x64c]", "bloque forzado: shd=2, svd=0, spl=0, ShutMode 0"),
    (0x43AE93CA, "edf703b0", "b.w 0x436d63d4", "SetReadZ: único salto a 0x436d63d4 (sin llamador de 0x43ae93ca)"),
    (0x436D63FC, "5b6b", "ldr r3,[r3,#0x34]", "0x436d63d4 despacha por vtable+0x34 (SetRead_ZAF)"),
]
CADENAS = {
    0x43CC8B31: "[IMAGING_CAP]: SplitExpRead (snr_expread_count %d, bulbFrameCount :%d)",
    0x43CC8C32: "[IMAGING_CAP]: ExposureTimerStart!(first)",
    0x43CC8C5C: "[IMAGING_CAP]: ExposureTimerEnd!",
    0x43CC89B3: "[IMAGING_CAP]: LongObMode [%x]",
    0x43CA6C02: "[CAMERA_MAIN_IM]: bulb Table",
}


def main() -> int:
    filas, fallos = [], 0
    for a, esp, mn, hecho in SITIOS:
        real = rd(a, len(esp) // 2).hex()
        ok = real == esp
        fallos += not ok
        filas.append({"addr": f"0x{a:08x}", "esperado": esp, "real": real, "ok": ok, "mnemonico": mn, "hecho": hecho, "etiqueta": "V"})
    cad: list[dict] = []
    for a, txt in CADENAS.items():
        leida = cstr(a, 100)
        ok = leida == txt
        fallos += not ok
        cad.append({"addr": f"0x{a:08x}", "esperado": txt, "real": leida, "ok": ok})
    zaf = cstr(0x43C9333C, 120)
    out = {"sha256_firmware": SHA, "sitios": filas, "cadenas": cad, "fallos": fallos, "setread_zaf_cadena": zaf}
    (ROOT / "analysis/e25-17/evidencia.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"{len(filas)} sitios, {len(cad)} cadenas, {fallos} fallos")
    for f in filas:
        if not f["ok"]:
            print("FALLO", f["addr"], f["esperado"], f["real"], f["hecho"])
    for c in cad:
        if not c["ok"]:
            print("FALLO cadena", c)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
