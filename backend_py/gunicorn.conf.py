# Configuration Gunicorn pour la production
# Supprime le header Server automatiquement

import gunicorn

# Supprimer le header Server
gunicorn.SERVER = ""

# Configuration de base
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Sécurité
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
