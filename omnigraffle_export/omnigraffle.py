import logging
import os
import time

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
    TIMEOUT = 5  # timeout waiting for export to be generated in seconds
    INTERVAL = 0.05  # interval at which to check for export completion (seconds)

    def __init__(self, og, doc):

        self.og = og
        self.doc = doc
        self.path = doc.path()

    def has_export_function(self):
        return tuple(map(int, self.og.version().split('.'))[:2]) >= (7, 8)

    def sandboxed(self):
        # real check using '/usr/bin/codesign --display --entitlements - /Applications/OmniGraffle.app'
        return self.og.version()[0] >= '6'

    def get_sandbox_path(self):
        version = self.og.version()[0]
        path = os.path.expanduser(OmniGraffle.SANDBOXED_DIR % version)

        if not os.path.exists(path):
            raise RuntimeError('OmniGraffle is sandboxed but missing sandbox path: %s' % path)

        return path

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

        # format
        if format not in OmniGraffleSchema.EXPORT_FORMATS:
            raise RuntimeError('Unknown format: %s' % format)

        export_format = OmniGraffleSchema.EXPORT_FORMATS[format]

        export_path = fname
        # Is OmniGraffle sandboxed?
        if self.sandboxed():
            export_path = self.get_sandbox_path() + os.path.basename(fname)
            logging.debug('OmniGraffle is sandboxed - exporting to: %s' % export_path)

         # find canvas
        canvas = [c for c in self.doc.canvases() if c.name() == canvasname]
        if len(canvas) == 1:
            canvas = canvas[0]
        else:
            raise RuntimeError('Canvas %s does not exist in %s' %
                         (canvasname, self.doc.path()))

        # export
        self.og.windows.first().canvas.set(canvas)

        if self.has_export_function():
            # Omnigraffle 7.8+
            if (export_format == None):
                self.doc.export(scope=k.all_graphics, to=export_path)
            else:
                self.doc.export(as_=export_format, scope=k.all_graphics, to=export_path)

            # Wait for the exported file to finish generating - doc.export is asynchronous
            waited = 0
            while not os.path.exists(export_path) and waited < self.TIMEOUT:
                time.sleep(self.INTERVAL)
                waited += self.INTERVAL

        else:
            # Omnigraffle < 7.8
            self.og.current_export_settings.area_type.set(k.all_graphics)

            # FIXME: does this return something or throw something?
            if (export_format == None):
                self.doc.save(in_=export_path)
            else:
                self.doc.save(as_=export_format, in_=export_path)

        if self.sandboxed():
            os.rename(export_path, fname)
            logging.debug('OmniGraffle is sandboxed - moving %s to: %s' % (export_path, fname))

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

    SANDBOXED_DIR = '~/Library/Containers/com.omnigroup.OmniGraffle%s/Data/'

    def __init__(self):
        names = ['OmniGraffle 5.app', 'OmniGraffle Professional 5.app', 'OmniGraffle']
        self.og = None
        for name in names:
            try:
                self.og = app(name)
                break
            except (ApplicationNotFoundError):
                continue

        if self.og == None:
            raise RuntimeError('Unable to connect to OmniGraffle (%s)' % ', '.join(names))

    def active_document(self):
        self.og.activate()
        window = self.og.windows.first()
        doc = window.document()

        if doc == None:
            # this means that the active window is actually an OmniGraffle document window
            # it can be for example the license window
            # we cannot do anything
            return None

        fname = doc.path()
        if fname == None:
            fname = "Untitled"
        logging.debug('Active OmniGraffle file: ' + fname)

        return OmniGraffleSchema(self.og, doc)

    def open(self, fname):
        fname = os.path.abspath(fname)
        if not os.path.isfile(fname) and \
                not os.path.isfile(os.path.join(fname, "data.plist")):
            raise ValueError('File: %s does not exists' % fname)

        fname = os.path.abspath(fname)
        self.og.activate()

        # adhoc fix for https://github.com/fikovnik/omnigraffle-export/issues/23
        # apparently the process is sandboxed and cannot access the file
        # 16/03/2015 13:01:54.000 kernel[0]: Sandbox: OmniGraffle(66840) deny file-read-data test.graffle
        # therefore we first try to open it manually

        import subprocess
        subprocess.call(['open',fname])

        window = self.og.windows.first()
        # doc = window.document()
        doc = self.og.open(fname)

        logging.debug('Opened OmniGraffle file: ' + fname)

        return OmniGraffleSchema(self.og, doc)
