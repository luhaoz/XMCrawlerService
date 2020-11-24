# -*- mode: python -*-
# -*- coding: utf-8 -*-
import os

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "http://host.docker.internal:%s" % os.environ.get("PROXY_PORT")
