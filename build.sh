#!/bin/bash
pip install -r requirements.txt
python src/manage.py collectstatic --no-input
