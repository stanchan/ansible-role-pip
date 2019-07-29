#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: pypi_version
    author: Stan Chan <stanchan@gmail.com>
    version_added: "2.8"
    short_description: get lastest version of a python package from pypi
    description:
        - This lookup returns the latest version of a python package from pypi.
    options:
      _terms:
        description: name of python package
        required: True
"""
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

import urllib.request, urllib.error
import socket
import json

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

URL_PATTERN = 'https://pypi.python.org/pypi/{package}/json'

class LookupModule(LookupBase):
    def run(self, terms, variables=None, req_timeout=3, **kwargs):
        ret = []
        for term in terms:
            term = str(term)
            url = URL_PATTERN.format(package=term)
            try:
                resp = urllib.request.urlopen(url, timeout=req_timeout).read().decode('utf-8')
            except urllib.error.HTTPError as e:
                raise AnsibleError("failed to acquire pypi metadata in lookup: {} (HTTPError: {}, URL: {})".format(term, e, url))
            except urllib.error.URLError as e:
                if isinstance(e.reason, socket.timeout):
                    raise AnsibleError("failed to acquire pypi metadata in lookup: {} (Socket Timeout, URL: {})".format(term, url))
                else:
                    raise AnsibleError("failed to acquire pypi metadata in lookup: {} (Error: {}, URL: {})".format(term, e, url))
            version = parse('0')
            try:
                j = json.loads(resp)
            except (ValueError, TypeError) as e:
                raise AnsibleError("failed to acquire pypi metadata in lookup: {} (Error: {}, URL: {})".format(term, e, url))
            releases = j.get('releases', [])
            version = max([parse(release) for release in releases if not parse(release).is_prerelease])
            ret.append(version)
        return ret
