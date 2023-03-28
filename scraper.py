from httpx import Client
from dataclasses import dataclass
from selectolax.parser import HTMLParser

@dataclass
class Product:
    name:str

@dataclass
class shopyfyScraper:
    base_url: str = 'https://www.80stees.com'
    def fetch(self, url):
        client = Client()
        response = client.get(url)
        client.close()
        return response.text

    def parser(self, html):
        tree = HTMLParser(html)
        products = tree.css('html > body > div:nth-child(6) > div:nth-child(2) > main > div:nth-child(5) > div > div')
        urls = []
        for product in products:
            url = self.base_url + product.css_first('a').attributes['href']
            urls.append(url)
        return urls

    def detail_parser(self, html):
        tree = HTMLParser(html)
        Product.name = tree.css_first('html > body > div:nth-child(5) > div:nth-child(2) > main > div:nth-child(2) > section > div > h1').text()
        return Product.name

if __name__ == '__main__':
    scraper = shopyfyScraper()
    urls = [f'https://www.80stees.com/a/search?q=chrismas&page={str(page)}' for page in range(1,2)]
    htmls = [scraper.fetch(url) for url in urls]
    detail_urls = []
    for html in htmls:
        detail_urls.extend(scraper.parser(html))
    detail_htmls = [scraper.fetch(url) for url in detail_urls]
    data = [scraper.detail_parser(html) for html in htmls]
    print(data)
    print(len(data))

