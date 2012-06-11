"""
Convert wordpress json files (created by parse.py) to rstblog posts.
First argument is the posts.json file.
Currently the script uses the categories as tags. If you want to use the real
tags, see the commented line below.
"""
import sys
import os
import errno
import json
from datetime import datetime

filename = sys.argv[1]
infile = open(filename, 'r')
posts = json.loads(infile.read())

for post in posts:
    title = post[u'title']
    print 'Processing %s...' % title

    dt = datetime.strptime(post[u'post_date'], '%Y/%m/%d %H:%M:%SZ')
    path = '%s/%s/%s' % (dt.year, dt.month, dt.day)

    try:
        os.makedirs('out/%s' % path)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

    with open('out/%s/%s.rst' % (path, post[u'name']), 'w') as outfile:
        print >> outfile, 'public: yes'
        #print >> outfile, ('tags: [%s]' % ','.join(post[u'tags'])).encode('utf-8')
        print >> outfile, ('tags: [%s]' % ','.join(post[u'categories'])).encode('utf-8')
        print >> outfile
        print >> outfile, post[u'title'].encode('utf-8')
        print >> outfile, '=' * len(post[u'title'])
        print >> outfile
        print >> outfile, post[u'content'].encode('utf-8')
