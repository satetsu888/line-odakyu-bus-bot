#!/bin/sh

action=$1
shift

case ${action} in
    webhook_app)
        (export FLASK_APP=webhook_app/app.py && flask run -h 0.0.0.0 -p 5000)
        ;;
    python)
        (python)
        ;;
    pip)
        (pip "$@" && pip freeze > requirements.txt)
        ;;
    sh)
        (/bin/sh)
        ;;
esac
