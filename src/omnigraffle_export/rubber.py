#!/usr/bin/env python

import sys
import os
import re
import omnigraffle_export

arg_re_ = re.compile('(.*):(.*)\.(.*)')

def export_one(input):
    input = arg_re_.match(input)

    if len(input.groups()) != 3:
        print >> sys.stderr, 'Invalid input: %s' % sys.argv[1]
        sys.exit(2)

    source, canvas, format = input.groups()
    source = os.path.abspath(source + '.graffle')
    target = '%s/%s:%s.%s' % (os.path.dirname(source), 
                              os.path.basename(source).replace('.graffle',''), 
                              canvas, format)
    
    schema = omnigraffle_export.OmniGraffleSchema(source)
    schema.export(canvas, target, format)
    
    sys.exit(0)

def export_all(source, targetdir, format):
    base_source = os.path.basename(source)
    nameprefix = base_source[:base_source.rindex('.graffle')]
    
    schema = omnigraffle_export.OmniGraffleSchema(source)
    schema.export_all(targetdir, format, True, lambda n: '%s:%s.pdf' % (nameprefix, n))
    
    sys.exit(0)    

def main():
    if len(sys.argv) not in [2,4]:
        name = os.path.basename(sys.argv[0])
        print >> sys.stderr, 'Usage: %s <path_to_omnigraffle_source>:<canvas_name>.<format>' % name
        print >> sys.stderr, '         exports one canvas\n'
        print >> sys.stderr, '       %s <path_to_omnigraffle_source> <output_directory> <format>' % name
        print >> sys.stderr, '         exports all canvases to output_directory'
        sys.exit(1)

    if len(sys.argv) == 2:
        export_one(sys.argv[1])
    elif len(sys.argv) == 4:
        export_all(*sys.argv[1:])
    

if __name__ == '__main__':
    main()
