#!/bin/zsh

if [[ $# -eq 0 ]]; then
    echo "Usage: $(basename ${0}) TARGET [TARGET...]"
    exit 1
fi
for TARGET in "$@"; do
    if X=$(dot -Tcanon $1); then
        for FMT in svg png; do
            OUTFILE="${TARGET}.${FMT}"
            echo "${X}" | dot -T${FMT} > "${OUTFILE}"
            if [[ $? -eq 0 ]]; then
                echo "Output written to ${OUTFILE}"
            fi
        done
    fi
done
