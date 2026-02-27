#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium --with-deps

mkdir -p database
mkdir -p app/static/screenshots
mkdir -p backups

python manage.py migrate

echo "✓ Build completed"