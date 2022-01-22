.PHONY:	clean dist usage

usage:
	@echo >&2 "Usage: make {clean | dist}"

clean:
	rm -fr dist/*

dist:
	python -m build
