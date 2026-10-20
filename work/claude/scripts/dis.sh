#!/bin/sh
# dis.sh ELF START END -> desensamblado Thumb (VA)
llvm-objdump --triple=thumbv7-none-eabi -D --no-show-raw-insn --start-address=$2 --stop-address=$3 "$1" | tail -n +7 | sed "s/<_binary_[^>]*>//"
