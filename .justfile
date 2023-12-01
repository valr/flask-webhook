# use default or current directory for temporary directories/files
set tempdir := "."

# list the recipes
default:
  @just --justfile {{justfile()}} --list --list-heading '' --unsorted

# initialise the virtual environment
init-venv:
  #!/usr/bin/env bash
  set -euo pipefail
  [ -d .venv ] && { echo "error: the virtual environment .venv already exists"; false; }
  python -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip setuptools wheel
  pip install --upgrade pip-tools

# install the requirements for a production environment
install-requirements-production:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }
  source .venv/bin/activate
  pip-sync requirements.txt

# install the requirements for a development environment
install-requirements-development:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }
  source .venv/bin/activate
  pip-sync requirements.txt dev-requirements.txt

# compile the requirements for production and development environments
compile-requirements:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }
  source .venv/bin/activate
  pip-compile --quiet requirements.in
  pip-compile --quiet dev-requirements.in

# upgrade the requirements for production and development environments
upgrade-requirements:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }
  source .venv/bin/activate
  pip-compile --quiet --upgrade requirements.in
  pip-compile --quiet --upgrade dev-requirements.in

# run the flask application in the development server
run-application:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }
  source .venv/bin/activate
  flask --debug run
