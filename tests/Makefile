# vim:ts=4:sw=4:noet

COVDIR	?= ../local/coverage
COVOPT	?= --rcfile=../pyproject.toml
COVXML	?= .coverage.xml
ENV		?= env PYTHONPATH=.. LOG_LEVEL=FATAL

.PHONY:	coverage coverage-ci coverage-html run-tests

coverage:
	$(ENV) coverage run $(COVOPT) --include='../postqf/*' -m unittest discover
	coverage report

coverage-ci:	coverage
	coverage xml $(COVOPT) -o $(COVXML)

coverage-html:	coverage
	coverage html -d $(COVDIR) --title='PostQF test coverage' --skip-empty --no-skip-covered
	open $(COVDIR)/index.html

run-tests:
	$(ENV) python -m unittest discover -v
