#!/bin/sh
set -eu

mkdir -p /app/data
if [ ! -e /app/data/nclex_simple.db ] && [ -f /app/data_loader/nclex_simple.db ]; then
    cp /app/data_loader/nclex_simple.db /app/data/nclex_simple.db
fi

exec "$@"
