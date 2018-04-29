#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function

import mechanize

from . import papget

def resolve_doi(url, browser=None):
    browser = papget.Provider.get_browser(browser)
    browser.open(url)
    return browser.geturl()
