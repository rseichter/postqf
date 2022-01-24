# vim:ts=4:sw=4:noet

COVERAGE	?= env PYTHONPATH=.. LOG_LEVEL=FATAL coverage
COVOPT		?= --rcfile=../pyproject.toml
HTMLDIR		?= ../local/coverage

.PHONY:	coverage coverage-html run-tests

coverage:
	$(COVERAGE) run $(COVOPT) --include='../postqf/*' -m unittest discover
	coverage report

coverage-html:	coverage
	[ -d $(HTMLDIR) ] || mkdir -p $(HTMLDIR)
	$(COVXML) html -d $(HTMLDIR) --title='PostQF test coverage' --skip-empty --no-skip-covered
	open $(HTMLDIR)/index.html

run-tests:
	$(COVERAGE) python -m unittest discover -v
