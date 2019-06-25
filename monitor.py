#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import requests
import time

from bs4 import BeautifulSoup

def log(s):
    output = "[{time}] {message}".format(time=datetime.now(), message=s)
    print(output)

def main():
    parser = argparse.ArgumentParser(description="Discord Shopify Monitor")
    parser.add_argument("-c", "--config", default="config.json", help="Config file")
    args = parser.parse_args()
    
    config_name = args.config
    with open(config_name) as config_file:
        config = json.load(config_file)
    
    process_config(config)
    

def process_config(config):
    if config['site'].lower() == 'yeezysupply':
        yeezy_monitor(config)
    else:
        print("Sorry, that website is not yet supported")
    
def yeezy_monitor(config):
    url = "https://yeezysupply.com"
    log("Monitoring Yeezy Supply")
    
    while True:
        log("Polling {}".format(url))
        r = requests.get(url)
        
        if "password" in r.url:
            yeezy_password_notify(config["webhook"])
            time.sleep(config['poll'])
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        products_json = soup.find(id='js-featured-json').text
        products = json.loads(products_json)
        
        for product in products["products"]:
            if product["available"] == False or product["type"] == "PLACEHOLDER":
                continue
                
            if contains_keyword(product["title"], config["keywords"]):
                log("Sending notification to Discord")
                yeezy_notify(config["webhook"], "YeezySupply", url, product)
            
        time.sleep(config['poll'])
    
def yeezy_notify(webhook_url, site, site_url, product):
    embed = {
        "title": site,
        "description": product["title"],
        "url": site_url + product["url"],
        "color": 4223072,
        "footer": {"text": "Discord Shopify Monitor by Eric"},
        "thumbnail": {"url": "https:" + product["i_220"]},
        "author": {"name": "Shopify Monitor"},
        "fields": [
            {"name": "Product", "value": product["handle"]},
            {"name": "Price", "value": '${:.2f}'.format(product["price"] / 100)},
        ]
    }
    
    data = {"embeds": [embed]}
    r = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    print(r.text)
    
def yeezy_password_notify(webhook_url):
    embed = {
        "title": "YeezySupply",
        "description": "Password Page is Up!",
        "url": "https://yeezysupply.com",
        "color": 4223072,
        "footer": {"text": "Discord Shopify Monitor by Eric"},
        "author": {"name": "Shopify Monitor"}
    }
    
    data = {"embeds": [embed]}
    r = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    print(r.text)
    
def contains_keyword(text, keywords):
    text = text.lower()
    for word in keywords:
        if word.lower() not in text:
            return False
    
    return True
    
    
if __name__ == "__main__":
    main()