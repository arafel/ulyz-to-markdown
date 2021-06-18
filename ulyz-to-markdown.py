#!/usr/bin/env python
import os.path
import sys
import logging
import zipfile

# External modules
from glob import glob

import bs4
from unidecode import unidecode

logger = logging.getLogger()


class FormatException(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)


def load_keywords(sheet):
    keywords = []
    attachments = sheet.find_all("attachment")
    for attachment in attachments:
        if attachment['type'] == 'keywords':
            keywords = attachment.text.split(',')
            break
    return keywords


def load_tag_definitions(sheet):
    tags = {}
    tag_definitions = sheet.markup.find_all('tag')
    logger.info(f"Processing {len(tag_definitions)} tag definitions")
    for tag in tag_definitions:
        if tag.has_attr('pattern'):
            tags[tag['definition']] = tag['pattern']
        elif tag.has_attr('startPattern'):
            tags[tag['definition']] = {'startPattern': tag['startPattern'], 'endPattern': tag['endPattern']}
        else:
            raise Exception(f"Unknown tag format {tag}")
    return tags


def process_tags(root_tag, tags):
    frags = []
    logger.debug("Processing tags", root_tag)
    for tag in root_tag:
        if tag.has_attr('kind'):
            kind = tag['kind']
            frags.append(tags.get(kind, ''))
        else:
            frags.append(tag.text)

    return ' '.join(frags)


def process_element(el, tags):
    frags = []
    kind = el['kind']
    logger.debug(f"Processing {kind} element")
    tag = tags[kind]
    return tag['startPattern'] + el.text + tag['endPattern']


def load_paragraphs(sheet, tags):
    out_paras = []
    in_paras = sheet.find('string').find_all('p')
    logger.info(f"Document has {len(in_paras)} line(s)")
    for line in in_paras:
        logging.debug("Line:", line)
        frags = []
        for child in line.children:
            logger.debug(f"Child: {child} ({child.name})")
            if child.name == 'tags':
                frags.append(process_tags(child, tags))
            elif child.name == 'element':
                frags.append(process_element(child, tags))
            elif child.name is None:
                frags.append(child.strip())
            else:
                raise Exception("Unhandled child", child)

        logger.debug("Frags", frags)
        out_line = ' '.join(frags) + "\n"
        logger.debug("Built", out_line)
        out_line = unidecode(out_line)
        # out_line = html.escape(out_line)
        out_paras.append(out_line)

    return out_paras


def load_sheet(fp):
    obj = bs4.BeautifulSoup(fp, 'xml')
    keywords = load_keywords(obj.sheet)
    tags = load_tag_definitions(obj.sheet)
    paras = load_paragraphs(obj.sheet, tags)
    return {
        'front_matter': {'tags': keywords},
        'text': paras
    }


# Press the green button in the gutter to run the script.
def write_markdown(fn, data):
    with open(fn, "w") as fp:
        fm = data.get("front_matter", None)
        text = data.get('text')
        if fm:
            tags = fm.get("tags", None)
            fp.write('---\n')
            fp.write("keywords: " + ", ".join(tags) + "\n")
            fp.write('---\n\n')
        fp.writelines(text)


def find_zipfile_member(zf):
    nl = zf.namelist()
    files = [filename for filename in nl if os.path.split(filename)[1] == 'Content.xml']
    assert(len(files) == 1)
    return files[0]


def open_file(filename):
    fn, ext = os.path.splitext(filename)
    if ext == '.xml':
        fp = open(filename)
    elif ext == '.ulyz':
        zf = zipfile.ZipFile(filename)
        zip_member = find_zipfile_member(zf)
        fp = zf.open(zip_member)
    else:
        raise FormatException(f"Unknown format {filename}")

    return fp


def process_file(in_fn, out_fn):
    data = None
    try:
        zf = None
        logger.info("Loading", in_fn)
        fp = open_file(in_fn)
        data = load_sheet(fp)
        if zf:
            zf.close()
    except FileNotFoundError as e:
        logger.exception("Error loading file", e)
        return

    try:
        logger.info("Saving", out_fn)
        write_markdown(out_fn, data)
    except (FileNotFoundError, OSError) as e:
        logger.exception("Error writing file", e)


def make_output_filename(in_fn, outdir=None):
    # Break it apart...
    logger.debug("make_output_filename - in_fn", in_fn)
    directory, fn = os.path.split(in_fn)
    logger.debug(f"Broke into {directory} {fn}")
    if outdir:
        directory = outdir
    filebase, ext = os.path.splitext(fn)
    logger.debug(f"Broke into {filebase} {ext}")
    # ... then glue it back together.
    return os.path.join(directory, f"{filebase}.md")


def run(args):
    if len(args) < 2:
        print(f"Usage: {args[0]} input [output]")
        print("")
        print("Input can be a file or a directory. The program will convert XML and .ulyz files.")
        print("If output is present:")
        print()
        print("- if input is a directory, output files will be written into this directory")
        print("- if input is a file, this will be used as the output filename")
        sys.exit(1)

    if os.path.isdir(args[1]):
        print("Loading files from", args[1])
        outdir = None
        if len(args) == 3:
            outdir = args[2]
            print(f"Using {outdir} as output directory")

        filenames = glob(os.path.join(args[1], "*.ulyz"))
        filenames.extend(glob(os.path.join(args[1], "*.xml")))
        for in_fn in filenames:
            out_fn = make_output_filename(in_fn, outdir)
            process_file(in_fn, out_fn)
    else:
        in_fn = args[1]
        if len(args) == 3:
            out_fn = args[2]
        else:
            out_fn = make_output_filename(in_fn)
        process_file(in_fn, out_fn)


if __name__ == '__main__':
    run(sys.argv)