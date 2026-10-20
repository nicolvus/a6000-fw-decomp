B=0x43541000
llvm-objdump -D --triple=thumbv7 --adjust-vma=$B --start-address=$(printf 0x%x $(( $1 - B ))) --stop-address=$(printf 0x%x $(( $2 - B ))) $(dirname $0)/av.elf | grep -E "^ *[0-9a-f]+:"
