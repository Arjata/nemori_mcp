ACTIVATE_PYTHON_ENVIRONMENT="source ./.__env/bin/activate";
exec bash -c "${ACTIVATE_PYTHON_ENVIRONMENT};mcp run ./src/main.py";