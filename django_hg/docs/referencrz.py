#!/usr/bin/env python
# coding=utf-8
"""
This a quick manual generator written as Sphinx was broken on my computer. So I
decide to write a this script that converts a Markdown file to an HTML file.

This script looks for files in a "source" directory and converts them in
HTML in a "build" directory, decorated with the HTML code that is located in the
"template/base.html" subfolders.
The replacement method uses Python formatting capacities (pre Python 2.6)

Currently the script doesn't support subfolders nor file ordering that differs
from os order.

This script requires py-markdown. I don't know if py-markdown2 is supported

@todo subfolders browsing and ordering capabilities
@todo handle breadcrumb and TOC
@todo convert the script to a class so we can remove the global template variable
"""
import os.path
import codecs
import markdown
import HTMLParser
import re

#settings
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

build_path = PROJECT_PATH + '/build'
source_path = PROJECT_PATH + '/source'
template_file = PROJECT_PATH + '/templates/base.html'

def browse():
    """
    Browse the "source" directory
    """
    dir_list = os.listdir(source_path)
    for file_name in dir_list:
        if not (file_name.startswith('.') or file_name.startswith('_')) :
            convert(file_name)
    print 'Markdown files successfully converted to HTML'


def convert(file_name) :
    """
    Do the actual conversion. We open the markdown file, convert it to HTML and
    place it into the template
    """
    global template
    input_file = codecs.open(source_path + '/' + file_name,
                             mode="r",
                             encoding="utf8")
    text = input_file.read()
    content = markdown.markdown(text, ['codehilite', 'toc']) #, extensions
    #toc = build_toc(content)

    build_name = file_name[0:file_name.rfind('.')]
    html = template % {'title': build_name.capitalize(), 'content': content}

    output_file = codecs.open(build_path + '/' + build_name + '.html',
                              "w",
                              encoding="utf8")
    output_file.write(html)

def init():
    """
    Do some checks before trying to run the conversion. This function also inits
    the template
    """
    try:
        os.listdir(source_path)
    except(OSError):
        print('Unable to find the source directory')
    try:
        os.listdir(build_path)
    except(OSError):
        print('Unable to find the build directory')
    try:
        open(template_file, 'r')
    except(OSError):
        print('Unable to find the template file')
    initialize_template()
    browse()

def initialize_template():
    """
    Replace template blocks with Python formatting
    """
    global template
    blocks = ['title', 'content']
    template = open(template_file, 'r').read()
    for block in blocks:
        template = template.replace('{{' + block + '}}', '%(' + block + ')s')

    return template

init()
