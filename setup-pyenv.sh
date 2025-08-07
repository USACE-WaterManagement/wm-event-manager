#!/bin/bash

# If user has pyenv installed, setup-pyenv.sh will install the targeted
# python version, create a venv, and install all required dev packages.

pyenv install -s 3.13.5
pyenv virtualenv -f 3.13.5 wm-event-manager
pip install -r api/requirements-dev.txt
