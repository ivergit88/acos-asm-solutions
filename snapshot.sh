#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
bash build.sh
mkdir -p reference
for name in min for double; do
    cp "build/$name" "build/$name.lst" "build/$name.disasm.txt" reference/
    sed -i 's/[[:space:]]*$//' "reference/$name.lst"
    readelf -SW "build/$name" > "reference/$name.sections.txt"
    nm -n "build/$name" > "reference/$name.symbols.txt"
done
cp build/source-map.json reference/
sha256sum min.asm for.asm double.asm reference/min reference/for reference/double > reference/SHA256SUMS
