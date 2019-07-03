help:
	@echo "    clean"
	@echo "        Remove python artifacts."
	@echo "    clean-eggs"
	@echo "        Remove egg artifacts."
	@echo "    clean-build"
	@echo "        Remove build artifacts."
	@echo "    setup"
	@echo "       Installs deps and configure pre-commit."
	@echo "    isort"
	@echo "       Sort import statements."
	@echo "    lint"
	@echo "        Check style with flake8."
	@echo "    format"
	@echo "        Format code with black."
	@echo "    test"
	@echo "        Run py.test"
	@echo '    run'
	@echo '        Run the project.'

clean: clean-eggs clean-build
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete

clean-eggs:
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

setup:
	poetry install
	poetry run pre-commit install

isort:
	poetry run isort . --recursive

lint:
	poetry run flake8 --ignore=E501,W503

format:
	poetry run black .

test:
	poetry run pytest -x .

run:
	poetry run python -m roguelike
