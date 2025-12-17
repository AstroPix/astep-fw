PYTHON_EXE?=python3.13

env: .venv/bin/activate requirements.txt
	@.venv/bin/pip3 install -r requirements.txt

env.beagle: env requirements-beagle.txt
	@.venv/bin/pip3 install -r requirements-beagle.txt

env.nexys: env requirements-nexys.txt
	@.venv/bin/pip3 install -r requirements-nexys.txt
	

.venv/bin/activate:
	@rm -Rf .venv
	@$(PYTHON_EXE) -m venv .venv
