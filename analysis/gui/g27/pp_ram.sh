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
[ "$(rd 1107141072 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x14 no es el original"; ok=0; }
[ "$(rd 1107143136 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x15 no es el original"; ok=0; }
[ "$(rd 1107145200 2061)" = "a174628d565b0f05668f7ce07633311b" ] || { echo "pp_ram: curva 0x17 no es el original"; ok=0; }
[ "$(rd 1107298908 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x16 no es el original"; ok=0; }
[ "$(rd 1107298916 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x18 no es el original"; ok=0; }
[ "$(rd 1107298920 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x19 no es el original"; ok=0; }
[ "$(rd 1107298924 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x1a no es el original"; ok=0; }
[ "$(rd 1107298928 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x1b no es el original"; ok=0; }
[ "$(rd 1107298900 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x14 no es el original"; ok=0; }
[ "$(rd 1107298904 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x15 no es el original"; ok=0; }
[ "$(rd 1107298912 2)" = "f1d3ff8443297732862df21dc4e57262" ] || { echo "pp_ram: puntero vídeo 0x17 no es el original"; ok=0; }
[ "$(rd 1105570678 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 3 no es el original"; ok=0; }
[ "$(rd 1105570679 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 4 no es el original"; ok=0; }
[ "$(rd 1105570680 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 5 no es el original"; ok=0; }
[ "$(rd 1105570681 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 6 no es el original"; ok=0; }
[ "$(rd 1105570682 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 7 no es el original"; ok=0; }
[ "$(rd 1105570683 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 8 no es el original"; ok=0; }
[ "$(rd 1105570684 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 9 no es el original"; ok=0; }
[ "$(rd 1105570685 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 10 no es el original"; ok=0; }
[ "$(rd 1105570686 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 11 no es el original"; ok=0; }
[ "$(rd 1105570687 1)" = "8f7cbbbe0e8f898a6fa93056b3de9c9c" ] || { echo "pp_ram: selector 12 no es el original"; ok=0; }
[ "$(rd 1107147264 6)" = "8dd6bb7329a71449b0a1b292b5999164" ] || { echo "pp_ram: dato tabla tipo→id no es el original"; ok=0; }
[ "$(rd 1107147272 9)" = "ff035bff2dcf972ee7dfd023455997ef" ] || { echo "pp_ram: dato matriz S-Gamut3 no es el original"; ok=0; }
[ "$(rd 1107147281 9)" = "ff035bff2dcf972ee7dfd023455997ef" ] || { echo "pp_ram: dato matriz S-Gamut3.Cine no es el original"; ok=0; }
[ "$(rd 1107147290 12)" = "1681ffc6e046c7af98c9e6c232a3fe0a" ] || { echo "pp_ram: dato deltas S-Gamut3 no es el original"; ok=0; }
[ "$(rd 1107147304 30)" = "a302a771ee0e3127b8950f0a67d17e49" ] || { echo "pp_ram: dato código switch no es el original"; ok=0; }
[ "$(rd 1107147336 24)" = "b203621a65475445e6fcdca717c667b5" ] || { echo "pp_ram: dato código matrices no es el original"; ok=0; }
[ "$(rd 1107147368 16)" = "70bc8f4b72a86921468bf8e8441dce51" ] || { echo "pp_ram: dato código deltas no es el original"; ok=0; }
[ "$(rd 1102927856 2)" = "a7a1cfaedcf8c24270c3c94e49d48b03" ] || { echo "pp_ram: gancho literal tabla de tipos no es el original"; ok=0; }
[ "$(rd 1102926859 1)" = "32a7c4eed331dfe55ba7ebd8d6d8c065" ] || { echo "pp_ram: gancho cmp tipo ≤ 10 no es el original"; ok=0; }
[ "$(rd 1102914977 1)" = "7c9c6b4bc03a09e0d73fe324c49752ac" ] || { echo "pp_ram: gancho cmp matriz ≤ 0x11 no es el original"; ok=0; }
[ "$(rd 1102914153 1)" = "e87e4e879514bd508b89a92df53c2d51" ] || { echo "pp_ram: gancho cmp conjunto ≤ 0x1a no es el original"; ok=0; }
[ "$(rd 1102914993 2)" = "917c26991541e31cccb6df6c66133fec" ] || { echo "pp_ram: gancho matrices no es el original"; ok=0; }
[ "$(rd 1102914173 2)" = "959e668830b5fa7f4b8dc7b3a19726fc" ] || { echo "pp_ram: gancho deltas no es el original"; ok=0; }
[ "$(rd 1102915289 2)" = "578c687a85a91476a0452ca9e88271b9" ] || { echo "pp_ram: gancho switch no es el original"; ok=0; }
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
[ "$(rd 1107141072 2061)" = "179c14231c139bdbcbd71d110f52bb06" ] || { echo "pp_ram: FALLO al escribir curva 0x14"; ok=0; }
dd if=$D bs=2 skip=12366 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107143136 2>/dev/null
[ "$(rd 1107143136 2061)" = "d36cd865223fcdbb62e42d66af52717d" ] || { echo "pp_ram: FALLO al escribir curva 0x15"; ok=0; }
dd if=$D bs=2 skip=14427 count=2061 2>/dev/null | dd of=/dev/mem bs=2 seek=1107145200 2>/dev/null
[ "$(rd 1107145200 2061)" = "f79bfeb6d344a1ab5c366b286b7877fa" ] || { echo "pp_ram: FALLO al escribir curva 0x17"; ok=0; }
dd if=$D bs=2 skip=16488 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298908 2>/dev/null
[ "$(rd 1107298908 2)" = "c4932a251d3dd289339b78c22cfab986" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x16"; ok=0; }
dd if=$D bs=2 skip=16490 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298916 2>/dev/null
[ "$(rd 1107298916 2)" = "6fe69d6c24f40519be3b91dc4aaa65b3" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x18"; ok=0; }
dd if=$D bs=2 skip=16492 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298920 2>/dev/null
[ "$(rd 1107298920 2)" = "29be1969c5c1f2928acff2729280ce39" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x19"; ok=0; }
dd if=$D bs=2 skip=16494 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298924 2>/dev/null
[ "$(rd 1107298924 2)" = "4abd0870160281bca4195c48b9b2c256" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x1a"; ok=0; }
dd if=$D bs=2 skip=16496 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298928 2>/dev/null
[ "$(rd 1107298928 2)" = "8cb45ad2e7018d3aefb7fcecbab9310e" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x1b"; ok=0; }
dd if=$D bs=2 skip=16498 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298900 2>/dev/null
[ "$(rd 1107298900 2)" = "fd6d3fa7aab34a17277d2ccf96ec41f7" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x14"; ok=0; }
dd if=$D bs=2 skip=16500 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298904 2>/dev/null
[ "$(rd 1107298904 2)" = "c9720d4aaa7b8696392b013cd99ec157" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x15"; ok=0; }
dd if=$D bs=2 skip=16502 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1107298912 2>/dev/null
[ "$(rd 1107298912 2)" = "729abb92ce8d0ec1b18c3c7d4acb1051" ] || { echo "pp_ram: FALLO al escribir puntero vídeo 0x17"; ok=0; }
dd if=$D bs=2 skip=16504 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570678 2>/dev/null
[ "$(rd 1105570678 1)" = "672349169aac4fcc07d73181b0fc3c41" ] || { echo "pp_ram: FALLO al escribir selector 3"; ok=0; }
dd if=$D bs=2 skip=16505 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570679 2>/dev/null
[ "$(rd 1105570679 1)" = "e1c06d85ae7b8b032bef47e42e4c08f9" ] || { echo "pp_ram: FALLO al escribir selector 4"; ok=0; }
dd if=$D bs=2 skip=16506 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570680 2>/dev/null
[ "$(rd 1105570680 1)" = "c4103f122d27677c9db144cae1394a66" ] || { echo "pp_ram: FALLO al escribir selector 5"; ok=0; }
dd if=$D bs=2 skip=16507 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570681 2>/dev/null
[ "$(rd 1105570681 1)" = "48f77b42a3bf1a5677b0a932a3298fc5" ] || { echo "pp_ram: FALLO al escribir selector 6"; ok=0; }
dd if=$D bs=2 skip=16508 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570682 2>/dev/null
[ "$(rd 1105570682 1)" = "31e812799bf986f2a05a1fabe50c71d9" ] || { echo "pp_ram: FALLO al escribir selector 7"; ok=0; }
dd if=$D bs=2 skip=16509 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570683 2>/dev/null
[ "$(rd 1105570683 1)" = "736ea4ce8c5035554d33d4973359495b" ] || { echo "pp_ram: FALLO al escribir selector 8"; ok=0; }
dd if=$D bs=2 skip=16510 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570684 2>/dev/null
[ "$(rd 1105570684 1)" = "9dd694e7e648d04b019c56ae7a58f014" ] || { echo "pp_ram: FALLO al escribir selector 9"; ok=0; }
dd if=$D bs=2 skip=16511 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570685 2>/dev/null
[ "$(rd 1105570685 1)" = "3f8680129fdc1402b47fa4bb3113df5a" ] || { echo "pp_ram: FALLO al escribir selector 10"; ok=0; }
dd if=$D bs=2 skip=16512 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570686 2>/dev/null
[ "$(rd 1105570686 1)" = "ac2e5a852157db6588906ebee3650b80" ] || { echo "pp_ram: FALLO al escribir selector 11"; ok=0; }
dd if=$D bs=2 skip=16513 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1105570687 2>/dev/null
[ "$(rd 1105570687 1)" = "195ca9ce2738a3f5e3e57cc60a7d3ad8" ] || { echo "pp_ram: FALLO al escribir selector 12"; ok=0; }
dd if=$D bs=2 skip=16514 count=6 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147264 2>/dev/null
[ "$(rd 1107147264 6)" = "db3369b2c21ff0e677e5ffe9e1556f60" ] || { echo "pp_ram: FALLO al escribir dato tabla tipo→id"; ok=0; }
dd if=$D bs=2 skip=16520 count=9 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147272 2>/dev/null
[ "$(rd 1107147272 9)" = "92ed40e565e3919638eceee6e028c795" ] || { echo "pp_ram: FALLO al escribir dato matriz S-Gamut3"; ok=0; }
dd if=$D bs=2 skip=16529 count=9 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147281 2>/dev/null
[ "$(rd 1107147281 9)" = "f2379f32d0eff63f3edf6af32ec1e7b6" ] || { echo "pp_ram: FALLO al escribir dato matriz S-Gamut3.Cine"; ok=0; }
dd if=$D bs=2 skip=16538 count=12 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147290 2>/dev/null
[ "$(rd 1107147290 12)" = "e029c3b0700083ef1c34b83b7bcb7738" ] || { echo "pp_ram: FALLO al escribir dato deltas S-Gamut3"; ok=0; }
dd if=$D bs=2 skip=16550 count=30 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147304 2>/dev/null
[ "$(rd 1107147304 30)" = "697f432bc5fa68fe84ab2ac3276cc535" ] || { echo "pp_ram: FALLO al escribir dato código switch"; ok=0; }
dd if=$D bs=2 skip=16580 count=24 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147336 2>/dev/null
[ "$(rd 1107147336 24)" = "2d61ce5d5ae2db732a095f71e219cfef" ] || { echo "pp_ram: FALLO al escribir dato código matrices"; ok=0; }
dd if=$D bs=2 skip=16604 count=16 2>/dev/null | dd of=/dev/mem bs=2 seek=1107147368 2>/dev/null
[ "$(rd 1107147368 16)" = "2a3fb34d428d9f499c0bada78afa9393" ] || { echo "pp_ram: FALLO al escribir dato código deltas"; ok=0; }
dd if=$D bs=2 skip=16620 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1102927856 2>/dev/null
[ "$(rd 1102927856 2)" = "c4829bf9295ea80d8ac52ba421de3f17" ] || { echo "pp_ram: FALLO al escribir gancho literal tabla de tipos"; ok=0; }
dd if=$D bs=2 skip=16622 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1102926859 2>/dev/null
[ "$(rd 1102926859 1)" = "bc98d3c32001d3a6f736bc60a0c68d26" ] || { echo "pp_ram: FALLO al escribir gancho cmp tipo ≤ 10"; ok=0; }
dd if=$D bs=2 skip=16623 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1102914977 2>/dev/null
[ "$(rd 1102914977 1)" = "925f0e90b8ad76095b36c93d179a966d" ] || { echo "pp_ram: FALLO al escribir gancho cmp matriz ≤ 0x11"; ok=0; }
dd if=$D bs=2 skip=16624 count=1 2>/dev/null | dd of=/dev/mem bs=2 seek=1102914153 2>/dev/null
[ "$(rd 1102914153 1)" = "978f95e1e092f476905588bca9a4d0dd" ] || { echo "pp_ram: FALLO al escribir gancho cmp conjunto ≤ 0x1a"; ok=0; }
dd if=$D bs=2 skip=16625 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1102914993 2>/dev/null
[ "$(rd 1102914993 2)" = "d797c46a0736897247a4c01d6c645278" ] || { echo "pp_ram: FALLO al escribir gancho matrices"; ok=0; }
dd if=$D bs=2 skip=16627 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1102914173 2>/dev/null
[ "$(rd 1102914173 2)" = "b1a1699018f921539a511a590a943a7b" ] || { echo "pp_ram: FALLO al escribir gancho deltas"; ok=0; }
dd if=$D bs=2 skip=16629 count=2 2>/dev/null | dd of=/dev/mem bs=2 seek=1102915289 2>/dev/null
[ "$(rd 1102915289 2)" = "7e38b53ff0559a8b58e9f6b2d67384e5" ] || { echo "pp_ram: FALLO al escribir gancho switch"; ok=0; }
[ $ok = 1 ] && echo "pp_ram: OK" || { echo "pp_ram: ERROR"; exit 1; }
( for t in 60 600 3600; do sleep $t; [ "$(rd 1107130752 2061)" = "ceede7d57442afc1bab3a3de4dd45c8e" ] || echo "pp_ram: curva 0x16 alterada a los ${t} s" ; [ "$(rd 1107132816 2061)" = "9241b3b6bbd2d45f6db504ce7d1b348a" ] || echo "pp_ram: curva 0x18 alterada a los ${t} s" ; [ "$(rd 1107134880 2061)" = "68af599683c90a06560bfe61ad9f312b" ] || echo "pp_ram: curva 0x19 alterada a los ${t} s" ; [ "$(rd 1107136944 2061)" = "bd30efe7ad68f4026661c427a0d9346f" ] || echo "pp_ram: curva 0x1a alterada a los ${t} s" ; [ "$(rd 1107139008 2061)" = "d03620d2700c36adade83302c3b1b20b" ] || echo "pp_ram: curva 0x1b alterada a los ${t} s" ; [ "$(rd 1107141072 2061)" = "179c14231c139bdbcbd71d110f52bb06" ] || echo "pp_ram: curva 0x14 alterada a los ${t} s" ; [ "$(rd 1107143136 2061)" = "d36cd865223fcdbb62e42d66af52717d" ] || echo "pp_ram: curva 0x15 alterada a los ${t} s" ; [ "$(rd 1107145200 2061)" = "f79bfeb6d344a1ab5c366b286b7877fa" ] || echo "pp_ram: curva 0x17 alterada a los ${t} s"; echo "pp_ram: comprobación ${t} s hecha"; done ) &  # ¿el núcleo pisa el hueco en uso real?
