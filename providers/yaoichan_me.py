#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml.html import document_fromstring
import re
import json

domainUri = 'http://yaoichan.me'
uriRegex = 'https?://(?:www\.)yaoichan.me/(?:manga|online)/\d+\-'
imagesRegex = '"fullimg":\s?\[(.*)?\]'


def test_url(url):
    test = re.match(uriRegex, url)
    if test is None:
        return False
    return len(test.groups()) > 0



def get_main_content(url, get=None, post=None):
    if re.search('me/online/\d+\-', url):
        content = get(url)
        parser = re.search('"content_id":\s?"(.+)",', content)
        if parser:
            url = domainUri + parser.groups()[0]
    return get(url)


def get_volumes(content=None, url=None):
    parser = document_fromstring(content).cssselect('td .manga > a')
    if not parser:
        return []
    list = [domainUri + i.get('href') for i in parser]
    list.reverse()
    return list


def get_archive_name(volume, index: int = None):
    parser = re.search('_(v\d+_ch\d+)', volume)
    if not parser:
        return 'vol_%s' % index
    return parser.groups()[0]


def get_images(main_content=None, volume=None, get=None, post=None):
    content = get(volume)
    parser = re.search(imagesRegex, content)
    if not parser:
        return []
    parser = parser.groups()[0].rstrip(',')
    list = json.loads('[' + parser + ']')
    return list


def get_manga_name(url, get=None):
    parser = re.search('\.me/.+/\d+\-(.*)\.html', url)
    if not parser:
        return ''
    return parser.groups()[0]


if __name__ == '__main__':
    print('Don\'t run this, please!')