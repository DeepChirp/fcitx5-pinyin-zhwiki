#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Usage:
#   convert.py input_filename
# input_filename is a file of Wikipedia article titles, one title per line.

import logging
import re
import sys
import os.path

import opencc
from pypinyin import lazy_pinyin

# Require at least 2 characters
_MINIMUM_LEN = 2
_LIST_PAGE_ENDINGS = [
    '列表',
    '对照表',
]
_LOG_EVERY = 1000

_PINYIN_SEPARATOR = '\''
_HANZI_RE = re.compile('^[\u4e00-\u9fa5]+$')
_TO_SIMPLIFIED_CHINESE = opencc.OpenCC('t2s.json')

_PINYIN_FIXES = {
    'n': 'en',  # https://github.com/felixonmars/fcitx5-pinyin-zhwiki/issues/13
}

logging.basicConfig(level=logging.INFO)


def is_good_title(title, previous_title=None):
    if not _HANZI_RE.match(title):
        return False

    # Skip single character & too long pages
    if len(title) < _MINIMUM_LEN:
        return False

    # Skip list pages
    if title.endswith(tuple(_LIST_PAGE_ENDINGS)):
        return False

    if previous_title and \
      len(previous_title) >= 4 and \
      title.startswith(previous_title):
        return False

    return True


def log_count(count):
    logging.info(f'{count} words generated')


def make_output(word, pinyin):
    return '\t'.join([word, pinyin, '0'])


def load_excluded_titles(filename="exclude_titles.txt"):
    excluded_titles = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                excluded_titles.add(line.strip())
        logging.info(f'Loaded {len(excluded_titles)} excluded titles from {filename}')
    else:
        logging.info(f'No excluded titles file found at {filename}, continuing without exclusions')
    return excluded_titles


def main():
    previous_title = None
    result_count = 0

    excluded_titles = load_excluded_titles()

    with open(sys.argv[1]) as f:
        for line in f:
            title = _TO_SIMPLIFIED_CHINESE.convert(line.strip())
            if title in excluded_titles:
                logging.debug(f'Excluded title: {title}')
                continue
            if is_good_title(title, previous_title):
                pinyin = [_PINYIN_FIXES.get(item, item) for item in lazy_pinyin(title)]
                pinyin = _PINYIN_SEPARATOR.join(pinyin)
                if pinyin == title:
                    logging.info(
                        f'Failed to convert to Pinyin. Ignoring: {pinyin}')
                    continue
                print(make_output(title, pinyin))
                result_count += 1
                if result_count % _LOG_EVERY == 0:
                    log_count(result_count)
                previous_title = title
    log_count(result_count)


if __name__ == '__main__':
    main()
