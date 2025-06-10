#!/usr/bin/env bash
set -e
script_dir="$(dirname "$(realpath "$0")")"
if [[ "$1" == "configure" ]]; then
    genaiscript configure
else
    genaiscript run "$script_dir/src/genaisrc/promptpex.genai.mts" $@
fi
