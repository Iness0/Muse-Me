#!/bin/bash
source venv/bin/activate
while true; do
    flask db migrate
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Migration command failed, retrying in 5 secs...
    sleep 5
done
flask db upgrade
flask translate compile
exec gunicorn -b :5000 --access-logfile - --error-logfile - muse_me:app