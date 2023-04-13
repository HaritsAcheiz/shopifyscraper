from httpx import Client
from dataclasses import dataclass
from selectolax.parser import HTMLParser
import csv
import os
from typing import List
import re
from google.cloud.sql.connector import Connector
import sqlalchemy

@dataclass
class shopifyScraper:
    base_url: str
    category: List[str]
    cred_path: str


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
        items = []
        child = tree.css('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > div:nth-of-type(2) > section > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(1) > ul:nth-of-type(2) > li')
        for variant in child:
            try:
                title = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > h1').text().strip()
                handle = title.lower().replace(' ','-')
                # sku = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > p').attributes['content']
                vsku = variant.css_first('a').attributes['data-vsku']
                img = tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > div:nth-child(4) > div:nth-child(1) > img').attributes['data-src']
                # price = float(re.findall("\d+\.\d+",tree.css_first('html > body > div:nth-child(7) > div:nth-child(2) > main > div:nth-child(9) > section > div > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > p:nth-child(10) > span:nth-child(3)').text()))
                price = float(re.findall("\d+\.\d+",variant.css_first('a').attributes['data-vprice'])[0])
                description = f"<p>{tree.css_first('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > section > div > div').child.html}</p>"
                # vendor = '80stees'
                product_type = tree.css_first('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > section:nth-of-type(4) > div > div > div:nth-of-type(1) > span:nth-of-type(1)').text().strip()
                product_category = 'Apparel & Accessories > Clothing > Shirts'
                for cat in self.category:
                    if product_type in cat:
                        product_category = cat
                        break
                tags = "shirt, hoodies, sweaters, sweatshirts, t-shirts"
                color = tree.css_first('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > section:nth-of-type(4) > div > div > div:nth-of-type(1) > span:nth-of-type(2)').text().strip()
                gender = tree.css_first('html > body > div:nth-of-type(5) > div:nth-of-type(2) > main > section:nth-of-type(4) > div > div > div:nth-of-type(2) > span:nth-of-type(1)').text().strip()
                size = variant.css_first('a').text().strip()
                item = {
                    'Handle':handle, 'Title':title, 'Body(HTML)':description, 'Vendor':'My Store', 'Product Category':product_category,
                    'Type':product_type, 'Tags':tags, 'Published':True, 'Option1 Name':'color', 'Option1 Value':color, 'Option2 Name':'gender',
                    'Option2 Value':gender, 'Option3 Name':'size', 'Option3 Value':size, 'Variant SKU':vsku, 'Variant Grams':200,
                    'Variant Inventory Tracker':'', 'Variant Inventory Qty':10, 'Variant Inventory Policy':'deny',
                    'Variant Fulfillment Service':'manual', 'Variant Price':price, 'Variant Compare At Price':price,
                    'Variant Requires Shipping':True, 'Variant Taxable':True, 'Variant Barcode':'', 'Image Src':img,
                    'Image Position':1, 'Image Alt Text':'', 'Gift Card':True, 'SEO Title':'', 'SEO Description':'',
                    'Google Shopping / Google Product Category':product_category, 'Google Shopping / Gender':gender,
                    'Google Shopping / Age Group':'', 'Google Shopping / MPN':'',
                    'Google Shopping / AdWords Grouping':'', 'Google Shopping / AdWords Labels':'',
                    'Google Shopping / Condition':'New', 'Google Shopping / Custom Product':'',
                    'Google Shopping / Custom Label 0':'', 'Google Shopping / Custom Label 1':'',
                    'Google Shopping / Custom Label 2':'', 'Google Shopping / Custom Label 3':'',
                    'Google Shopping / Custom Label 4':'', 'Variant Image':'', 'Variant Weight Unit':'g',
                    'Variant Tax Code':'', 'Cost per item':'', 'Price / International':price, 'Compare At Price / International':'',
                    'Status':'active'}
                items.append(item)
            except Exception as e:
                print(e)
        return items

    def to_csv(self, datas, filename):
        try:
            for data in datas:
                for child in data:
                    try:
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
                            if child != None:
                                writer.writerow(child)
                            else:
                                pass
                    except Exception as e:
                        print(e)
                        continue
        except:
            pass

    def to_db(self, datas):
        connector = Connector()

        def getconn():
            conn = connector.connect(
                "river-nectar-383405:asia-southeast2:myteesdb",
                "pg8000",
                user="harits",
                password="mitsutani",
                db="myteesdb"
            )
            return conn

        pool = sqlalchemy.create_engine(
            "postgresql+pg8000://harits:mitsutani@34.101.171.107/myteesdb",
            creator=getconn
        )

        # connect to connection pool
        with pool.connect() as db_conn:
            # create products table in our sandwiches database
            # db_conn.execute(
            #     sqlalchemy.text(
            #         '''
            #         CREATE TABLE IF NOT EXISTS products
            #         ("Handle" VARCHAR(255) NOT NULL,
            #         "Title" VARCHAR(255) NOT NULL,
            #         "Body(HTML)" TEXT NOT NULL,
            #         "Vendor" VARCHAR(255) NOT NULL,
            #         "Product Category" VARCHAR(255) NOT NULL,
            #         "Type" VARCHAR(255) NOT NULL,
            #         "Tags" VARCHAR(255) NOT NULL,
            #         "Published" BOOLEAN NOT NULL,
            #         "Option1 Name" VARCHAR(255),
            #         "Option1 Value" VARCHAR(255),
            #         "Option2 Name" VARCHAR(255),
            #         "Option2 Value" VARCHAR(255),
            #         "Option3 Name" VARCHAR(255),
            #         "Option3 Value" VARCHAR(255),
            #         "Variant SKU" VARCHAR(255),
            #         "Variant Grams" SMALLINT NOT NULL,
            #         "Variant Inventory Tracker" VARCHAR(255),
            #         "Variant Inventory Qty" INT NOT NULL,
            #         "Variant Inventory Policy" VARCHAR(255),
            #         "Variant Fulfillment Service" VARCHAR(255),
            #         "Variant Price" FLOAT NOT NULL,
            #         "Variant Compare At Price" FLOAT NOT NULL,
            #         "Variant Requires Shipping" BOOLEAN NOT NULL,
            #         "Variant Taxable" BOOLEAN NOT NULL,
            #         "Variant Barcode" VARCHAR(255),
            #         "Image Src" TEXT NOT NULL,
            #         "Image Position" INT,
            #         "Image Alt Text" TEXT,
            #         "Gift Card" BOOLEAN NOT NULL,
            #         "SEO Title" VARCHAR(255),
            #         "SEO Description" TEXT,
            #         "Google Shopping / Google Product Category" VARCHAR(255),
            #         "Google Shopping / Gender" VARCHAR(255),
            #         "Google Shopping / Age Group" VARCHAR(255),
            #         "Google Shopping / MPN" VARCHAR(255),
            #         "Google Shopping / AdWords Grouping" VARCHAR(255),
            #         "Google Shopping / AdWords Labels" VARCHAR(255),
            #         "Google Shopping / Condition" VARCHAR(255),
            #         "Google Shopping / Custom Product" VARCHAR(255),
            #         "Google Shopping / Custom Label 0" VARCHAR(255),
            #         "Google Shopping / Custom Label 1" VARCHAR(255),
            #         "Google Shopping / Custom Label 2" VARCHAR(255),
            #         "Google Shopping / Custom Label 3" VARCHAR(255),
            #         "Google Shopping / Custom Label 4" VARCHAR(255),
            #         "Variant Image" TEXT NOT NULL,
            #         "Variant Weight Unit" VARCHAR(255) NOT NULL,
            #         "Variant Tax Code" VARCHAR(255),
            #         "Cost per item" FLOAT NOT NULL,
            #         "Price / International" FLOAT NOT NULL,
            #         "Compare At Price / International" FLOAT NOT NULL,
            #         "Status" VARCHAR(255) NOT NULL);
            #         '''
            #     )
            # )
            #
            # # commit transaction (SQLAlchemy v2.X.X is commit as you go)
            # db_conn.commit()
            #
            # # insert data into our ratings table
            # for page in datas:
            #     for data in page:
            #         insert_stmt = sqlalchemy.text(
            #             '''INSERT INTO products ("Handle", "Title", "Body(HTML)","Vendor", "Product Category", "Type", "Tags",
            #             "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value",
            #             "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
            #             "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", "Variant Requires Shipping",
            #             "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Gift Card",
            #             "SEO Title", "SEO Description", "Google Shopping / Google Product Category", "Google Shopping / Gender",
            #             "Google Shopping / Age Group", "Google Shopping / MPN", "Google Shopping / AdWords Grouping",
            #             "Google Shopping / AdWords Labels", "Google Shopping / Condition", "Google Shopping / Custom Product",
            #             "Google Shopping / Custom Label 0", "Google Shopping / Custom Label 1", "Google Shopping / Custom Label 2",
            #             "Google Shopping / Custom Label 3", "Google Shopping / Custom Label 4", "Variant Image", "Variant Weight Unit",
            #             "Variant Tax Code", "Cost per item", "Price / International", "Compare At Price / International", "Status")
            #             VALUES (:handle, :title, :body, :vendor, :product_category, :type, :tags, :published, :option1_name, :option1_value,
            #             :option2_name, :option2_value, :option3_name, :option3_value, :variant_sku, :variant_grams, :variant_inventory_tracker,
            #             :variant_inventory_qty, :variant_inventory_policy, :variant_fulfillment_service, :variant_price, :variant_compare_at_price,
            #             :variant_requires_shipping, :variant_taxable, :variant_barcode, :image_src, :image_position, :image_alt_text,
            #             :gift_card, :seo_title, :seo_description, :google_shopping_google_product_category, :google_shopping_gender,
            #             :google_shopping_age_group, :google_shopping_MPN, :google_shopping_adWords_grouping, :google_shopping_adWords_labels,
            #             :google_shopping_condition, :google_shopping_custom_product, :google_shopping_custom_label_0, :google_shopping_custom_label_1,
            #             :google_shopping_custom_label_2, :google_shopping_custom_label_3, :google_shopping_custom_label_4, :variant_image,
            #             :variant_weight_unit, :variant_tax_code, :cost_per_item, :price_international, :compare_at_price_International, :status)
            #             '''
            #         )
            #
            #     # insert entries into table
            #         db_conn.execute(insert_stmt, parameters={
            #             "handle":data["Handle"],
            #             "title":data["Title"],
            #             "body":data["Body(HTML)"],
            #             "vendor":data["Vendor"],
            #             "product_category":data["Product Category"],
            #             "type":data["Type"],
            #             "tags":data["Tags"],
            #             "published":data["Published"],
            #             "option1_name":data["Option1 Name"],
            #             "option1_value":data["Option1 Value"],
            #             "option2_name":data["Option2 Name"],
            #             "option2_value":data["Option1 Value"],
            #             "option3_name":data["Option3 Name"],
            #             "option3_value":data["Option1 Value"],
            #             "variant_sku":data["Variant SKU"],
            #             "variant_grams":data["Variant Grams"],
            #             "variant_inventory_tracker":data["Variant Inventory Tracker"],
            #             "variant_inventory_qty":data["Variant Inventory Qty"],
            #             "variant_inventory_policy":data["Variant Inventory Policy"],
            #             "variant_fulfillment_service":data["Variant Fulfillment Service"],
            #             "variant_price":data["Variant Price"],
            #             "variant_compare_at_price":data["Variant Compare At Price"],
            #             "variant_requires_shipping":data["Variant Requires Shipping"],
            #             "variant_taxable":data["Variant Taxable"],
            #             "variant_barcode":data["Variant Barcode"],
            #             "image_src":data["Image Src"],
            #             "image_position":data["Image Position"],
            #             "image_alt_text":data["Image Alt Text"],
            #             "gift_card":data["Gift Card"],
            #             "seo_title":data["SEO Title"],
            #             "seo_description":data["SEO Description"],
            #             "google_shopping_google_product_category":data["Google Shopping / Google Product Category"],
            #             "google_shopping_gender":data["Google Shopping / Gender"],
            #             "google_shopping_age_group":data["Google Shopping / Age Group"],
            #             "google_shopping_MPN":data["Google Shopping / MPN"],
            #             "google_shopping_adWords_grouping":data["Google Shopping / AdWords Grouping"],
            #             "google_shopping_adWords_labels":data["Google Shopping / AdWords Labels"],
            #             "google_shopping_condition":data["Google Shopping / Condition"],
            #             "google_shopping_custom_product":data["Google Shopping / Custom Product"],
            #             "google_shopping_custom_label_0":data["Google Shopping / Custom Label 0"],
            #             "google_shopping_custom_label_1":data["Google Shopping / Custom Label 1"],
            #             "google_shopping_custom_label_2":data["Google Shopping / Custom Label 2"],
            #             "google_shopping_custom_label_3":data["Google Shopping / Custom Label 3"],
            #             "google_shopping_custom_label_4":data["Google Shopping / Custom Label 4"],
            #             "variant_image":data["Variant Image"],
            #             "variant_weight_unit":data["Variant Weight Unit"],
            #             "variant_tax_code":data["Variant Tax Code"],
            #             "cost_per_item":data["Cost per item"],
            #             "price_international":data["Price / International"],
            #             "compare_at_price_International":data["Compare At Price / International"],
            #             "status":data["Status"]})
            #
            #         # commit transactions
            #         db_conn.commit()

            # query and fetch ratings table
            results = db_conn.execute(sqlalchemy.text("SELECT * FROM products")).fetchall()

            # show results
            for row in results:
                print(row)

if __name__ == '__main__':
    base_url = 'https://www.80stees.com'
    cred_path = r'C:\Users\Muhammad Harits R\AppData\Roaming\gcloud\application_default_credentials.json'
    cat_file = open("category.txt", "r")
    cat = cat_file.read()
    cat_file.close()
    cat_list = cat.split("\n")
    scraper = shopifyScraper(base_url=base_url, category=cat_list, cred_path=cred_path)
    # urls = [f'https://www.80stees.com/a/search?q=chrismas&page={str(page)}' for page in range(1,5)]
    # htmls = [scraper.fetch(url) for url in urls]
    # detail_urls = []
    # for html in htmls:
    #     detail_urls.extend(scraper.parser(html))
    # detail_htmls = [scraper.fetch(url) for url in detail_urls]
    # data = [scraper.detail_parser(html) for html in detail_htmls]
    # scraper.to_csv(data,filename='result.csv')
    # data = scraper.detail_parser(detail_htmls[0])
    data = list()
    scraper.to_db(data)