from os import environ

REGISTRAR_URL = environ.get("REGISTRAR_URL", "http://localhost:5000")
BALLOTSERVER_URL = environ.get("BALLOTSERVER_URL", "http://localhost:8000")
