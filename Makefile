.PHONY: install test gates

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest

gates:
	python scripts/check_gates.py
