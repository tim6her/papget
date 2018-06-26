#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import os

import click
import yaml
import datetime as dt

import bibtexparser as bibtex

import papget.doi

@click.command()
@click.option('--info/--no-info', default=True,
              help='Do you want to write a log to an info file?')
@click.option('--overwrite/--keep', default=True,
              help='Do you want to overwrite existant PDFs?')
@click.option('--debug/--no-debug', default=False,
              help='Do you want to raise errors?')
@click.option('--network', default=None,
              help='Which network are you currently using, '
                   'TU Wien etc.?')
@click.argument('files', nargs=-1, type=click.Path())
def main(info=True, overwrite=True, debug=False, files=None, network=None):
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
                succ = False
                fn = name_format(f)
                if not overwrite and os.path.isfile(fn):
                    continue

                d = dict(doi=url,
                         note='automatically downloaded with '
                              '<https://github.com/tim6her/papget/>')
                if network:
                    d['network'] = network
                target, provider = get_target(url, browser)
                d['url'] = target
                d['provider'] = provider.NAME

                if debug:
                    click.echo(f)
                    click.echo(provider.NAME)
                fn = name_format(f)
                if not overwrite and os.path.isfile(fn):
                    continue

                try:
                    succ = provider.papget(target, fn)
                except BaseException as e:
                    if debug:
                        raise e
                    click.echo(e)
                if not succ:
                    try:
                        succ = try_scihub(url, f)
                        d['provider'] = papget.SciHub.NAME
                    except BaseException as e:
                        if debug:
                            raise e
                        click.echo(e)
                if succ:
                    d['date'] = dt.datetime.now().strftime('%Y-%m-%d')
                    desc = 'automatically downloaded by tim6her on {}, {}'
                    desc = desc.format(d['date'], d['url'])
                    d['short description'] = desc
                    if info:
                        fn = name_format(f, ext='info')
                        write_info(d, fn)


def try_scihub(url, f, browser=None):
    fn = name_format(f)
    return papget.SciHub.papget(url, fn, browser)

def write_info(d, filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as info:
            d_info = yaml.load(info)
    else:
        d_info = {}
    d_info['download'] = d
    with open(filename, 'w') as info:
        yaml.safe_dump(d_info, info,
                       default_flow_style=False)

def get_target(url, browser=None):
    target = papget.doi.resolve_doi(url, browser)

    for provider in papget.ALL_PROVIDERS:
        if provider.RE_URL.search(target):
            return target, provider
    return url, papget.SciHub

def name_format(bib_name, style='shelah', ext='pdf'):
    fn = os.path.basename(bib_name)
    nr = fn.split('-')[0]
    return '{}.{}'.format(nr, ext)

if __name__ == '__main__':
    main()
