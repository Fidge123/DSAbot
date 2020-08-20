import json
import os
from hashlib import sha256

from bs4 import BeautifulSoup
import requests

base = "http://ulisses-regelwiki.de/"
blacklist = [
    "index.php/start.html",
    "index.php/kontakt.html",
    "index.php/impressum.html",
    "index.php/datenschutzerklaerung.html",
]
regelwiki = []
skipped = []


def validate(link):
    try:
        return (
            link["href"].startswith("index.php")
            and "#" not in link["href"]
            and link["href"] not in blacklist
        )
    except:
        return False


def hash_and_clean(soup):
    soup.header.decompose()
    soup.footer.decompose()
    for form in soup.find_all("form"):
        form.decompose()

    soup_hash = sha256(soup.prettify(encoding="utf-8")).hexdigest()

    for bc in soup.find_all("div", class_="breadcrumb_boxed"):
        bc.decompose()
    for content in soup.find_all("div", id="main"):
        content.decompose()

    return soup_hash


def find_page(url, sitemap):
    for site in sitemap:
        if site["url"] == url:
            return site
    return {}


def parse(url, sitemap, level=0):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        soup_hash = hash_and_clean(soup)

        site = find_page(url, sitemap)
        if getattr(site, "hash", None) == soup_hash:
            return site

        title = soup.title.string.split("- DSA Regel Wiki")[0].strip()

        print("  " * level + title)

        subpages = [
            parse(link, getattr(site, "subpages", []), level + 1)
            for link in [
                base + link["href"]
                for link in soup.find_all("a")
                if validate(link) and link not in categories
            ]
        ]

        return {"title": title, "url": url, "hash": soup_hash, "subpages": subpages}
    except:
        print("Skipped: ", url)
        skipped.append(url)
        return {"url": url}


res = requests.get(base)
soup = BeautifulSoup(res.text, "lxml")
categories = [
    base + link["href"] for link in soup.header.nav.find_all("a") if validate(link)
]

with open("regelwiki.json") as sitemap_file:
    sitemap = json.loads(sitemap_file.read())
    for url in categories:
        regelwiki.append(parse(url, sitemap))
        with open("temp.json", "w") as temp:
            temp.write(json.dumps(regelwiki, indent=2) + "\n")

with open("skipped.json", "w") as file:
    file.write(json.dumps(skipped) + "\n")

with open("regelwiki.json", "w") as rw_file:
    rw_file.write(json.dumps(regelwiki, indent=2) + "\n")
    os.remove("temp.json")
