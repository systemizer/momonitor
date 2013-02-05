# see http://gunicorn.org/configure.html
import os
__pwd = os.path.abspath(__file__)
workers = 5 
timeout = 120
bind = "127.0.0.1:5008"
loglevel = 'debug'
