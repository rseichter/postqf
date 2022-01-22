# PostQF

Postfix queue data filter. Operates on JSON data produced by "postqueue -j".

Copyright © 2022 Ralph Seichter

## Installation

PostQF is distributed via [PyPI.org](https://test.pypi.org/project/postqf/) and can be installed using the following
commands:

```bash
# Minimal installation
pip install postqf
```

The only requirement is Python 3.7 or newer. No additional packages will be installed.

```bash
# Advanced installation using a Python virtual environment
mkdir ~/postqf
cd ~/postqf
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip postqf
```

## Usage

