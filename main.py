#!/usr/bin/env python
import pdb

# External modules
import untangle


class FormatException(Exception):
    def __init__(self):
        super().__init__(self)

def write_front_matter(fp, tags):
    pass


def load_keywords(sheet):
    tags = []
    if sheet.attachment['type'] == 'keywords':
        tags = sheet.attachment.cdata.split(',')
    return tags


def load_sheet(filename):
    obj = untangle.parse(filename)
    print(dir(obj.sheet))
    print(obj.sheet.attachment)
    print(obj.sheet.markup)
    pdb.set_trace()
    tags = load_keywords(obj.sheet)
    if obj.sheet.markup["identifier"] != 'markdownl':
        raise FormatException(f"Don't understand format {obj.sheet.markup.identifier}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = load_sheet("Content.xml")

