#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p database
mkdir -p app/static/screenshots

python manage.py migrate

echo "Build complete"
