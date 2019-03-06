#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: pypi_version
    author: Stan Chan <stanchan@gmail.com>
    version_added: "2.4"
    short_description: get lastest version of a python package from pypi
    description:
        - This lookup returns the latest version of a python package from pypi.
    requirements:
      - requests library installed
    options:
      _terms:
        description: name of python package
        required: True
"""
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

import json
try:
    import requests
    HAS_REQUESTS = True
except ImportError as e:
    HAS_REQUESTS = False

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

URL_PATTERN = 'https://pypi.python.org/pypi/{package}/json'

class LookupModule(LookupBase):
    def run(self, terms, variables=None, req_timeout=1, **kwargs):
        if not HAS_REQUESTS:
            raise AnsibleError('Requests library is required for pypi_version lookup, try `pip install requests`.')

        ret = []
        for term in terms:
            term = str(term)
            try:
                req = requests.get(URL_PATTERN.format(package=term), timeout=req_timeout)
            except requests.exceptions.RequestException as e:
                raise AnsibleError("failed to acquire pypi metadata in lookup: {}".format(term))
            version = parse('0')
            if req.status_code == requests.codes.ok:
                j = json.loads(req.text.encode('utf-8'))
                releases = j.get('releases', [])
                version = max([parse(release) for release in releases if not parse(release).is_prerelease])
                ret.append(version)
        return ret
