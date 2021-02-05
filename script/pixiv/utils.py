from core.util import path_format
import os


class Space(object):
    @classmethod
    def author(cls, item):
        author_path = "%s_%s" % (item['author']['name'], item['author']['id'])
        return path_format(author_path)

    @classmethod
    def work(cls, item):
        work_path = "%s_%s" % (item['title'], item['id'])
        return path_format(work_path)

    @classmethod
    def space(cls, item):
        return os.path.join(
            cls.author(item),
            cls.work(item),
        )


class Novel(object):
    @classmethod
    def html(cls, title, novel):
        _html = '''
               <html>
                   <head>
                       <title>%s</title>
                       <style type="text/css">
                           body{
                               width: 650px;
                               margin: auto;
                           }
                           .img{
                              text-align: center;
                           }
                           img{
                               width:80%%;
                           }
                       </style>
                   </head>
                   <body>
                       %s
                   </body>
               </html>
           ''' % (title, novel)
        return _html

    @classmethod
    def format(cls, novel_text):
        _html = novel_text
        _html = ''.join("<p>%s</p>" % line for line in _html.split("\n") if len(line.strip()) > 0)
        _html = _html.replace("[newpage]", "")
        return _html

    @classmethod
    def novel_bind_image(cls, novel, images: dict):
        _html = cls.format(novel)
        for id, image in images.items():
            _tag_image = '[pixivimage:%s]' % id
            _img_html = '<div class="img" ><img src="%s" /></div>' % image
            _html = _html.replace(_tag_image, _img_html)
        return _html
