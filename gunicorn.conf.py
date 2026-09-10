# gunicorn.conf.py
workers = 4
threads = 2
bind = "0.0.0.0:8050"
timeout = 120
keepalive = 5