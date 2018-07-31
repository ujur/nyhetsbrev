#!/usr/bin/env python3
# encoding: UTF-8
from __future__ import print_function
import json
import argparse
# import datetime
import sys
import time
from utils import pip_install
# Install dependencies if required
# try:
import feedparser
import requests
from html2text import html2text
from yattag import Doc, indent
from bs4 import BeautifulSoup
# except ImportError:
#     pip_install("feedparser", "requests", "html2text", "beautifulsoup4")
#     print("Software installed, restart program. Exiting in 5 seconds.")
#     time.sleep(5)
#     exit(0)


def output(*args):
    """
    Helper method to correctly format output.
    some mail readers, like outlook, strips line feeds  from text.
    to avoid this, we insert a space on the end of every line
    """
#     print(*args, " ")


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("-out", help="output file name")
    return parser.parse_args()


def get_plaintext(html):
    return html2text(html).strip()


def print_title(title):
    #     output("---------------------------------------")
    output(title)
#     output("*" + title + "*")
    output("---------------------------------------")


def fetch_feeds():
    #     today = datetime.date.today()
    #     first = today.replace(day=1)
    #     lastMonth = first - datetime.timedelta(days=32)
    #     print(lastMonth.strftime("%Y%m%d"))
    URLs = ["http://www.idunn.no/tools/rss?tidsskrift=arbeid",
            #             "http://www.idunn.no/tools/rss?tidsskrift=ip", # ended 2015?
            "http://www.idunn.no/tools/rss?tidsskrift=jv",
            "http://www.idunn.no/tools/rss?tidsskrift=lor",
            #             "https://www.idunn.no/tools/rss?tidsskrift=nd&marketplaceId=2000",
            "http://www.idunn.no/tools/rss?tidsskrift=skatt",
            "http://www.idunn.no/tools/rss?tidsskrift=stat",
            "http://www.idunn.no/tools/rss?tidsskrift=tfr",
            "https://www.idunn.no/tools/rss?tidsskrift=kritisk_juss&marketplaceId=2000",
            "https://www.idunn.no/tools/rss?tidsskrift=tidsskrift_for_eiendomsrett&marketplaceId=2000",
            "https://www.idunn.no/tools/rss?tidsskrift=tidsskrift_for_familierett_arverett_og_barnevernrettslige_sp&marketplaceId=2000",
            "https://www.idunn.no/tools/rss?tidsskrift=tidsskrift_for_forretningsjus&marketplaceId=2000",
            "https://www.idunn.no/tools/rss?tidsskrift=tidsskrift_for_strafferett",
            "https://www.idunn.no/tools/rss?tidsskrift=tidsskrift_for_erstatningsrett_forsikringsrett_og_trygderett&marketplaceId=2000",
            "https://www.idunn.no/tools/rss?tidsskrift=oslo_law_review&marketplaceId=2000",
            "http://ejil.oxfordjournals.org/rss/current.xml",
            #             "http://www.tandfonline.com/action/showFeed?type=etoc&feed=rss&jc=rnhr20",
            ]
    feeds = [feedparser.parse(URL) for URL in URLs]
#     print(feeds)
    for feed in feeds:
        # output(feed["channel"]["title"])
        for item in feed["items"][:1]:
            print_title(item["title"])
#             output(item["date"])
#             output(item["date_parsed"])
            output(get_plaintext(item["summary"]))
#             output(item["summary"])
            output(item["link"], "\n")


def fetch_norart():
    URLs = [
        #         "http://www.nb.no/baser/norart/trip.php?_b=norart&issn-ntid=1399-140X",
        "http://www.nb.no/baser/norart/trip.php?_b=norart&issn-ntid=0105-1121",
    ]

    for URL in URLs:
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "lxml")
        items = soup.findAll('tr', {"class": "zebra"})
        formatted = [[data.text.replace("\xa0", " ").strip()
                      for data in item.find_all('td')[1:4]] for item in items]
        # find title  of the last issue
        last_issue = formatted[0][2]
        print_title(last_issue)
        for item in formatted:
            if item[2] == last_issue:
                output("%s (%s)" % (item[0], item[1]))
        output()


def fetch_books(URL="https://ub-tilvekst.uio.no/lists/72.json"):
    """
    Fetch books from UB tilvekst
    """
    response = requests.get(URL)
    books = json.loads(response.text)

    for book in books:
        with tag("a", href=book["primo_link"]):
            text(book["title"])
        doc.stag("br")
        if book["author"]:
            text(book["author"])
            doc.stag("br")
        edition = book["edition"] if book["edition"] else "1. utg."
        text(edition, " ")
        if book["publication_date"]:
            text(book["publication_date"])
        doc.stag("br")
        doc.stag("br")


def fetch_all():
    #     fetch_feeds()
    #     fetch_norart()
    fetch_books()


if __name__ == '__main__':
    options = get_arguments()
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='utf-8')
        with tag('body'):
            fetch_all()

    result = indent(doc.getvalue())

    if options.out:
        with open(options.out, "w") as outFile:
            print(result, file=outFile)
    else:
        print(result)
