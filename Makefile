# vim:ts=4:sw=4:noet

VENV	= $(shell realpath .venv)

.PHONY:	clean dist prep usage

usage:
	@echo >&2 "Usage: make {clean | dist}"

clean:	prep
	rm -fr dist/*

dist:
	python -m build

prep:
	@which pip | grep -q '^$(VENV)/bin/pip' || (echo 'Please execute:\n\n  source $(VENV)/bin/activate\n'; exit 1)
