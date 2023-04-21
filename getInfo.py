import csv
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def extract_content(url):
    driver.get(url)

    try:
        # Wait for the presence of the meta tag with name="description"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[name="description"]')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content = soup.find('meta', {'name': 'description'})['content']
        script_tag = soup.find('script', {'type': 'application/ld+json'})

    except Exception as e:
        print(f"Error while waiting for element: {e}")
        return None

    if content and script_tag:
        json_data = json.loads(script_tag.string)
        production_date = json_data.get('productionDate', '')
        price = json_data.get('offers', {}).get('price', '')

        match = re.match(r'(.*?), (.*?), (.*?)( \((\d{4})\))?, (.*?)(, )?(\d+(/| )?(1/)?\d? × \d+ in)', content)
        if match:
            return list(match.groups()[0:3]) + [match.groups()[4]] + list(match.groups()[5:7]) + [match.groups()[8]] + [production_date, price]

    return None

chrome_options = Options()

# Add arguments to simulate a regular user browser
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

# Initialize the Chrome web driver with the added options
driver = webdriver.Chrome(options=chrome_options)

# Read the URLs from the "urls.csv" file
urls = []
with open('urls.csv', mode='r', newline='', encoding='utf-8') as infile:
    csv_reader = csv.reader(infile)
    for row in csv_reader:
        urls.append(row[0])

# Define the output and failed URLs CSV filenames
output_csv_filename = 'output.csv'
failed_csv_filename = 'failed_urls.csv'

# Loop through the URLs and extract the content
for url in urls:
    data = extract_content(url)
    if data:
        with open(output_csv_filename, mode='a', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(data)
    else:
        print(f"No content found for URL {url}")
        with open(failed_csv_filename, mode='a', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow([url])

# Close the browser window
driver.quit()
