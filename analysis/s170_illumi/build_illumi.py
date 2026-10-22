#!/usr/bin/env python3
"""S170 — construye analysis/s170_illumi/illumi.json con los datos estructurados."""
import json
import re
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
U32 = struct.Struct("<I").unpack_from

FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}

# nombre de la función -> evidencia
FUNCNAMES = {
    0x435abf7a: ("IllumiDiag::Handler(void*, void*)", "pretty @0x43c4052a"),
    0x435ac138: ("IllumiDiag::Init()", "pretty @0x43c406a4"),
    0x435ac184: ("IllumiDiag::Exit()", "pretty @0x43c40558"),
    0x435aca80: ("IllumiGain::SetGainMode(u8)", "traza 'gainMode'/'gain_pre'"),
    0x435acb90: ("IllumiGain::JudgeGainChange()", "pretty @0x43c406bc"),
    0x435acdd0: ("IllumiLevel::SendEvent(handle, level, key_code)",
                 "traza '<Send Event> key_code'"),
    0x435acf00: ("IllumiLevel::CalcIllumiLevel()", "pretty @0x43c40828"),
    0x435ad0fc: ("IllumiAd::Stop()", "pretty @0x43c40857 / vtable slot 2"),
    0x435ad150: ("IllumiAd::Start(void (*)())", "pretty @0x43c409ae / vtable slot 1"),
    0x435ad1b8: ("IllumiAd::Exit()", "pretty @0x43c40875 / vtable slot 3"),
    0x435ad270: ("IllumiAd (ranura 0 de la vtable: ctor/arranque)",
                 "vtable slot 0 / traza osal_alloc_timer"),
    0x435ad4dc: ("Illumi::C_AD()  (correccion lineal del AD)",
                 "trazas 'AD MAXOVER' / 'C_AD. ADcor'"),
    0x435ad680: ("Illumi::TareaPeriodica()  (callback del temporizador)",
                 "puntero de callback @0x44020dd8"),
    0x435ad7ac: ("IllumiCam::Exit()", "pretty @0x43c40a2b / vtable slot 3"),
    0x435ad7dc: ("IllumiCam::Stop()", "pretty @0x43c40a01 / vtable slot 2"),
    0x435ad82c: ("IllumiCam::Start(void (*)())",
                 "pretty @0x43c409d7 / vtable slot 1"),
    0x435adaf4: ("IllumiRPR0400::Stop()", "pretty @0x43c40b8c / vtable slot 2"),
    0x435adb90: ("IllumiRPR0400::Start(void (*)())",
                 "pretty @0x43c40be2 / vtable slot 1"),
    0x435adc38: ("IllumiRPR0400::Exit()", "pretty @0x43c40bbf / vtable slot 3"),
    0x435ade38: ("IllumiRPR0400::ReadDevice(u16, u8, u8*, u8*)",
                 "pretty @0x43c40adb"),
    0x435adffc: ("IllumiRPR0400::GetAD()", "pretty @0x43c40e0f / vtable slot 4"),
    0x435ae058: ("IllumiRPR0400::PollingDevice()", "pretty @0x43c40e89"),
    0x435ae0a8: ("IllumiRPR0400::WriteDevice(u16, u8, u8*, u8*)",
                 "pretty @0x43c40b33"),
    0x435ae228: ("IllumiRPR0400::InitializeDevice()", "pretty @0x43c40e5b"),
    0x435ae328: ("IllumiRPR0400::Init()", "pretty @0x43c40e38 / vtable slot 0"),
}

PRETTY = {
    0x43c4052a: "static void IllumiDiag::Handler(void*, void*)",
    0x43c40558: "void IllumiDiag::Exit()",
    0x43c406a4: "void IllumiDiag::Init()",
    0x43c406bc: "static void IllumiGain::JudgeGainChange()",
    0x43c40828: "bool IllumiLevel::CalcIllumiLevel()",
    0x43c40857: "virtual void IllumiAd::Stop()",
    0x43c40875: "virtual void IllumiAd::Exit()",
    0x43c409ae: "virtual void IllumiAd::Start(void (*)())",
    0x43c409d7: "virtual void IllumiCam::Start(void (*)())",
    0x43c40a01: "virtual void IllumiCam::Stop()",
    0x43c40a2b: "virtual void IllumiCam::Exit()",
    0x43c40adb: ("static OSAL_ERR IllumiRPR0400::ReadDevice(__uint16_t, __uint8_t,"
                 " __uint8_t*, __uint8_t)"),
    0x43c40b33: ("static OSAL_ERR IllumiRPR0400::WriteDevice(__uint16_t, __uint8_t,"
                 " __uint8_t*, __uint8_t)"),
    0x43c40b8c: "virtual void IllumiRPR0400::Stop()",
    0x43c40bbf: "virtual void IllumiRPR0400::Exit()",
    0x43c40be2: "virtual void IllumiRPR0400::Start(void (*)())",
    0x43c40e0f: "static __uint16_t IllumiRPR0400::GetAD()",
    0x43c40e38: "virtual void IllumiRPR0400::Init()",
    0x43c40e5b: "static void IllumiRPR0400::InitializeDevice()",
    0x43c40e89: "static bool IllumiRPR0400::PollingDevice()",
}

RTTI = {
    "IllumiDev": {"name_addr": 0x43c4084c, "typeinfo": 0x43fdaa74,
                  "vptr": 0x43fd04f8, "vtable_ap": 0x43fbb5c0,
                  "slots": [0x439b4145] * 5,
                  "nota": "abstracta: las 5 ranuras apuntan a __cxa_pure_virtual "
                          "(0x439b4145)"},
    "IllumiAd": {"name_addr": 0x43c40893, "typeinfo": 0x43fdaa7c,
                 "vptr": 0x43fd03d8, "vtable_ap": 0x43fbb5e0,
                 "slots": [0x435ad271, 0x435ad151, 0x435ad0fd, 0x435ad1b9,
                           0x435ad5e9],
                 "base": "IllumiDev"},
    "IllumiCam": {"name_addr": 0x43c40a20, "typeinfo": 0x43fdaa8c,
                  "vptr": 0x43fd03d8, "vtable_ap": 0x43fbb600,
                  "slots": [0x43a4a1c5, 0x435ad82d, 0x435ad7dd, 0x435ad7ad,
                            0x435ad9f9],
                  "base": "IllumiDev"},
    "IllumiRPR0400": {"name_addr": 0x43c40baf, "typeinfo": 0x43fdaa98,
                      "vptr": 0x43fd03d8, "vtable_ap": 0x43fbb620,
                      "slots": [0x435ae329, 0x435adb91, 0x435adaf5,
                                0x435adc39, 0x435ade21],
                      "base": "IllumiDev"},
}


def main():
    raw = json.load(open("analysis/s170_illumi/illumi_strings_raw.json"))
    pic = json.load(open("analysis/s170_illumi/illumi_pic_sites.json"))
    fmap = json.load(open("analysis/s170_illumi/illumi_func_map.json"))
    ver = json.load(open("analysis/s170_illumi/illumi_pic_verificado.json"))
    diff = json.load(open("analysis/s170_illumi/illumi_diff.json"))
    rtti_diff = json.load(open("analysis/s170_illumi/illumi_rtti_diff.json"))

    strings = []
    for r in pic:
        strings.append({
            "vaddr": int(r["string_addr"], 16),
            "file_offset": int(r["string_addr"], 16) - BASE,
            "texto": r["texto"],
            "n_sitios": r["n_sitios_local"],
            "sitios": [int(x, 16) for x in r["sitios_local"]],
            "sites_global_map": [int(x, 16) for x in r["sitios_global"]],
        })
    strings.sort(key=lambda x: x["vaddr"])

    funcs = []
    for f in fmap["funciones"]:
        fa = int(f["func"], 16)
        nm, ev = FUNCNAMES.get(fa, ("(sin nombre)", ""))
        funcs.append({
            "func": fa,
            "nombre": nm,
            "evidencia_nombre": ev,
            "n_sitios": f["n_sitios"],
            "sitios": [{"sitio": int(s["sitio"], 16),
                        "string_addr": int(s["string_addr"], 16),
                        "texto": s["texto"]} for s in f["sitios"]],
        })
    funcs.sort(key=lambda x: x["func"])

    out = {
        "hito": "S170",
        "modulo": "[ILLUMI]",
        "imagen": {"path": FILES["A6000_fw321"],
                   "base": BASE,
                   "size": len(B),
                   "sha256": None},
        "cifras": {
            "cadenas_distintas": len(strings),
            "ocurrencias_token_a6000": raw["A6000_fw321"]["n_ocurrencias_token"],
            "cadenas_muertas": 0,
            "sitios_pic": sum(s["n_sitios"] for s in strings),
            "funciones": len(funcs),
            "pares_pic_verificados": len(ver),
            "pares_pic_sin_reuso_de_registro": sum(1 for v in ver if v["flag"] == "ok"),
            "clases_rtti": 4,
            "cadenas_pretty_function": len(PRETTY),
        },
        "cadenas": strings,
        "funciones": funcs,
        "pretty_function": {hex(k): v for k, v in sorted(PRETTY.items())},
        "rtti": RTTI,
        "constantes": {
            "id_modulo_trazas": 0x133,
            "cola_eventos_camara": 0x7a0020,
            "servicio_adc_liro": 0x720018,
            "bus_dispositivo_rpr0400": 0x520250,
            "cola_sync_illumi_cam": 0x13303be,
            "cola_sync_illumi_diag": 0x13303ba,
            "backup_ids": [0x133003c, 0x133003d],
            "key_codes_nivel": [0x17000001, 0x17000002],
            "tabla_osal_0x10600xx": {"addr": 0x43fdaaa4, "n": 19},
            "msg_id_adc_get_d": 0xfff0,
            "registro_ad_dispositivo": 0x46,
            "direccion_dispositivo": 0x39,
            "periodo_temporizador": 0x4e20,
        },
        "diferencial": diff,
        "diferencial_cadenas_Illumi": {
            "A6000_fw321": {"apariciones": 45, "cadenas_distintas": 43},
            "A7S_fw320": {"apariciones": 4, "cadenas_distintas": 4},
            "A6300_fw201": {"apariciones": 4, "cadenas_distintas": 4},
        },
        "rtti_diferencial": rtti_diff,
    }
    import hashlib
    out["imagen"]["sha256"] = hashlib.sha256(B).hexdigest()
    json.dump(out, open("analysis/s170_illumi/illumi.json", "w"), indent=1, ensure_ascii=False)
    print("escrito analysis/s170_illumi/illumi.json")
    print(json.dumps(out["cifras"], indent=1))


if __name__ == "__main__":
    main()
