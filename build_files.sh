#!/usr/bin/env bash

set -o errexit

python3 -m pip install -r requirements.txt
python manage.py migrate