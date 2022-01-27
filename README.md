# PostQF

<sup>Copyright © 2022 Ralph Seichter</sup>

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

### Time based filters

Arrival time filters do not use regular expressions, but support the following formats instead:

1. [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) time strings.
2. [Unix time](https://en.wikipedia.org/wiki/Unix_time) (the number of seconds since January 1, 1970). This is the
   representation of arrival time returned in JSON-format Postfix queue data.
3. Time difference, expressed as one or more digits followed by a single "unit" character _s, m, h,_ or _d_. These units
   designate seconds, minutes, hours and or days. The resulting timestamp will be in the past, as in "now minus the
   difference".

Please keep in mind that formats 1 and 2 are used for fixed timestamps, while format 3 represents time differences
against the time of running PostQF. When format 3 is used with static input data (say, JSON data you saved to disk
sevaral days ago) the results may vary as time progresses. When in doubt, use absolute time formats.

The command line option `-a X` means "message arrived after time **X**", and `-b Y` means "message arrived before
time **Y**". The filter string can have any of the supported formats, and you can mix them freely. Here are some
examples of valid command line arguments:

* `-a 2022-01-23T08:30 -b 2022-01-23T17:45` January 23, 2022 between 08:30 and 17:45.
* `-a 1642923000 -b 1642956300` The same time interval, specified in Unix time.
* `-a 90m` Less than 90 minutes ago.
* `-b 36h` More than 36 hours ago.

## Command line usage

```
postqf [-h] [-i] [-d [REGEX]] [-q [REGEX]] [-r [REGEX]] [-s [REGEX]]
       [-a [TS]] [-b [TS]] [-o [PATH]] [PATH [PATH ...]]

positional arguments:
  PATH        Input file. Use a dash "-" for standard input.

optional arguments:
  -h, --help  show this help message and exit
  -i          ID output only.
  -o [PATH]   Output file. Use a dash "-" for standard output.

Regular expression filters:
  -d [REGEX]  Delay reason filter.
  -q [REGEX]  Queue name filter.
  -r [REGEX]  Recipient address filter.
  -s [REGEX]  Sender address filter.

Arrival time filters:
  -a [TS]     Message arrived after TS.
  -b [TS]     Message arrived before TS.
```

## Installation

The only installation requirement is Python 3.7 or newer. PostQF is distributed via
[PyPI.org](https://pypi.org/project/postqf/) and is typically installed using either _pip_ or _pip3_, depending on your
Python distribution.

I also provide an installer script as an alternative. It will download the latest PostQF release into the current
directory, and generate an executable launcher. A small disadvantage of this method is that it will not check if you
have a supported Python version installed.

```bash
# Typical: Installation using 'pip'.
pip install postqf
```

The _pip_ installation process also adds a `postqf` launcher executable. The exact location depends on your Python
distribution, and you might need to modify your PATH environment variable for easy access.

```bash
# Alternative: Official installation script.
mkdir ~/postqf
cd ~/postqf
# Download and run the install script. If successful, it will print a message
# similar to "You can now launch PostQF using /home/alice/postqf/postqf".
curl -fL https://github.com/rseichter/postqf/raw/master/scripts/install | bash
```

## Contact

The project is hosted on GitHub in the [rseichter/postqf](https://github.com/rseichter/postqf) repository. If you have
suggestions or run into any problems, please check the
[discussions](https://github.com/rseichter/postqf/discussions) section first. There is also an
[issue](https://github.com/rseichter/postqf/issues) tracker available, and the
[build configuration](https://github.com/rseichter/postqf/blob/master/setup.cfg) file contains a contact email address.

