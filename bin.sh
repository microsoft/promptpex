#!/usr/bin/env bash
if [[ "$1" == "serve" ]]; then
    npm run serve
elif [[ "$1" == "configure" ]]; then
    npm run configure
else
    npm run genai promptpex $@
fi