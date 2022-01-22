# vim:ts=4:sw=4:noet

PYPI_REPO	?= testpypi
VENV		= $(shell realpath .venv)

.PHONY:		clean dist prep pypi-upload usage

usage:
	@echo >&2 "Usage: make {clean | dist | pypi-upload}"

clean:	prep
	rm -fr dist/*

dist:
	python -m build

prep:
	@which pip | grep -q '^$(VENV)/bin/pip' || (echo 'Please execute:\n\n  source $(VENV)/bin/activate\n'; exit 1)

pypi-upload:	prep
	twine upload --sign --identity 6AE2A84723D56D985B340BC08E5FA4709F69E911 --repository $(PYPI_REPO) dist/*
