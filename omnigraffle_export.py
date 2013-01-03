#!/usr/bin/env python

import os
import sys
import optparse
import logging
import tempfile
import hashlib

from Foundation import NSURL, NSMutableDictionary
from Quartz import PDFKit
from omnigraffle import *

def export(source, target, canvasname=None, format='pdf', debug=False, force=False):

    # logging
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    # target
    target = os.path.abspath(target)

    # mode
    export_all = os.path.isdir(target)

    # determine the canvas
    if not export_all:
        # guess from filename
        if not canvasname:
            canvasname = os.path.basename(target)
            canvasname = canvasname[:canvasname.rfind('.')]

        if not canvasname or len(canvasname) == 0:
            print >> sys.stderr, "Without canvas name, the target (-t) "\
                                       "must be a directory"
            sys.exit(1)

    # determine the format
    if not export_all:
        # guess from the suffix
        if not format:
            format = target[target.rfind('.')+1:]

    if not format or len(format) == 0:
        format = 'pdf'
    else:
        format = format.lower()

    # check source
    if not os.access(source, os.R_OK):
        print >> sys.stderr, "File: %s could not be opened for reading" % source
        sys.exit(1)

    og = OmniGraffle()
    schema = og.open(source)

    if export_all:
        namemap=lambda c, f: '%s.%s' % (c, f) if f else c

        for c in schema.get_canvas_list():
            targetfile = os.path.join(os.path.abspath(target),
                                      namemap(c, format))
            logging.debug("Exporting `%s' into `%s' as %s" %
                          (c, targetfile, format))
            export_one(schema, targetfile, c, format, force)
    else:
        export_one(schema, target, canvasname, format, force)

def export_one(schema, filename, canvasname, format='pdf', force=False):
    def _checksum(filepath):
        assert os.path.isfile(filepath), '%s is not a file' % filepath

        c = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(128), ''):
                c.update(chunk)

        return c.hexdigest()

    def _checksum_pdf(filepath):
        assert os.path.isfile(filepath), '%s is not a file' % filepath

        url = NSURL.fileURLWithPath_(filepath)
        pdfdoc = PDFKit.PDFDocument.alloc().initWithURL_(url)
        
        assert pdfdoc != None
        
        chsum = None
        attrs = pdfdoc.documentAttributes()
        if PDFKit.PDFDocumentSubjectAttribute in attrs:
            chksum = pdfdoc.documentAttributes()[PDFKit.PDFDocumentSubjectAttribute]
        else:
            return None

        if not chksum.startswith(OmniGraffleSchema.PDF_CHECKSUM_ATTRIBUTE):
            return None
        else:
            return chksum[len(OmniGraffleSchema.PDF_CHECKSUM_ATTRIBUTE):]

    def _compute_canvas_checksum(canvasname):
        tmpfile = tempfile.mkstemp(suffix='.png')[1]
        os.unlink(tmpfile)

        export_one(schema, tmpfile, canvasname, 'png')

        try:
            chksum = _checksum(tmpfile)
            return chksum
        finally:
            os.unlink(tmpfile)

    # checksum
    chksum = None
    if os.path.isfile(filename) and not force:
        existing_chksum = _checksum(filename) if format != 'pdf' \
                                              else _checksum_pdf(filename)

        new_chksum = _compute_canvas_checksum(canvasname)

        if existing_chksum == new_chksum and existing_chksum != None:
            logging.debug('Not exporting `%s` into `%s` as `%s` - canvas has not been changed' % (canvasname, filename, format))
            return False
        else:
            chksum = new_chksum

    elif format == 'pdf':
        chksum = _compute_canvas_checksum(canvasname)

    try:
        schema.export(canvasname, filename, format=format)
    except RuntimeError as e:
        print >> sys.stderr, e.message
        return False

    # update checksum
    if format == 'pdf':
        # save the checksum
        url = NSURL.fileURLWithPath_(filename)
        pdfdoc = PDFKit.PDFDocument.alloc().initWithURL_(url)
        attrs = NSMutableDictionary.alloc().initWithDictionary_(pdfdoc.documentAttributes())

        attrs[PDFKit.PDFDocumentSubjectAttribute] = \
            '%s%s' % (OmniGraffleSchema.PDF_CHECKSUM_ATTRIBUTE, chksum)

        pdfdoc.setDocumentAttributes_(attrs)
        pdfdoc.writeToFile_(filename)

    return True


def main():
    usage = "Usage: %prog [options] <source> <target>"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-c',
                      help='canvas name. If not given it will be guessed from '
                      'the target filename unless it is a directory.',
                      metavar='NAME', dest='canvasname')
    parser.add_option('-f',
                      help='format (one of: pdf, png, svg, eps). Guessed '
                      'from the target filename suffix unless it is a '
                      'directory. Defaults to pdf',
                      metavar='FMT', dest='format')
    parser.add_option('--force', action='store_true', help='force the export',
                      dest='force')
    parser.add_option('--debug', action='store_true', help='debug',
                      dest='debug')

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        sys.exit(1)

    (source, target) = args

    export(source, target, options.canvasname, options.format, 
        options.debug, options.force)

if __name__ == '__main__':
    main()
