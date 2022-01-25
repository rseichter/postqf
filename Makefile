# vim:ts=4:sw=4:noet

PYPI_REPO	?= testpypi
VENV		= $(shell realpath .venv)

.PHONY:		clean dist prep push pypi-upload setver usage

usage:
	@echo >&2 "Usage: make {clean | dist | pypi-upload}"

clean:	prep
	rm -fr dist/*

dist:
	python -m build

prep:
	@which pip | grep -q '^$(VENV)/bin/pip' || (echo 'Please execute:\n\n  source $(VENV)/bin/activate\n'; exit 1)

push:
	@for r in $(shell git remote); do git push $$r; done

pypi-upload:	prep
	twine upload --sign --identity 6AE2A84723D56D985B340BC08E5FA4709F69E911 --repository $(PYPI_REPO) dist/*

V	?= $(shell echo "0.3.dev$$(date -u +'%j%H%M' | sed -e 's/^0//')")
VQ	= '$(V)'
SED	= sed -i"" -E -e "s/(^version =).*/\1

setver:
	$(SED) $(VQ)/i" postqf/__init__.py
	$(SED) $(V)/i" setup.cfg
