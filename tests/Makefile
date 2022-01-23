# vim:ts=4:sw=4:noet

ENV		= env PYTHONPATH=.. LOG_LEVEL=FATAL
COVDIR	?= ../local/coverage

.PHONY:	coverage coverage-html run-tests

coverage:
	$(ENV) coverage run --rcfile=../pyproject.toml --include='../postqf/*' -m unittest discover
	coverage report

coverage-html:	coverage
	coverage html -d $(COVDIR) --title='PostQF test coverage' --skip-empty --no-skip-covered
	open $(COVDIR)/index.html

run-tests:
	$(ENV) python -m unittest discover -v
