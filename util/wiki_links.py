import json

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


def remove_other(soup):
    soup.header.decompose()
    soup.footer.decompose()
    for bc in soup.find_all("div", class_="breadcrumb_boxed"):
        bc.decompose()
    for content in soup.find_all("div", id="main"):
        content.decompose()


def find_page(url, sitemap):
    for site in sitemap:
        if site.url == url:
            return site


def parse(url, sitemap, level=0):
    try:
        res = requests.get(url)
        page_hash = hash(res.text)

        site = find_page(url, sitemap)
        if site:
            if site.hash == page_hash:
                return site
            else:
                sitemap = site.subpages
        else:
            sitemap = []

        soup = BeautifulSoup(res.text, "lxml")
        remove_other(soup)

        title = soup.title.string.split("- DSA Regel Wiki")[0].strip()

        print("  " * level + title)

        subpages = [
            parse(link, sitemap, level + 1)
            for link in [
                base + link["href"]
                for link in soup.find_all("a")
                if validate(link) and link not in categories
            ]
        ]

        return {"title": title, "url": url, "hash": page_hash, "subpages": subpages}
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Skipped: ", url)
        skipped.append(url)
        return {"url": url}


with open("regelwiki.json") as sitemap_file:
    sitemap = json.loads(sitemap_file.read())
    print(sitemap)
    res = requests.get(base)
    soup = BeautifulSoup(res.text, "lxml")
    categories = [
        base + link["href"]
        for link in soup.header.nav.find_all("a", limit=4)
        if validate(link)
    ]

    try:
        for url in categories:
            print("Category: ", url)
            regelwiki.append(parse(url, sitemap))
    except:
        pass

    with open("regelwiki.json", "w") as file:
        file.write(json.dumps(regelwiki, indent=2))
    with open("skipped.json", "w") as file:
        file.write(json.dumps(skipped))
