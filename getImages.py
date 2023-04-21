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

def main():
    csv_file = 'image_urls.csv'
    download_folder = Path(os.path.expanduser('~/Downloads/ArtsyImages'))

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            url, artist_name, art_piece_name = row
            try:
                download_image(url, download_folder, artist_name, art_piece_name)
                print(f"Downloaded image '{artist_name}_{art_piece_name}' from {url}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image '{artist_name}_{art_piece_name}' from {url}: {e}")

if __name__ == '__main__':
    main()
