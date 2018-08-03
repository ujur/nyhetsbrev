#!/usr/bin/env python3
# encoding: UTF-8
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
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


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("-out", help="output file name", default="tilvekst.html")
    return parser.parse_args()


def get_plaintext(html):
    return html2text(html).strip()


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
            #             "http://ejil.oxfordjournals.org/rss/current.xml",
            #             "http://www.tandfonline.com/action/showFeed?type=etoc&feed=rss&jc=rnhr20",
            ]
    feeds = [feedparser.parse(URL) for URL in URLs]
#     print(feeds)
    for feed in feeds:
        # print(feed["channel"]["title"])
        for item in feed["items"][:1]:
            heading(item["title"])
#             print(item["date"])
#             print(item["date_parsed"])
            doc.asis(item["summary"])
#             print(item["summary"])
            link(item["link"], "Fulltekst")


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
        heading(last_issue)
        for item in formatted:
            if item[2] == last_issue:
                text("%s (%s)" % (item[0], item[1]))
                doc.stag("br")


def heading(title, level="h2"):
    """
    Add heading to the accumulated  HTML
    """
    with tag(level):
        text(title)


def link(target, description):
    "Add link to the accumulated HTML"
    with tag("a", href=target):
        text(description)


def list_book(book):
    link(book["primo_link"], book["title"])
    doc.stag("br")
    if book["author"]:
        text(book["author"])
        doc.stag("br")
    if book["series"]:
        text("Serie: ", book["series"])
        doc.stag("br")
    # edition = book["edition"] if book["edition"] else "1. utg."
    if book["edition"]:
        text(book["edition"], " ")
    if book["publication_date"]:
        text(book["publication_date"])
        doc.stag("br")
#     if book["receiving_or_activation_date"]:
#         text("Mottatt: ", book["receiving_or_activation_date"].split()[0])
#         doc.stag("br")
    doc.stag("br")


def get_number(book):
    """
    Get the l-skjema call number of the book
    """
    try:
        return int(float(book["permanent_call_number"].split()[0]))
#         book["permanent_call_number_type"] == "Other scheme"
    except ValueError as e:
        print(book["title"], book["permanent_call_number"])
#         print(e)
        return 0


def fetch_books(URL="https://ub-tilvekst.uio.no/lists/72.json?days=60"):
    """
    Fetch books from UB tilvekst
    """
    partitions = [("Rettsvitenskap i alminnelighet", 1, 107),
                  ("Privatrett", 108, 637),
                  ("Offentlig rett", 638, 1127),
                  ("Folkerett", 1129, 1235),
                  ("Kirkerett", 1236, 1287)]

    response = requests.get(URL)
    books = json.loads(response.text)
    # Only list books that are catalogued
    books = [book for book in books if book["permanent_call_number"] and book["location_name"] != "UJUR Kontor"]
    for partition in partitions:
        description, start, to = partition
        current = [book for book in books if start <= get_number(book) <= to]
        if current:
            # Remove current partition from books
            books = [item for item in books if item not in current]
            heading(description)
            for book in current:
                list_book(book)
    if books:
        heading("Resten")
        for book in books:
            list_book(book)


def fetch_all():
    heading("Nye bøker", level="h1")
    fetch_books()
    heading("Tidsskrifter", level="h1")
    fetch_feeds()
    fetch_norart()


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
        with open(options.out, "w", encoding="utf-8") as outFile:
            print(result, file=outFile)
    else:
        print(result)