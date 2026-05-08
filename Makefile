# vim: ts=4 sw=4 noet

PYPI_REPO	?= testpypi
VERSION		?= $(shell echo "0.5.dev$$(date -u +'%j%H%M' | sed -e 's/^0//')")

SEDI		= sed -i -E -e
VERSIONQ	= '$(VERSION)'

.PHONY:		clean dist push pypi-upload release setver

define usage

  clean
  dist
  pypi-upload  PYPI_REPO=...
  release      VERSION=...
  setver       VERSION=...

endef

help:
	@$(info $(usage))
	@exit 0

clean:
	rm -fr dist/*

dist:
	python -m build

pypi-upload:
	twine upload --sign --identity 6AE2A84723D56D985B340BC08E5FA4709F69E911 --repository $(PYPI_REPO) dist/*

release:	setver
	$(SEDI) "s/(RELEASE=).*/\1$(VERSIONQ)/" scripts/install

setver:
	$(SEDI) "s/(^VERSION =).*/\1 $(VERSIONQ)/" postqf/__init__.py
	$(SEDI) "s/(^version =).*/\1 $(VERSION)/" setup.cfg
