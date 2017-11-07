#!/usr/bin/env python2
# coding:utf-8

"""
Script to generate PDF with words
"""

# python3 compatibility
from __future__ import print_function
from __future__ import division

import sys
from os.path import exists, basename, dirname, split, realpath, splitext
from os import listdir
from glob import glob
import re

from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import A4, landscape

########################## Variables here can be adjusted ###################
LINE_X_MARGIN = 10
FOOTER_VPOS = 12
FOOTER_HPOS = 20
SITE_URL = "Accelerated Growth by Michal Juhas"
URL_WIDTH = 120

FONT = 'Helvetica'
WORDS_HEIGHT = 200
BOTTOM_MARGIN = 30
SIDE_MARGIN = 20

TITLE_TOP_MARGIN = 150
TITLE_FONT = 'Times-Roman' # just for test
TITLE_FONT_SIZE = 80
######################### do not change the program below this line #########



THIS = sys.modules[__name__]
THIS.DEBUG = True


def to_stderr(out, prefix='ERROR'):
    """
    common function to write to stderr (no more prints!)
    """
    if not isinstance(out, (list, tuple)):
        out = [out]
    sys.stderr.write(prefix + ': ' + ' '.join((str(x) for x in out)) + '\n')


def error(*out):
    """
    Print error message and quit, cannot continue
    """
    to_stderr(out)
    sys.exit(1)


def warning(*out):
    """
    Print warning message and continue execution
    """
    to_stderr(out, prefix='WARNING')


def debug(*out):
    """
    Verbose messages about internal state, not really debugging, more like logging
    """
    if THIS.DEBUG:
        to_stderr(out, prefix='DEBUG')


def add_footer(canv, nset, pagenum):
    """
    Return 'text' object
    """

    footerright = SITE_URL
    canv.setFont('Helvetica', 12)
    canv.setLineWidth(.3)
    canv.setFillGray(0.8)

    canv.drawRightString(A4[1] - FOOTER_HPOS, FOOTER_VPOS, footerright)


def add_generated_page(canv, threewords, nset, pagenum):
    """
    Returns nothing
    footer is 'text' object
    """
    part = 1
    third = A4[0] / 3
    canv.setFillGray(0.0)
    for word in threewords:
        canv.setLineWidth(.3)
        this_word_height = WORDS_HEIGHT
        # try to find optimal font height to fit page width
        while True:
            wordwidth = canv.stringWidth(word, FONT, this_word_height)
            if wordwidth < A4[0] - SIDE_MARGIN * 2:
                break
            this_word_height *= 0.9
        canv.setFont(FONT, this_word_height)
        canv.drawCentredString(A4[1] / 2, BOTTOM_MARGIN + (third - this_word_height) / 2 \
                                          + third * part, word)
        part -= 1
    add_footer(canv, nset, pagenum)

    # add page to PDF
    canv.showPage()


def get_title(filename, nset):
    """
    Trying to determine [Lang].. from file name

    """
    tokens = filename.split('/')

    for token in tokens:
        if re.match('[A-Z]{2}$', token):
            language = token
    title = splitext(basename(filename))[0].replace('-', ' ')
    return title


def add_metadata(canv, title):
    """
    TODO: need to determine Author
    """
    canv.setAuthor(SITE_URL)
    canv.setTitle(title)


def generate_title_page(canv, title):
    """
    Just a simple page with the set name (same as you have in the footer)
    """
    height, width = A4 # landscape

    canv.setStrokeGray(0.6)
    canv.line(LINE_X_MARGIN, height / 2, width - LINE_X_MARGIN, height / 2)
    # put division -> category -> ...
    if title:
        canv.setPageSize(landscape(A4))
        canv.setStrokeGray(0)
        canv.setFont(TITLE_FONT, TITLE_FONT_SIZE)
        canv.drawCentredString(width / 2, height / 2 - TITLE_TOP_MARGIN, title)
    canv.showPage()


def generate_pdf(wordlist, outfname, nset, title=None):
    """
    Return nothing
    Creates multiple-pages PDF
    """
    canv = canvas.Canvas(outfname)

    if title:
        add_metadata(canv, title + ' — ' + SITE_URL)
    generate_title_page(canv, title)
    pagenum = 1

    canv.setPageSize(landscape(A4))

    for i in range(0, len(wordlist), 1):
        threew = wordlist[i : i + 1]
        add_generated_page(canv, threew, nset, pagenum)
        pagenum += 1
    canv.save()
    print(outfname, 'saved')


def find_output_root_dir():
    """
    Try to find Output directory
    """
    main_dir = split(dirname(realpath(sys.argv[0])))[0]
    debug('Should be main Output directory:', main_dir + '/Output')
    out_dir = main_dir + '/Output'
    if not exists(out_dir):
        error('Cannot find output directory "%s"' % out_dir)
    return out_dir


def find_input_root_dir():
    """
    Try to find Input directory from script location
    """
    maindir = split(dirname(realpath(sys.argv[0])))[0]
    debug('Should be main Input directory:', maindir + '/Input')
    inputdir = maindir + '/Input'
    if not exists(inputdir):
        error('Cannot find input directory %s' % inputdir)
    return inputdir


def main():
    """
    Called when not imported as module, also see first line ("shebang")
    """
    root_dir = find_input_root_dir()
    if len(sys.argv) > 1:
        places = ["%s/%s" % (root_dir, x) for x in sys.argv[1:]]
    else:
        places = ["%s/%s" % (root_dir, x) for x in listdir(root_dir)]
    debug('input directories:' + str(places))
    out_dir = find_output_root_dir()
    for langdir in places:
        lang = basename(langdir)
        for fname in glob(langdir + '/*.txt'):
            name = basename(fname)
            if '-' not in name:
                warning('incompatible text file name "%s", '
                        'should be "NN-something.txt", skipping' % name)
                continue
            nset = int(name[:name.index('-')])
            title = get_title(fname, nset)
            f = open(fname, 'rt')
            words = []
            for word in f.read().split():
                words.append(word)
            outname = '%s/%s-%s.pdf' % (out_dir, lang, name[:-4])
            generate_pdf(words, outname, nset, title)


if __name__ == "__main__":
    main()
