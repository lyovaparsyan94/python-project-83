#!/usr/bin/env bash

# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Вместо source используем точку, которая работает во всех POSIX-совместимых оболочках
. $HOME/.local/bin/env

# Установка и настройка базы данных
make install && psql -a -d $DATABASE_URL -f database.sql
