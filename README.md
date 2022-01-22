# PostQF

Copyright © 2022 Ralph Seichter

PostQF is a user-friendly Postfix queue data filter which operates on JSON data produced by "postqueue -j". It allows
analysis and and cleanup of mail queues in a convenient manner.

I have used the all-purpose JSON manipulation utility _jq_ before, but found it inconvenient for everyday Postfix
administration tasks. _jq_ offers great flexibility, but it comes at the cost of complexity. PostQF is an alternative
specifically tailored for easier access to Postfix queues.

To facilitate the use of Unix-like [pipelines](https://en.wikipedia.org/wiki/Pipeline_%28Unix%29), PostQF usually reads
from _stdin_ and writes to _stdout_. Using command line arguments, you can override this behaviour and define one or
more input files and/or an output file. Depending on the context, a horizontal dash `-` represents either _stdin_ or
_stdout_. See the command line usage description below.

## Filters

Queue entries can be easily filtered by

* Queue name
* Sender address
* Recipient address
* Delay reason

and combinations thereof, using
[regular expressions](https://docs.python.org/3/library/re.html#regular-expression-syntax). Anchoring is optional,
meaning that plain text is treated as a substring pattern.

## Example usage

Find all messages in the _deferred_ queue where the delay reason contains the string _connection timed out_.

```bash
postqueue -j | postqf -q deferred -d 'connection timed out'
```

Find all messages in the _active_ or _hold_ queues which have at least one recipient in the _example.com_ or
_example.org_ domains, and write the matching JSON records into the file _/tmp/output_.

```bash
postqueue -j | postqf -q 'active|hold' -r '@example\.(com|org)' -o /tmp/output
```

Find all messages all queues for which the sender address is _alice@gmail.com_ or _bob@gmail.com_, and pipe the queue
IDs to _postsuper_ in order to place the matching messages on hold.

```bash
postqueue -j | postqf -s '^(alice|bob)@gmail\.com$' -i | postsuper -h -
```

## Command line usage

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

## Installation

The only installation requirement is Python 3.7 or newer. PostQF is distributed via
[PyPI.org](https://pypi.org/project/postqf/) and can usually be installed using _pip_. If this fails, or if both Python
2.x and 3.x are installed on your machine, use _pip3_ instead.

If possible, use the recommended installation with a Python virtual environment. Site-wide installation usually requires
root privileges.

```bash
# Recommended: Installation using a Python virtual environment.
mkdir ~/postqf
cd ~/postqf
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip postqf
```

```bash
# Alternative: Site-wide installation, requires root access.
sudo pip install postqf
```

The _pip_ installation process adds a launcher executable `postqf`, either site-wide or in the Python virtual
environment. In the latter case, the launcher will be placed into the directory `.venv/bin` which is automatically added
to your PATH variable when you activate the venv environment as shown above.

## Contact

The project is hosted on GitHub in the [rseichter/postqf](https://github.com/rseichter/postqf) repository. If you have
suggestions or run into any problems, please use the [issue tracker](https://github.com/rseichter/postqf/issues). The
[build configuration](https://github.com/rseichter/postqf/blob/master/setup.cfg) file contains a contact email address. 