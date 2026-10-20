bash $(dirname $0)/d.sh $1 $2 | sed 's/<_binary[^>]*>//; s/ *@ 0x[0-9a-f]* *$//; s/ *@ imm = .*//' | awk '{$1=$1};1' | cut -c1-80
