# PostQF

Copyright © 2022 Ralph Seichter

PostQF is a user-friendly [Postfix](http://www.postfix.org/) queue data filter which operates on data produced by
[postqueue -j](http://www.postfix.org/postqueue.1.html). See the manual page's subsection titled "JSON object format"
for details. PostQF offers convenient features for analysis and and cleanup of Postfix mail queues.

I have used the all-purpose JSON manipulation utility "jq" before, but found it inconvenient for everyday Postfix
administration tasks. "jq" offers great flexibility and handles all sorts of JSON input, but it comes at the cost of
complexity. PostQF is an alternative specifically tailored for easier access to Postfix queues.

To facilitate the use of Unix-like [pipelines](https://en.wikipedia.org/wiki/Pipeline_%28Unix%29), PostQF usually reads
from _stdin_ and writes to _stdout_. Using command line arguments, you can override this behaviour and define one or
more input files and/or an output file. Depending on the context, a horizontal dash `-` represents either _stdin_ or
_stdout_. See the command line usage description below.

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

Print the number of messages which arrived during the last 30 minutes.

```bash
postqueue -j | postqf -a 30m | wc -l
```

The final example assumes a directory `/tmp/data` with several files, each containing JSON output produced at some
previous time. The command pipes all queue IDs which have ever been in the _hold_ queue into the file _idlist_, relying
on BASH wildcard expansion to generate a list of input files.

```bash
postqf -i -q hold /tmp/data/*.json > idlist
```

## Filters

Queue entries can be easily filtered by

* Arrival time
* Delay reason
* Queue name
* Recipient address
* Sender address

and combinations thereof, using
[regular expressions](https://docs.python.org/3/library/re.html#regular-expression-syntax). Anchoring is optional,
meaning that plain text is treated as a substring pattern.

The arrival time filters do not use regular expressions, but instead a human-readable representation of a time
difference. The format is **W unit**, without spaces. **W** is a "whole number" (i.e. an number ≥ 0). The **unit** is a
single letter among _s, m, h, d_ (seconds, minutes, hours, days).

`-b 3d` and `-a 90m` are both examples of valid command line arguments. Note that arrival filters are interpreted
relative to the time PostQF is run. The two examples signify "message arrived more than 3 days ago" (before timestamp)
and "message arrived less than 90 minutes ago" (after timestamp), respectively.

## Command line usage

```
postqf [-h] [-i] [-d [REGEX]] [-q [REGEX]] [-r [REGEX]] [-s [REGEX]]
       [-a [TS] | -b [TS]] [-o [PATH]] [PATH [PATH ...]]

positional arguments:
  PATH        Input file. Use a dash "-" for standard input.

optional arguments:
  -h, --help  show this help message and exit
  -i          ID output only
  -o [PATH]   Output file. Use a dash "-" for standard output.

Regular expression filters:
  -d [REGEX]  Delay reason filter
  -q [REGEX]  Queue name filter
  -r [REGEX]  Recipient address filter
  -s [REGEX]  Sender address filter

Arrival time filters (mutually exclusive):
  -a [TS]     Message arrived after TS
  -b [TS]     Message arrived before TS

postqf 0.1 Copyright © 2022 Ralph Seichter
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
suggestions or run into any problems, please check the
[discussions](https://github.com/rseichter/postqf/discussions) section first. There is also an
[issue](https://github.com/rseichter/postqf/issues) tracker available, and the
[build configuration](https://github.com/rseichter/postqf/blob/master/setup.cfg) file contains a contact email address.
