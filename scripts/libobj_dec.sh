#!/bin/sh
# Uso: scripts/libobj_dec.sh libX.so salida.json 0xADDR(+t)... — decompila en proyecto Ghidra local analysis/ghidra/a6000-libs (importa si falta; sin autoanálisis)
lib=$1; out=$2; shift 2
D=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib
J="$PWD/tools/providers/jdk-21.0.12.1+1"; G=tools/providers/ghidra_12.1.4_PUBLIC/support/analyzeHeadless
[ -e analysis/ghidra/a6000-libs.rep/idata/$lib.imp ] || env JAVA_HOME=$J $G analysis/ghidra a6000-libs -import $D/$lib -processor ARM:LE:32:v7 -noanalysis >/dev/null 2>&1
env JAVA_HOME=$J timeout 580 $G analysis/ghidra a6000-libs -process $lib -noanalysis -readOnly -scriptPath analysis/ghidra -postScript DecompAt.java "$PWD/$out" "$@" >/dev/null 2>&1
python3 -I -c "
import json,sys
for x in json.load(open(sys.argv[1])): print('//',x['entry'],x['status']);print(x.get('pseudo_code',''))" "$out"
