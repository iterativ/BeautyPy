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
# date on Mar 23, 2012
# @author: github.com/maersu

import os
import time
from string import Template

class SourceHandler():
    def __init__(self, rootpath, dry=False):
        self.rootpath = rootpath
        self.dry = dry
        self.meta_handlers = [GitHandler, HgHandler, BaseMetaHandler]
        
        if self.dry:
            print 'Dry run!'
        
    def _find_sourcefiles(self, start_dir, source_ext):
        sources = []        
        if source_ext[0] != '.':
            source_ext = '.%s' % source_ext
        
        def _find(arg, dirname, names):
            for name in names:
                if (name.endswith(source_ext)):
                    sources.append(os.path.join(dirname, name))
        os.path.walk(start_dir, _find, None)
        return sources
    
    def get_file_metas(self, source_ext):
        sources = self._find_sourcefiles(self.rootpath, source_ext)
        
        for handler in self.meta_handlers:
            h = handler(self.rootpath)
            method = h.method
            try:
                print "Get Metainformation with '%s' ..." % method
                return h.get_file_metas(sources)
            except Exception, e:
                print "\tNot working with '%s'. try fallback" % method
                pass

    def set_header(self, source_ext, template, comment):
        
        metas = self.get_file_metas(source_ext)
        
        if os.path.isfile(template):
            template = open(template, 'r').read()
        
        template = Template(template)
        import codecs
        for meta in metas:
            filepath = meta['file']
                        
            if os.path.isfile(filepath):
                content = unicode(template.substitute(**meta))
                old_header = True
                
                for line in codecs.open(filepath, 'r', "utf-8"):
                    
                    if old_header and line[0] in [comment, '\n']:
                        pass
                    else:
                        old_header = False
                        content += unicode(line)
                
                if self.dry == False:
                    open(filepath, 'w').write(content.encode('UTF-8'))

        return len(metas)          
       
class BaseMetaHandler(object):

    method = 'Os'

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def _init_ctx(self, filepath):
        return {'date': '', 'author': '', 'file': filepath, 'year': ''}

    def _secs_to_str(self, secs):
        t = time.localtime(secs)
        
        return {'date': time.strftime("%b %d, %Y", t), 
                'year': time.strftime("%Y", t)}

    def get_file_metas(self, source_files):
        files = []
        import getpass
        user = getpass.getuser()
        for afile in source_files:
            fdict = self._init_ctx(afile)
            fdict['author'] = user
            fdict.update(self._secs_to_str(os.path.getctime(afile)))
            files.append(fdict)
        return files

class GitHandler(BaseMetaHandler):

    method = 'git'

    def get_file_metas(self, source_files):
        import git
        self.repo = git.Repo(self.rootpath) 
        files = []
        for afile in source_files:
            idx = 0
            fdict = self._init_ctx(afile)  
            authors = []
            for commit in self.repo.iter_commits(paths=afile):
                if idx == 0:
                    fdict.update(self._secs_to_str(commit.authored_date))
                user = commit.author.name
                if commit.author.email:
                    user = '%s <%s>' % (user, commit.author.email)
                authors.append(user)
                idx += 1

            fdict['author']  = ', '.join(set(authors))
            files.append(fdict)    
 
        return files

class HgHandler(BaseMetaHandler):

    method = 'hg'

    def get_file_metas(self, source_files):
        
        from mercurial import ui, hg
        from mercurial.context import changectx, filectx
        self.repo = hg.repository(ui.ui(), self.rootpath)
        
        files = []
        
        cctx = changectx(self.repo)
        for afile in source_files:
            idx = 0
            fdict = self._init_ctx(afile)
            authors = []
            fctx = filectx(self.repo, afile.replace(self.rootpath,''), changectx=cctx)
            idx = 0
            
            for id in fctx.filelog():
                fctx_parent = fctx.filectx(id)
                if idx == 0:
                    fdict.update(self._secs_to_str(fctx_parent.date()[0]))
                authors.append(fctx_parent.user())
                idx += 1

            fdict['author']  = ', '.join([u for u in set(authors) if u != self.method])
            files.append(fdict)
            
        return files
