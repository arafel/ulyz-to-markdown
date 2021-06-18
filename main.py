#!/usr/bin/env python
import sys
import logging

# External modules
import bs4
from unidecode import unidecode

logger = logging.getLogger()


class FormatException(Exception):
    def __init__(self):
        super().__init__(self)


def load_keywords(sheet):
    keywords = []
    attachments = sheet.find_all("attachment")
    for attachment in attachments:
        if attachment['type'] == 'keywords':
            keywords = attachment.text.split(',')
            break
    return keywords


def load_tags(sheet):
    tags = {}
    tag_defs = sheet.markup.find_all('tag')
    logger.info(f"Processing {len(tag_defs)} tag definitions")
    for tag in tag_defs:
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
        logger.debug("Line:", line)
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


def load_sheet(filename):
    with open(filename, "r") as fp:
        obj = bs4.BeautifulSoup(fp, 'xml')

    keywords = load_keywords(obj.sheet)
    tags = load_tags(obj.sheet)
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input output")
        sys.exit(1)

    in_fn = sys.argv[1]
    out_fn = sys.argv[2]

    try:
        print("Loading", in_fn)
        data = load_sheet(in_fn)
    except FileNotFoundError as e:
        logger.exception("Error loading file", e)
        sys.exit(0)

    try:
        print("Saving", out_fn)
        write_markdown(out_fn, data)
    except (FileNotFoundError, OSError) as e:
        logger.exception("Error writing file", e)