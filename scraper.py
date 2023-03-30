from httpx import Client
from dataclasses import dataclass, asdict
from selectolax.parser import HTMLParser

@dataclass
class Product:
    name:str
    sku:str
    img:str
    price:str


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
        try:
            name = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > h1').text()
        except:
            name = ''
        try:
            sku = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > p').attributes['content']
        except:
            sku = ''
        try:
            img = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > div:nth-child(4) > div:nth-child(1) > img').attributes['data-src']
        except:
            img = ''
        try:
            price = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > p:nth-child(10) > span:nth-child(3)').text()
        except:
            price = ''
        item = Product(name=name, sku=sku, img=img, price=price)
        return asdict(item)


if __name__ == '__main__':
    scraper = shopyfyScraper()
    urls = [f'https://www.80stees.com/a/search?q=chrismas&page={str(page)}' for page in range(1,3)]
    htmls = [scraper.fetch(url) for url in urls]
    detail_urls = []
    for html in htmls:
        detail_urls.extend(scraper.parser(html))
    detail_htmls = [scraper.fetch(url) for url in detail_urls]
    data = [scraper.detail_parser(html) for html in detail_htmls]
    # data = scraper.detail_parser(detail_htmls[0])
    print(data)
    print(len(data))

