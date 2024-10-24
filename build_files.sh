#!/usr/bin/env bash

set -o errexit

python3 -m pip install -r requirements.txt
python manage.py collectstatic --noinput -skip-errors
python manage.py migrate