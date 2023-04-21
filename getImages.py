import os
import csv
import requests
from pathlib import Path
from urllib.parse import urlparse

def sanitize_image_name(image_name):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        image_name = image_name.replace(char, '_')
    return image_name

def download_image(url, save_path, artist_name, art_piece_name):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    file_ext = os.path.splitext(urlparse(url).path)[-1]

    if not file_ext:
        file_ext = '.jpg'  # Fallback file extension

    artist_name = sanitize_image_name(artist_name)
    art_piece_name = sanitize_image_name(art_piece_name)
    file_name = f"{artist_name}_{art_piece_name}{file_ext}"

    with open(save_path / file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def save_failed_url(url):
    with open('failed_urls.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url])

def save_skipped_row(row):
    with open('info.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

# used for inspection if there are many urls in dataset 
def save_summary(row_num, row, status):
    with open('summary.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([row_num, row, status])

def main():
    csv_file = 'image_urls.csv'
    download_folder = Path(os.path.expanduser('~/Downloads'))

    downloaded_urls = set()

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row_num, row in enumerate(reader, start=1):
            print(f"Processing row {row_num}: {row}")

            # error handling 
            if len(row) != 3:
                print(f"Skipping row {row_num} due to missing data")
                save_skipped_row(row)
                save_summary(row_num, row, 'skipped (missing data)')
                continue

            url, artist_name, art_piece_name = row

            if url in downloaded_urls:
                print(f"Skipping row {row_num} due to duplicate URL: {url}")
                save_skipped_row(row)
                save_summary(row_num, row, 'skipped (duplicate URL)')
                continue

            try:
                download_image(url, download_folder, artist_name, art_piece_name)
                downloaded_urls.add(url)
                print(f"Downloaded image '{artist_name}_{art_piece_name}' from {url}")
                save_summary(row_num, row, 'success')
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image '{artist_name}_{art_piece_name}' from {url}: {e}")
                save_failed_url(url)
                save_summary(row_num, row, 'failed')

if __name__ == '__main__':
    main()
