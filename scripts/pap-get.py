#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import os

import click
import mechanize
import yaml

import bibtexparser as bibtex

import papget.doi

@click.command()
@click.option('--info/--no-info', default=True,
              help='Do you want to write a log to an info file')
@click.argument('files', nargs=-1, type=click.Path())
def main(info=True, files=None):
    """ Small script for downloading papers from bibtex files
    """
    files = filter(lambda f: os.path.splitext(f)[-1] == '.bib', files)
    if len(files) == 0:
        return
    browser = papget.Provider.get_browser()
    with click.progressbar(files) as ff:
        for f in ff:
            ff.label = f
            with open(f) as fin:
                bib = bibtex.load(fin)
            has_url = filter(lambda e: 'url' in e, bib.entries)
            urls = [e['url'] for e in has_url]
            for url in urls:
                target, provider = get_target(url, browser)
                if target:
                    provider.papget(target, 'temp.pdf')


def get_target(url, browser=None):
    try:
        target = papget.doi.resolve_doi(url, browser)
    except mechanize.HTTPError:
        click.echo(browser.response())
        return None, None

    for provider in papget.ALL_PROVIDERS:
        if provider.RE_URL.search(target):
            return target, provider
    return None, None

if __name__ == '__main__':
    main()
