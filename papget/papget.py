# !/usr/bin/env python2
# -*- coding: utf-8 -*-
""" Collected methods and classes for providers of papers, e.g.
Springer.
"""

from __future__ import print_function, division, unicode_literals

import re

from bs4 import BeautifulSoup
import requests
from mechanize import Browser

class Provider(object):
    """ Class representing the providers of papers

    Note:
        Do not instance this class but inherit from it and overwrite
    :func:`need_to_pay` and :func:`get_pdf_url`.
    """
    NAME = ''
    """ (str): Name of provider
    """
    RE_URL = None
    """ (:class:`re.RegexObject`):
            Compiled regex used for matching URLs to this
            provider
    """
    def __repr__(self):
        return self.NAME

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
        browser = cls.get_browser(browser)
        if not cls.need_to_pay(url, browser):
            link = cls.get_pdf_url(url, browser)
            req = requests.get(link)
            with open(filename, 'wb') as pdf:
                pdf.write(req.content)
            return filename

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
            browser.addheaders = [(
                'User-agent',
                ('Mozilla/5.0 (X11; U; Linux i686; en-US; '
                'rv:1.9.0.1) Gecko/2008071615 '
                'Fedora/3.0.1-1.fc9 Firefox/3.0.1'))]

        return browser

class Springer(Provider):
    """ Provider implementation for Springer

    Examples:
        >>> url = 'https://link.springer.com/article/10.1007%2Fs40065-017-0185-1'
        >>> bool(Springer.need_to_pay(url))
        False
        >>> Springer.get_pdf_url(url)
        u'https://link.springer.com/content/pdf/...
        >>> Springer.papget(url, 'temp.pdf')
        u'temp.pdf'
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
        return soup.find('span', attrs={'class': 'buybox__buy'})

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        soup = cls.get_soup(url, browser)
        pdf = soup.find('a',
                        title=('Download this book in PDF '
                        'format'))
        if pdf:
            link = pdf['href']
            return 'https://link.springer.com%s' % link
        pdf = soup.find('span', string='PDF')
        a = pdf.parent
        link = a['href']
        return 'https://link.springer.com%s' % link



class Cammbridge(Provider):
    """ Provider implementation for Cammbridge University Press

    Examples:
        >>> url = 'https://bit.ly/2KoN7vU'
        >>> bool(Cammbridge.need_to_pay(url))
        False
        >>> Cammbridge.get_pdf_url(url)
        u'https://www.cambridge.org/core/services/aop-...
        >>> Cammbridge.papget(url, 'temp.pdf')
        u'temp.pdf'
        >>> import os; os.remove('temp.pdf')
        >>> url2 = 'https://bit.ly/2HBtD9F'
        >>> bool(Cammbridge.need_to_pay(url2))
        True
    """
    NAME = 'Cammbridge University Press'
    RE_URL = re.compile('www.cambridge.org')

    @classmethod
    def need_to_pay(cls, url, browser=None):
        soup = cls.get_soup(url, browser)
        return soup.find('a', string='Get access')

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        soup = cls.get_soup(url, browser)
        pdf = soup.find('a',
                        attrs={'aria-label': 'Download PDF'})
        link = pdf['href']
        return 'https://www.cambridge.org%s' % link

class Ams(Provider):
    """ Provider implementation for American Mathematical
    Society

    Examples:
        >>> url = 'https://bit.ly/2HEalfN'
        >>> bool(Ams.need_to_pay(url))
        False
        >>> Ams.get_pdf_url(url)
        u'http://www.ams.org/journals/jams/2016-29-01/...
        >>> Ams.papget(url, 'temp.pdf')
        u'temp.pdf'
        >>> import os; os.remove('temp.pdf')
    """
    NAME = 'American Mathematical Society'
    RE_URL = re.compile('www.ams.org')

    @classmethod
    def need_to_pay(cls, url, browser=None):
        soup = cls.get_soup(url, browser)
        return soup.find('div',
                         id='buy_in_amsbookstore_div')

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        browser = cls.get_browser(browser)
        soup = cls.get_soup(url, browser)
        pdf = soup.find('a', string='Full-text PDF')
        link = pdf['href']
        browser.open(url)
        browser.open(link)
        return browser.geturl()

class SciHub(Provider):
    """ Provider implementation for Sci-Hub

    Raises:
        RuntimeError: if a CAPTACHA is encountered.
    """
    NAME = 'Sci-Hub'
    RE_URL = re.compile('sci-hub.tw')

    @classmethod
    def need_to_pay(cls, url, browser=None):
        return False

    @classmethod
    def get_pdf_url(cls, url, browser=None):
        doi = re.match(r'http://dx.doi.org/(.*)', url).group(1)
        scihub = 'http://sci-hub.tw/'
        browser = cls.get_browser(browser)
        soup = cls.get_soup(scihub + doi, browser)
        pdf = soup.find('div',
                        attrs={'class': 'button',
                               'id': 'save'}
                       )

        link = pdf.p.a['onclick']
        link = re.match(r'.*?=\'(.*)\'', link).group(1)
        return link

    @classmethod
    def papget(cls, url, filename, browser=None):
        browser = cls.get_browser(browser)
        if not cls.need_to_pay(url, browser):
            link = cls.get_pdf_url(url, browser)
            req = requests.get(link)
            if 'CaptchaRedirect' in req.text:
                raise RuntimeError('Captach encountered')
            content = req.content
            if len(content) < 3000:
                msg = 'File size too small to be valid PDF: {}'
                raise RuntimeError(msg.format(len(content)))

            with open(filename, 'wb') as pdf:
                pdf.write(req.content)
            return filename

ALL_PROVIDERS = [Springer, Cammbridge, Ams]
