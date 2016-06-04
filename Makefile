VENV=./venv

virtualenv: $(VENV)
	$(VENV)/bin/pip install pip --upgrade
	$(VENV)/bin/pip install -r requirements.txt

$(VENV):
	virtualenv -p python3 $(VENV)
