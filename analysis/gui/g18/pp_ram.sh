#!/bin/sh
# pp_ram.sh (G18, generado por pp_curves_patch.py): gammas PP en la RAM del núcleo. Lo lanza s_start_android.sh.
D=/usr/bin/pp_curvas.bin
rd() { dd if=/dev/mem bs=2 skip=$1 count=$2 2>/dev/null | md5sum | cut -c1-32; }  # en medias palabras: $(( )) de ash es de 32 bits
echo "pp_ram: inicio $(date)"
ok=1
[ "$(rd 1107130752 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x16 no es el original"; ok=0; }
[ "$(rd 1107132816 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x18 no es el original"; ok=0; }
[ "$(rd 1107134880 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x19 no es el original"; ok=0; }
[ "$(rd 1107136944 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x1a no es el original"; ok=0; }
[ "$(rd 1107139008 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x1b no es el original"; ok=0; }
[ "$(rd 1107141072 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x1c no es el original"; ok=0; }
[ "$(rd 1107143136 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x1d no es el original"; ok=0; }
[ "$(rd 1107298908 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x16 no es el original"; ok=0; }
[ "$(rd 1107298916 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x18 no es el original"; ok=0; }
[ "$(rd 1107298920 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x19 no es el original"; ok=0; }
[ "$(rd 1107298924 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x1a no es el original"; ok=0; }
[ "$(rd 1107298928 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x1b no es el original"; ok=0; }
[ "$(rd 1105570678 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 3 no es el original"; ok=0; }
[ "$(rd 1105570679 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 4 no es el original"; ok=0; }
[ "$(rd 1105570680 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 5 no es el original"; ok=0; }
[ "$(rd 1105570681 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 6 no es el original"; ok=0; }
[ "$(rd 1105570682 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 7 no es el original"; ok=0; }
[ "$(rd 1105570683 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 8 no es el original"; ok=0; }
[ "$(rd 1105570684 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 9 no es el original"; ok=0; }
[ $ok = 1 ] || { echo "pp_ram: av-cam distinto, no se escribe nada"; exit 1; }
dd if=$D bs=2 skip=0 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107130752 2>/dev/null
[ "$(rd 1107130752 2061)" = "ceede7d57442afc1bab3a3de4dd45c8e" ] || { echo "pp_ram: FALLO al escribir curva 0x16"; ok=0; }
dd if=$D bs=2 skip=2061 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107132816 2>/dev/null
[ "$(rd 1107132816 2061)" = "9241b3b6bbd2d45f6db504ce7d1b348a" ] || { echo "pp_ram: FALLO al escribir curva 0x18"; ok=0; }
dd if=$D bs=2 skip=4122 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107134880 2>/dev/null
[ "$(rd 1107134880 2061)" = "68af599683c90a06560bfe61ad9f312b" ] || { echo "pp_ram: FALLO al escribir curva 0x19"; ok=0; }
dd if=$D bs=2 skip=6183 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107136944 2>/dev/null
[ "$(rd 1107136944 2061)" = "bd30efe7ad68f4026661c427a0d9346f" ] || { echo "pp_ram: FALLO al escribir curva 0x1a"; ok=0; }
dd if=$D bs=2 skip=8244 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107139008 2>/dev/null
[ "$(rd 1107139008 2061)" = "d03620d2700c36adade83302c3b1b20b" ] || { echo "pp_ram: FALLO al escribir curva 0x1b"; ok=0; }
dd if=$D bs=2 skip=10305 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107141072 2>/dev/null
[ "$(rd 1107141072 2061)" = "8f765a3c3174aa10f45cb876450d11c2" ] || { echo "pp_ram: FALLO al escribir curva 0x1c"; ok=0; }
dd if=$D bs=2 skip=12366 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107143136 2>/dev/null
[ "$(rd 1107143136 2061)" = "1e3dca5a433f43b642c1e5e959d4fa92" ] || { echo "pp_ram: FALLO al escribir curva 0x1d"; ok=0; }
dd if=$D bs=2 skip=14427 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298908 2>/dev/null
[ "$(rd 1107298908 2)" = "c4932a251d3dd289339b78c22cfab986" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x16"; ok=0; }
dd if=$D bs=2 skip=14429 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298916 2>/dev/null
[ "$(rd 1107298916 2)" = "6fe69d6c24f40519be3b91dc4aaa65b3" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x18"; ok=0; }
dd if=$D bs=2 skip=14431 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298920 2>/dev/null
[ "$(rd 1107298920 2)" = "29be1969c5c1f2928acff2729280ce39" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x19"; ok=0; }
dd if=$D bs=2 skip=14433 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298924 2>/dev/null
[ "$(rd 1107298924 2)" = "4abd0870160281bca4195c48b9b2c256" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x1a"; ok=0; }
dd if=$D bs=2 skip=14435 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298928 2>/dev/null
[ "$(rd 1107298928 2)" = "8cb45ad2e7018d3aefb7fcecbab9310e" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x1b"; ok=0; }
dd if=$D bs=2 skip=14437 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570678 2>/dev/null
[ "$(rd 1105570678 1)" = "672349169aac4fcc07d73181b0fc3c41" ] || { echo "pp_ram: FALLO al escribir selector 3"; ok=0; }
dd if=$D bs=2 skip=14438 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570679 2>/dev/null
[ "$(rd 1105570679 1)" = "e1c06d85ae7b8b032bef47e42e4c08f9" ] || { echo "pp_ram: FALLO al escribir selector 4"; ok=0; }
dd if=$D bs=2 skip=14439 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570680 2>/dev/null
[ "$(rd 1105570680 1)" = "c4103f122d27677c9db144cae1394a66" ] || { echo "pp_ram: FALLO al escribir selector 5"; ok=0; }
dd if=$D bs=2 skip=14440 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570681 2>/dev/null
[ "$(rd 1105570681 1)" = "48f77b42a3bf1a5677b0a932a3298fc5" ] || { echo "pp_ram: FALLO al escribir selector 6"; ok=0; }
dd if=$D bs=2 skip=14441 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570682 2>/dev/null
[ "$(rd 1105570682 1)" = "31e812799bf986f2a05a1fabe50c71d9" ] || { echo "pp_ram: FALLO al escribir selector 7"; ok=0; }
dd if=$D bs=2 skip=14442 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570683 2>/dev/null
[ "$(rd 1105570683 1)" = "736ea4ce8c5035554d33d4973359495b" ] || { echo "pp_ram: FALLO al escribir selector 8"; ok=0; }
dd if=$D bs=2 skip=14443 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570684 2>/dev/null
[ "$(rd 1105570684 1)" = "9dd694e7e648d04b019c56ae7a58f014" ] || { echo "pp_ram: FALLO al escribir selector 9"; ok=0; }
[ $ok = 1 ] && echo "pp_ram: OK" || { echo "pp_ram: ERROR"; exit 1; }
( for t in 60 600 3600; do sleep $t; [ "$(rd 1107130752 2061)" = "ceede7d57442afc1bab3a3de4dd45c8e" ] || echo "pp_ram: curva 0x16 alterada a los ${t} s" ; [ "$(rd 1107132816 2061)" = "9241b3b6bbd2d45f6db504ce7d1b348a" ] || echo "pp_ram: curva 0x18 alterada a los ${t} s" ; [ "$(rd 1107134880 2061)" = "68af599683c90a06560bfe61ad9f312b" ] || echo "pp_ram: curva 0x19 alterada a los ${t} s" ; [ "$(rd 1107136944 2061)" = "bd30efe7ad68f4026661c427a0d9346f" ] || echo "pp_ram: curva 0x1a alterada a los ${t} s" ; [ "$(rd 1107139008 2061)" = "d03620d2700c36adade83302c3b1b20b" ] || echo "pp_ram: curva 0x1b alterada a los ${t} s" ; [ "$(rd 1107141072 2061)" = "8f765a3c3174aa10f45cb876450d11c2" ] || echo "pp_ram: curva 0x1c alterada a los ${t} s" ; [ "$(rd 1107143136 2061)" = "1e3dca5a433f43b642c1e5e959d4fa92" ] || echo "pp_ram: curva 0x1d alterada a los ${t} s"; echo "pp_ram: comprobación ${t} s hecha"; done ) &  # ¿el núcleo pisa el hueco en uso real?
( sleep 20; echo -ne '\006' | dd of=/dev/mem bs=1 seek=2213410775 2>/dev/null; echo "pp_ram: prueba selector=6 en 0x83edf7d7" ) &
( sleep 20; echo -ne '\006' | dd of=/dev/mem bs=1 seek=2213367491 2>/dev/null; echo "pp_ram: prueba selector=6 en 0x83ed4ec3" ) &
