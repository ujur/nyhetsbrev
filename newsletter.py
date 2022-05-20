#!/usr/bin/env python3
# encoding: UTF-8
"""
Script for making lists of newly acquired books and articles
"""

import json
from operator import itemgetter, attrgetter, methodcaller
import argparse
import datetime
import sys
import time
import subprocess
# Install dependencies if required
try:
    import feedparser
    import requests
    from html2text import html2text
    from yattag import Doc, indent
    from bs4 import BeautifulSoup
    from unidecode import unidecode
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip',
                           'install', '-r', 'requirements.txt'])
    print("Software installed, restart program. Exiting in 5 seconds.")
    time.sleep(5)
    exit(0)


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("-out", help="output file name", default="tilvekst.html")
    parser.add_argument(
        "-days",
        help="number of days to include",
        type=int,
        default="16")
    return parser.parse_args()


def get_plaintext(html):
    return html2text(html).strip()


idunn_URLs = [
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=arbeidsrett',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=jv',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=kp',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=kj',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=lor',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=njhr',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=njsp',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=nd',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=olr',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=skatterett',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=tfei',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=teft',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=fab',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=tff',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=tfr',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=strafferett',
    'https://www.idunn.no/action/showFeed?type=etoc&feed=rss&jc=stat',
    #             "http://ejil.oxfordjournals.org/rss/current.xml",
    #             "http://www.tandfonline.com/action/showFeed?type=etoc&feed=rss&jc=rnhr20",
]


def fetch_feeds(URLs,
                # item_count=1,
                filter_title=None):
    """
    Fetch a list of RSS feeds.
    The content of each feed is output to the results file.

    Params:
        URLs: a list of URL strings
        item_count: the number of items to fetch from each URL
        filter_title: include only items containing this string in the title
    """
    feeds = [feedparser.parse(URL) for URL in URLs]
#     print(feeds)
    for feed in feeds:
        channel_title = feed['channel']['title'].replace('Table of Contents', '')
        heading(channel_title, level='h2')

        if options.verbose:
            print(unidecode(channel_title))  # to console, for debugging
        items = feed["items"]
        # remove duplicate items by URL
        items_seen = set()

        if filter_title:
            items = [item for item in items if filter_title in item["title"]]

        # fix prism data
        for item in items:
            if 'prism_publicationdate' in item and not 'published' in item:
                date = item['prism_publicationdate']
                item['published'] = date
#                 item['published_parsed'] = datetime.datetime.strptime(date)
                item['published_parsed'] = feedparser._parse_date(date)

        # sort items
        if len(items) > 1:
            if 'published' in items[0]:
                items.sort(key=lambda x: (x["published"], x["title"]), reverse=True)
                # filter by start_date if available
                if start_date:
                    items = [item for item in items
                             if not item['published_parsed'] or datetime.date.fromtimestamp(time.mktime(item['published_parsed'])) >= start_date]

        # for item in items[:item_count]:
        for item in items:
            if item['link'] not in items_seen:
                items_seen.add(item['link'])
                heading(item["title"])
    #             print(item["date"])
    #             print(item["date_parsed"])
                if "content" in item:
                    # get description without href
                    doc.asis(item['content'][1]['value'])
                    # print(item.summary)
                if "published" in item:
                    text("Publisert: %s" % item["published"])
                with tag('p'):
                    link(f'https://login.ezproxy.uio.no/login?url={item["link"]}',
                         "Fulltekst")


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


def heading(title, level="h3"):
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


def is_ebook(book):
    return not book["item_id"]


def get_number(book):
    """
    Get the l-skjema call number of the book
    """
    number = 0
    if not is_ebook(book):
        if book["permanent_call_number_type"] != "Dewey Decimal classification":
            permanent_call_number = book["permanent_call_number"]
            if permanent_call_number:
                permanent_call_number = permanent_call_number.split()[0]
                if permanent_call_number.isnumeric():
                    number = int(permanent_call_number)
                else:
                    try:
                        number = float(permanent_call_number)
                    except ValueError as e:
                        print('Couldn\'t parse permanent_call_number, included in "Andre fag og skjønnlitteratur":',
                              unidecode(book["title"]), book["permanent_call_number"], e)
            else:
                print('No permanent_call_number, included in "Andre fag og skjønnlitteratur":',
                      unidecode(book["title"]),
                      book["permanent_call_number"])
    return number


L_skjema = [("Festskrift", 19, 19),
            ("Rettsinformatikk", 39, 39.9),
            ("Rettsvitenskap i alminnelighet", 1, 107),
            ("Kvinnerett", 152, 152.9),
            ("Privatrett", 108, 637),
            ("Offentlig rett", 638, 1127),
            ("Menneskerettigheter", 1164, 1164),
            ("Folkerett", 1129, 1235),
            ("Kirkerett", 1236, 1287)]


def fetch_books(URL, partitions=None):
    """
    Fetch books from UB tilvekst
    """

    def include_book(book):
        try:
            publication_date = book.get('publication_date')
            return (is_ebook(book)
                    or
                    (publication_date > current_year - 3
                     # and book["permanent_call_number"]
                     and book["location_name"] not in ignore_collections))
        except Exception as e:
            if options.verbose:
                print("Error for title:", book["title"], "link:", book["self_link"], e)
            return True

    response = requests.get(URL)
    books = json.loads(response.text)
    ignore_collections = ["UJUR Kontor", "UJUR Skranken - Ikke til hjemlån"]
    current_year = datetime.datetime.now().year
    # Only list books that are catalogued
    books = [book for book in books if include_book(book)]
    # Order by title
    books = sorted(books, key=itemgetter("title"))
    print('Number of books:', len(books))

    if partitions:
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
        if partitions:
            heading("Andre fag og skjønnlitteratur")
        for book in books:
            list_book(book)


def fetch_all():
    heading("Nyhetsbrev fra Juridisk bibliotek", level="h1")
    # Boilerplate intro
    text("""I dette nyhetsbrevet finner du nye bøker,
        e-bøker anskaffet ved Juridisk bibliotek, samt nyeste utgaver av en rekke sentrale norske tidsskrift.""")
    doc.stag("p")
    text("""De trykte bøkene er sortert på overordnet emne ut fra deres plassering i biblioteket.
        En bok kan ha flere emner og klassifikasjoner. Overskriftene og inndelingen er  tar utgangspunkt i """)
    link("http://app.uio.no/ub/ujur/l-skjema/", "L-skjema")
    text(""", bibliotekets klassifikasjonssystem. Listen under er sortert etter hovedemnet de er stilt opp på i biblioteket.""")
    doc.stag("p")
    text("""En del e-bøker ligger i databaser og er ikke synlige i Oria. Se siden vår for """)
    link("https://www.ub.uio.no/fag/jus/jus/juridiske-eboker.html", "juridiske e-bøker")
    text(""" for oversikt over baser som inneholder e-bøker.
         Videre er det viktig å huske på at e-bøker innen andre fag, ikke er synlige i dette nyhetsbrevet.""")
    doc.stag("p")
    text("""NB husk å  skru på HTML-visning i Outlook. Tilbakemeldinger, endringsforslag m.m. kan sendes til """)
    link("s.e.ostbye@ub.uio.no", "Sigrid Elisabeth Østbye")

    heading("Nye e-bøker", level="h2")
    fetch_books("https://ub-tilvekst.uio.no/lists/72.json?days=%d" % options.days)

#     heading("Nye e-bøker fra Cambridge", level="h2")
#     fetch_feeds(["https://www.cambridge.org/core/rss/subject/id/7C9FB6788DD8D7E6696263BC774F4D5B"], item_count=-1, filter_title='[Book]')

#     heading("Nye e-bøker fra Springer", level="h2")
#     fetch_feeds(["https://link.springer.com/search.rss?facet-discipline=%22Law%22&showAll=false&facet-language=%22En%22&facet-content-type=%22Book%22"], item_count=-1)

    heading("Nye trykte bøker", level="h2")
    fetch_books(
        "https://ub-tilvekst.uio.no/lists/68.json?days=%d" %
        options.days, partitions=L_skjema)

    heading("Tidsskrifter", level="h2")
    fetch_feeds(idunn_URLs)
    # fetch_norart()
    #fetch_feeds(["https://www.cambridge.org/core/rss/subject/id/7C9FB6788DD8D7E6696263BC774F4D5B"], item_count=-1, filter_title='[Article]')


if __name__ == '__main__':
    options = get_arguments()
    today = datetime.date.today()
    start_date = today - datetime.timedelta(options.days)
#     first = today.replace(day=1)
#     lastMonth = first - datetime.timedelta(days=32)
#     print(lastMonth.strftime("%Y%m%d"))
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
