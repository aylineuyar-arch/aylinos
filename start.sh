#!/bin/bash
set -e
python -m pip install --no-cache-dir -r requirements.txt
exec python -m gunicorn api.server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --timeout 120
