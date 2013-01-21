# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2012 ITerativ GmbH. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Created on Mar 23, 2012
# @author: github.com/maersu

import sys
import getopt
from optparse import OptionParser
from source_files import SourceHandler
SOURCE_HEADERS = [{
                   'ext': 'py',
                   'tmpl' : "# -*- coding: utf-8 -*-\n#\n# Created on ${date}\n# @author: ${author}\n\n",
                   'comment': '#'
                   },
                   {
                   'ext': 'js',
                   'tmpl' : "/*\n* Created on ${date}\n* @author: ${author}\n*/\n\n",
                   'comment': ['/*', '*', '*/']
                   },
                   {
                   'ext': 'css',
                   'tmpl' : "/*\n* Created on ${date}\n* @author: ${author}\n*/\n\n",
                   'comment': ['/*', '*', '*/'],
                   },
                   {
                   'ext': 'scss',
                   'tmpl' : "/*\n* Created on ${date}\n* @author: ${author}\n*/\n\n",
                   'comment': ['/*', '*', '*/']
                   }]

def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-d", "--dry",
                      action="store_true",
                      dest='dry_run',
                      default=False,
                      help="execute without file manipulation")   
            
    for header in SOURCE_HEADERS:
        
        parser.add_option("-%s" % header['ext'][0], "--%s"  % header['ext'],
                          action="store",
                          dest=header['ext'],
                          default=None,
                          help="Location to a template for '%s' files" % header['ext'])    
    
    (options, args) = parser.parse_args()

    # process arguments
    count = 0
    for arg in args:
        sh = SourceHandler(arg, options.dry_run)
        for header in SOURCE_HEADERS:     
            tmpl = getattr(options, header['ext'])
            
            if tmpl is None:
                tmpl = header['tmpl']
            
            count += sh.set_header(header['ext'], tmpl, header['comment'])
            
    print '%s files processed' % count

if __name__ == "__main__":
    main()