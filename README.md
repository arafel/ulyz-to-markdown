# Ulysses to Markdown

I like using the Ulysses app for writing. However, while you write in Markdown in the app, exporting seems to be limited
to HTML, Doc, ePub etc. I couldn't find a way to export to simple Markdown.

So I wrote one.

## Setting up an environment

The easiest way to install the required packages without conflicting with anything else on your machine is to use a
virtual environment. It's easy to set up, assuming you have a `python3` binary available:

```
python3 -m venv envdir
source envdir/bin/activate
# We're now using Python from the virtual environment, so we get python 3 when we run 'python'
pip install wheel
pip install -r requirements.txt
```

To go back to using the 'normal' version of Python in that terminal, you can just run `deactivate`. (Or just close the terminal.)

You'll need to use the `source envdir/bin/activate` command each time you start a new Terminal and want to run the
script.  You won't need to install packages each time, that's just a one-off.

## Required packages

The following Python packages are required:

* BeautifulSoup 4
* lxml
* unidecode 

In most cases `pip install -r requirements.txt` should do it. 

You should then be able to run without an error:

```
$ ./ulyz-to-markdown.py
Usage: ./ulyz-to-markdown.py input [output]

[etc]
```

## Getting your sheets into the filesystem
* Open Finder
* Open Ulysses
* Drag the sheet(s) you want to the Finder window

## Processing the sheets

`ulyz-to-markdown` has one required parameter and one optional one.

### Input

Input is the required parameter.

`ulyz-to-markdown` will accept three kinds of input:

* a `.ulyz` file
* a `Contents.xml` file extracted from a `.ulyz` file
* an input directory - it will search for `*.ulyz` and `*.xml' files.

### Output

If the input is a single file, the output parameter is used as the output filename.

If the input is a directory, the output parameter is used as an output directory. It must exist before running, the script won't create it.

## Problems?

### SyntaxError: invalid syntax

If you see this error on a line with something like:

```
f"A string with {something in curly braces}"
```

Then this usually means you're trying to run using Python 2.  The script will run using the command 'python', which on
some systems (including macOS) is Python 2:

```
$ python --version
Python 2.7.18
```

You probably have `python3` in your path (try `python3 --version`). If you do then see the `environment` section above.
If not, see [the Python website](https://www.python.org/).
