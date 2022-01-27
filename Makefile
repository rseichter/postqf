# vim:ts=4:sw=4:noet

PYPI_REPO	?= testpypi
VERSION		?= $(shell echo "0.3.dev$$(date -u +'%j%H%M' | sed -e 's/^0//')")

SEDI		= sed -i'' -E -e
VENV		= $(shell realpath .venv)
VERSIONQ	= '$(VERSION)'

.PHONY:		clean dist push pypi-upload release setver

define usage

  clean
  dist
  push
  pypi-upload  PYPI_REPO=...
  release      VERSION=...
  setver       VERSION=...

endef

help:
	@$(info $(usage))
	@exit 1

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

release:	setver
	$(SEDI) "s/(RELEASE=')[0-9].+/\1$(VERSION)'/" scripts/install

setver:
	$(SEDI) "s/(^VERSION =).*/\1 $(VERSIONQ)/" postqf/__init__.py
	$(SEDI) "s/(^version =).*/\1 $(VERSION)/" setup.cfg
