# -*- coding: UTF-8 -*-
import sys
import inspect
import os
from urllib import parse
import hashlib
import socket
import emoji


def md5(text):
    hashlib_md5 = hashlib.md5()
    hashlib_md5.update(text.encode(encoding='utf-8'))
    return hashlib_md5.hexdigest()


def list_chunks(list_data, size):
    for index in range(0, len(list_data), size):
        yield list_data[index:index + size]


def path_format(path: str):
    r_dir_filter = [
        ('/', '_'),
        ('\\', '_'),
        (':', '：'),
        ('*', '_'),
        ('?', u'？'),
        ('"', '_'),
        ('<', '['),
        ('>', ']'),
        ('|', '_'),
        ('\t', '_'),
    ]

    path = emoji.demojize(path)
    for filter_ele in r_dir_filter:

        path = path.replace(filter_ele[0], filter_ele[1])
    return path


def url_query(url):
    return dict(parse.parse_qsl(parse.urlparse(url).query))


def package(name, path):
    _package = sys.modules[name].__package__
    return '%s.%s' % (_package, path)


def service_ready(ip, port):
    try:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect((ip, port))
        return True
    except:
        return False
