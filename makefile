ACTIVATE_PYTHON_ENVIRONMENT=source ./.__env/bin/activate

PORT:=8877

default_action:start_openapi

install_deps:
	python3 -m venv .__env;
	bash -c "${ACTIVATE_PYTHON_ENVIRONMENT};pip install -e ./3rd_dependencies/nemori -r ./requirements.txt;";
	bash -c "${ACTIVATE_PYTHON_ENVIRONMENT};python -m spacy download en_core_web_sm;python -m spacy download zh_core_web_sm;";
start_openapi:
	bash -c "${ACTIVATE_PYTHON_ENVIRONMENT};mcpo --port ${PORT} -- mcp run ./src/main.py";
clean_memory:
	$(RM) -r ./memories ./chroma_db;