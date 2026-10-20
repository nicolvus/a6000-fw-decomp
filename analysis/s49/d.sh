# uso: d.sh DIR_INI DIR_FIN (direcciones reales, base 0x43541000)
D=$(dirname $0); B=0x43541000
llvm-objdump -D --triple=thumbv7 --adjust-vma=$B --start-address=$(printf 0x%x $(( $1 - B ))) --stop-address=$(printf 0x%x $(( $2 - B ))) $D/av.elf | grep -E "^ *[0-9a-f]+:" 
