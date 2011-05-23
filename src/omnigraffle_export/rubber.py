#!/usr/bin/env python

import sys
import os
import re
import omnigraffle_export

arg_re_ = re.compile('(.*):(.*)\.(.*)')

def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Usage: %s: <path_to_omnigraffle_source>:<canvas_name>.<format>' % sys.argv[0]
        sys.exit(1)

    input = arg_re_.match(sys.argv[1])

    if len(input.groups()) != 3:
        print >> sys.stderr, 'Invalid input: %s' % sys.argv[1]
        sys.exit(2)

    source, canvas, format = input.groups()
    source = os.path.abspath(source + '.graffle')
    target = '%s/%s:%s.%s' % (os.path.dirname(source), os.path.basename(source).replace('.graffle',''), canvas, format)
    
    schema = omnigraffle_export.OmniGraffleSchema(source)
    schema.export(canvas, target, format)
    sys.exit(0)

if __name__ == '__main__':
    main()
