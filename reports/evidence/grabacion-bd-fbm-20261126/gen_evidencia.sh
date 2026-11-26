#!/bin/bash
# Genera los desensamblados de evidencia de este informe.
set -e
cd "$(dirname "$0")/../../.."          # raiz del repo
E=reports/evidence/grabacion-bd-fbm-20261126
DIS="python3 reports/evidence/fbm-sector31-consola-20261126/evidencia/mprdis.py"
mkdir -p "$E/dis"
sha256sum analysis/camera-extract/usr/lib/libmpr.so > "$E/sha256.txt"

gen() { $DIS "$1" > "$E/dis/$2" 2>&1; }

gen 0x37fb54:0x104   01-bkup-read-r4-0x37fb54.txt
gen 0x37fc80:0x200   02-bkup-getbasediff-0x37fc80.txt
gen 0x38fe68:0xa0    03-dcf-initbackuptbl-0x38fe68.txt
gen 0x61d930:0x60    04-mmgr-0x61d930.txt
gen 0x61d8d0:0x60    05-mmgr-mediaid-0x61d8d0.txt
gen 0x2b2f48:0x90    06-getindex-0x2b2f48.txt
gen 0x2b39b8:0x90    07-readfirstpack-0x2b39b8.txt
gen 0x2b3d24:0x100   08-writepackbegin-0x2b3d24.txt
gen 0x2b4030:0x120   09-writebasedata-0x2b4030.txt
gen 0x2b41b4:0x90    10-changesector-0x2b41b4.txt
gen 0x5c9aec:0x30    11-m2psifo-registro-0x5c9aec.txt
gen 0x5ca0b4:0x100   12-m2psifo-write-0x5ca0b4.txt
gen 0x5ca294:0x80    13-m2psifo-writebasedata-0x5ca294.txt
gen 0x5e7a60:0x1a0   14-m2psifo-openrecfile-0x5e7a6c.txt
gen 0x5e7d28:0x180   15-m2psifo-closerecfile-0x5e7d28.txt
gen 0x5e7ec0:0x180   16-m2psifo-cancelrec-0x5e7ec0.txt
gen 0x5ca5d4:0x60    17-m2psifo-read-0x5ca5d4.txt
gen 0x2b5598:0xb0    18-ltc01-0x2b5598.txt
gen 0x5c9f48:0x80    19-m2psifo-changesector-0x5c9f48.txt
gen 0x2b3000:0xa0    20-getsectorhandle-0x2b3000.txt
gen 0x2b3f7c:0x60    21-calluserfunc-0x2b3f7c.txt
gen 0x2b1dec:0x60    22-entrywritebasedata-0x2b1dec.txt
gen 0x5ca5c0:0x40    23-m2psifo-read2-0x5ca5c0.txt

# xrefs (llamantes bl) y tabla de escritores de fn
X="python3 reports/evidence/fbm-sector31-consola-20261126/evidencia/xref_bl.py"
{ echo "# llamantes bl (libmpr.so, VA=offset ELF)"; for t in \
    0x2b1dec 0x2b43f0 0x2b41b4 0x2b39b8 0x35ea1c 0x34e638 0x5ca0b4 0x5c9f48 0x61d930 0x2b3d24 0x2b3c64 0x2b3b94; do
    python3 "$E/xref_all.py" $t; done; } > "$E/xrefs.txt" 2>&1

python3 "$E/tabla_escritores.py" > "$E/escritores-fn.txt" 2>&1 || true
python3 "$E/tabla_estatica.py"   > "$E/tabla-0x9d23fc.txt" 2>&1 || true
echo "ok"
