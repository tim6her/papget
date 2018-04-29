# !/usr/bin/env python2
# -*- coding: utf-8 -*-
""" Collected methods and classes for providers of papers, e.g.
Springer.
"""

from __future__ import print_function, division, unicode_literals

import re
import urllib

from bs4 import BeautifulSoup
from mechanize import Browser

class Provider(object):
    """ Class representing the providers of papers

    Do not instance this class but inherit from it and overwrite
    :func:`need_to_pay` and :func:`papget`.
    """
    NAME = None
    """ (str): Name of provider
    """
    RE_URL = None
    """ (:class:`re.RegexObject`):
            Compiled regex used for matching URLs to this
            provider
    """

    @classmethod
    def get_soup(cls, url, browser=None):
        """ Get a parsed version of the HTML source of an URL

        Args:
            url (str):
                    URL pointing to desired webpage
            browser (Optional[:class:`mechanize.Browser`]):
                    If no browser is provided, a new instance
                    will be created.

        Returns:
            (:class:`bs4.BeautifulSoup`)
                Parsed version of HTML source
        """
        browser = cls.get_browser(browser)
        browser.open(url)
        html = browser.response().read()
        return BeautifulSoup(html, 'html5lib')

    @classmethod
    def need_to_pay(cls, url, browser=None):
        """ Check whether one needs to pay for PDF download

        Args:
            url (str):
                    URL pointing to desired webpage
            browser (Optional[:class:`mechanize.Browser`]):
                    If no browser is provided, a new instance
                    will be created.
        """
        pass

    @classmethod
    def papget(cls, url, filename, browser=None):
        """ Comfortably download the PDF from a given URL

        Args:
            url (str):
                    URL pointing to desired webpage
            browser (Optional[:class:`mechanize.Browser`]):
                    If no browser is provided, a new instance
                    will be created.
        """
        pass

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        """ Get URL of PDF resource

        Args:
            url (str):
                    URL pointing to desired webpage
            browser (Optional[:class:`mechanize.Browser`]):
                    If no browser is provided, a new instance
                    will be created.
        """
        pass

    @staticmethod
    def get_browser(browser=None):
        """ Create new browser if none is present.

        Returns:
            (:class:`mechanize.Browser`)
        """
        if not browser:
            browser = Browser()
            browser.set_handle_robots(False)
        return browser

class Springer(Provider):
    """ Provider implementation for Springer

    Examples:
        >>> url = 'https://link.springer.com/article/10.1007%2Fs40065-017-0185-1'
        >>> bool(Springer.need_to_pay(url))
        False
        >>> Springer.get_pdf_url(url)
        u'https://link.springer.com/content/pdf/10.1007%2Fs40065-017-0185-1.pdf'
        >>> Springer.papget(url, 'temp.pdf')
        (u'temp.pdf', ...
        >>> import os; os.remove('temp.pdf')
    """
    NAME = 'Springer'
    """ (str): Name of provider
    """
    RE_URL = re.compile(r'https://link.springer.com')
    """ (:class:`re.RegexObject`):
            Compiled regex used for matching URLs to this
            provider
    """

    @classmethod
    def need_to_pay(cls, url, browser=None):
        soup = cls.get_soup(url, browser)
        return soup.find('span', attrs={'class', 'buybox__buy'})

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        soup = cls.get_soup(url, browser)
        pdf = soup.find('span', string='PDF')
        a = pdf.parent
        link = a['href']
        return 'https://link.springer.com%s' % link

    @classmethod
    def papget(cls, url, filename, browser=None):
        browser = cls.get_browser(browser)
        if not cls.need_to_pay(url, browser):
            link = cls.get_pdf_url(url, browser)
            return urllib.urlretrieve(link, filename)

ALL_PROVIDERS = [Springer]
