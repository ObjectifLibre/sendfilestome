#!/bin/sh

./manage.py migrate
exec gunicorn -b 0.0.0.0:8000 sendfilestome.wsgi
