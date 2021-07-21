#!/usr/bin/env bash

export CURR_DIR="$(pwd)"

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "Transposing: $CURR_DIR/$*"

pipenv run python transpose.py "$CURR_DIR/$1"
