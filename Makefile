
#export PYTHON ?= /usr/bin/python3.12

## Cleaning
#######
mrproper:
	@make -C fw/astep24-3l mrproper
	@rm -Rf docs/site docs/.venv
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete


## Docs
############
ci_docs: export PYTHONPATH := :$(BASE)/fw/astep24-3l/common:$(BASE)/fw/common/verification:$(PYTHONPATH)
ci_docs:
	@xvfb-run icf_doc

ci_deps:
	@sudo apt install tcl tcllib xvfb
	@icf_update_drawio

docs: export PYTHONPATH := :$(BASE)/fw/astep24-3l/common:$(BASE)/fw/common/verification:$(PYTHONPATH)
docs: docs/site/index.html
docs/site/index.html: docs/mkdocs.yml
	@icf_doc

docs.serve: export PYTHONPATH := :$(BASE)/fw/astep24-3l/common:$(BASE)/fw/common/verification:$(PYTHONPATH)
docs.serve:
	@icf_doc --serve

serve:
	@icf_doc --serve
