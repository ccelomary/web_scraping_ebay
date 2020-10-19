#!/bin/bash
sudo apt update
sudo apt install python3.8
sudo apt install python3-pip
pip3 install requests pillow bs4
clear
echo  "Usage:
                ./ebay_scrap_items.py 'search_keyword'
        " 