#from xml.etree.ElementPath
import datetime
import subprocess
import lxml.etree as etree
import json

from optparse import OptionParser


class WP_Importer(object):
    '''Wordpress Importer'''

    def __init__(self, filename, do_convert):
        self.filename = filename
        self.do_convert = do_convert

    def convert_To_Rst(self, html):
        '''Converts html to Rst'''
        p = subprocess.Popen(['pandoc', '--from=html', '--to=rst'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate(unicode(html).encode('utf-8'))
#        if stderr != "":
#            print 'ERROR CONVERTING THE FOLLOWING TO RST :'
#            print 'ATTEMPTING TO CONVERT : %s' % html[0:80]
#            print 'ERROR: %s' % stderr
        return stdout

    def parse(self):
        data = etree.parse(self.filename)
        root = data.find("channel")
        blog = {
            'title': root.findtext('title'),
            'description': root.findtext('description'),
            'link': root.findtext('link'),
        }

        # Categories
        cats = root.findall('{http://wordpress.org/export/1.1/}category')
        categories = []
        for c in cats:
            categories.append({
                'name': c.findtext('{http://wordpress.org/export/1.1/}cat_name'),
                'nice_name': c.findtext('{http://wordpress.org/export/1.1/}category_nicename'),
                'parent': c.findtext('{http://wordpress.org/export/1.1/}parent')
            })
        # Tags
        tags = []
        tagElements = root.findall('{http://wordpress.org/export/1.1/}tag')
        for t in tagElements:
            tags.append({
                'name': t.findtext('{http://wordpress.org/export/1.1/}tag_name'),
                'tag_slug': t.findtext('{http://wordpress.org/export/1.1/}tag_slug')
            })
        # posts
        posts = []
        for post in data.findall("channel/item"):
            p = {
                'id': post.findtext('{http://wordpress.org/export/1.1/}post_id'),
                'title': post.findtext('title'),
                'name': post.findtext('{http://wordpress.org/export/1.1/}post_name'),
                'link': post.findtext('link'),
                'creator': post.findtext('{http://purl.org/dc/elements/1.1/}creator'),
                'categories': dict([(c.findtext("."), "") for c in post.findall("category[@domain='category']")]).keys(),
                'tags': dict([(c.findtext("."), "") for c in post.findall("category[@domain='post_tag']")]).keys(),
                'description': post.findtext('description'),
                'content': post.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') if not self.do_convert else self.convert_To_Rst(post.findtext('{http://purl.org/rss/1.0/modules/content/}encoded')),
                'post_date': datetime.datetime.strptime(post.findtext('{http://wordpress.org/export/1.1/}post_date'), "%Y-%m-%d %H:%M:%S").strftime("%Y/%m/%d %H:%M:%SZ"),
                'status': post.findtext('{http://wordpress.org/export/1.1/}status'),
                'comments': []
            }
            comments = []
            # post comments
            post_comments = post.findall('{http://wordpress.org/export/1.1/}comment')

            if (len(post_comments)):
                for c in post_comments:
                    cmt = {
                        'author': c.findtext('{http://wordpress.org/export/1.1/}comment_author'),
                        'author_email': c.findtext('{http://wordpress.org/export/1.1/}comment_author_email'),
                        'author_url': c.findtext('{http://wordpress.org/export/1.1/}comment_author_url'),
                        'author_ip': c.findtext('{http://wordpress.org/export/1.1/}comment_author_IP'),
                        'post_date': datetime.datetime.strptime(c.findtext("{http://wordpress.org/export/1.1/}comment_date_gmt"),"%Y-%m-%d %H:%M:%S").strftime("%Y/%m/%d %H:%M:%SZ"),
                        'content': c.findtext('{http://wordpress.org/export/1.1/}comment_content') if not self.do_convert else self.convert_To_Rst(c.findtext('{http://wordpress.org/export/1.1/}comment_content'))
                    }
                    comments.append(cmt)
                p['comments'] = comments
            posts.append(p)

        blog['categories'] = categories
        blog['tags'] = tags
        blog['posts'] = posts

        return blog


def save_to_json(o, filename, append=False):
    """Saves python object to json, optionally appending to specified filename"""
    writemode = 'w' if not append else 'a'
    with open(filename, writemode) as f:
        json.dump(o, sort_keys=True, indent=4, fp=f)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", '--file', dest='filename', help='Wordpress export xml file', metavar="FILE")
    parser.add_option("-o", '--outfile', dest='outfilename', help='Filename to save output to (JSON)', metavar="OUTFILE")
    parser.add_option("-c", '--convert', dest='convert', help='perform conversion to RestructedText', action="store_true", default=False)
    parser.add_option("-s", '--split-output', dest='split', help='Split data into separate files eg categories.json, tags.json, posts.json', action="store_true", default=False)
    parser.add_option("-d", '--dry-run', dest='dryrun', help='Performs a dry run, will not save any output', action="store_true", default=False)

    (options, args) = parser.parse_args()

    if options.filename != None:
        print "Parsing Wordpress export xml file : %s " % options.filename
        print "--"
        i = WP_Importer(options.filename, options.convert)
        blog = i.parse()
        print 'Number of tags found: %s ' % str(len(blog['tags']))
        print 'Number of categories found: %s ' % str(len(blog['categories']))
        print 'Number of posts found: %s ' % str(len(blog['posts']))
        print "--"
        if options.outfilename:
            if options.split:
                categories = blog['categories']
                tags = blog['tags']
                posts = blog['posts']
                del blog['categories']
                del blog['tags']
                del blog['posts']
                save_to_json(blog, options.outfilename.replace('.json', '-blog.json'), False)
                save_to_json(categories, options.outfilename.replace('.json', '-categories.json'), False)
                save_to_json(tags, options.outfilename.replace('.json', '-tags.json'), False)
                save_to_json(posts, options.outfilename.replace('.json', '-posts.json'), False)
            else:
                save_to_json(blog, options.outfilename, False)
    else:
        parser.print_help()
        exit()
