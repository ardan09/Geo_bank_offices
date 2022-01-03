# -*- coding: utf-8 -*-

import requests      
import numpy as np   
import pandas as pd  
import re
import math
import time  
import random 
from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
# UserAgent().chrome
from selenium.common.exceptions import WebDriverException

driver = webdriver.Chrome("chromedriver.exe")

def get_url(page, region):
    url = 'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=2&p='+ str(page) + '&region=' +  str(region)
    return url

def get_content(response):
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    return soup

def find_num(text):
    ans = ''.join(re.findall(r'[0-9.]*[0-9]+', text))
    if ans == '':
        return 0
    else:
        return float(ans)

def offer_count(soup):
    n_offers = find_num(soup.html.head.title.text)
    return n_offers

def get_url_list(soup):
    OfferCards = soup.find_all('div', {'data-name': 'CommercialOfferCard'})
    url_list = []
    for i in range(len(OfferCards)):
        url = soup.find_all('a', {'class': 'c6e8ba5398--header-link--3XZlV'}, href=True)[i]['href']
        url_list.append(url)
    return url_list

def get_adress(html_list):
    html_list = html_list.find_all('address', {'class': 'a10a3f92e9--address--140Ec'})
    adress_clean = []
    adress = html_list[0].find_all('a')
    for i in adress:
        adress_clean.append(i.text)
    return ", ".join(adress_clean)


def get_price_area(soup, address, url):
    adress = address
    url = url
    prices = soup.find_all('div', {'data-name': 'AreaParts'})
    all_trade = pd.DataFrame({"address":[], "area":[], "metr_price":[],"price":[], "url":[]}) 
    dict_tz = {}
    
    if len(prices) > 0:  
        for i in range(1, len(prices)):           
            area = prices[i].find_all('div', {'class': 'a10a3f92e9--area--3Ti0u'})[0].text
            metr_price = prices[i].find_all('div', {'class': 'a10a3f92e9--price-of-meter--1EZnw'})[0].text
            price = prices[i].find_all('div', {'class': 'a10a3f92e9--price--23kex'})[0].text                       
            dict_tz["address"] = adress
            dict_tz["area"] = area
            dict_tz["metr_price"] = metr_price
            dict_tz["price"] = price
            dict_tz["url"] = url
            all_trade = all_trade.append(pd.DataFrame([dict_tz]))
            
    else: 
        area = soup.find_all('div', {'class': 'a10a3f92e9--info-value--18c8R'})[0].text
        metr_price = soup.find_all('div', {'a10a3f92e9--price_per_meter--hKPtN a10a3f92e9--price_per_meter--commercial--1CGBC'})[0].text
        price = soup.find_all('div', {'class': 'a10a3f92e9--value--2rq_x'})[0].text
        dict_tz["address"] = adress
        dict_tz["area"] = area
        dict_tz["metr_price"] = metr_price
        dict_tz["price"] = price
        dict_tz["url"] = url
        all_trade = all_trade.append(pd.DataFrame([dict_tz]))
        
    return all_trade

regions_code_zian = {'25ulan_ude':5056} #{'01msc':1}

cities = list(regions_code_zian.keys())
cities.sort()
cities = cities

for city in cities:
    all_trade_points = pd.DataFrame({"address":[], "area":[], "metr_price":[],"price":[], "url":[]})
    region = regions_code_zian[city]
    try:
        response = driver.get(get_url(1, region))
    except WebDriverException:
        driver.quit()
        driver = webdriver.Chrome("chromedriver.exe")
        response = driver.get(get_url(1, region))
        
    soup = get_content(response)
    num_pages = int(offer_count(soup) / 25 + 1)
    if num_pages == 1:
        inp = input()
    print (city, " ", str(num_pages)," страниц")
    for page in range(1, num_pages + 1):
        print(str(page)," страница")
        try:
            response = driver.get(get_url(page, region))
        except WebDriverException:
            driver.quit()
            driver = webdriver.Chrome("chromedriver.exe")
            response = driver.get(get_url(page, region))
        soup = get_content(response)
        url_list = get_url_list(soup)
        if len(url_list) == 0:
            continue
        for url in url_list:
            try:
                response = driver.get(url)
            except WebDriverException:
                driver.quit()
                driver = webdriver.Chrome("chromedriver.exe")
                response = driver.get(url)
            soup = get_content(response)          
            try:
                address = get_adress(soup)
                all_trade = get_price_area(soup, address, url)
                all_trade_points = all_trade_points.append(all_trade, ignore_index = True)
            except (ValueError, IndexError) as e:
#                 inp = input()
                continue
            time.sleep(random.randrange(10,12))
        all_trade_points.to_csv("trade_1" + city + ".csv", sep = ";", encoding='utf-8-sig')
        print (all_trade_points)
        time.sleep(random.randrange(10,15))
    time.sleep(random.randrange(10,20))

all_trade_points.to_csv("trade_" + city + ".csv", sep = ";", encoding='utf-8-sig')

all_trade_points['url'][1]

driver.close()
driver.quit()