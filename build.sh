#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p build
for name in min for double; do
    nasm -f elf64 "$name.asm" -o "build/$name.o" -l "build/$name.lst"
    ld -o "build/$name" "build/$name.o"
    objdump -d -M intel --wide "build/$name" > "build/$name.disasm.txt"
    objcopy -O binary -j .text "build/$name" "build/$name.text.bin"
done
python3 source_map.py
printf 'Built: min, for, double\n'
