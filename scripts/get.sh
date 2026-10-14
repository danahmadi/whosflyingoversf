#!/bin/bash
# usage: get.sh YYYY.MM.DD
d=$1; tag=v$d-planes-readsb-prod-0; out=/workspace/adsb/$d; mkdir -p $out
base=https://github.com/adsblol/globe_history_2026/releases/download/$tag/$tag.tar
( curl -sL $base.aa; curl -sL $base.ab ) | tar -x -C $out --wildcards '*trace_full_aa3b5a*' '*trace_full_a783b4*' '*trace_full_aaec64*' '*trace_full_a06bba*' '*trace_full_ad9518*' 2>&1 | tail -2
find $out -type f | head
