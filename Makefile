.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
USING_POETRY=$(shell grep "tool.poetry" pyproject.toml && echo "yes")

.PHONY: help
help:             	## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: venv
venv:			## Create a virtual environment
	@echo "Creating virtualenv ..."
	@rm -rf .venv
	@if command -v uv >/dev/null 2>&1; then \
		uv venv .venv; \
		uv pip install -U pip; \
	else \
		python3 -m venv .venv; \
		./.venv/bin/pip install -U pip; \
	fi
	@echo
	@echo "Run 'source .venv/bin/activate' to enable the environment"

.PHONY: install
install:        ## Install dependencies
	@if command -v uv >/dev/null 2>&1; then \
		export UV_INDEX_URL="$$(pip config get global.extra-index-url)"; \
		export UV_HTTP_TIMEOUT=8400; \
		if [ -d ".venv" ]; then \
			uv pip install --reinstall -e ".[dev, test]"; \
		else \
			uv pip install --system -e ".[dev, test]"; \
		fi \
	else \
		python -m pip install -U pip; \
		pip install -e ".[dev, test]"; \
	fi

.PHONY: clean
clean:			## Clean unused files.
	@rm -rf build
	@rm -rf reports/ || true
	@rm -f .coverage || true

.PHONY: lint
lint:			## Run linters.
	mkdir -p reports
	ruff check --exit-zero --output-format json -o reports/lint-report-ruff.json .
	ruff check --exit-zero --output-format concise .

.PHONY: test
test:			## Run tests and coverage
	mkdir -p reports
	python -m pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/html --cov-report xml:reports/coverage.xml --junitxml=reports/junit.xml --cov-fail-under 65 --cov=hack_onboard_field_support_chatbot tests

.PHONY: security
security:		## Run dependency security check
	mkdir -p reports
	safety check -r requirements.txt --output screen

.PHONY: build
build:			## Build locally the python artifact
	python -m build

.PHONY: upload
upload:			## Upload the python artifact to artifactory
	twine upload -r cosmos dist/*

.PHONY: Run
run: 			## Run uvicorn
	APP_ENVIRONMENT=dev LOCAL_MODE=si uvicorn hack_onboard_field_support_chatbot.__main__:app --host 127.0.0.1 --port 3000 --log-level debug --timeout-keep-alive 9999999999999
