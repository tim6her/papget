# !/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function, division, unicode_literals

import re
import urllib

from bs4 import BeautifulSoup
from mechanize import Browser

class Provider(object):
    """ Class representing the providers of papers

    Do not instance this class but inherit from it and overwrite
    :func:`need_to_pay` and :func:`papget`.

    Attributes:
        RE_URL (str):           Regex matching urls from this provider
        NAME (Optional[str]):   Name of provider

    """
    NAME = None
    RE_URL = None

    @classmethod
    def get_soup(cls, url, browser=None):
        browser = cls.get_browser(browser)
        browser.open(url)
        html = browser.response().read()
        return BeautifulSoup(html, 'lxml')

    @classmethod
    def need_to_pay(cls, url, browser=None):
        pass

    @classmethod
    def papget(cls, url, filename, browser=None):
        pass

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        pass

    @staticmethod
    def get_browser(browser=None):
        if not browser:
            browser = Browser()
            browser.set_handle_robots(False)
        return browser

class Springer(Provider):
    NAME = 'Springer'
    RE_URL = re.compile(r'https://link.springer.com')

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
