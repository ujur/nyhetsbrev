#!/usr/bin/env python3
# encoding: UTF-8
from __future__ import print_function
import argparse
import feedparser
import datetime
import sys
from html2text import html2text


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("-out", help="output file name")
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
            "https://www.idunn.no/tools/rss?tidsskrift=nd&marketplaceId=2000",
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
            ]
    feeds = [feedparser.parse(URL) for URL in URLs]
#     print(feeds)
    for feed in feeds:
        #         print(feed["channel"]["title"])
        for item in feed["items"][:1]:
            print("----------------------------------------------------------------------")
            print(item["title"])
            print("----------------------------------------------------------------------")
#             print(item["date"])
#             print(item["date_parsed"])
            print(get_plaintext(item["summary"]))
#             print(item["summary"])
            print(item["link"], "\n")


def fetch_all():
    fetch_feeds()


def main():
    options = get_arguments()
    if options.out:
        with open(options.out, "w") as outFile:
            sys.stdout, temp = outFile, sys.stdout
            fetch_all()
            sys.stdout = temp
    else:
        fetch_all()


if __name__ == '__main__':
    main()
