#!/usr/bin/env bash
set -e
echo "$@"
script_dir="$(dirname "$(realpath "$0")")"
if [[ "$1" == "configure" ]]; then
    genaiscript configure
else
    genaiscript run "$script_dir/src/genaisrc/promptpex.genai.mts" -ma rules=large -ma evals=large -ma baseline=large -- $@
fi
