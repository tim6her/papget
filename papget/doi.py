#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A collection of funcitons handling DOI-s
"""

from __future__ import unicode_literals, division, print_function

import mechanize

from . import papget

def resolve_doi(url, browser=None):
    """ Get target url from DOI

    Args:
        url (str):
                DOI in URL format
        browser (Optional[:class:`mechanize.Browser`]):
                A :class:`mechanize.Browser` instance. If none is
                provided a new browser will be created.

    Returns:
        str:    Target of DOI

    Example:
        >>> resolve_doi('https://doi.org/10.1109/5.771073')
        'https://ieeexplore.ieee.org/document/771073/'
    """
    browser = papget.Provider.get_browser(browser)
    try:
        browser.open(url)
    except mechanize.HTTPError:
        pass
    return browser.geturl()
