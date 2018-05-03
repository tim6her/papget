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
@click.option('--debug/--no-debug', default=False,
              help='Do you want to raise errors?')
@click.argument('files', nargs=-1, type=click.Path())
def main(info=True, debug=False, files=None):
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
                try:
                    target, provider = get_target(url, browser)
                except BaseException as e:
                    if debug:
                        raise e
                    next

                if not target:
                    next
                if debug:
                    click.echo(f)
                    click.echo(provider)
                fn = name_format(f)
                try:
                    succ = provider.papget(target, fn)
                except BaseException as e:
                    if debug:
                        raise e
                if not succ:
                    succ = False
                    try_scihub(url, f)


def try_scihub(url, f, browser=None):
    fn = name_format(f)
    papget.SciHub.papget(url, fn, browser)

def get_target(url, browser=None):
    target = papget.doi.resolve_doi(url, browser)

    for provider in papget.ALL_PROVIDERS:
        if provider.RE_URL.search(target):
            return target, provider
    return url, papget.SciHub

def name_format(bib_name, style='shelah'):
    fn = os.path.basename(bib_name)
    nr = fn.split('-')[0]
    if nr in name_format.cache:
        name_format.cache[nr] += 1
        nr = '{}-{}'.format(nr, name_format.cache[nr])
    else:
        name_format.cache[nr] = 1
    return '{}.pdf'.format(nr)
name_format.cache = {}

if __name__ == '__main__':
    main()
