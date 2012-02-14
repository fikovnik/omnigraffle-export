import os
import tempfile
import unittest
import shutil
import time
import logging

import omnigraffle_export

class OmniGraffleExportTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(OmniGraffleExportTest, self).__init__(methodName)
        self.files_to_remove = []

    def setUp(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_data', 'basic', 'test.graffle')
        self.schema = omnigraffle_export.OmniGraffleSchema(path)
        self.assertTrue(self.schema != None)

        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        for f in self.files_to_remove:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)

    def testGetCanvasList(self):
        self.assertEqual(['Canvas 1', 'Canvas 2'], self.schema.get_canvas_list())

    def testExport(self):
        tmpfile = self.genTempFileName('pdf')

        self.assertTrue(self.schema.export('Canvas 1', tmpfile))
        chksum = omnigraffle_export.checksum(tmpfile)

        self.assertFalse(self.schema.export('Canvas 1', tmpfile))
        self.assertEqual(chksum, omnigraffle_export.checksum(tmpfile))

        self.files_to_remove.append(tmpfile)

    def testExportWithForceOption(self):
        tmpfile = self.genTempFileName('pdf')

        self.assertTrue(self.schema.export('Canvas 1', tmpfile))
        chksum = omnigraffle_export.checksum(tmpfile)
        time.sleep(2)

        self.assertTrue(self.schema.export('Canvas 1', tmpfile, force=True))
        self.assertNotEqual(chksum, omnigraffle_export.checksum(tmpfile))

        self.files_to_remove.append(tmpfile)

    def testNotExportingIfNotChanged(self):
        tmpfile = self.genTempFileName('pdf')

        self.assertTrue(self.schema.export('Canvas 1', tmpfile))

        time.sleep(2)

        self.assertFalse(self.schema.export('Canvas 1', tmpfile))

        time.sleep(2)

        self.assertTrue(self.schema.export('Canvas 1', tmpfile, force=True))

        self.files_to_remove.append(tmpfile)

    def testExportAll(self):
        tmpdir = tempfile.mkdtemp()

        self.schema.export_all(tmpdir)
        self.assertTrue(os.path.exists(os.path.join(tmpdir, 'Canvas 1.pdf')))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, 'Canvas 2.pdf')))

        self.files_to_remove.append(tmpdir)

    @staticmethod
    def genTempFileName(suffix):
        tmpfile = tempfile.mkstemp(suffix='.pdf')[1]
        os.unlink(tmpfile)

        return tmpfile

if __name__ == '__main__':
    unittest.main()

