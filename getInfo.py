import time
import csv
import re
import json
from selenium import webdriver
from bs4 import BeautifulSoup

def extract_content(url):
    # create a new Chrome web driver
    driver = webdriver.Chrome()

    # navigate to the URL
    driver.get(url)

    # wait for the page to fully load
    time.sleep(5)  # increase the wait time to 5 seconds

    # get the HTML content of the page
    html = driver.page_source

    # close the browser window
    driver.quit()

    # parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # find the meta tag with the desired data
    meta_tag = soup.find('meta', {'name': 'description'})

    # get the content attribute of the meta tag
    content = meta_tag['content'] if meta_tag else None

    # find the script tag containing the JSON data
    script_tag = soup.find('script', {'type': 'application/ld+json'})

    if content and script_tag:
        # load the JSON data from the script tag
        json_data = json.loads(script_tag.string)

        # extract the productionDate and price from the JSON data
        production_date = json_data.get('productionDate', '')
        price = json_data.get('offers', {}).get('price', '')

        # match the different parts of the content string using regular expressions
        match = re.match(r'(.*?), (.*?), (.*?)( \((\d{4})\))?, (.*?)(, )?(\d+(/| )?(1/)?\d? × \d+ in)', content)
        if match:
            return list(match.groups()[0:3]) + [match.groups()[4]] + list(match.groups()[5:7]) + [match.groups()[8]] + [production_date, price]
    return None

# Read URLs from the urls.csv file
urls_csv_filename = 'urls.csv'
urls = []

with open(urls_csv_filename, mode='r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        urls.append(row[0])  # assuming the URL is in the first column

# Loop through the URLs and extract data
output_csv_filename = 'output.csv'
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
    time.sleep(5)  # add a delay of 2 seconds between requests to avoid rate limiting or blocking
