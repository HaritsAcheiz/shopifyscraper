from httpx import Client
from dataclasses import dataclass, asdict
from selectolax.parser import HTMLParser
import json
import csv
import os

@dataclass
class Product:
    Handle:str
    Title:str
    Body_HTML:str
    Vendor: str
    Product_Category: str
    Type: str
    Tags: str
    Published: str
    Option1_Name: str
    Option1_Value: str
    Option2_Name: str
    Option2_Value: str
    Option3_Name: str
    Option3_Value: str
    Variant_SKU: str
    Variant_Grams: str
    Variant_Inventory_Tracker: str
    Variant_Inventory_Qty: str
    Variant_Inventory_Policy: str
    Variant_Fulfillment_Service: str
    Variant_Price: str
    Variant_Compare_At_Price: str
    Variant_Requires_Shipping: str
    Variant_Taxable: str
    Variant_Barcode: str
    Image_Src: str
    Image_Position: str
    Image_Alt_Text: str
    Gift_Card: str
    SEO_Title: str
    SEO_Description: str
    Google_Shopping_Google_Product_Category: str
    Google_Shopping_Gender: str
    Google_Shopping_Age_Group: str
    Google_Shopping_MPN:str
    Google_Shopping_AdWords_Grouping: str
    Google_Shopping_AdWords_Labels: str
    Google_Shopping_Condition: str
    Google_Shopping_Custom_Product: str
    Google_Shopping_Custom_Label_0 : str
    Google_Shopping_Custom_Label_1: str
    Google_Shopping_Custom_Label_2: str
    Google_Shopping_Custom_Label_3: str
    Google_Shopping_Custom_Label_4: str
    Variant_Image: str
    Variant_Weight_Unit: str
    Variant_Tax_Code: str
    Cost_per_item: str
    Price_International: str
    Compare_At_Price_International: str
    Status: str

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
            writer.writerow(data)

if __name__ == '__main__':
    scraper = shopyfyScraper()
    urls = [f'https://www.80stees.com/a/search?q=chrismas&page={str(page)}' for page in range(1,3)]
    htmls = [scraper.fetch(url) for url in urls]
    detail_urls = []
    for html in htmls:
        detail_urls.extend(scraper.parser(html))
    detail_htmls = [scraper.fetch(url) for url in detail_urls]
    data = [scraper.to_csv(scraper.detail_parser(html), filename='result.csv') for html in detail_htmls]
    # data = scraper.detail_parser(detail_htmls[0])

