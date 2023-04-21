import time
import csv
import json
from selenium import webdriver
from bs4 import BeautifulSoup

def extract_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', {'type': 'application/ld+json'})

    if script_tag:
        json_data = json.loads(script_tag.string)
        
        context = json_data.get('@context', '')
        _type = json_data.get('@type', '')
        name = json_data.get('name', '')
        image = json_data.get('image', '')
        description = json_data.get('description', '')
        url = json_data.get('url', '')
        width = json_data.get('width', '')
        height = json_data.get('height', '')
        depth = json_data.get('depth', '')
        brand = json_data.get('brand', {}).get('name', '')
        category = json_data.get('category', '')
        production_date = json_data.get('productionDate', '')
        price = json_data.get('offers', {}).get('price', '')
        price_currency = json_data.get('offers', {}).get('priceCurrency', '')
        availability = json_data.get('offers', {}).get('availability', '')

        return [context, _type, name, image, description, url, width, height, depth, brand, category, production_date, price, price_currency, availability]

    return None

urls_csv_filename = 'urls.csv'
urls = []

with open(urls_csv_filename, mode='r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if row:  # Check if the row is not empty
            urls.append(row[0])  # assuming the URL is in the first column


output_csv_filename = 'output2.csv'
failed_urls_csv_filename = 'failed_urls.csv'

for url in urls:
    content_pieces = extract_content(url)
    if content_pieces:
        with open(output_csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(content_pieces)
        print(f"Content written to {output_csv_filename} for URL {url}:")
        print(content_pieces)
    else:
        with open(failed_urls_csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([url])
        print(f"No content found for URL {url}; added to {failed_urls_csv_filename}")
    time.sleep(2)
