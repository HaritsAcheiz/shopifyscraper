from httpx import Client
from dataclasses import dataclass, asdict
from selectolax.parser import HTMLParser
import json
import csv
import os
from typing import List

@dataclass
class shopyfyScraper:
    base_url: str
    category: List[str]

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
        item = None
        try:
            title = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > h1').text().strip()
            handle = title.lower().replace(' ','-')
            sku = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > p').attributes['content']
            img = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > div:nth-child(4) > div:nth-child(1) > img').attributes['data-src']
            price = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > p:nth-child(10) > span:nth-child(3)').text()
            description = f"<p>{tree.css_first('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > section > div > div').child.html}</p>"
            vendor = '80stees'
            product_type = tree.css_first('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > section:nth-of-type(4) > div > div > div:nth-of-type(1) > span:nth-of-type(1)').text().strip()
            product_category = 'Apparel & Accessories > Clothing > Shirts'
            for cat in self.category:
                if product_type in cat:
                    product_category = cat
                    break
            tags = "shirt, hoodies, sweaters, sweatshirts, t-shirts"
            item = {
                'Handle':handle, 'Title':title, 'Body(HTML)':description, 'Vendor':vendor, 'Product Category':product_category,
                'Type':product_type, 'Tags':tags, 'Published':'', 'Option1 Name':'', 'Option1 Value':'', 'Option2 Name':'',
                'Option2 Value':'', 'Option3 Name':'', 'Option3 Value':'', 'Variant SKU':sku, 'Variant Grams':'',
                'Variant Inventory Tracker':'', 'Variant Inventory Qty':'', 'Variant Inventory Policy':'',
                'Variant Fulfillment Service':'', 'Variant Price':'', 'Variant Compare At Price':'',
                'Variant Requires Shipping':'', 'Variant Taxable':'', 'Variant Barcode':'', 'Image Src':img,
                'Image Position':'', 'Image Alt Text':'', 'Gift Card':'', 'SEO Title':'', 'SEO Description':'',
                'Google Shopping / Google Product Category':'', 'Google Shopping / Gender':'',
                'Google Shopping / Age Group':'', 'Google Shopping / MPN':'',
                'Google Shopping / AdWords Grouping':'', 'Google Shopping / AdWords Labels':'',
                'Google Shopping / Condition':'', 'Google Shopping / Custom Product':'',
                'Google Shopping / Custom Label 0':'', 'Google Shopping / Custom Label 1':'',
                'Google Shopping / Custom Label 2':'', 'Google Shopping / Custom Label 3':'',
                'Google Shopping / Custom Label 4':'', 'Variant Image':'', 'Variant Weight Unit':'',
                'Variant Tax Code':'', 'Cost per item':'', 'Price / International':price, 'Compare At Price / International':'',
                'Status':''}
        except Exception as e:
            print(e)
        return item

    def to_csv(self, data, filename):
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', encoding='utf-16') as f:
            headers = ['Handle', 'Title', 'Body(HTML)', 'Vendor', 'Product Category', 'Type', 'Tags',
                       'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
                       'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker',
                       'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service',
                       'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable',
                       'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card',
                       'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category',
                       'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN',
                       'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels',
                       'Google Shopping / Condition', 'Google Shopping / Custom Product',
                       'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1',
                       'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3',
                       'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit',
                       'Variant Tax Code', 'Cost per item', 'Price / International', 'Compare At Price / International',
                       'Status']
            writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            if data != None:
                writer.writerow(data)
            else:
                pass

if __name__ == '__main__':
    base_url = 'https://www.80stees.com'
    cat_file = open("category.txt", "r")
    cat = cat_file.read()
    cat_file.close()
    cat_list = cat.split("\n")
    scraper = shopyfyScraper(base_url=base_url, category=cat_list)
    urls = [f'https://www.80stees.com/a/search?q=chrismas&page={str(page)}' for page in range(1,3)]
    htmls = [scraper.fetch(url) for url in urls]
    detail_urls = []
    for html in htmls:
        detail_urls.extend(scraper.parser(html))
    detail_htmls = [scraper.fetch(url) for url in detail_urls]
    data = [scraper.to_csv(scraper.detail_parser(html), filename='result.csv') for html in detail_htmls]
    # data = scraper.detail_parser(detail_htmls[0])

