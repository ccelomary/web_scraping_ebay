#!/bin/env python3.8
"""
AUTHOR: Celomary
TOPIC:  WEB SCRAPING EXAMPLE
"""
from io import BytesIO
from bs4 import BeautifulSoup as soup
from random import choices
from string import ascii_letters, digits
import requests
from PIL import Image
from sys import argv
import os
import shutil
import csv, json, xml.etree.ElementTree as et
from datetime import datetime as dt

BASE_DIR = os.path.split(os.path.abspath('__file__'))[0]
FIELDS = ('title', 'price', 'image', 'shipping', 'watchers')
TEXT_TO_CHOOSE = ascii_letters + digits

def createdir(name):
    path = os.path.join(BASE_DIR, name)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    return path

def download_image(image_url, dest):
    response = requests.get(image_url, stream=True)
    image = Image.open(BytesIO(response.content))
    image = image.resize((200, 200))
    name = ''.join(choices(TEXT_TO_CHOOSE, k=15)) + '.' + image_url.split('.')[-1]
    image_path = os.path.join(dest, name)
    image.save(image_path)
    return image_path

url = "https://www.ebay.com/sch/i.html"
parameter = {"_nkw": argv[1]}

def get_data_from_site(home_dir):
    response = requests.get(url, parameter, stream=True)
    sp = soup(response.content, 'html.parser')
    sitems = sp.find_all('li', attrs={'class': 's-item'})
    image_path_folder = os.path.join(home_dir, 'images')
    if os.path.exists(image_path_folder):
        shutil.rmtree(image_path_folder)
    os.mkdir(image_path_folder)
    for item in sitems:
        if img := item.find('img', attrs={'class': 's-item__image-img'}):
            src = img.attrs.get('src')
            title = item.find('h3', attrs={'class': 's-item__title'}).text
            price = item.find('span', attrs={'class': 's-item__price'}).text
            if watchers := item.find('span', attrs={'class': 's-item__hotness s-item__itemHotness'}):
                watchers = watchers.text
            if shipping := item.find('span', attrs={'class': 's-item__shipping s-item__logisticsCost'}):
                shipping = shipping.text
            image_path = download_image(src, image_path_folder)
            yield (title, price, image_path, shipping, watchers)

def put_csv_file(data, home_dir):
    with open(os.path.join(home_dir, argv[1] + '.csv'),'w') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter=',')
        writer.writeheader()
        for line in data:
            writer.writerow(dict(zip(FIELDS, line)))

def put_json_file(data, home_dir):
    json_data = json.dumps([dict(zip(FIELDS, line)) for line in data], indent=4)
    with open(os.path.join(home_dir, argv[1] + '.json'), 'w') as f:
        f.write(json_data)

def put_xml_file(data, home_dir):
    parent = et.Element(argv[1])
    for line in data:
        sub_parent = et.SubElement(parent, 'data')
        for field, item in zip(FIELDS, line):
            sub_data = et.SubElement(sub_parent, field)
            sub_data.text = item
    xml_text = et.tostring(parent)
    with open(os.path.join(home_dir, argv[1] + '.xml'), 'wb') as f:
        f.write(xml_text)

            
if '__main__' == __name__:
    home_dir = createdir(dt.strftime(dt.now(), '%d_%B_%Y_%I_%M_%p'))
    data = list(get_data_from_site(home_dir))
    put_csv_file(data, home_dir)
    put_json_file(data, home_dir)
    put_xml_file(data, home_dir)