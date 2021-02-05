# -*- mode: python -*-
# -*- coding: utf-8 -*-
import os
from .ziputil import ZipUtil
import zipfile
from scrapy.pipelines.files import FileException, FilesPipeline
from twisted.internet import defer, threads
from datetime import datetime
from scrapy.utils.misc import md5sum
import time


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        pass
        # request.meta['proxy'] = "http://host.docker.internal:%s" % os.environ.get("PROXY_PORT")
        # request.meta['proxy'] = "http://127.0.0.1:10809"


class ZipFilesStore(object):
    def __init__(self, basedir):
        self.__basedir = basedir

    def __get_filesystem_path(self, path):
        _zip_dir_path = os.path.join(self.__basedir, os.path.dirname(path))
        # os.makedirs(_zip_dir_path, exist_ok=True)
        return _zip_dir_path

    def __get_filesystem_package(self, path):
        return '%s.zip' % self.__get_filesystem_path(path)

    def __get_file(self, path):
        return os.path.basename(path)

    def __threads_persist_file(self, path, buf, info, meta=None, headers=None):

        _zip_path = self.__get_filesystem_package(path)
        _base_dir = os.path.dirname(_zip_path)
        os.makedirs(_base_dir, exist_ok=True)

        _file_path = self.__get_file(path)
        with ZipUtil(_zip_path) as _zip_file:
            _zip_file.replace(_file_path, buf.getvalue())
        # with zipfile.ZipFile(_zip_path, 'a', zipfile.ZIP_LZMA) as _zip_file:
        #     if _file_path not in _zip_file.namelist():
        #         _zip_file.writestr(_file_path, buf.getvalue())

    def __threads_stat_file(self, path, info):
        _zip_path = self.__get_filesystem_package(path)
        if zipfile.is_zipfile(_zip_path) is False:
            return {}
        try:
            last_modified = os.path.getmtime(_zip_path)
        except os.error:
            return {}
        _file_path = self.__get_file(path)
        with zipfile.ZipFile(_zip_path, 'r', compression=zipfile.ZIP_LZMA, compresslevel=9) as _zip_file:
            _file_exists = _file_path in _zip_file.namelist()
            if _file_exists is False:
                return {}
            _time = datetime(*_zip_file.getinfo(_file_path).date_time)
            _last_modified = time.mktime(_time.timetuple())
            checksum = md5sum(_zip_file.read(_file_path))
            return {'last_modified': _last_modified, 'checksum': checksum}

    def persist_file(self, path, buf, info, meta=None, headers=None):
        # return threads.deferToThread(self.__threads_persist_file, path, buf, info, meta, headers)
        return self.__threads_persist_file(path, buf, info, meta, headers)

    def stat_file(self, path, info):
        # return threads.deferToThread(self.__threads_stat_file, path, info)
        return self.__threads_stat_file(path, info)


class ZipFilesPipeline(FilesPipeline):
    def _get_store(self, uri):
        return ZipFilesStore(uri)
