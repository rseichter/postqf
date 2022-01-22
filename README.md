# PostQF

Copyright © 2022 Ralph Seichter

PostQF is a user-friendly Postfix queue data filter which operates on JSON data produced by "postqueue -j". It allows
you to analyse and cleanup your mail queues in a comfortable manner.

I have used the all-purpose JSON manipulation utility _jq_ before, but found it inconvenient for everyday Postfix
administration tasks. _jq_ offers great flexibility, but it comes at the cost of complexity. PostQF is an alternative
specifically tailored for easier access to Postfix queues.

In default operation, PostQF reads from stdin and writes to stdout, but you can use command line arguments to specify an
output file and/or one or more input files.

## Filters

Queue entries can be easily filtered by

* Queue name
* Sender address
* Recipient address
* Delay reason

and combinations thereof, using
[regular expressions](https://docs.python.org/3/library/re.html#regular-expression-syntax). Anchoring is optional,
meaning that plain text is treated as a substring pattern.

## Examples

```bash
# Find all messages in the "deferred" queue where the delay reason contains
# the string 'connection timed out'.
postqueue -j | postqf -q deferred -d 'connection timed out'
```

```bash
# Find all messages in the "active" or "hold" queues which have at least one
# recipient in the example.com or example.org domains, and write the matching
# JSON records into the file /tmp/output.
postqueue -j | postqf -q 'active|hold' -r '@example\.(com|org)' -o /tmp/output
```

```bash
# Find all messages all queues for which the sender address is exactly one of
# alice@gmail.com or bob@gmail.com, and print the queue IDs to stdout.
postqueue -j | postqf -s '^(alice|bob)@gmail\.com$' -i
```

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

The _pip_ installation process adds a launcher executable `postqf`, either site-wide or in the Python virtual
environment. In the latter case, the launcher will be placed in `.venv/bin`, and this directory is added to your PATH
variable when you activate the venv environment as shown above.

## Usage

```
postqf [-h] [-d [REGEX]] [-q [REGEX]] [-r [REGEX]] [-s [REGEX]] [-i]
       [-l [LEVEL]] [-o [PATH]] [PATH [PATH ...]]

positional arguments:
  PATH        Input file. Use a dash "-" for standard input.

optional arguments:
  -h, --help  show this help message and exit
  -d [REGEX]  Delay reason filter
  -q [REGEX]  Queue name filter
  -r [REGEX]  Recipient address filter
  -s [REGEX]  Sender address filter
  -i          Output only raw queue IDs
  -l [LEVEL]  Log level (default: WARNING)
  -o [PATH]   Output file. Use a dash "-" for standard output.
```
