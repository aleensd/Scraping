
SHELL := /bin/bash
SOURCE_VENV := source venv/bin/activate
PYTHON_INTERPRETER := python3.11
PIP := $(PYTHON_INTERPRETER) -m pip
VENV_DIR = venv

.PHONY: clean venv

clean:
	rm -rf venv server/__pycache__ tests/__pycache__

venv:
	$(PYTHON_INTERPRETER) -m venv $(VENV_DIR)
	$(SOURCE_VENV) && $(PIP) install --upgrade pip
	$(SOURCE_VENV) && $(PIP) install -r requirements.txt