from bs4 import BeautifulSoup
import requests

base = "http://ulisses-regelwiki.de/"
blacklist = [
    "index.php/start.html",
    "index.php/kontakt.html",
    "index.php/impressum.html",
    "index.php/datenschutzerklaerung.html",
]
regelwiki = {}


def validate(link):
    try:
        return (
            link["href"].startswith("index.php")
            and "#" not in link["href"]
            and link["href"] not in blacklist
        )
    except:
        return False


def sitemap(url):
    result = {}
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")
    soup.header.decompose()
    soup.footer.decompose()
    for bc in soup.find_all("div", class_="breadcrumb_boxed"):
        bc.decompose()
    title = soup.title.string.split("- DSA Regel Wiki")[0].strip()

    sub_categories = [
        base + link["href"]
        for link in soup.find_all("a")
        if validate(link) and link not in categories
    ]
    print(title, sub_categories)
    for link in sub_categories:
        t, r = sitemap(link)
        result[t] = r

    if len(sub_categories) > 0:
        return title, result
    return title, url


res = requests.get(base)
soup = BeautifulSoup(res.text, "lxml")
categories = [
    base + link["href"]
    for link in soup.header.nav.find_all("a", limit=3)
    if validate(link)
]
for url in categories:
    title, result = sitemap(url)
    regelwiki[title] = result
print(regelwiki)
