import multiprocessing

# Django WSGI application path
wsgi_app = "daospace.wsgi:application"
# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1
# The socket to bind
bind = "0.0.0.0:8000"
# Log to stdout
accesslog = "-"
errorlog = "-"