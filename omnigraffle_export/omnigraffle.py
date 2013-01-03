import logging
import os

from appscript import *

class OmniGraffleSchema(object):
    """ A class that encapsulates an OmniGraffle schema file"""

    # supported formarts
    EXPORT_FORMATS = {
        "eps": "EPS",
        "pdf": "PDF",
        "png": "PNG",
        
        # FIXME
        # "svg": "SVG",
        # "tiff" : "TIFF",
        # "gif" : "GIF",
        # "jpeg" : "JPEG",
    }

    # attribute header in PDF document that contains the checksum
    PDF_CHECKSUM_ATTRIBUTE = 'OmnigraffleExportChecksum: '

    def __init__(self, og, doc):

        self.og = og
        self.doc = doc
        self.path = doc.path()

    def get_canvas_list(self):
        """
        Returns a list of names of all the canvases in the document
        """

        return [c.name() for c in self.doc.canvases()]

    def export(self, canvasname, fname, format='pdf'):
        """
        Exports one canvas named `canvasname into `fname` using `format` format.
        """

        # canvas name
        assert canvasname and len(canvasname) > 0, 'canvasname is missing'

        self.og.current_export_settings.area_type.set(k.all_graphics)

        # format
        if format not in OmniGraffleSchema.EXPORT_FORMATS:
            raise RuntimeError('Unknown format: %s' % format)

         # find canvas
        canvas = [c for c in self.doc.canvases() if c.name() == canvasname]
        if len(canvas) == 1:
            canvas = canvas[0]
        else:
            raise RuntimeError('Canvas %s does not exist in %s' %
                         (canvasname, self.doc.path()))

        # export
        self.og.windows.first().canvas.set(canvas)
        export_format = OmniGraffleSchema.EXPORT_FORMATS[format]
        # FIXME: does this return something or throw something?
        if (export_format == None):
            self.doc.save(in_=fname)
        else:
            self.doc.save(as_=export_format, in_=fname)

        logging.debug("Exported `%s' into `%s' as %s" % (canvasname, fname, format))

        # appscript.reference.CommandError: Command failed:
        # OSERROR: -50
        # MESSAGE: The document cannot be exported to the specified format.
        # COMMAND: app(u'/Applications/OmniGraffle Professional 5.app').documents[u'schemas.graffle'].save(in_=u'/Users/krikava/Documents/Research/Thesis/phd-manuscript/thesis/figures/mape-k.pdf', as_='Apple PDF pasteboard type')
        # raise RuntimeError('Failed to export canvas: %s to %s' % (canvasname, fname))

    def active_canvas_name(self):
        """
        Returns an active canvas name. The canvas that is currently selected in the the active OmniGraffle window.
        """
        window = self.og.windows.first()
        canvas = window.canvas()
        return canvas.name()

class OmniGraffle(object):

    def __init__(self):
        self.og = app('OmniGraffle 5.app')

    def active_document(self):
        self.og.activate()
        window = self.og.windows.first()
        doc = window.document()

        fname = doc.path()
        logging.debug('Active OmniGraffle file: ' + fname)

        return OmniGraffleSchema(self.og, doc)

    def open(self, fname):
        fname = os.path.abspath(fname)
        if not os.path.isfile(fname) and \
                not os.path.isfile(os.path.join(fname, "data.plist")):
            raise ValueError('File: %s does not exists' % fname)

        fname = os.path.abspath(fname)
        self.og.activate()
        doc = self.og.open(fname)

        logging.debug('Opened OmniGraffle file: ' + fname)

        return OmniGraffleSchema(self.og, doc)
