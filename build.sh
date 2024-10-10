#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

python QuakStore/manage.py collectstatic --no-input

python QuakStore/manage.py migrate