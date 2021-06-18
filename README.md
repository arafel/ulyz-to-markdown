# Ulysses to Markdown

I like using the Ulysses app for writing. However, while you write in Markdown in the app, exporting seems to be limited to HTML, Doc, ePub etc. I couldn't find a way to export to simple Markdown.

So I wrote one.

## Required packages

The following Python packages are required:

* BeautifulSoup 4
* lxml
* unidecode 

In most cases `pip install -r requirements.txt` should do it. 

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